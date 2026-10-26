"""Hosted LLM provider adapter (OpenAI-compatible).

Supports OpenAI, OpenRouter, Groq, vLLM, and any OpenAI-compatible API endpoint.
Ensures API keys are never exposed in logs or serialized representations.
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
    ToolCall,
    ToolDefinition,
    mask_secret,
)

logger = logging.getLogger(__name__)


class HostedOpenAIProvider(BaseLLMProvider):
    """Adapter for hosted OpenAI-compatible APIs.

    Parameters:
        api_key: Secret API key for authentication.
        base_url: Endpoint base URL (default: 'https://api.openai.com/v1').
        model_name: Model identifier (default: 'gpt-4o-mini').
        timeout_seconds: Request timeout in seconds.
        client: Optional httpx.Client instance for testing / connection pooling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model_name: str = "gpt-4o-mini",
        timeout_seconds: float = 60.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key or ""
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
        """Call hosted OpenAI chat completions endpoint."""
        if not self._api_key:
            raise ValueError(
                "API key is not configured for hosted LLM provider. "
                "Set MA_LLM_API_KEY environment variable or pass api_key."
            )

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # Format messages
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
        }

        if tools:
            payload["tools"] = [t.to_openai_schema() for t in tools]

        owns_client = False
        client = self._client
        if client is None:
            client = httpx.Client(timeout=self._timeout_seconds)
            owns_client = True

        logger.info(
            "Dispatching request to hosted provider: url=%s, model=%s, key=%s",
            url,
            self._model_name,
            mask_secret(self._api_key),
        )

        try:
            response = client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Hosted provider returned HTTP {response.status_code}: {response.text}"
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return LLMResponse(content="", finish_reason="stop", raw_response=data)

            choice = choices[0]
            message_data = choice.get("message", {})
            raw_content = message_data.get("content")
            finish_reason = choice.get("finish_reason", "stop")

            parsed_tool_calls: List[ToolCall] = []
            for rtc in message_data.get("tool_calls", []):
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

        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Hosted provider connection failed to {self._base_url}: {exc}"
            ) from exc
        finally:
            if owns_client:
                client.close()

    def name(self) -> str:
        return "hosted"

    def model_name(self) -> str:
        return self._model_name

    def limitations(self) -> List[str]:
        return [
            "Requires active internet connectivity and valid API credentials.",
            "Subject to remote rate limits, token costs, and third-party terms of service.",
            "Network latency may be higher than local inference.",
        ]

    def __repr__(self) -> str:
        return (
            f"HostedOpenAIProvider(model='{self._model_name}', "
            f"base_url='{self._base_url}', api_key='{mask_secret(self._api_key)}')"
        )

