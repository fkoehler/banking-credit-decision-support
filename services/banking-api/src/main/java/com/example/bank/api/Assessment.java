package com.example.bank.api;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "assessments")
public class Assessment {
    @Id
    private UUID id;
    private UUID caseId;
    private double riskProbability;
    private String riskBand;
    @Column(columnDefinition = "text")
    private String positiveFactorsJson;
    @Column(columnDefinition = "text")
    private String riskFactorsJson;
    @Column(columnDefinition = "text")
    private String summary;
    @Column(columnDefinition = "text")
    private String citationsJson;
    private String generationMode;
    private String modelVersion;
    private String correlationId;
    private Instant createdAt;

    protected Assessment() {}

    Assessment(UUID caseId, AiClient.AiAssessment result, String correlationId, String positiveFactorsJson,
               String riskFactorsJson, String citationsJson) {
        this.id = UUID.randomUUID();
        this.caseId = caseId;
        this.riskProbability = result.riskProbability();
        this.riskBand = result.riskBand();
        this.positiveFactorsJson = positiveFactorsJson;
        this.riskFactorsJson = riskFactorsJson;
        this.summary = result.summary();
        this.citationsJson = citationsJson;
        this.generationMode = result.generationMode();
        this.modelVersion = result.modelVersion();
        this.correlationId = correlationId;
        this.createdAt = Instant.now();
    }

    public UUID getId() { return id; }
    public UUID getCaseId() { return caseId; }
    public double getRiskProbability() { return riskProbability; }
    public String getRiskBand() { return riskBand; }
    public String getPositiveFactorsJson() { return positiveFactorsJson; }
    public String getRiskFactorsJson() { return riskFactorsJson; }
    public String getSummary() { return summary; }
    public String getCitationsJson() { return citationsJson; }
    public String getGenerationMode() { return generationMode; }
    public String getModelVersion() { return modelVersion; }
    public String getCorrelationId() { return correlationId; }
    public Instant getCreatedAt() { return createdAt; }
}

