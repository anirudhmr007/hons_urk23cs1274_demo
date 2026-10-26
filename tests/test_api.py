"""Tests for the FastAPI application.

Covers the ``/health`` and ``/tools`` endpoints.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from modular_agent.api.app import app


class TestHealthEndpoint:

    def test_returns_200(self) -> None:
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_response_body(self) -> None:
        client = TestClient(app)
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["app_name"] == "Modular-Agent"
        assert "version" in data
        assert "registered_tools" in data


class TestToolsEndpoint:

    def test_returns_200(self) -> None:
        client = TestClient(app)
        resp = client.get("/tools")
        assert resp.status_code == 200

    def test_response_body(self) -> None:
        client = TestClient(app)
        data = client.get("/tools").json()
        assert "registered_tools" in data
        assert "tool_names" in data
        assert isinstance(data["tool_names"], list)

