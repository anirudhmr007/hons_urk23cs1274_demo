"""Tests for the tool registry.

Covers:
* Register / retrieve / list / unregister.
* Duplicate registration.
* Missing-tool errors.
* Status and error tracking.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from modular_agent.models.registry import (
    DuplicateToolError,
    ToolEntry,
    ToolNotFoundError,
    ToolRegistry,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

class _DummyInput(BaseModel):
    text: str


class _DummyOutput(BaseModel):
    label: str


def _make_entry(name: str = "test_tool") -> ToolEntry:
    return ToolEntry(
        name=name,
        description="A dummy test tool",
        callable=lambda **kw: {"label": "test"},
        input_schema=_DummyInput,
        output_schema=_DummyOutput,
        adapter=MagicMock(),
    )


# ── Tests ────────────────────────────────────────────────────────────────────

class TestRegistration:

    def test_register_and_retrieve(self, registry: ToolRegistry) -> None:
        entry = _make_entry()
        registry.register(entry)
        assert registry.has("test_tool")
        assert registry.get("test_tool").name == "test_tool"

    def test_duplicate_raises(self, registry: ToolRegistry) -> None:
        registry.register(_make_entry("dup"))
        with pytest.raises(DuplicateToolError):
            registry.register(_make_entry("dup"))

    def test_duplicate_error_is_recorded(self, registry: ToolRegistry) -> None:
        registry.register(_make_entry("dup"))
        with pytest.raises(DuplicateToolError):
            registry.register(_make_entry("dup"))
        assert len(registry.errors) == 1
        assert "dup" in registry.errors[0]


class TestLookup:

    def test_get_nonexistent_raises(self, registry: ToolRegistry) -> None:
        with pytest.raises(ToolNotFoundError):
            registry.get("ghost")

    def test_has_returns_false(self, registry: ToolRegistry) -> None:
        assert registry.has("ghost") is False


class TestListing:

    def test_list_empty(self, registry: ToolRegistry) -> None:
        assert registry.list_tools() == []

    def test_list_multiple(self, registry: ToolRegistry) -> None:
        registry.register(_make_entry("a"))
        registry.register(_make_entry("b"))
        names = {t.name for t in registry.list_tools()}
        assert names == {"a", "b"}


class TestUnregister:

    def test_unregister_existing(self, registry: ToolRegistry) -> None:
        registry.register(_make_entry("removable"))
        registry.unregister("removable")
        assert not registry.has("removable")

    def test_unregister_nonexistent_raises(self, registry: ToolRegistry) -> None:
        with pytest.raises(ToolNotFoundError):
            registry.unregister("ghost")


class TestStatus:

    def test_tool_count(self, registry: ToolRegistry) -> None:
        assert registry.tool_count == 0
        registry.register(_make_entry("x"))
        assert registry.tool_count == 1

    def test_status_dict(self, registry: ToolRegistry) -> None:
        registry.register(_make_entry("x"))
        s = registry.status()
        assert s["registered_tools"] == 1
        assert "x" in s["tool_names"]
        assert isinstance(s["errors"], list)

