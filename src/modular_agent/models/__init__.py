"""Model adapter interfaces and concrete implementations."""

from modular_agent.models.base import FieldContract, ModelAdapter, ModelContract
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import (
    DuplicateToolError,
    ToolEntry,
    ToolNotFoundError,
    ToolRegistry,
)
from modular_agent.models.bootstrap import bootstrap_default_models
from modular_agent.models.rest_api_model import RestApiModelAdapter, default_fraud_evaluator
from modular_agent.models.sklearn_model import SklearnModelAdapter

__all__ = [
    "FieldContract",
    "ModelContract",
    "ModelAdapter",
    "DemoSentimentModel",
    "SklearnModelAdapter",
    "RestApiModelAdapter",
    "default_fraud_evaluator",
    "bootstrap_default_models",
    "ToolRegistry",
    "ToolEntry",
    "DuplicateToolError",
    "ToolNotFoundError",
]
