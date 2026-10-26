"""Tests for Agent Orchestration, tool routing, bounded retries, and execution traces."""

from __future__ import annotations

import pytest

from modular_agent.agent import AgentOrchestrator, ConversationMemory, ExecutionTracer
from modular_agent.ingestion.engine import IngestionEngine, ModelConfig
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import ToolRegistry
from modular_agent.providers.base import LLMResponse, ToolCall
from modular_agent.providers.mock_provider import MockLLMProvider


@pytest.fixture
def agent_setup():
    """Sets up an agent with an ingested sentiment demonstration tool and mock LLM."""
    registry = ToolRegistry()
    engine = IngestionEngine(registry)
    engine.ingest(ModelConfig(model_type="demo", name="sentiment_tool"))

    provider = MockLLMProvider()
    memory = ConversationMemory()
    tracer = ExecutionTracer()

    orchestrator = AgentOrchestrator(
        provider=provider,
        registry=registry,
        memory=memory,
        tracer=tracer,
        max_retries=2,
    )
    return orchestrator, provider, registry, memory, tracer


def test_agent_routes_to_tool_on_sentiment_query(agent_setup) -> None:
    orchestrator, provider, registry, memory, tracer = agent_setup

    result = orchestrator.run(
        user_query="Can you classify the sentiment of this review: 'I loved this device, it is brilliant!'",
        session_id="test_session",
    )

    assert result.tool_called is True
    assert result.tool_name == "sentiment_tool"
    assert result.tool_input is not None
    assert "text" in result.tool_input
    assert result.tool_output is not None
    assert result.tool_output["label"] in ("positive", "negative")
    assert result.tool_output["model_type"] == "demonstration"
    assert "positive" in result.response.lower()

    # Verify execution trace events
    events = [e["event_type"] for e in result.trace_events]
    assert "REQUEST_RECEIVED" in events
    assert "TOOL_SELECTION" in events
    assert "ARG_VALIDATION" in events
    assert "TOOL_EXECUTION" in events
    assert "OUTPUT_VALIDATION" in events
    assert "RESPONSE_GENERATION" in events


def test_agent_avoids_unnecessary_tool_execution(agent_setup) -> None:
    orchestrator, provider, registry, memory, tracer = agent_setup

    result = orchestrator.run(
        user_query="Hello! What is your name?",
        session_id="chat_session",
    )

    assert result.tool_called is False
    assert result.tool_name is None
    assert result.tool_output is None
    assert "without calling any tool" in result.response

    events = [e["event_type"] for e in result.trace_events]
    assert "REQUEST_RECEIVED" in events
    assert "TOOL_SELECTION" not in events
    assert "TOOL_EXECUTION" not in events
    assert "RESPONSE_GENERATION" in events


def test_agent_handles_argument_validation_retry(agent_setup) -> None:
    orchestrator, provider, registry, memory, tracer = agent_setup

    # Queue first response with invalid argument (empty string for 'text')
    bad_tool_call = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_bad",
                name="sentiment_tool",
                arguments={"text": ""},  # Empty string will fail DemoSentimentModel validation
            )
        ],
        finish_reason="tool_calls",
    )
    # Second response with valid argument
    fixed_tool_call = LLMResponse(
        tool_calls=[
            ToolCall(
                id="call_fixed",
                name="sentiment_tool",
                arguments={"text": "Excellent service!"},
            )
        ],
        finish_reason="tool_calls",
    )
    final_synthesis = LLMResponse(
        content="The corrected sentiment analysis indicates positive sentiment.",
        finish_reason="stop",
    )

    provider.queue_response(bad_tool_call)
    provider.queue_response(fixed_tool_call)
    provider.queue_response(final_synthesis)

    result = orchestrator.run(
        user_query="Analyze sentiment please.",
        session_id="retry_session",
    )

    assert result.tool_called is True
    assert result.tool_input == {"text": "Excellent service!"}
    assert result.tool_output["label"] == "positive"

    events = [e["event_type"] for e in result.trace_events]
    assert "ERROR" in events
    assert "RETRY_ATTEMPT" in events
    assert "TOOL_EXECUTION" in events


def test_agent_exhausts_retries_gracefully(agent_setup) -> None:
    orchestrator, provider, registry, memory, tracer = agent_setup

    # Queue invalid tool calls that repeatedly fail
    for i in range(5):
        provider.queue_response(
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id=f"bad_{i}",
                        name="nonexistent_tool",
                        arguments={},
                    )
                ],
                finish_reason="tool_calls",
            )
        )

    result = orchestrator.run(
        user_query="Please call a tool.",
        session_id="failing_session",
    )

    assert "repeated errors" in result.response
    events = [e["event_type"] for e in result.trace_events]
    assert "RETRY_ATTEMPT" in events


def test_agent_multi_turn_memory(agent_setup) -> None:
    orchestrator, provider, registry, memory, tracer = agent_setup

    # Turn 1: Classify sentiment
    r1 = orchestrator.run(
        user_query="Review: 'Fantastic build quality and high performance.' Classify sentiment.",
        session_id="conv_1",
    )
    assert r1.tool_called is True

    # Turn 2: Follow-up question
    r2 = orchestrator.run(
        user_query="Could you summarize why that was classified that way?",
        session_id="conv_1",
    )

    # In turn 2, the message history must contain the prior messages and tool results
    history = memory.get_messages("conv_1")
    # Turn 1 added: user + assistant (tool call) + tool result + assistant (synthesis) = 4
    # Turn 2 added: user + assistant (direct reply) = 2
    assert len(history) == 6


def test_agent_explicit_target_tool(agent_setup) -> None:
    orchestrator, provider, registry, memory, tracer = agent_setup

    # Explicit target tool execution without relying on LLM routing
    result = orchestrator.run(
        user_query="The screen is flickering and battery drains fast.",
        session_id="target_tool_session",
        target_tool="sentiment_tool",
    )
    assert result.tool_called is True
    assert result.tool_name == "sentiment_tool"
    assert result.tool_output is not None


def test_agent_bootstrap_models() -> None:
    from modular_agent.models.bootstrap import bootstrap_default_models
    fresh_registry = ToolRegistry()
    bootstrap_default_models(fresh_registry)

    # Must contain at least the demo sentiment classifier and remote transaction evaluator
    assert fresh_registry.has("demo_sentiment_classifier")
    assert fresh_registry.has("remote_transaction_evaluator")

    # Ingested models must be executable
    remote_tool = fresh_registry.get("remote_transaction_evaluator")
    res = remote_tool.callable(transaction_id="TX-TEST", amount=5000.0, user_country="DE")
    assert res["prediction"] in ("approved", "flagged_for_review", "declined")
    assert res["model_type"] == "remote_rest_api"


