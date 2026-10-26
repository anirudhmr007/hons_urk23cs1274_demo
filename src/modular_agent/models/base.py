"""Abstract base class for predictive model adapters.

Every model that participates in the Modular-Agent framework must implement
this interface.  The adapter cleanly separates *deterministic* model inference
from any *probabilistic* LLM orchestration layer that may invoke it later.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel, Field


# ── Contract primitives ──────────────────────────────────────────────────────

class FieldContract(BaseModel):
    """Schema definition for a single field in a model's I/O contract."""

    type: str = Field(
        ...,
        description="Python type name: str, int, float, bool, list",
    )
    required: bool = Field(
        default=True,
        description="Whether the field must be present in every request",
    )
    description: str = Field(
        default="",
        description="Human-readable explanation of the field",
    )
    default: Any = Field(
        default=None,
        description="Default value when *required* is False",
    )


class ModelContract(BaseModel):
    """Declares the full input or output contract of a model adapter."""

    fields: Dict[str, FieldContract]


# ── Adapter ABC ──────────────────────────────────────────────────────────────

class ModelAdapter(ABC):
    """Abstract base class for predictive model adapters.

    Concrete subclasses must implement every abstract method so that
    the ingestion engine can:

    * Load the model into memory.
    * Discover its I/O contract.
    * Generate Pydantic schemas for validation.
    * Create a callable tool wrapper.
    * Register the tool by name and description.

    Lifecycle
    ---------
    1. ``__init__()`` — construct (no heavy work).
    2. ``load()``     — train / deserialize / connect.
    3. ``predict()``  — execute inference (repeatable).
    """

    def __init__(self) -> None:
        self._loaded: bool = False

    # ── Abstract interface ───────────────────────────────────────────────

    @abstractmethod
    def load(self) -> None:
        """Load (or train) the model.  Must set ``self._loaded = True``."""
        ...

    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on *input_data*.

        Args:
            input_data: Dictionary whose keys match :meth:`input_contract`.

        Returns:
            Dictionary whose keys match :meth:`output_contract`.

        Raises:
            ValueError:    If *input_data* is invalid.
            RuntimeError:  If the model has not been loaded.
        """
        ...

    @abstractmethod
    def input_contract(self) -> ModelContract:
        """Declare the expected input fields."""
        ...

    @abstractmethod
    def output_contract(self) -> ModelContract:
        """Declare the returned output fields."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Unique tool name used for registration."""
        ...

    @abstractmethod
    def description(self) -> str:
        """Human-readable description used for tool registration."""
        ...

    # ── Concrete helpers ─────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        """Whether :meth:`load` has completed successfully."""
        return self._loaded

