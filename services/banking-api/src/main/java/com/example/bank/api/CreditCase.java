package com.example.bank.api;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "credit_cases")
public class CreditCase {
    @Id
    private UUID id;
    private String profession;
    private BigDecimal annualIncome;
    private BigDecimal practiceRevenue;
    private int practiceAgeYears;
    private BigDecimal existingDebt;
    private BigDecimal requestedCredit;
    private BigDecimal equity;
    private int latePayments;
    @Enumerated(EnumType.STRING)
    private CaseStatus status;
    private Instant createdAt;

    protected CreditCase() {}

    CreditCase(ApiModels.CreateCaseRequest request) {
        this.id = UUID.randomUUID();
        this.profession = request.profession();
        this.annualIncome = request.annualIncome();
        this.practiceRevenue = request.practiceRevenue();
        this.practiceAgeYears = request.practiceAgeYears();
        this.existingDebt = request.existingDebt();
        this.requestedCredit = request.requestedCredit();
        this.equity = request.equity();
        this.latePayments = request.latePayments();
        this.status = CaseStatus.DRAFT;
        this.createdAt = Instant.now();
    }

    public UUID getId() { return id; }
    public String getProfession() { return profession; }
    public BigDecimal getAnnualIncome() { return annualIncome; }
    public BigDecimal getPracticeRevenue() { return practiceRevenue; }
    public int getPracticeAgeYears() { return practiceAgeYears; }
    public BigDecimal getExistingDebt() { return existingDebt; }
    public BigDecimal getRequestedCredit() { return requestedCredit; }
    public BigDecimal getEquity() { return equity; }
    public int getLatePayments() { return latePayments; }
    public CaseStatus getStatus() { return status; }
    public Instant getCreatedAt() { return createdAt; }
    void markPendingReview() { this.status = CaseStatus.PENDING_REVIEW; }
    void decide(CaseStatus status) { this.status = status; }

    enum CaseStatus { DRAFT, PENDING_REVIEW, APPROVED, REJECTED, MORE_INFORMATION_REQUIRED }
}

