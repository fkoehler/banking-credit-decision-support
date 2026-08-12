package com.example.bank.api;

import java.math.BigDecimal;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class AiClient {
    private final RestClient restClient;

    public AiClient(RestClient.Builder builder, @Value("${app.ai-service-url}") String baseUrl) {
        this.restClient = builder.baseUrl(baseUrl).build();
    }

    AiAssessment assess(CreditCase creditCase, String correlationId) {
        var request = new AiAssessmentRequest(
            creditCase.getProfession(), creditCase.getAnnualIncome(), creditCase.getPracticeRevenue(),
            creditCase.getPracticeAgeYears(), creditCase.getExistingDebt(), creditCase.getRequestedCredit(),
            creditCase.getEquity(), creditCase.getLatePayments(), correlationId
        );
        return restClient.post()
            .uri("/internal/v1/assess")
            .contentType(MediaType.APPLICATION_JSON)
            .body(request)
            .retrieve()
            .body(AiAssessment.class);
    }

    ApiModels.DocumentResponse ingest(ApiModels.DocumentRequest request) {
        return restClient.post()
            .uri("/internal/v1/documents")
            .contentType(MediaType.APPLICATION_JSON)
            .body(request)
            .retrieve()
            .body(ApiModels.DocumentResponse.class);
    }

    ApiModels.DocumentSummary[] listDocuments() {
        return restClient.get()
            .uri("/internal/v1/documents")
            .retrieve()
            .body(ApiModels.DocumentSummary[].class);
    }

    record AiAssessmentRequest(
        String profession, BigDecimal annualIncome, BigDecimal practiceRevenue,
        int practiceAgeYears, BigDecimal existingDebt, BigDecimal requestedCredit,
        BigDecimal equity, int latePayments, String correlationId
    ) {}

    record AiAssessment(
        double riskProbability, String riskBand, List<String> positiveFactors,
        List<String> riskFactors, String summary, List<ApiModels.Citation> citations,
        String generationMode, String modelVersion
    ) {}
}

