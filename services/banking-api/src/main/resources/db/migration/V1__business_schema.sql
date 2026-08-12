CREATE TABLE credit_cases (
    id UUID PRIMARY KEY,
    profession VARCHAR(80) NOT NULL,
    annual_income NUMERIC(16,2) NOT NULL,
    practice_revenue NUMERIC(16,2) NOT NULL,
    practice_age_years INTEGER NOT NULL,
    existing_debt NUMERIC(16,2) NOT NULL,
    requested_credit NUMERIC(16,2) NOT NULL,
    equity NUMERIC(16,2) NOT NULL,
    late_payments INTEGER NOT NULL,
    status VARCHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE assessments (
    id UUID PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES credit_cases(id),
    risk_probability DOUBLE PRECISION NOT NULL,
    risk_band VARCHAR(20) NOT NULL,
    positive_factors_json TEXT NOT NULL,
    risk_factors_json TEXT NOT NULL,
    summary TEXT NOT NULL,
    citations_json TEXT NOT NULL,
    generation_mode VARCHAR(30) NOT NULL,
    model_version VARCHAR(120) NOT NULL,
    correlation_id VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX assessments_case_id_idx ON assessments(case_id);

CREATE TABLE human_decisions (
    id UUID PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES credit_cases(id),
    decision VARCHAR(40) NOT NULL,
    comment VARCHAR(2000) NOT NULL,
    decided_by VARCHAR(200) NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX human_decisions_case_id_idx ON human_decisions(case_id);

