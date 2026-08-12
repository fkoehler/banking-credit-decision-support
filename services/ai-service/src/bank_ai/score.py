"""Azure ML scoring entry point for the registered synthetic risk model."""

from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import pandas as pd

_bundle = None


def init() -> None:
    global _bundle
    model_root = Path(os.environ["AZUREML_MODEL_DIR"])
    artifact = next(model_root.rglob("risk-model.joblib"))
    _bundle = joblib.load(artifact)


def run(raw_data: str) -> dict[str, float | str]:
    if _bundle is None:
        raise RuntimeError("Model is not initialized")
    payload = json.loads(raw_data)
    frame = pd.DataFrame(payload["input_data"]["data"], columns=payload["input_data"]["columns"])
    frame = frame[_bundle["features"]]
    probability = float(_bundle["model"].predict_proba(frame)[0, 1])
    return {"riskProbability": probability, "modelVersion": _bundle["version"]}
