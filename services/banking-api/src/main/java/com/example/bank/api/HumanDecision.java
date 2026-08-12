package com.example.bank.api;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "human_decisions")
public class HumanDecision {
    @Id
    private UUID id;
    private UUID caseId;
    private String decision;
    private String comment;
    private String decidedBy;
    private Instant decidedAt;

    protected HumanDecision() {}

    HumanDecision(UUID caseId, String decision, String comment, String decidedBy) {
        this.id = UUID.randomUUID();
        this.caseId = caseId;
        this.decision = decision;
        this.comment = comment;
        this.decidedBy = decidedBy;
        this.decidedAt = Instant.now();
    }

    public UUID getId() { return id; }
    public UUID getCaseId() { return caseId; }
    public String getDecision() { return decision; }
    public String getComment() { return comment; }
    public String getDecidedBy() { return decidedBy; }
    public Instant getDecidedAt() { return decidedAt; }
}

