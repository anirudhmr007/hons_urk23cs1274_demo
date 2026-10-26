"""Tests for Gradio UI backend handlers."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from modular_agent.ui.app import (
    build_app,
    get_dashboard_summary,
    get_trace_log_view,
    handle_agent_chat,
    handle_generate_deployment,
    handle_model_ingestion,
    handle_reset_chat,
)


def test_get_dashboard_summary() -> None:
    health, prov, mod, count, table = get_dashboard_summary()
    assert "Healthy" in health
    assert prov != ""
    assert mod != ""
    assert int(count) >= 1
    assert len(table) >= 1
    # Check that demo model is present in the table
    tool_names = [row[0] for row in table]
    assert "demo_sentiment_classifier" in tool_names


def test_handle_model_ingestion_demo() -> None:
    status, schema_in, schema_out = handle_model_ingestion(
        model_type="demo",
        name="ui_sentiment_tool",
        description="Sentiment classifier from UI",
        sklearn_path="",
        rest_url="",
        rest_method="POST",
        custom_contracts_json="",
    )
    assert "Successfully ingested" in status
    assert "properties" in json.loads(schema_in)
    assert "properties" in json.loads(schema_out)


def test_handle_model_ingestion_invalid_sklearn() -> None:
    status, schema_in, schema_out = handle_model_ingestion(
        model_type="sklearn",
        name="bad_sklearn",
        description="",
        sklearn_path="",
        rest_url="",
        rest_method="POST",
        custom_contracts_json="",
    )
    assert "Error" in status


def test_handle_agent_chat_and_reset() -> None:
    # Chat with tool call
    new_hist, info, t_in, t_out = handle_agent_chat(
        user_query="Please classify sentiment of: 'This software is wonderful and works great!'",
        history=[],
        session_id="ui_test_sess",
    )
    assert len(new_hist) == 1
    assert "Tool Invoked" in info
    assert "positive" in t_out.lower() or "label" in t_out

    # Chat without tool call
    new_hist2, info2, _, _ = handle_agent_chat(
        user_query="Hello there!",
        history=new_hist,
        session_id="ui_test_sess",
    )
    assert len(new_hist2) == 2
    assert "No predictive tool" in info2

    # Reset
    empty_hist, reset_msg, _, _ = handle_reset_chat("ui_test_sess")
    assert empty_hist == []
    assert "reset" in reset_msg.lower()


def test_get_trace_log_view() -> None:
    rows = get_trace_log_view()
    assert isinstance(rows, list)
    if rows:
        # Check columns: Time, Event Type, Status, Duration, Message, Payload
        assert len(rows[0]) == 6


def test_handle_generate_deployment(tmp_path: Path) -> None:
    status, dockerfile_txt, compose_txt, zip_path = handle_generate_deployment(
        app_name="ui-agent",
        port=8000,
        python_ver="3.12-slim",
        provider="mock",
        model="llama3.1",
        out_dir="test_ui_deploy",
    )
    assert "Successfully created" in status or "successfully created" in status
    assert "EXPOSE 8000" in dockerfile_txt
    assert "8000:8000" in compose_txt
    assert Path(zip_path).exists()


def test_build_app_instantiates_blocks() -> None:
    demo = build_app()
    assert demo is not None

