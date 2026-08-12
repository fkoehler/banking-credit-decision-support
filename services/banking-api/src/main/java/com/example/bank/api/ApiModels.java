package com.example.bank.api;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

final class ApiModels {
    private ApiModels() {}

    record CreateCaseRequest(
        @NotBlank String profession,
        @NotNull @DecimalMin("0") BigDecimal annualIncome,
        @NotNull @DecimalMin("0") BigDecimal practiceRevenue,
        @Min(0) @Max(100) int practiceAgeYears,
        @NotNull @DecimalMin("0") BigDecimal existingDebt,
        @NotNull @DecimalMin("1") BigDecimal requestedCredit,
        @NotNull @DecimalMin("0") BigDecimal equity,
        @Min(0) @Max(100) int latePayments
    ) {}

    record CaseResponse(
        UUID id, String profession, BigDecimal annualIncome, BigDecimal practiceRevenue,
        int practiceAgeYears, BigDecimal existingDebt, BigDecimal requestedCredit,
        BigDecimal equity, int latePayments, String status, Instant createdAt,
        List<AssessmentResponse> assessments, List<DecisionResponse> decisions
    ) {}

    record AssessmentResponse(
        UUID id, UUID caseId, double riskProbability, String riskBand,
        List<String> positiveFactors, List<String> riskFactors, String summary,
        List<Citation> citations, String generationMode, String modelVersion,
        String correlationId, Instant createdAt
    ) {}

    record Citation(String documentId, String title, String section, double score) {}
    record DecisionRequest(@NotBlank String decision, @NotBlank String comment) {}
    record DecisionResponse(UUID id, String decision, String comment, String decidedBy, Instant decidedAt) {}
    record DocumentRequest(@NotBlank String title, @NotBlank String content, String source) {}
    record DocumentResponse(String documentId, String title, String checksum, int chunkCount) {}
    record DocumentSummary(String documentId, String title, String source, int chunkCount) {}
}
