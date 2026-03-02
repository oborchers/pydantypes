"""Internal utilities for Pydantic type construction."""

from __future__ import annotations

import sys
from typing import Any

if sys.version_info >= (3, 11):
    from enum import StrEnum as StrEnum  # noqa: PLC0414 — intentional re-export
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum backcompat shim for Python 3.10."""

        def __str__(self) -> str:
            return str(self.value)


from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


def _str_type_core_schema(cls: Any, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
    """Build a Pydantic core schema for a str-subclass validated type."""
    return core_schema.json_or_python_schema(
        json_schema=core_schema.no_info_after_validator_function(
            cls._validate, core_schema.str_schema()
        ),
        python_schema=core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.no_info_after_validator_function(
                    cls._validate, core_schema.str_schema()
                ),
            ]
        ),
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda v: str(v), info_arg=False
        ),
    )
