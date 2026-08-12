package com.example.bank.api;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class CreditCaseTest {
    @Test
    void newCaseStartsAsDraftAndKeepsFinancialInputs() {
        var request = new ApiModels.CreateCaseRequest(
            "DENTIST", new BigDecimal("185000"), new BigDecimal("620000"), 4,
            new BigDecimal("80000"), new BigDecimal("450000"), new BigDecimal("100000"), 0
        );

        CreditCase creditCase = new CreditCase(request);

        assertThat(creditCase.getStatus()).isEqualTo(CreditCase.CaseStatus.DRAFT);
        assertThat(creditCase.getRequestedCredit()).isEqualByComparingTo("450000");
        assertThat(creditCase.getId()).isNotNull();
    }
}

