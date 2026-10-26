"""Tests for the model ingestion engine.

Covers:
* Happy-path ingestion of the demo model.
* Custom tool name override.
* Unsupported model type.
* Duplicate registration.
* Tool callable execution + input validation.
* Schema JSON structure.
* Malformed configuration.
"""

from __future__ import annotations

import pytest

from modular_agent.ingestion.engine import (
    IngestionEngine,
    ModelConfig,
    _ADAPTER_REGISTRY,
    register_adapter_type,
)
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import ToolRegistry


@pytest.fixture(autouse=True)
def _clean_adapter_registry():
    """Isolate each test from the global adapter registry."""
    saved = _ADAPTER_REGISTRY.copy()
    _ADAPTER_REGISTRY.clear()
    register_adapter_type("demo", DemoSentimentModel)
    yield
    _ADAPTER_REGISTRY.clear()
    _ADAPTER_REGISTRY.update(saved)


class TestIngestionHappyPath:

    def test_ingest_demo_model(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        result = engine.ingest(ModelConfig(model_type="demo"))

        assert result.success is True
        assert result.tool_name == "demo_sentiment_classifier"
        assert result.errors == []
        assert result.input_schema_json is not None
        assert result.output_schema_json is not None
        assert registry.has("demo_sentiment_classifier")

    def test_custom_name_override(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        result = engine.ingest(
            ModelConfig(model_type="demo", name="my_tool"),
        )
        assert result.success is True
        assert result.tool_name == "my_tool"
        assert registry.has("my_tool")

    def test_custom_description_override(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        result = engine.ingest(
            ModelConfig(model_type="demo", description="Custom desc"),
        )
        assert result.success is True
        tool = registry.get(result.tool_name)
        assert tool.description == "Custom desc"


class TestIngestionErrors:

    def test_unsupported_model_type(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        result = engine.ingest(ModelConfig(model_type="xgboost_v99"))

        assert result.success is False
        assert any("Unsupported" in e for e in result.errors)

    def test_duplicate_registration(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        r1 = engine.ingest(ModelConfig(model_type="demo"))
        assert r1.success is True

        r2 = engine.ingest(ModelConfig(model_type="demo"))
        assert r2.success is False
        assert any("already registered" in e for e in r2.errors)

    def test_missing_model_type_field(self) -> None:
        """ModelConfig requires model_type — Pydantic should reject."""
        with pytest.raises(Exception):  # ValidationError
            ModelConfig()  # type: ignore[call-arg]


class TestToolCallable:

    def test_callable_executes_prediction(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        engine.ingest(ModelConfig(model_type="demo"))

        tool = registry.get("demo_sentiment_classifier")
        result = tool.callable(text="I love this, it's great")
        assert result["label"] in ("positive", "negative")
        assert isinstance(result["confidence"], float)
        assert result["model_type"] == "demonstration"

    def test_callable_rejects_invalid_type(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        engine.ingest(ModelConfig(model_type="demo"))

        tool = registry.get("demo_sentiment_classifier")
        with pytest.raises(ValueError, match="Input validation failed"):
            tool.callable(text=["not", "a", "string"])

    def test_callable_missing_required_arg(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        engine.ingest(ModelConfig(model_type="demo"))

        tool = registry.get("demo_sentiment_classifier")
        with pytest.raises(ValueError, match="Input validation failed"):
            tool.callable()  # missing 'text'


class TestSchemaOutput:

    def test_input_schema_json_structure(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        result = engine.ingest(ModelConfig(model_type="demo"))

        schema = result.input_schema_json
        assert "properties" in schema
        assert "text" in schema["properties"]

    def test_output_schema_json_structure(self, registry: ToolRegistry) -> None:
        engine = IngestionEngine(registry)
        result = engine.ingest(ModelConfig(model_type="demo"))

        schema = result.output_schema_json
        assert "properties" in schema
        assert "label" in schema["properties"]
        assert "confidence" in schema["properties"]
        assert "model_type" in schema["properties"]

