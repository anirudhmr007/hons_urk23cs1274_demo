"""Model ingestion engine.

Orchestrates the full pipeline:

1. **Validate** the :class:`ModelConfig`.
2. **Instantiate** the correct :class:`ModelAdapter` subclass.
3. **Load** the model.
4. **Generate** Pydantic input/output schemas from the adapter's contracts.
5. **Wrap** the adapter in a validated callable.
6. **Register** the resulting tool in a :class:`ToolRegistry`.

The engine is *LLM-agnostic*: it never imports or depends on any LLM
provider.  The registered tool callable is a plain Python function that
can be invoked directly or wrapped by a later orchestration layer.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from modular_agent.models.base import ModelAdapter, ModelContract
from modular_agent.models.demo_model import DemoSentimentModel
from modular_agent.models.registry import ToolEntry, ToolRegistry
from modular_agent.models.rest_api_model import RestApiModelAdapter
from modular_agent.models.sklearn_model import SklearnModelAdapter
from modular_agent.schemas.tool_schemas import (
    SchemaGenerationError,
    generate_pydantic_schema,
)

logger = logging.getLogger(__name__)

# ── Adapter type registry (module-level) ─────────────────────────────────────
# Maps short names ("demo", "sklearn", …) to ModelAdapter subclasses.

_ADAPTER_REGISTRY: Dict[str, Type[ModelAdapter]] = {
    "demo": DemoSentimentModel,
    "sklearn": SklearnModelAdapter,
    "rest_api": RestApiModelAdapter,
}


def register_adapter_type(type_name: str, adapter_class: Type[ModelAdapter]) -> None:
    """Make *adapter_class* available under *type_name* for ingestion configs."""
    _ADAPTER_REGISTRY[type_name] = adapter_class


def get_adapter_types() -> List[str]:
    """Return the currently registered adapter type names."""
    return list(_ADAPTER_REGISTRY.keys())


# ── Configuration & result models ────────────────────────────────────────────

class ModelConfig(BaseModel):
    """Describes a model to ingest.

    Attributes:
        model_type:  Registered adapter type name (e.g. ``"demo"``).
        name:        Override for the generated tool name.
        description: Override for the generated tool description.
        parameters:  Keyword arguments forwarded to the adapter constructor.
    """

    model_config = ConfigDict(protected_namespaces=())

    model_type: str = Field(..., description="Adapter type name")
    name: Optional[str] = Field(default=None, description="Override tool name")
    description: Optional[str] = Field(default=None, description="Override tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class IngestionResult(BaseModel):
    """Outcome of a single ingestion attempt."""

    model_config = ConfigDict(protected_namespaces=())

    success: bool
    tool_name: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    input_schema_json: Optional[Dict[str, Any]] = None
    output_schema_json: Optional[Dict[str, Any]] = None


# ── Engine ───────────────────────────────────────────────────────────────────

class IngestionEngine:
    """Stateless engine that ingests models into a :class:`ToolRegistry`."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    # ── Public entry point ───────────────────────────────────────────

    def ingest(self, config: ModelConfig) -> IngestionResult:
        """Run the full ingestion pipeline for *config*.

        This method never raises.  All errors are captured in the
        returned :class:`IngestionResult`.
        """
        errors: List[str] = []

        # 1 ── resolve adapter class ──────────────────────────────────
        adapter_class = _ADAPTER_REGISTRY.get(config.model_type)
        if adapter_class is None:
            errors.append(
                f"Unsupported model type '{config.model_type}'. "
                f"Supported types: {get_adapter_types()}"
            )
            return IngestionResult(success=False, errors=errors)

        # 2 ── instantiate adapter ────────────────────────────────────
        try:
            adapter = adapter_class(**config.parameters)
        except Exception as exc:
            errors.append(f"Failed to instantiate adapter: {exc}")
            return IngestionResult(success=False, errors=errors)

        # 3 ── load model ─────────────────────────────────────────────
        try:
            adapter.load()
        except Exception as exc:
            errors.append(f"Failed to load model: {exc}")
            return IngestionResult(success=False, errors=errors)

        if not adapter.is_loaded:
            errors.append("Adapter.load() returned but is_loaded is still False.")
            return IngestionResult(success=False, errors=errors)

        # 4 ── resolve name / description ─────────────────────────────
        tool_name = config.name or adapter.name()
        tool_description = config.description or adapter.description()

        if not tool_name or not tool_name.strip():
            errors.append("Tool name must not be empty.")
            return IngestionResult(success=False, errors=errors)

        # 5 ── generate input schema ──────────────────────────────────
        try:
            input_contract = adapter.input_contract()
            input_schema = generate_pydantic_schema(
                input_contract, f"{tool_name}_Input",
            )
        except SchemaGenerationError as exc:
            errors.append(f"Input schema generation failed: {exc}")
            return IngestionResult(success=False, errors=errors)

        # 6 ── generate output schema ─────────────────────────────────
        try:
            output_contract = adapter.output_contract()
            output_schema = generate_pydantic_schema(
                output_contract, f"{tool_name}_Output",
            )
        except SchemaGenerationError as exc:
            errors.append(f"Output schema generation failed: {exc}")
            return IngestionResult(success=False, errors=errors)

        # 7 ── build callable wrapper ─────────────────────────────────
        tool_callable = self._make_tool_callable(
            adapter, input_schema, output_schema, tool_name,
        )

        # 8 ── register ───────────────────────────────────────────────
        entry = ToolEntry(
            name=tool_name,
            description=tool_description,
            callable=tool_callable,
            input_schema=input_schema,
            output_schema=output_schema,
            adapter=adapter,
        )

        try:
            self._registry.register(entry)
        except Exception as exc:
            errors.append(f"Tool registration failed: {exc}")
            return IngestionResult(success=False, errors=errors)

        logger.info("Successfully ingested model as tool '%s'", tool_name)

        return IngestionResult(
            success=True,
            tool_name=tool_name,
            input_schema_json=input_schema.model_json_schema(),
            output_schema_json=output_schema.model_json_schema(),
        )

    # ── Internal helpers ─────────────────────────────────────────────

    @staticmethod
    def _make_tool_callable(
        adapter: ModelAdapter,
        input_schema: Type[BaseModel],
        output_schema: Type[BaseModel],
        tool_name: str,
    ) -> Callable[..., Dict[str, Any]]:
        """Return a closure that validates → predicts → validates."""

        def _call(**kwargs: Any) -> Dict[str, Any]:
            # validate input
            try:
                validated_input = input_schema(**kwargs)
            except ValidationError as ve:
                raise ValueError(f"Input validation failed: {ve}") from ve

            # execute prediction
            result = adapter.predict(validated_input.model_dump())

            # validate output (warn only — do not block)
            try:
                output_schema(**result)
            except ValidationError as ve:
                logger.warning(
                    "Output validation warning for tool '%s': %s",
                    tool_name, ve,
                )

            return result

        _call.__name__ = tool_name
        _call.__doc__ = adapter.description()
        return _call

