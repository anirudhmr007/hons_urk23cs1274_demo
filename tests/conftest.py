"""Shared pytest fixtures."""

from __future__ import annotations

import os

# Guarantee deterministic test execution independent of local daemons/credentials
os.environ["MA_LLM_PROVIDER"] = "mock"
os.environ["MA_LLM_MODEL"] = "mock-agent-model"

import pytest

from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import ToolRegistry


@pytest.fixture
def registry() -> ToolRegistry:
    """A fresh, empty tool registry."""
    return ToolRegistry()


@pytest.fixture
def demo_model() -> DemoSentimentModel:
    """A loaded demonstration sentiment model."""
    model = DemoSentimentModel()
    model.load()
    return model


@pytest.fixture
def unloaded_demo_model() -> DemoSentimentModel:
    """An unloaded demonstration sentiment model."""
    return DemoSentimentModel()

