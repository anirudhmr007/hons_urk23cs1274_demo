"""Tests for ingesting Sklearn and REST API models via IngestionEngine."""

from __future__ import annotations

from pathlib import Path
import joblib
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
import httpx

from modular_agent.ingestion.engine import IngestionEngine, ModelConfig
from modular_agent.models.registry import ToolRegistry


@pytest.fixture
def sample_sklearn_file(tmp_path: Path) -> Path:
    X = np.array([[1.0, 2.0], [2.0, 3.0], [5.0, 6.0], [6.0, 7.0]])
    y = np.array(["neg", "neg", "pos", "pos"])
    clf = LogisticRegression(solver="liblinear")
    clf.fit(X, y)
    path = tmp_path / "model.joblib"
    joblib.dump(clf, path)
    return path


def test_ingest_sklearn_model(sample_sklearn_file: Path, registry: ToolRegistry) -> None:
    engine = IngestionEngine(registry)
    result = engine.ingest(
        ModelConfig(
            model_type="sklearn",
            name="custom_classifier",
            description="Classifies numeric feature pairs.",
            parameters={"model_path": str(sample_sklearn_file)},
        )
    )
    assert result.success is True
    assert result.tool_name == "custom_classifier"
    assert registry.has("custom_classifier")

    tool = registry.get("custom_classifier")
    pred = tool.callable(features=[1.5, 2.5])
    assert pred["prediction"] in ("pos", "neg")
    assert pred["model_type"] == "sklearn"


def test_ingest_rest_api_model(registry: ToolRegistry) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"prediction": "fraud_detected", "risk_score": 0.88})

    client = httpx.Client(transport=httpx.MockTransport(handler))

    engine = IngestionEngine(registry)
    result = engine.ingest(
        ModelConfig(
            model_type="rest_api",
            name="fraud_detector",
            description="Evaluates transaction fraud risk.",
            parameters={
                "endpoint_url": "https://risk.internal/check",
                "client": client,
            },
        )
    )
    assert result.success is True
    assert result.tool_name == "fraud_detector"

    tool = registry.get("fraud_detector")
    pred = tool.callable(query="card_tx_99812")
    assert pred["prediction"] == "fraud_detected"
    assert pred["risk_score"] == 0.88

