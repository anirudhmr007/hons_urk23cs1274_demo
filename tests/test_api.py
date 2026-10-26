"""Tests for the FastAPI application endpoints."""

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
        assert data["registered_tools"] >= 1


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


class TestAgentEndpoints:

    def test_agent_chat_endpoint(self) -> None:
        client = TestClient(app)
        resp = client.post(
            "/agent/chat",
            json={
                "query": "Classify sentiment: 'This is absolutely wonderful and great!'",
                "session_id": "api_test_session",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert data["tool_called"] is True
        assert data["tool_name"] in ("demo_sentiment_classifier", "real_sentiment_pipeline")
        assert "tool_output" in data
        assert data["tool_output"].get("label") == "positive" or data["tool_output"].get("prediction") == "positive"

    def test_agent_trace_endpoint(self) -> None:
        client = TestClient(app)
        resp = client.get("/agent/trace")
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert isinstance(data["events"], list)
        assert len(data["events"]) > 0

    def test_agent_reset_endpoint(self) -> None:
        client = TestClient(app)
        resp = client.post("/agent/reset", params={"session_id": "api_test_session"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
