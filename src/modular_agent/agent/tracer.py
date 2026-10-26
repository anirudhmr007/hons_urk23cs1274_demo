"""Execution tracer for recording actual agent events.

Captures real-time execution steps, timestamps, status codes, and execution durations
while ensuring secrets and sensitive information are never exposed in logs or traces.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from modular_agent.providers.base import mask_secret


class TraceEventType(str, Enum):
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    TOOL_SELECTION = "TOOL_SELECTION"
    ARG_VALIDATION = "ARG_VALIDATION"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    OUTPUT_VALIDATION = "OUTPUT_VALIDATION"
    RETRY_ATTEMPT = "RETRY_ATTEMPT"
    ERROR = "ERROR"
    RESPONSE_GENERATION = "RESPONSE_GENERATION"


class EventStatus(str, Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"


class TraceEvent(BaseModel):
    """An immutable record of a single step in the agent execution pipeline."""

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of the event.",
    )
    event_type: TraceEventType = Field(..., description="Categorical event type.")
    status: EventStatus = Field(default=EventStatus.INFO, description="Status code.")
    message: str = Field(..., description="Human-readable event message.")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Sanitized contextual data associated with the event.",
    )
    duration_ms: Optional[float] = Field(
        default=None,
        description="Elapsed duration for this step in milliseconds.",
    )


_SENSITIVE_CONTAINS = {
    "password",
    "secret",
    "api_key",
    "apikey",
    "auth_token",
    "access_token",
    "private_key",
    "authorization",
}
_SENSITIVE_TOKENS = {"password", "secret", "token", "auth", "api_key", "apikey"}


def is_sensitive_key(key: str) -> bool:
    """Return True if key represents a credential or secret."""
    lower = key.lower().replace("-", "_")
    if any(term in lower for term in _SENSITIVE_CONTAINS):
        return True
    parts = set(lower.split("_"))
    return bool(parts & _SENSITIVE_TOKENS)


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize sensitive keys (e.g. api_key, password, token)."""
    sanitized: Dict[str, Any] = {}

    for k, v in payload.items():
        if is_sensitive_key(k):
            sanitized[k] = mask_secret(str(v)) if v is not None else "[NOT SET]"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_payload(v)
        elif isinstance(v, (list, tuple)):
            sanitized[k] = [
                sanitize_payload(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            sanitized[k] = v

    return sanitized


class ExecutionTracer:
    """Manages recording and query access to execution traces."""

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []
        self._step_start_times: Dict[str, float] = {}

    def start_timer(self, step_key: str) -> None:
        """Start tracking duration for a specific step."""
        self._step_start_times[step_key] = time.perf_counter()

    def stop_timer(self, step_key: str) -> Optional[float]:
        """Stop tracking duration and return elapsed time in milliseconds."""
        start_time = self._step_start_times.pop(step_key, None)
        if start_time is None:
            return None
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return round(elapsed, 2)

    def record(
        self,
        event_type: TraceEventType,
        message: str,
        status: EventStatus = EventStatus.INFO,
        payload: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> TraceEvent:
        """Record a new trace event with automatic secret sanitization."""
        clean_payload = sanitize_payload(payload or {})
        event = TraceEvent(
            event_type=event_type,
            status=status,
            message=message,
            payload=clean_payload,
            duration_ms=duration_ms,
        )
        self._events.append(event)
        return event

    def get_events(self) -> List[TraceEvent]:
        """Return a copy of all recorded events."""
        return list(self._events)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Return serializable representation of all events."""
        return [event.model_dump() for event in self._events]

    def clear(self) -> None:
        """Reset the trace history."""
        self._events.clear()
        self._step_start_times.clear()
