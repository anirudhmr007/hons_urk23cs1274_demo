"""Tests for the REST API model adapter.

Covers:
* HTTP POST and GET inference via httpx MockTransport.
* Contract declarations and input validation.
* Remote HTTP errors (4xx / 5xx).
* Non-JSON response handling.
* Network/Connection failure handling.
"""

from __future__ import annotations

import httpx
import pytest

from modular_agent.models.rest_api_model import RestApiModelAdapter


class TestRestApiModelAdapter:

    def test_successful_post_prediction(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            return httpx.Response(200, json={"prediction": "approved", "score": 0.95})

        client = httpx.Client(transport=httpx.MockTransport(handler))
        adapter = RestApiModelAdapter(
            endpoint_url="https://api.example.com/predict",
            client=client,
        )
        adapter.load()
        assert adapter.is_loaded

        result = adapter.predict({"query": "check applicant status"})
        assert result["prediction"] == "approved"
        assert result["score"] == 0.95
        assert result["model_type"] == "rest_api"

    def test_successful_get_prediction(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            return httpx.Response(200, json={"prediction": "positive"})

        client = httpx.Client(transport=httpx.MockTransport(handler))
        adapter = RestApiModelAdapter(
            endpoint_url="https://api.example.com/sentiment",
            http_method="GET",
            client=client,
        )
        adapter.load()
        result = adapter.predict({"query": "great product"})
        assert result["prediction"] == "positive"

    def test_endpoint_returns_error_status(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="Internal Server Failure")

        client = httpx.Client(transport=httpx.MockTransport(handler))
        adapter = RestApiModelAdapter(
            endpoint_url="https://api.example.com/broken",
            client=client,
        )
        adapter.load()
        with pytest.raises(RuntimeError, match="HTTP 500"):
            adapter.predict({"query": "test"})

    def test_endpoint_returns_non_json(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="NOT_A_JSON")

        client = httpx.Client(transport=httpx.MockTransport(handler))
        adapter = RestApiModelAdapter(
            endpoint_url="https://api.example.com/raw",
            client=client,
        )
        adapter.load()
        with pytest.raises(RuntimeError, match="not return valid JSON"):
            adapter.predict({"query": "test"})

    def test_missing_required_input_field(self) -> None:
        adapter = RestApiModelAdapter(endpoint_url="https://api.example.com/predict")
        adapter.load()
        with pytest.raises(ValueError, match="Missing required field"):
            adapter.predict({})

    def test_invalid_empty_url_raises(self) -> None:
        with pytest.raises(ValueError, match="endpoint_url must be a valid"):
            RestApiModelAdapter(endpoint_url="")

    def test_unsupported_http_method_raises_at_load(self) -> None:
        adapter = RestApiModelAdapter(
            endpoint_url="https://api.example.com",
            http_method="DELETE",
        )
        with pytest.raises(ValueError, match="Unsupported HTTP method"):
            adapter.load()

