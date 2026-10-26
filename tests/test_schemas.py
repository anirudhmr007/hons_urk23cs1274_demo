"""Tests for Pydantic schema generation from model contracts.

Covers:
* Simple and multi-field schemas.
* Optional fields with defaults.
* Every supported type (str, int, float, bool, list).
* Unsupported type rejection.
* Empty contract rejection.
* Pydantic validation of generated schemas.
* JSON Schema output.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from modular_agent.models.base import FieldContract, ModelContract
from modular_agent.schemas.tool_schemas import (
    SchemaGenerationError,
    generate_pydantic_schema,
)


class TestHappyPath:

    def test_single_str_field(self) -> None:
        contract = ModelContract(fields={
            "name": FieldContract(type="str", required=True, description="A name"),
        })
        Schema = generate_pydantic_schema(contract, "SingleStr")
        assert Schema(name="hello").name == "hello"

    def test_multiple_field_types(self) -> None:
        contract = ModelContract(fields={
            "text": FieldContract(type="str", required=True),
            "count": FieldContract(type="int", required=True),
            "score": FieldContract(type="float", required=True),
            "flag": FieldContract(type="bool", required=True),
            "items": FieldContract(type="list", required=True),
        })
        Schema = generate_pydantic_schema(contract, "MultiField")
        inst = Schema(text="hi", count=3, score=0.9, flag=True, items=[1, 2])
        assert inst.text == "hi"
        assert inst.count == 3
        assert inst.items == [1, 2]

    def test_optional_field_with_default(self) -> None:
        contract = ModelContract(fields={
            "name": FieldContract(type="str", required=True),
            "tag": FieldContract(
                type="str", required=False, default="default_tag",
            ),
        })
        Schema = generate_pydantic_schema(contract, "WithOptional")
        inst = Schema(name="hello")
        assert inst.tag == "default_tag"


class TestValidation:

    def test_rejects_wrong_type(self) -> None:
        contract = ModelContract(fields={
            "count": FieldContract(type="int", required=True),
        })
        Schema = generate_pydantic_schema(contract, "IntOnly")
        with pytest.raises(ValidationError):
            Schema(count="not_an_int")

    def test_rejects_missing_required(self) -> None:
        contract = ModelContract(fields={
            "name": FieldContract(type="str", required=True),
        })
        Schema = generate_pydantic_schema(contract, "Required")
        with pytest.raises(ValidationError):
            Schema()


class TestUnsupportedConfigs:

    def test_unsupported_type_raises(self) -> None:
        contract = ModelContract(fields={
            "data": FieldContract(type="numpy_array", required=True),
        })
        with pytest.raises(SchemaGenerationError, match="Unsupported field type"):
            generate_pydantic_schema(contract, "Bad")

    def test_empty_contract_raises(self) -> None:
        contract = ModelContract(fields={})
        with pytest.raises(SchemaGenerationError, match="at least one field"):
            generate_pydantic_schema(contract, "Empty")


class TestJsonSchemaOutput:

    def test_json_schema_has_properties(self) -> None:
        contract = ModelContract(fields={
            "text": FieldContract(
                type="str", required=True, description="Input text",
            ),
        })
        Schema = generate_pydantic_schema(contract, "JsonTest")
        js = Schema.model_json_schema()
        assert "properties" in js
        assert "text" in js["properties"]
        assert js["properties"]["text"]["description"] == "Input text"

