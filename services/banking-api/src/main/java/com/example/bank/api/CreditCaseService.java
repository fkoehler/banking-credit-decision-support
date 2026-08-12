package com.example.bank.api;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.security.Principal;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class CreditCaseService {
    private final CreditCaseRepository caseRepository;
    private final AssessmentRepository assessmentRepository;
    private final HumanDecisionRepository decisionRepository;
    private final AiClient aiClient;
    private final ObjectMapper objectMapper;

    CreditCaseService(CreditCaseRepository caseRepository, AssessmentRepository assessmentRepository,
                      HumanDecisionRepository decisionRepository, AiClient aiClient, ObjectMapper objectMapper) {
        this.caseRepository = caseRepository;
        this.assessmentRepository = assessmentRepository;
        this.decisionRepository = decisionRepository;
        this.aiClient = aiClient;
        this.objectMapper = objectMapper;
    }

    @Transactional
    ApiModels.CaseResponse create(ApiModels.CreateCaseRequest request) {
        return toResponse(caseRepository.save(new CreditCase(request)));
    }

    @Transactional(readOnly = true)
    ApiModels.CaseResponse get(UUID id) {
        return toResponse(findCase(id));
    }

    @Transactional
    ApiModels.AssessmentResponse assess(UUID caseId, String correlationId) {
        CreditCase creditCase = findCase(caseId);
        AiClient.AiAssessment result = aiClient.assess(creditCase, correlationId);
        try {
            Assessment saved = assessmentRepository.save(new Assessment(
                caseId, result, correlationId,
                objectMapper.writeValueAsString(result.positiveFactors()),
                objectMapper.writeValueAsString(result.riskFactors()),
                objectMapper.writeValueAsString(result.citations())
            ));
            creditCase.markPendingReview();
            caseRepository.save(creditCase);
            return toAssessment(saved);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("Could not persist AI result", e);
        }
    }

    @Transactional
    ApiModels.DecisionResponse decide(UUID caseId, ApiModels.DecisionRequest request, Principal principal) {
        CreditCase creditCase = findCase(caseId);
        CreditCase.CaseStatus status;
        try {
            status = CreditCase.CaseStatus.valueOf(request.decision());
        } catch (IllegalArgumentException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unsupported decision");
        }
        if (status != CreditCase.CaseStatus.APPROVED && status != CreditCase.CaseStatus.REJECTED
            && status != CreditCase.CaseStatus.MORE_INFORMATION_REQUIRED) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unsupported decision");
        }
        creditCase.decide(status);
        caseRepository.save(creditCase);
        HumanDecision saved = decisionRepository.save(
            new HumanDecision(caseId, status.name(), request.comment(), principal.getName())
        );
        return new ApiModels.DecisionResponse(saved.getId(), saved.getDecision(), saved.getComment(),
            saved.getDecidedBy(), saved.getDecidedAt());
    }

    private CreditCase findCase(UUID id) {
        return caseRepository.findById(id)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Case not found"));
    }

    private ApiModels.CaseResponse toResponse(CreditCase creditCase) {
        List<ApiModels.AssessmentResponse> assessments = assessmentRepository
            .findByCaseIdOrderByCreatedAtDesc(creditCase.getId()).stream().map(this::toAssessment).toList();
        List<ApiModels.DecisionResponse> decisions = decisionRepository
            .findByCaseIdOrderByDecidedAtDesc(creditCase.getId()).stream()
            .map(d -> new ApiModels.DecisionResponse(d.getId(), d.getDecision(), d.getComment(),
                d.getDecidedBy(), d.getDecidedAt())).toList();
        return new ApiModels.CaseResponse(
            creditCase.getId(), creditCase.getProfession(), creditCase.getAnnualIncome(),
            creditCase.getPracticeRevenue(), creditCase.getPracticeAgeYears(), creditCase.getExistingDebt(),
            creditCase.getRequestedCredit(), creditCase.getEquity(), creditCase.getLatePayments(),
            creditCase.getStatus().name(), creditCase.getCreatedAt(), assessments, decisions
        );
    }

    private ApiModels.AssessmentResponse toAssessment(Assessment assessment) {
        try {
            List<String> positives = objectMapper.readValue(assessment.getPositiveFactorsJson(), new TypeReference<>() {});
            List<String> risks = objectMapper.readValue(assessment.getRiskFactorsJson(), new TypeReference<>() {});
            List<ApiModels.Citation> citations = objectMapper.readValue(assessment.getCitationsJson(), new TypeReference<>() {});
            return new ApiModels.AssessmentResponse(
                assessment.getId(), assessment.getCaseId(), assessment.getRiskProbability(),
                assessment.getRiskBand(), positives, risks, assessment.getSummary(), citations,
                assessment.getGenerationMode(), assessment.getModelVersion(), assessment.getCorrelationId(),
                assessment.getCreatedAt()
            );
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("Could not read persisted AI result", e);
        }
    }
}

