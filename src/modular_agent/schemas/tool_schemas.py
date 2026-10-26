"""Dynamic Pydantic schema generation from model contracts.

Given a :class:`~modular_agent.models.base.ModelContract`, this module
creates a runtime Pydantic ``BaseModel`` subclass whose fields, types,
and constraints mirror the contract.  The generated model can then be
used for both *input validation* and *output validation* within tool
wrappers.

Supported contract type names
-----------------------------
``str``, ``int``, ``float``, ``bool``, ``list``

Any other type string produces a :class:`SchemaGenerationError` with a
clear message listing the supported alternatives.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, ConfigDict, Field, create_model

from modular_agent.models.base import FieldContract, ModelContract


# ── Type mapping ─────────────────────────────────────────────────────────────

_TYPE_MAP: Dict[str, Type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
}

SUPPORTED_TYPES: frozenset[str] = frozenset(_TYPE_MAP)


# ── Errors ───────────────────────────────────────────────────────────────────

class SchemaGenerationError(Exception):
    """Raised when a contract cannot be converted to a Pydantic schema."""


# ── Public API ───────────────────────────────────────────────────────────────

def _resolve_type(field: FieldContract) -> Type:
    """Map a contract type name to its Python type, or raise."""
    python_type = _TYPE_MAP.get(field.type)
    if python_type is None:
        raise SchemaGenerationError(
            f"Unsupported field type '{field.type}'. "
            f"Supported types: {sorted(SUPPORTED_TYPES)}"
        )
    return python_type


def generate_pydantic_schema(
    contract: ModelContract,
    schema_name: str,
) -> Type[BaseModel]:
    """Create a Pydantic model class from *contract*.

    Args:
        contract:    Declares the fields, types, and optionality.
        schema_name: Class name for the generated model.

    Returns:
        A dynamically created :class:`pydantic.BaseModel` subclass.

    Raises:
        SchemaGenerationError: If any field type is unsupported or the
            contract defines zero fields.
    """
    if not contract.fields:
        raise SchemaGenerationError(
            "Contract must define at least one field."
        )

    field_definitions: Dict[str, Any] = {}

    for field_name, field_spec in contract.fields.items():
        python_type = _resolve_type(field_spec)

        if field_spec.required:
            field_definitions[field_name] = (
                python_type,
                Field(..., description=field_spec.description),
            )
        else:
            field_definitions[field_name] = (
                Optional[python_type],
                Field(default=field_spec.default, description=field_spec.description),
            )

    return create_model(
        schema_name,
        __config__=ConfigDict(protected_namespaces=()),
        **field_definitions,
    )

