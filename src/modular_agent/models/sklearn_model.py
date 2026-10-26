"""Scikit-learn model adapter.

Loads a serialized scikit-learn estimator or Pipeline from a ``.joblib`` or
``.pkl`` file, validates its interface against a declared I/O contract,
and provides structured predictions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np

from modular_agent.models.base import FieldContract, ModelAdapter, ModelContract

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".joblib", ".pkl", ".pickle"}


class SklearnModelAdapter(ModelAdapter):
    """Adapter for scikit-learn estimators and pipelines.

    Parameters:
        model_path: Path to the serialized model file (.joblib or .pkl).
        model_name: Unique tool name for this model.
        description: Functional description for LLM tool selection.
        input_contract: Explicit dictionary of input field contracts, or None
                        for single-feature text input default.
        output_contract: Explicit dictionary of output field contracts, or None
                         for default prediction contract.
    """

    def __init__(
        self,
        model_path: Union[str, Path],
        model_name: str = "sklearn_model",
        description: str = "Scikit-learn predictive model.",
        input_contract: Optional[Dict[str, Any]] = None,
        output_contract: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._model_path = Path(model_path)
        self._model_name = model_name
        self._description = description
        self._custom_input_contract = input_contract
        self._custom_output_contract = output_contract
        self._estimator: Any = None

    def load(self) -> None:
        """Load and validate the serialized scikit-learn estimator."""
        if not self._model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at: {self._model_path.resolve()}"
            )

        suffix = self._model_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported model file format '{suffix}'. "
                f"Supported formats: {sorted(SUPPORTED_EXTENSIONS)}"
            )

        try:
            loaded_obj = joblib.load(self._model_path)
        except Exception as exc:
            raise ValueError(
                f"Failed to deserialize scikit-learn model from "
                f"'{self._model_path}': {exc}"
            ) from exc

        # Basic verification that the loaded object behaves like an estimator
        if not hasattr(loaded_obj, "predict"):
            raise TypeError(
                f"Loaded object of type {type(loaded_obj).__name__} does not "
                f"implement required 'predict()' method."
            )

        self._estimator = loaded_obj
        self._loaded = True
        logger.info(
            "Successfully loaded scikit-learn estimator: %s from %s",
            type(self._estimator).__name__,
            self._model_path,
        )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference using the loaded estimator."""
        if not self.is_loaded or self._estimator is None:
            raise RuntimeError("Model is not loaded. Call load() first.")

        # Determine features array based on contract
        contract = self.input_contract()
        for field_name, field_spec in contract.fields.items():
            if field_spec.required and field_name not in input_data:
                raise ValueError(f"Missing required field: '{field_name}'")

        # Convert input dictionary to an ordered feature matrix or list
        if "features" in input_data:
            raw_features = input_data["features"]
            if not isinstance(raw_features, (list, tuple)):
                raise ValueError("Field 'features' must be a list of numbers.")
            X = np.array([raw_features])
        elif "text" in input_data:
            raw_text = input_data["text"]
            if not isinstance(raw_text, str) or not raw_text.strip():
                raise ValueError("Field 'text' must be a non-empty string.")
            X = [raw_text]
        else:
            # Order according to input contract keys
            ordered_values = [input_data[k] for k in contract.fields.keys()]
            X = np.array([ordered_values])

        try:
            raw_pred = self._estimator.predict(X)[0]
        except Exception as exc:
            raise RuntimeError(f"Prediction execution failed: {exc}") from exc

        # Format prediction
        pred_value = raw_pred.item() if hasattr(raw_pred, "item") else raw_pred

        result: Dict[str, Any] = {
            "prediction": pred_value,
            "model_type": "sklearn",
        }

        # Include probabilities if the estimator supports predict_proba
        if hasattr(self._estimator, "predict_proba"):
            try:
                probabilities = self._estimator.predict_proba(X)[0]
                conf = float(np.max(probabilities))
                result["confidence"] = round(conf, 4)
            except Exception as exc:
                logger.debug("Failed to calculate probabilities: %s", exc)

        return result

    def input_contract(self) -> ModelContract:
        """Return the declared or derived input contract."""
        if self._custom_input_contract:
            fields = {
                k: FieldContract(**v) if isinstance(v, dict) else v
                for k, v in self._custom_input_contract.items()
            }
            return ModelContract(fields=fields)

        # Default fallback input contract
        return ModelContract(
            fields={
                "features": FieldContract(
                    type="list",
                    required=True,
                    description="List of numeric feature values for the model.",
                )
            }
        )

    def output_contract(self) -> ModelContract:
        """Return the declared or derived output contract."""
        if self._custom_output_contract:
            fields = {
                k: FieldContract(**v) if isinstance(v, dict) else v
                for k, v in self._custom_output_contract.items()
            }
            return ModelContract(fields=fields)

        # Default output contract
        fields = {
            "prediction": FieldContract(
                type="str",
                required=True,
                description="Model prediction output (class label or numeric value).",
            ),
            "model_type": FieldContract(
                type="str",
                required=True,
                description="Identifies the model runtime format ('sklearn').",
            ),
        }
        if self._estimator is not None and hasattr(self._estimator, "predict_proba"):
            fields["confidence"] = FieldContract(
                type="float",
                required=False,
                description="Prediction confidence / maximum class probability.",
            )
        return ModelContract(fields=fields)

    def name(self) -> str:
        return self._model_name

    def description(self) -> str:
        return self._description

