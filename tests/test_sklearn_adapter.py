"""Tests for the Scikit-learn model adapter.

Covers:
* Model file loading (.joblib, .pkl).
* Estimator inference (predictions + confidence).
* Unsupported file extensions.
* Missing file handling.
* Incompatible object handling (missing predict method).
* Input and output contract declarations.
"""

from __future__ import annotations

from pathlib import Path
import joblib
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

from modular_agent.models.sklearn_model import SklearnModelAdapter


@pytest.fixture
def trained_sklearn_model(tmp_path: Path) -> Path:
    """Train a simple toy classifier and save to a temporary .joblib file."""
    X = np.array([[1.0, 2.0], [2.0, 3.0], [5.0, 6.0], [6.0, 7.0]])
    y = np.array(["low", "low", "high", "high"])

    clf = LogisticRegression(solver="liblinear")
    clf.fit(X, y)

    model_file = tmp_path / "simple_clf.joblib"
    joblib.dump(clf, model_file)
    return model_file


class TestSklearnModelAdapterLoading:

    def test_load_valid_joblib(self, trained_sklearn_model: Path) -> None:
        adapter = SklearnModelAdapter(model_path=trained_sklearn_model)
        assert adapter.is_loaded is False
        adapter.load()
        assert adapter.is_loaded is True

    def test_load_missing_file_raises(self, tmp_path: Path) -> None:
        adapter = SklearnModelAdapter(model_path=tmp_path / "nonexistent.joblib")
        with pytest.raises(FileNotFoundError, match="Model file not found"):
            adapter.load()

    def test_load_unsupported_format_raises(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "model.onnx"
        bad_file.write_text("dummy")
        adapter = SklearnModelAdapter(model_path=bad_file)
        with pytest.raises(ValueError, match="Unsupported model file format"):
            adapter.load()

    def test_load_incompatible_object_raises(self, tmp_path: Path) -> None:
        bad_obj_file = tmp_path / "bad_object.joblib"
        joblib.dump({"not_an_estimator": 42}, bad_obj_file)
        adapter = SklearnModelAdapter(model_path=bad_obj_file)
        with pytest.raises(TypeError, match=r"does not implement required 'predict\(\)'"):
            adapter.load()


class TestSklearnModelAdapterPrediction:

    def test_predict_with_features(self, trained_sklearn_model: Path) -> None:
        adapter = SklearnModelAdapter(model_path=trained_sklearn_model)
        adapter.load()

        result = adapter.predict({"features": [1.2, 2.3]})
        assert result["prediction"] in ("low", "high")
        assert result["model_type"] == "sklearn"
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_before_load_raises(self, trained_sklearn_model: Path) -> None:
        adapter = SklearnModelAdapter(model_path=trained_sklearn_model)
        with pytest.raises(RuntimeError, match="Model is not loaded"):
            adapter.predict({"features": [1.0, 2.0]})

    def test_predict_missing_required_features(self, trained_sklearn_model: Path) -> None:
        adapter = SklearnModelAdapter(model_path=trained_sklearn_model)
        adapter.load()
        with pytest.raises(ValueError, match="Missing required field"):
            adapter.predict({})

    def test_predict_invalid_features_type(self, trained_sklearn_model: Path) -> None:
        adapter = SklearnModelAdapter(model_path=trained_sklearn_model)
        adapter.load()
        with pytest.raises(ValueError, match="must be a list of numbers"):
            adapter.predict({"features": "not-a-list"})


class TestSklearnModelAdapterContracts:

    def test_custom_contract_override(self, trained_sklearn_model: Path) -> None:
        custom_input = {
            "x1": {"type": "float", "required": True, "description": "Param 1"},
            "x2": {"type": "float", "required": True, "description": "Param 2"},
        }
        adapter = SklearnModelAdapter(
            model_path=trained_sklearn_model,
            input_contract=custom_input,
        )
        contract = adapter.input_contract()
        assert "x1" in contract.fields
        assert "x2" in contract.fields
        assert contract.fields["x1"].type == "float"

