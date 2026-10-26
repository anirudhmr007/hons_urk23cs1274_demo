"""Common LLM provider abstraction and messaging data structures.

Decouples probabilistic LLM cognitive orchestration from concrete model backends
(Ollama, OpenAI, OpenRouter, vLLM, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from modular_agent.models.registry import ToolEntry


def mask_secret(value: Optional[str]) -> str:
    """Safely mask secret strings (such as API keys) for logging and display."""
    if not value:
        return "[NOT SET]"
    if len(value) <= 8:
        return "***"
    return f"{value[:3]}...{value[-4:]}"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """Represents a structured tool invocation requested by the LLM."""

    id: str = Field(default="", description="Unique identifier for the tool call.")
    name: str = Field(..., description="Name of the target tool to execute.")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parsed keyword arguments for the tool function.",
    )


class ChatMessage(BaseModel):
    """Normalized chat message structure across all LLM providers."""

    role: MessageRole = Field(..., description="The role of the message participant.")
    content: Optional[str] = Field(default=None, description="Textual message content.")
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="List of tool calls requested by the model (assistant only).",
    )
    tool_call_id: Optional[str] = Field(
        default=None,
        description="ID of the tool call this message responds to (tool role only).",
    )
    name: Optional[str] = Field(
        default=None,
        description="Optional name of the tool or author.",
    )


class ToolDefinition(BaseModel):
    """Normalized tool schema declaration sent to LLMs."""

    name: str = Field(..., description="Unique tool name.")
    description: str = Field(..., description="Tool description for model routing.")
    parameters: Dict[str, Any] = Field(
        ...,
        description="JSON Schema object describing input parameters.",
    )

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to standard OpenAI-compatible tool specification format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class LLMResponse(BaseModel):
    """Structured response returned by an LLM provider."""

    content: Optional[str] = Field(
        default=None,
        description="Generated natural language response.",
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Parsed tool invocation requests.",
    )
    finish_reason: Optional[str] = Field(
        default="stop",
        description="Completion stop reason (e.g. 'stop', 'tool_calls').",
    )
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw provider payload for debugging/tracing.",
    )

    @property
    def has_tool_calls(self) -> bool:
        """True if the model generated at least one tool call request."""
        return len(self.tool_calls) > 0


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers.

    All implementations must support:
    - Multi-turn conversation messages.
    - Dynamic tool definitions and structured function calling.
    - Safe error reporting and fallback.
    """

    @abstractmethod
    def generate(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Generate a completion for the provided message sequence and tools."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'ollama', 'openai', 'mock')."""
        ...

    @abstractmethod
    def model_name(self) -> str:
        """Name of the model being invoked (e.g. 'llama3.1', 'gpt-4o-mini')."""
        ...

    @abstractmethod
    def limitations(self) -> List[str]:
        """Documented provider-specific tool-calling limitations."""
        ...

    def convert_tool_to_definition(self, tool: ToolEntry) -> ToolDefinition:
        """Convert a registered :class:`ToolEntry` into an LLM :class:`ToolDefinition`."""
        schema_dict = tool.input_schema.model_json_schema()
        # Clean up title if present
        schema_dict.pop("title", None)
        return ToolDefinition(
            name=tool.name,
            description=tool.description,
            parameters=schema_dict,
        )

