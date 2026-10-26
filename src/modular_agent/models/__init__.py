"""Model adapter interfaces and concrete implementations."""

from modular_agent.models.base import FieldContract, ModelAdapter, ModelContract
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import (
    DuplicateToolError,
    ToolEntry,
    ToolNotFoundError,
    ToolRegistry,
)
from modular_agent.models.rest_api_model import RestApiModelAdapter
from modular_agent.models.sklearn_model import SklearnModelAdapter

__all__ = [
    "FieldContract",
    "ModelContract",
    "ModelAdapter",
    "DemoSentimentModel",
    "SklearnModelAdapter",
    "RestApiModelAdapter",
    "ToolRegistry",
    "ToolEntry",
    "DuplicateToolError",
    "ToolNotFoundError",
]
