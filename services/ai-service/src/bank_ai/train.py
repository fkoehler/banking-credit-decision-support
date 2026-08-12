from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "profession_code",
    "annual_income",
    "practice_revenue",
    "practice_age_years",
    "existing_debt",
    "requested_credit",
    "equity",
    "late_payments",
    "debt_to_income",
    "equity_ratio",
]
PROFESSION_CODES = {"PHYSICIAN": 0, "DENTIST": 1, "PHARMACIST": 2, "THERAPIST": 3}


def generate_synthetic_data(rows: int = 8_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    profession = rng.integers(0, 4, rows)
    annual_income = rng.lognormal(11.7, 0.42, rows).clip(35_000, 650_000)
    practice_revenue = (annual_income * rng.uniform(2.1, 4.8, rows)).clip(80_000, 2_500_000)
    practice_age = rng.integers(0, 31, rows)
    existing_debt = rng.gamma(2.0, 65_000, rows).clip(0, 900_000)
    requested_credit = rng.lognormal(12.7, 0.6, rows).clip(25_000, 2_000_000)
    equity = (requested_credit * rng.beta(2.1, 5.0, rows)).clip(0, 700_000)
    late_payments = rng.poisson(0.35, rows).clip(0, 8)
    debt_to_income = existing_debt / np.maximum(annual_income, 1)
    equity_ratio = equity / np.maximum(requested_credit, 1)

    logit = (
        -3.6
        + 0.85 * debt_to_income
        + 0.55 * (requested_credit / np.maximum(practice_revenue, 1))
        + 0.75 * late_payments
        - 2.0 * equity_ratio
        - 0.055 * practice_age
        + 0.25 * (profession == 3)
        + 0.7 * ((practice_age < 2) & (equity_ratio < 0.12))
    )
    probability = 1 / (1 + np.exp(-logit))
    default = rng.binomial(1, probability)
    return pd.DataFrame(
        {
            "profession_code": profession,
            "annual_income": annual_income,
            "practice_revenue": practice_revenue,
            "practice_age_years": practice_age,
            "existing_debt": existing_debt,
            "requested_credit": requested_credit,
            "equity": equity,
            "late_payments": late_payments,
            "debt_to_income": debt_to_income,
            "equity_ratio": equity_ratio,
            "default": default,
        }
    )


def metrics_for(model, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    probability = model.predict_proba(x)[:, 1]
    prediction = probability >= 0.5
    return {
        "roc_auc": round(float(roc_auc_score(y, probability)), 6),
        "pr_auc": round(float(average_precision_score(y, probability)), 6),
        "recall_at_0_5": round(float(recall_score(y, prediction, zero_division=0)), 6),
        "brier_score": round(float(brier_score_loss(y, probability)), 6),
    }


def train(output_dir: Path, rows: int = 8_000) -> dict:
    data = generate_synthetic_data(rows=rows)
    train_end = int(rows * 0.7)
    validation_end = int(rows * 0.85)
    train_frame = data.iloc[:train_end]
    validation_frame = data.iloc[train_end:validation_end]
    test_frame = data.iloc[validation_end:]

    x_train, y_train = train_frame[FEATURES], train_frame["default"]
    x_validation, y_validation = validation_frame[FEATURES], validation_frame["default"]
    x_test, y_test = test_frame[FEATURES], test_frame["default"]

    candidates = {
        "logistic-regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1_000, class_weight="balanced", random_state=42)
        ),
        "gradient-boosting": GradientBoostingClassifier(random_state=42),
    }
    validation_metrics = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        validation_metrics[name] = metrics_for(model, x_validation, y_validation)

    selected_name = min(validation_metrics, key=lambda name: validation_metrics[name]["brier_score"])
    selected_model = candidates[selected_name]
    selected_model.fit(pd.concat([x_train, x_validation]), pd.concat([y_train, y_validation]))
    test_metrics = metrics_for(selected_model, x_test, y_test)
    version = f"synthetic-pd-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": selected_model, "features": FEATURES, "version": version},
        output_dir / "risk-model.joblib",
    )
    report = {
        "demo_only": True,
        "dataset": {"kind": "synthetic", "rows": rows, "seed": 42, "split": "70/15/15"},
        "selected_model": selected_name,
        "model_version": version,
        "validation": validation_metrics,
        "untouched_test": test_metrics,
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    output_dir = Path(__file__).resolve().parents[2] / "artifacts"
    report = train(output_dir)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

