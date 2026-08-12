package com.example.bank.api;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

interface CreditCaseRepository extends JpaRepository<CreditCase, UUID> {}
interface AssessmentRepository extends JpaRepository<Assessment, UUID> {
    List<Assessment> findByCaseIdOrderByCreatedAtDesc(UUID caseId);
}
interface HumanDecisionRepository extends JpaRepository<HumanDecision, UUID> {
    List<HumanDecision> findByCaseIdOrderByDecidedAtDesc(UUID caseId);
}

