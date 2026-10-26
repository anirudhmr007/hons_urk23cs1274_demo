"""Tests for session-based conversational memory."""

from __future__ import annotations

from modular_agent.agent.memory import ConversationMemory
from modular_agent.providers.base import MessageRole


def test_memory_add_and_retrieve_messages() -> None:
    mem = ConversationMemory()
    mem.add_user_message("sess_1", "What is the sentiment?")
    mem.add_assistant_message("sess_1", "Calling tool...")
    mem.add_tool_result("sess_1", "call_1", "sentiment_tool", '{"label": "positive"}')
    mem.add_assistant_message("sess_1", "The sentiment is positive.")

    msgs = mem.get_messages("sess_1")
    assert len(msgs) == 4
    assert msgs[0].role == MessageRole.USER
    assert msgs[0].content == "What is the sentiment?"
    assert msgs[2].role == MessageRole.TOOL
    assert msgs[2].name == "sentiment_tool"


def test_session_isolation() -> None:
    mem = ConversationMemory()
    mem.add_user_message("user_A", "Question from A")
    mem.add_user_message("user_B", "Question from B")

    msgs_a = mem.get_messages("user_A")
    msgs_b = mem.get_messages("user_B")

    assert len(msgs_a) == 1
    assert msgs_a[0].content == "Question from A"
    assert len(msgs_b) == 1
    assert msgs_b[0].content == "Question from B"


def test_get_last_tool_result() -> None:
    mem = ConversationMemory()
    mem.add_user_message("sess", "Question")
    assert mem.get_last_tool_result("sess") is None

    mem.add_tool_result("sess", "c1", "t1", '{"score": 1}')
    mem.add_assistant_message("sess", "Reply")
    last_tool = mem.get_last_tool_result("sess")
    assert last_tool is not None
    assert last_tool.content == '{"score": 1}'


def test_reset_session() -> None:
    mem = ConversationMemory()
    mem.add_user_message("sess", "Hello")
    assert mem.session_message_count("sess") == 1
    mem.reset_session("sess")
    assert mem.session_message_count("sess") == 0
    assert mem.get_messages("sess") == []

