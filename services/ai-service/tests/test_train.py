from pathlib import Path

from bank_ai.ml import RiskModel
from bank_ai.models import CreditFeatures
from bank_ai.train import train


def test_training_produces_loadable_model(tmp_path: Path):
    report = train(tmp_path, rows=1_000)
    model = RiskModel(tmp_path / "risk-model.joblib")
    probability, positives, risks = model.predict(
        CreditFeatures(
            profession="DENTIST",
            annualIncome=185_000,
            practiceRevenue=620_000,
            practiceAgeYears=4,
            existingDebt=80_000,
            requestedCredit=450_000,
            equity=100_000,
            latePayments=1,
        )
    )

    assert report["dataset"]["kind"] == "synthetic"
    assert 0 <= probability <= 1
    assert positives
    assert risks
