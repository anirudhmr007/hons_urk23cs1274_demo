"""Mock LLM provider for deterministic offline testing.

Enables full agent orchestration testing without live Ollama instances or API keys.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import uuid

from modular_agent.providers.base import (
    BaseLLMProvider,
    ChatMessage,
    LLMResponse,
    MessageRole,
    ToolCall,
    ToolDefinition,
)


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock LLM provider for testing agent behaviors.

    Can be programmed with:
    - Pre-defined response queues.
    - Rule-based auto-routing based on user message content.
    - Simulated tool calls or standard text completions.
    """

    def __init__(
        self,
        model_name: str = "mock-agent-model",
        custom_router: Optional[
            Callable[[List[ChatMessage], Optional[List[ToolDefinition]]], LLMResponse]
        ] = None,
    ) -> None:
        self._model_name = model_name
        self._custom_router = custom_router
        self._responses_queue: List[LLMResponse] = []
        self._call_history: List[List[ChatMessage]] = []

    def queue_response(self, response: LLMResponse) -> None:
        """Enqueue an explicit response to return on subsequent generate() calls."""
        self._responses_queue.append(response)

    @property
    def call_count(self) -> int:
        return len(self._call_history)

    def generate(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Generate response via queue, custom router, or intelligent defaults."""
        self._call_history.append(list(messages))

        # 1. Use queued response if available
        if self._responses_queue:
            return self._responses_queue.pop(0)

        # 2. Use custom router if provided
        if self._custom_router:
            return self._custom_router(messages, tools)

        # 3. Default rule-based behavior
        last_message = messages[-1] if messages else None
        if not last_message:
            return LLMResponse(content="No message received.", finish_reason="stop")

        # If previous message is a tool response, synthesize an explanation
        if last_message.role == MessageRole.TOOL:
            return LLMResponse(
                content=f"Based on the tool result: {last_message.content}",
                finish_reason="stop",
            )

        # If user asks for sentiment analysis and a sentiment tool is present
        user_text = (last_message.content or "").lower()
        if tools and any("sentiment" in user_text or "classify" in user_text or "review" in user_text for _ in [1]):
            # Find matching tool
            matching_tool = next(
                (t for t in tools if "sentiment" in t.name or "sentiment" in t.description.lower()),
                tools[0] if tools else None,
            )
            if matching_tool:
                call_id = f"call_{uuid.uuid4().hex[:8]}"
                # Extract plausible text parameter from prompt
                return LLMResponse(
                    content=None,
                    tool_calls=[
                        ToolCall(
                            id=call_id,
                            name=matching_tool.name,
                            arguments={"text": last_message.content or "Sample text"},
                        )
                    ],
                    finish_reason="tool_calls",
                )

        # If user asks for transaction evaluation and a transaction/remote tool is present
        if tools and any("transaction" in user_text or "remote" in user_text or "fraud" in user_text or "tx-" in user_text for _ in [1]):
            matching_tool = next(
                (t for t in tools if "transaction" in t.name or "remote" in t.name or "fraud" in t.name or "rest" in t.name),
                None,
            )
            if matching_tool:
                call_id = f"call_{uuid.uuid4().hex[:8]}"
                return LLMResponse(
                    content=None,
                    tool_calls=[
                        ToolCall(
                            id=call_id,
                            name=matching_tool.name,
                            arguments={
                                "transaction_id": "TX-8041",
                                "amount": 15000.0,
                                "user_country": "DE",
                            },
                        )
                    ],
                    finish_reason="tool_calls",
                )

        # If user asks for risk evaluation / numerical features
        if tools and any("risk" in user_text or "feature" in user_text or "diagnos" in user_text for _ in [1]):
            matching_tool = next(
                (t for t in tools if "risk" in t.name or "feature" in t.name),
                None,
            )
            if matching_tool:
                call_id = f"call_{uuid.uuid4().hex[:8]}"
                return LLMResponse(
                    content=None,
                    tool_calls=[
                        ToolCall(
                            id=call_id,
                            name=matching_tool.name,
                            arguments={"features": [17.99, 10.38, 122.8, 1001.0]},
                        )
                    ],
                    finish_reason="tool_calls",
                )

        # Standard conversation reply
        return LLMResponse(
            content=f"I processed your message: '{last_message.content}' without calling any tool.",
            finish_reason="stop",
        )

    def name(self) -> str:
        return "mock"

    def model_name(self) -> str:
        return self._model_name

    def limitations(self) -> List[str]:
        return [
            "Mock provider generates simulated responses.",
            "Useful for deterministic testing; does not perform real neural language generation.",
        ]

