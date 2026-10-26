"""Tool registry for managing model-backed tools.

Each tool is identified by a unique name and backed by a
:class:`~modular_agent.models.base.ModelAdapter`.  The registry provides
lookup, enumeration, lifecycle management, and error tracking.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel

from modular_agent.models.base import ModelAdapter

logger = logging.getLogger(__name__)


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ToolEntry:
    """An immutable record of a registered tool."""

    name: str
    description: str
    callable: Callable[..., Dict[str, Any]]
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    adapter: ModelAdapter


# ── Errors ───────────────────────────────────────────────────────────────────

class DuplicateToolError(Exception):
    """A tool with the same name is already registered."""


class ToolNotFoundError(Exception):
    """The requested tool does not exist in the registry."""


# ── Registry ─────────────────────────────────────────────────────────────────

class ToolRegistry:
    """Registry that maps unique tool names to :class:`ToolEntry` records.

    Thread-safety is **not** guaranteed — the registry is intended for use
    within a single application process, protected by the web-framework's
    own concurrency model.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolEntry] = {}
        self._errors: List[str] = []

    # ── Mutators ─────────────────────────────────────────────────────

    def register(self, entry: ToolEntry) -> None:
        """Register *entry*.  Raises on duplicate names."""
        if entry.name in self._tools:
            msg = f"Tool '{entry.name}' is already registered."
            self._errors.append(msg)
            raise DuplicateToolError(msg)
        self._tools[entry.name] = entry
        logger.info("Registered tool: '%s'", entry.name)

    def unregister(self, name: str) -> None:
        """Remove the tool identified by *name*."""
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' not found in registry.")
        del self._tools[name]
        logger.info("Unregistered tool: '%s'", name)

    # ── Queries ──────────────────────────────────────────────────────

    def get(self, name: str) -> ToolEntry:
        """Return the :class:`ToolEntry` for *name*, or raise."""
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' not found in registry.")
        return self._tools[name]

    def has(self, name: str) -> bool:
        """Return ``True`` if *name* is registered."""
        return name in self._tools

    def list_tools(self) -> List[ToolEntry]:
        """Return a list of all registered tool entries."""
        return list(self._tools.values())

    # ── Introspection ────────────────────────────────────────────────

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    @property
    def errors(self) -> List[str]:
        """Accumulated registration errors (informational)."""
        return list(self._errors)

    def status(self) -> Dict[str, Any]:
        """Return a JSON-serialisable status summary."""
        return {
            "registered_tools": self.tool_count,
            "tool_names": list(self._tools.keys()),
            "errors": self.errors,
        }

