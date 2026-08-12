from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from bank_ai.models import CreditFeatures
from bank_ai.train import PROFESSION_CODES


class RiskModel:
    def __init__(self, artifact_path: Path):
        if not artifact_path.exists():
            raise RuntimeError(f"Model artifact not found: {artifact_path}. Run ./dev bootstrap.")
        bundle = joblib.load(artifact_path)
        self.model = bundle["model"]
        self.features = bundle["features"]
        self.version = bundle["version"]

    def predict(self, case: CreditFeatures) -> tuple[float, list[str], list[str]]:
        debt_to_income = case.existingDebt / max(case.annualIncome, 1)
        equity_ratio = case.equity / max(case.requestedCredit, 1)
        row = pd.DataFrame(
            [
                {
                    "profession_code": PROFESSION_CODES.get(case.profession.upper(), 0),
                    "annual_income": case.annualIncome,
                    "practice_revenue": case.practiceRevenue,
                    "practice_age_years": case.practiceAgeYears,
                    "existing_debt": case.existingDebt,
                    "requested_credit": case.requestedCredit,
                    "equity": case.equity,
                    "late_payments": case.latePayments,
                    "debt_to_income": debt_to_income,
                    "equity_ratio": equity_ratio,
                }
            ]
        )[self.features]
        probability = float(self.model.predict_proba(row)[0, 1])
        positives: list[str] = []
        risks: list[str] = []
        (positives if equity_ratio >= 0.2 else risks).append(
            f"Equity ratio: {equity_ratio:.1%}"
        )
        (positives if debt_to_income < 1.0 else risks).append(
            f"Existing debt to annual income: {debt_to_income:.2f}"
        )
        (positives if case.practiceAgeYears >= 3 else risks).append(
            f"Practice operating history: {case.practiceAgeYears} years"
        )
        (positives if case.latePayments == 0 else risks).append(
            f"Recorded late payments: {case.latePayments}"
        )
        return probability, positives, risks


def risk_band(probability: float) -> str:
    if probability < 0.05:
        return "LOW"
    if probability < 0.15:
        return "MEDIUM"
    return "HIGH"

