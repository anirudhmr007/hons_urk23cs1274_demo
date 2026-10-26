"""Session-based conversational memory.

Maintains multi-turn context including user prompts, model decisions, tool calls,
and actual tool outputs for each independent conversation session.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from modular_agent.providers.base import ChatMessage, MessageRole

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages multi-turn conversation histories keyed by session_id."""

    def __init__(self, max_history_turns: int = 50) -> None:
        self._max_history_turns = max_history_turns
        self._sessions: Dict[str, List[ChatMessage]] = {}

    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Return a copy of the message history for a given session."""
        return list(self._sessions.get(session_id, []))

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Append a message to the specified session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(message)

        # Enforce history bound to avoid unbounded memory growth
        if len(self._sessions[session_id]) > self._max_history_turns * 2:
            self._sessions[session_id] = self._sessions[session_id][-self._max_history_turns * 2:]

    def add_user_message(self, session_id: str, content: str) -> None:
        """Helper to append a user message."""
        self.add_message(
            session_id,
            ChatMessage(role=MessageRole.USER, content=content),
        )

    def add_assistant_message(
        self,
        session_id: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[Any]] = None,
    ) -> None:
        """Helper to append an assistant message."""
        self.add_message(
            session_id,
            ChatMessage(
                role=MessageRole.ASSISTANT,
                content=content,
                tool_calls=tool_calls,
            ),
        )

    def add_tool_result(
        self,
        session_id: str,
        tool_call_id: str,
        name: str,
        result_content: str,
    ) -> None:
        """Helper to append an actual tool result to the conversation."""
        self.add_message(
            session_id,
            ChatMessage(
                role=MessageRole.TOOL,
                content=result_content,
                tool_call_id=tool_call_id,
                name=name,
            ),
        )

    def get_last_tool_result(self, session_id: str) -> Optional[ChatMessage]:
        """Retrieve the most recent tool execution message if one exists."""
        history = self._sessions.get(session_id, [])
        for msg in reversed(history):
            if msg.role == MessageRole.TOOL:
                return msg
        return None

    def reset_session(self, session_id: str) -> None:
        """Clear all conversation history for a given session."""
        if session_id in self._sessions:
            self._sessions[session_id].clear()
            logger.info("Reset conversation history for session: %s", session_id)

    def list_sessions(self) -> List[str]:
        """Return all active session IDs."""
        return list(self._sessions.keys())

    def session_message_count(self, session_id: str) -> int:
        """Return the number of messages recorded for this session."""
        return len(self._sessions.get(session_id, []))
