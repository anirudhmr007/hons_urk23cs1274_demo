"""Ollama local LLM provider adapter.

Connects to a locally running Ollama instance via its REST API.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from modular_agent.providers.base import (
    BaseLLMProvider,
    ChatMessage,
    LLMResponse,
    MessageRole,
    ToolCall,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Local LLM provider utilizing Ollama.

    Parameters:
        base_url: Base URL where Ollama is listening (default: 'http://localhost:11434').
        model_name: Target Ollama model (e.g. 'llama3.1', 'mistral', 'qwen2.5').
        timeout_seconds: Request timeout in seconds.
        client: Optional httpx.Client instance for testing / reuse.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3.1",
        timeout_seconds: float = 60.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds
        self._client = client

    def generate(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Call Ollama chat API with support for function tools."""
        url = f"{self._base_url}/v1/chat/completions"

        # Format messages for OpenAI-compatible endpoint
        formatted_messages: List[Dict[str, Any]] = []
        for msg in messages:
            item: Dict[str, Any] = {
                "role": msg.role.value,
                "content": msg.content or "",
            }
            if msg.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            if msg.name:
                item["name"] = msg.name
            formatted_messages.append(item)

        payload: Dict[str, Any] = {
            "model": self._model_name,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": False,
        }

        if tools:
            payload["tools"] = [t.to_openai_schema() for t in tools]

        owns_client = False
        client = self._client
        if client is None:
            client = httpx.Client(timeout=self._timeout_seconds)
            owns_client = True

        try:
            response = client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Ollama returned HTTP {response.status_code}: {response.text}"
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return LLMResponse(content="", finish_reason="stop", raw_response=data)

            choice = choices[0]
            message_data = choice.get("message", {})
            raw_content = message_data.get("content")
            finish_reason = choice.get("finish_reason", "stop")

            # Parse tool calls if returned
            parsed_tool_calls: List[ToolCall] = []
            raw_tool_calls = message_data.get("tool_calls", [])
            for rtc in raw_tool_calls:
                fn = rtc.get("function", {})
                fn_name = fn.get("name", "")
                fn_args_raw = fn.get("arguments", "{}")
                if isinstance(fn_args_raw, str):
                    try:
                        fn_args = json.loads(fn_args_raw)
                    except json.JSONDecodeError:
                        fn_args = {"raw_input": fn_args_raw}
                else:
                    fn_args = fn_args_raw

                parsed_tool_calls.append(
                    ToolCall(
                        id=rtc.get("id", f"call_{len(parsed_tool_calls)}"),
                        name=fn_name,
                        arguments=fn_args,
                    )
                )

            return LLMResponse(
                content=raw_content,
                tool_calls=parsed_tool_calls,
                finish_reason=finish_reason,
                raw_response=data,
            )

        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {self._base_url}. "
                "Ensure the Ollama application or daemon is running."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Ollama request error for model '{self._model_name}': {exc}"
            ) from exc
        finally:
            if owns_client:
                client.close()

    def name(self) -> str:
        return "ollama"

    def model_name(self) -> str:
        return self._model_name

    def limitations(self) -> List[str]:
        return [
            "Tool calling capability depends on the loaded local model (e.g. Llama 3.1, Mistral, Qwen 2.5 support tools; small 1B/3B models may produce inconsistent schemas).",
            "Local inference speed depends on host hardware and GPU acceleration.",
            "Requires an active Ollama instance running locally (default: http://localhost:11434).",
        ]

