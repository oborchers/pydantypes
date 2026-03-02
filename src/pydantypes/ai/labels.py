"""AI classification label types with lifecycle management."""

from __future__ import annotations

import warnings
from enum import Enum
from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError, core_schema


class Label:
    """Descriptor for LabelEnum members with lifecycle metadata."""

    __slots__ = ("aliases", "deprecated", "description", "note", "retired", "successor", "value")

    def __init__(
        self,
        value: str,
        *,
        description: str = "",
        note: str = "",
        deprecated: bool = False,
        retired: bool = False,
        successor: str | None = None,
        aliases: list[str] | None = None,
    ) -> None:
        self.value = value
        self.description = description
        self.note = note
        self.deprecated = deprecated
        self.retired = retired
        self.successor = successor
        self.aliases = aliases or []


class LabelEnum(str, Enum):
    """Enum base class for LLM classification labels with lifecycle management.

    Produces clean JSON Schema compatible with OpenAI structured outputs,
    LangChain with_structured_output, and all Pydantic-based LLM frameworks.

    Lifecycle stages: active -> deprecated -> retired -> removed.
    """

    description: str
    note: str
    deprecated: bool
    retired: bool
    successor: str | None
    aliases: list[str]

    def __new__(cls, label: Label | str) -> LabelEnum:
        if isinstance(label, str):
            label = Label(label)
        obj = str.__new__(cls, label.value)
        obj._value_ = label.value
        obj.description = label.description
        obj.note = label.note
        obj.deprecated = label.deprecated
        obj.retired = label.retired
        obj.successor = label.successor
        obj.aliases = label.aliases
        return obj

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def active_labels(cls) -> list[LabelEnum]:
        """Return all non-deprecated, non-retired members."""
        return [m for m in cls if not m.deprecated and not m.retired]

    @classmethod
    def deprecated_labels(cls) -> list[LabelEnum]:
        """Return all deprecated (but not retired) members."""
        return [m for m in cls if m.deprecated and not m.retired]

    @classmethod
    def retired_labels(cls) -> list[LabelEnum]:
        """Return all retired members."""
        return [m for m in cls if m.retired]

    @classmethod
    def schema_values(cls) -> list[str]:
        """Return values for JSON Schema enum array (excludes retired)."""
        return [m.value for m in cls if not m.retired]

    @classmethod
    def alias_map(cls) -> dict[str, LabelEnum]:
        """Return mapping of alias strings to their target members."""
        return {alias: m for m in cls for alias in m.aliases}

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        alias_lookup = cls.alias_map()

        def _validate(value: Any) -> LabelEnum:
            # Pass through already-instantiated enum members
            if isinstance(value, cls):
                return value
            # Check aliases first — aliases take priority over retired direct matches
            if value in alias_lookup:
                return alias_lookup[value]
            # Try direct enum resolution
            for member in cls:
                if member.value == value:
                    if member.retired:
                        raise PydanticCustomError(
                            "retired_label",
                            "Label '{value}' is retired. Use '{successor}' instead.",
                            {"value": value, "successor": member.successor or "?"},
                        )
                    if member.deprecated:
                        warnings.warn(
                            f"Label '{value}' is deprecated."
                            + (f" Use '{member.successor}' instead." if member.successor else ""),
                            DeprecationWarning,
                            stacklevel=4,
                        )
                    return member
            raise PydanticCustomError(
                "invalid_label",
                "'{value}' is not a valid {enum_name}",
                {"value": value, "enum_name": cls.__name__},
            )

        return core_schema.no_info_plain_validator_function(
            _validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: v.value, info_arg=False
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "string",
            "enum": cls.schema_values(),
            "title": cls.__name__,
        }
