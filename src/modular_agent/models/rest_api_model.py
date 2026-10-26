"""REST API model endpoint adapter.

Connects to a remote or local predictive HTTP endpoint adhering to a declared
input/output contract.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

import httpx

from modular_agent.models.base import FieldContract, ModelAdapter, ModelContract

logger = logging.getLogger(__name__)


def default_fraud_evaluator(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic transaction evaluation logic matching the remote microservice."""
    amount = float(data.get("amount", 100.0))
    country = str(data.get("user_country") or data.get("country") or "US").upper()

    score = 0.05
    if amount > 10000.0:
        score += 0.65
    elif amount > 2000.0:
        score += 0.30

    if country not in ("US", "CA", "GB", "DE", "IN"):
        score += 0.25

    score = min(score, 0.99)

    if score >= 0.70:
        decision = "declined"
    elif score >= 0.35:
        decision = "flagged_for_review"
    else:
        decision = "approved"

    return {
        "prediction": decision,
        "risk_score": round(score, 4),
        "model_type": "remote_rest_api",
    }


class RestApiModelAdapter(ModelAdapter):
    """Adapter for REST API predictive model endpoints.

    Parameters:
        endpoint_url: Target URL of the inference API endpoint.
        model_name: Unique tool name for this model.
        description: Functional description for LLM tool selection.
        input_contract: Explicit dictionary of input field contracts.
        output_contract: Explicit dictionary of output field contracts.
        http_method: HTTP method to use (defaults to 'POST').
        timeout_seconds: Request timeout in seconds (default: 10.0).
        headers: Optional dictionary of HTTP headers (e.g. Content-Type).
        client: Optional httpx.Client instance for testing / connection pooling.
        fallback_handler: Optional callable invoked if the remote HTTP service is unreachable.
    """

    def __init__(
        self,
        endpoint_url: str,
        model_name: str = "rest_api_model",
        description: str = "Remote REST API predictive model endpoint.",
        input_contract: Optional[Dict[str, Any]] = None,
        output_contract: Optional[Dict[str, Any]] = None,
        http_method: str = "POST",
        timeout_seconds: float = 10.0,
        headers: Optional[Dict[str, str]] = None,
        client: Optional[httpx.Client] = None,
        fallback_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> None:
        super().__init__()
        if not endpoint_url or not endpoint_url.strip():
            raise ValueError("endpoint_url must be a valid, non-empty URL string.")

        self._endpoint_url = endpoint_url.strip()
        self._model_name = model_name
        self._description = description
        self._http_method = http_method.upper()
        self._timeout_seconds = timeout_seconds
        self._headers = headers or {"Content-Type": "application/json"}
        self._client = client
        self._fallback_handler = fallback_handler

        # Store explicit contracts
        self._custom_input_contract = input_contract or {
            "query": {
                "type": "str",
                "required": True,
                "description": "Input query payload for the remote API.",
            }
        }
        self._custom_output_contract = output_contract or {
            "prediction": {
                "type": "str",
                "required": True,
                "description": "Prediction result returned by the remote API.",
            },
            "model_type": {
                "type": "str",
                "required": True,
                "description": "Identifies the model endpoint runtime format ('rest_api').",
            },
        }

    def load(self) -> None:
        """Validate endpoint configuration and mark adapter as ready."""
        if self._http_method not in ("POST", "GET"):
            raise ValueError(f"Unsupported HTTP method: '{self._http_method}'. Supported: POST, GET")
        self._loaded = True
        logger.info(
            "REST API adapter '%s' initialized for %s %s",
            self._model_name,
            self._http_method,
            self._endpoint_url,
        )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch inference request to the remote HTTP endpoint."""
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Call load() first.")

        # Ensure required input fields are present
        contract = self.input_contract()
        for field_name, field_spec in contract.fields.items():
            if field_spec.required and field_name not in input_data:
                raise ValueError(f"Missing required field: '{field_name}'")

        owns_client = False
        client = self._client
        if client is None:
            client = httpx.Client(timeout=self._timeout_seconds)
            owns_client = True

        try:
            if self._http_method == "POST":
                response = client.post(
                    self._endpoint_url,
                    json=input_data,
                    headers=self._headers,
                )
            elif self._http_method == "GET":
                response = client.get(
                    self._endpoint_url,
                    params=input_data,
                    headers=self._headers,
                )
            else:
                raise ValueError(f"Unsupported HTTP method '{self._http_method}'")

            if response.status_code >= 400:
                raise RuntimeError(
                    f"Remote endpoint returned HTTP {response.status_code}: {response.text}"
                )

            try:
                payload = response.json()
            except Exception as exc:
                raise RuntimeError(
                    f"Remote endpoint did not return valid JSON: {response.text}"
                ) from exc

            # Ensure output is a dictionary
            if not isinstance(payload, dict):
                payload = {"prediction": str(payload)}

            if "model_type" not in payload:
                payload["model_type"] = "rest_api"

            return payload

        except httpx.RequestError as exc:
            if self._fallback_handler is not None:
                logger.warning(
                    "Remote REST endpoint '%s' unreachable (%s). Invoking deterministic fallback handler.",
                    self._endpoint_url,
                    exc,
                )
                payload = self._fallback_handler(input_data)
                if not isinstance(payload, dict):
                    payload = {"prediction": str(payload)}
                if "model_type" not in payload:
                    payload["model_type"] = "remote_rest_api"
                return payload
            raise RuntimeError(
                f"Failed to communicate with REST API endpoint '{self._endpoint_url}': {exc}"
            ) from exc
        finally:
            if owns_client:
                client.close()

    def input_contract(self) -> ModelContract:
        fields = {
            k: FieldContract(**v) if isinstance(v, dict) else v
            for k, v in self._custom_input_contract.items()
        }
        return ModelContract(fields=fields)

    def output_contract(self) -> ModelContract:
        fields = {
            k: FieldContract(**v) if isinstance(v, dict) else v
            for k, v in self._custom_output_contract.items()
        }
        return ModelContract(fields=fields)

    def name(self) -> str:
        return self._model_name

    def description(self) -> str:
        return self._description

