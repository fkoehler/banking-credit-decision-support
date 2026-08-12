import json

import numpy as np

from bank_ai import score


class FakeModel:
    def predict_proba(self, frame):
        assert list(frame.columns) == ["a", "b"]
        return np.array([[0.8, 0.2]])


def test_azure_ml_score_contract():
    score._bundle = {"model": FakeModel(), "features": ["a", "b"], "version": "test-v1"}

    result = score.run(json.dumps({"input_data": {"columns": ["a", "b"], "data": [[1, 2]]}}))

    assert result == {"riskProbability": 0.2, "modelVersion": "test-v1"}
