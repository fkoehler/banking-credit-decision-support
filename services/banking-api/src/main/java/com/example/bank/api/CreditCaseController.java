package com.example.bank.api;

import jakarta.validation.Valid;
import java.security.Principal;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/cases")
public class CreditCaseController {
    private final CreditCaseService service;

    CreditCaseController(CreditCaseService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    ApiModels.CaseResponse create(@Valid @RequestBody ApiModels.CreateCaseRequest request) {
        return service.create(request);
    }

    @GetMapping("/{caseId}")
    ApiModels.CaseResponse get(@PathVariable UUID caseId) {
        return service.get(caseId);
    }

    @PostMapping("/{caseId}/assessments")
    @ResponseStatus(HttpStatus.CREATED)
    ApiModels.AssessmentResponse assess(
        @PathVariable UUID caseId,
        @RequestHeader(value = "X-Correlation-ID", required = false) String correlationId
    ) {
        return service.assess(caseId, correlationId == null ? UUID.randomUUID().toString() : correlationId);
    }

    @PostMapping("/{caseId}/decisions")
    @ResponseStatus(HttpStatus.CREATED)
    ApiModels.DecisionResponse decide(@PathVariable UUID caseId,
                                      @Valid @RequestBody ApiModels.DecisionRequest request,
                                      Principal principal) {
        return service.decide(caseId, request, principal);
    }
}

