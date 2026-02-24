"""MIME type with parsed components."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema


# Source: https://datatracker.ietf.org/doc/html/rfc6838
class MimeType(str):
    """A MIME type like application/json or text/html;charset=utf-8."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<type>[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_.+]*)"
        r"/(?P<subtype>[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_.+]*)"
        r"(?P<params>;.*)?$"
    )

    type: str
    subtype: str
    parameters: dict[str, str]

    def __new__(cls, value: str) -> MimeType:
        """Create and validate a new MimeType instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "mime_type",
                "Invalid MIME type: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.type = m.group("type")
        instance.subtype = m.group("subtype")
        params_str = m.group("params") or ""
        params: dict[str, str] = {}
        if params_str:
            for param in params_str.split(";"):
                param = param.strip()
                if not param:
                    continue
                if "=" in param:
                    k, v_param = param.split("=", 1)
                    params[k.strip()] = v_param.strip()
        instance.parameters = params
        return instance

    @classmethod
    def _validate(cls, value: str) -> MimeType:
        """Validate a string as a MIME type."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for MimeType."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for MimeType."""
        return {
            "type": "string",
            "format": "mime-type",
            "pattern": cls._pattern.pattern,
            "description": "A MIME type like application/json or text/html;charset=utf-8",
            "examples": ["application/json", "text/html;charset=utf-8"],
            "title": "MimeType",
        }
