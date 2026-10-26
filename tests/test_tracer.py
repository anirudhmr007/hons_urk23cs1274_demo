"""Tests for the execution tracer and secret sanitization."""

from __future__ import annotations

import time
from modular_agent.agent.tracer import (
    EventStatus,
    ExecutionTracer,
    TraceEventType,
    sanitize_payload,
)


def test_sanitize_payload_masks_sensitive_keys() -> None:
    raw = {
        "user_query": "hello",
        "api_key": "sk-1234567890abcdef",
        "auth_token": "bearer-xyz-123456",
        "nested": {
            "password": "supersecretpassword",
            "normal_field": 42,
        },
        "list_items": [
            {"secret_key": "hidden_val"},
            {"safe_key": "visible_val"},
        ],
    }

    sanitized = sanitize_payload(raw)
    assert sanitized["user_query"] == "hello"
    assert "1234567890" not in sanitized["api_key"]
    assert "xyz" not in sanitized["auth_token"]
    assert "supersecret" not in sanitized["nested"]["password"]
    assert sanitized["nested"]["normal_field"] == 42
    assert "hidden_val" not in sanitized["list_items"][0]["secret_key"]
    assert sanitized["list_items"][1]["safe_key"] == "visible_val"


def test_execution_tracer_records_and_times() -> None:
    tracer = ExecutionTracer()
    tracer.start_timer("step_1")
    time.sleep(0.01)
    duration = tracer.stop_timer("step_1")

    event = tracer.record(
        event_type=TraceEventType.TOOL_EXECUTION,
        status=EventStatus.SUCCESS,
        message="Executed tool",
        payload={"param": 10},
        duration_ms=duration,
    )

    assert event.event_type == TraceEventType.TOOL_EXECUTION
    assert event.status == EventStatus.SUCCESS
    assert event.duration_ms is not None
    assert event.duration_ms > 0
    assert len(tracer.get_events()) == 1

    dict_list = tracer.to_dict_list()
    assert len(dict_list) == 1
    assert dict_list[0]["message"] == "Executed tool"


def test_execution_tracer_clear() -> None:
    tracer = ExecutionTracer()
    tracer.record(TraceEventType.REQUEST_RECEIVED, "Request")
    assert len(tracer.get_events()) == 1
    tracer.clear()
    assert len(tracer.get_events()) == 0

