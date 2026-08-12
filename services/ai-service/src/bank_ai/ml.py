from __future__ import annotations

from pathlib import Path
from typing import Protocol

import httpx
import joblib
import pandas as pd
from azure.identity import DefaultAzureCredential

from bank_ai.config import Settings
from bank_ai.models import CreditFeatures
from bank_ai.train import PROFESSION_CODES


class RiskPredictor(Protocol):
    version: str

    def predict(self, case: CreditFeatures) -> tuple[float, list[str], list[str]]: ...


class LocalRiskModel:
    def __init__(self, artifact_path: Path):
        if not artifact_path.exists():
            raise RuntimeError(f"Model artifact not found: {artifact_path}. Run ./dev bootstrap.")
        bundle = joblib.load(artifact_path)
        self.model = bundle["model"]
        self.features = bundle["features"]
        self.version = bundle["version"]

    def predict(self, case: CreditFeatures) -> tuple[float, list[str], list[str]]:
        row = pd.DataFrame([feature_row(case)])[self.features]
        probability = float(self.model.predict_proba(row)[0, 1])
        positives, risks = input_factors(case)
        return probability, positives, risks


class AzureMlRiskModel:
    def __init__(self, settings: Settings):
        if not settings.azure_ml_endpoint:
            raise ValueError("AZURE_ML_ENDPOINT is required for azure-ml inference")
        self.endpoint = settings.azure_ml_endpoint
        self.api_key = settings.azure_ml_api_key
        self.credential = DefaultAzureCredential() if not self.api_key else None
        self.version = "azure-ml-managed-endpoint"

    def predict(self, case: CreditFeatures) -> tuple[float, list[str], list[str]]:
        row = feature_row(case)
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            token = self.credential.get_token("https://ml.azure.com/.default")
            headers["Authorization"] = f"Bearer {token.token}"
        response = httpx.post(
            self.endpoint,
            headers=headers,
            json={"input_data": {"columns": list(row), "data": [list(row.values())]}},
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        probability = float(payload["riskProbability"])
        self.version = payload.get("modelVersion", self.version)
        positives, risks = input_factors(case)
        return probability, positives, risks


def build_risk_predictor(settings: Settings) -> RiskPredictor:
    if settings.ai_inference_provider == "azure-ml":
        return AzureMlRiskModel(settings)
    return LocalRiskModel(settings.ai_model_path)


def feature_row(case: CreditFeatures) -> dict[str, float | int]:
    debt_to_income = case.existingDebt / max(case.annualIncome, 1)
    equity_ratio = case.equity / max(case.requestedCredit, 1)
    return {
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


def input_factors(case: CreditFeatures) -> tuple[list[str], list[str]]:
    debt_to_income = case.existingDebt / max(case.annualIncome, 1)
    equity_ratio = case.equity / max(case.requestedCredit, 1)
    positives: list[str] = []
    risks: list[str] = []
    (positives if equity_ratio >= 0.2 else risks).append(f"Equity ratio: {equity_ratio:.1%}")
    (positives if debt_to_income < 1.0 else risks).append(
        f"Existing debt to annual income: {debt_to_income:.2f}"
    )
    (positives if case.practiceAgeYears >= 3 else risks).append(
        f"Practice operating history: {case.practiceAgeYears} years"
    )
    (positives if case.latePayments == 0 else risks).append(
        f"Recorded late payments: {case.latePayments}"
    )
    return positives, risks


def risk_band(probability: float) -> str:
    if probability < 0.05:
        return "LOW"
    if probability < 0.15:
        return "MEDIUM"
    return "HIGH"
