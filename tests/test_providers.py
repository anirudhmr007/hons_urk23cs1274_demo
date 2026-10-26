"""Tests for LLM provider abstraction and adapters.

Covers:
* MockLLMProvider deterministic responses and tool calling simulation.
* OllamaProvider OpenAI-compatible payload generation and tool call parsing.
* HostedOpenAIProvider authentication, payload dispatch, and error handling.
* Secret masking utility (no exposed API keys).
* Tool schema translation from ToolEntry to OpenAI tool definitions.
* Provider factory (create_llm_provider).
"""

from __future__ import annotations

import httpx
import pytest
from pydantic import BaseModel

from modular_agent.config import AppConfig
from modular_agent.models.registry import ToolEntry
from modular_agent.providers import (
    ChatMessage,
    HostedOpenAIProvider,
    LLMResponse,
    MessageRole,
    MockLLMProvider,
    OllamaProvider,
    ToolCall,
    ToolDefinition,
    create_llm_provider,
    mask_secret,
)


class _SampleInput(BaseModel):
    text: str


class _SampleOutput(BaseModel):
    label: str


def _make_dummy_tool(name: str = "sentiment_tool") -> ToolEntry:
    return ToolEntry(
        name=name,
        description="Analyzes sentiment of text.",
        callable=lambda text: {"label": "positive"},
        input_schema=_SampleInput,
        output_schema=_SampleOutput,
        adapter=None,  # type: ignore[arg-type]
    )


class TestSecretMasking:

    def test_masks_normal_api_key(self) -> None:
        masked = mask_secret("sk-proj-1234567890abcdef")
        assert "1234567890" not in masked
        assert masked.startswith("sk-")
        assert masked.endswith("cdef")

    def test_masks_short_key(self) -> None:
        assert mask_secret("12345") == "***"

    def test_handles_none_or_empty(self) -> None:
        assert mask_secret(None) == "[NOT SET]"
        assert mask_secret("") == "[NOT SET]"


class TestMockLLMProvider:

    def test_queued_response_returned(self) -> None:
        provider = MockLLMProvider()
        expected = LLMResponse(content="Custom queued answer", finish_reason="stop")
        provider.queue_response(expected)

        resp = provider.generate([ChatMessage(role=MessageRole.USER, content="Hello")])
        assert resp.content == "Custom queued answer"
        assert provider.call_count == 1

    def test_auto_generates_tool_call_for_sentiment(self) -> None:
        provider = MockLLMProvider()
        tool_entry = _make_dummy_tool()
        tool_def = provider.convert_tool_to_definition(tool_entry)

        resp = provider.generate(
            messages=[ChatMessage(role=MessageRole.USER, content="What is the sentiment of this text?")],
            tools=[tool_def],
        )
        assert resp.has_tool_calls is True
        assert resp.tool_calls[0].name == "sentiment_tool"
        assert "text" in resp.tool_calls[0].arguments

    def test_synthesizes_tool_response(self) -> None:
        provider = MockLLMProvider()
        resp = provider.generate([
            ChatMessage(role=MessageRole.USER, content="Query"),
            ChatMessage(role=MessageRole.TOOL, content='{"label": "positive"}'),
        ])
        assert resp.content is not None
        assert "positive" in resp.content


class TestOllamaProvider:

    def test_generates_and_parses_tool_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/chat/completions"
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_123",
                                        "type": "function",
                                        "function": {
                                            "name": "sentiment_tool",
                                            "arguments": '{"text": "good product"}',
                                        },
                                    }
                                ],
                            },
                        }
                    ]
                },
            )

        client = httpx.Client(transport=httpx.MockTransport(handler))
        provider = OllamaProvider(client=client)

        resp = provider.generate([ChatMessage(role=MessageRole.USER, content="Analyze this")])
        assert resp.has_tool_calls is True
        assert resp.tool_calls[0].name == "sentiment_tool"
        assert resp.tool_calls[0].arguments == {"text": "good product"}

    def test_connection_failure_raises_clear_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        client = httpx.Client(transport=httpx.MockTransport(handler))
        provider = OllamaProvider(client=client)

        with pytest.raises(RuntimeError, match="Could not connect to Ollama"):
            provider.generate([ChatMessage(role=MessageRole.USER, content="Hi")])


class TestHostedOpenAIProvider:

    def test_raises_if_api_key_missing(self) -> None:
        provider = HostedOpenAIProvider(api_key="")
        with pytest.raises(ValueError, match="API key is not configured"):
            provider.generate([ChatMessage(role=MessageRole.USER, content="Test")])

    def test_sends_authorization_header(self) -> None:
        captured_auth: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured_auth.append(request.headers.get("Authorization", ""))
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {"role": "assistant", "content": "Hello from cloud LLM"},
                        }
                    ]
                },
            )

        client = httpx.Client(transport=httpx.MockTransport(handler))
        provider = HostedOpenAIProvider(api_key="sk-test-secret-key-12345", client=client)

        resp = provider.generate([ChatMessage(role=MessageRole.USER, content="Hi")])
        assert resp.content == "Hello from cloud LLM"
        assert captured_auth[0] == "Bearer sk-test-secret-key-12345"

    def test_repr_does_not_leak_raw_api_key(self) -> None:
        provider = HostedOpenAIProvider(api_key="sk-super-secret-key-abcdefg")
        repr_str = repr(provider)
        assert "sk-super-secret-key-abcdefg" not in repr_str
        assert "sk-...defg" in repr_str


class TestProviderFactory:

    def test_creates_mock_provider(self) -> None:
        cfg = AppConfig(llm_provider="mock", llm_model="test-mock")
        provider = create_llm_provider(cfg)
        assert provider.name() == "mock"
        assert provider.model_name() == "test-mock"

    def test_creates_ollama_provider(self) -> None:
        cfg = AppConfig(llm_provider="ollama", llm_model="llama3.1")
        provider = create_llm_provider(cfg)
        assert provider.name() == "ollama"
        assert provider.model_name() == "llama3.1"

    def test_creates_hosted_provider(self) -> None:
        cfg = AppConfig(llm_provider="hosted", llm_api_key="sk-1234567890")
        provider = create_llm_provider(cfg)
        assert provider.name() == "hosted"

    def test_unsupported_provider_raises(self) -> None:
        cfg = AppConfig(llm_provider="unknown-provider")
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm_provider(cfg)

