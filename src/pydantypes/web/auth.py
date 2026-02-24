"""Validated types for HTTP authentication headers."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema


# Source: https://datatracker.ietf.org/doc/html/rfc6750
class BearerToken(str):
    """A Bearer token string like 'Bearer <token>' with the extracted token value."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(r"^Bearer ([a-zA-Z0-9._~+/]+=*)$")

    token: str

    def __new__(cls, value: str) -> BearerToken:
        """Create and validate a new BearerToken instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "bearer_token",
                "Invalid Bearer token: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.token = m.group(1)
        return instance

    @classmethod
    def _validate(cls, value: str) -> BearerToken:
        """Validate a string as a Bearer token."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for BearerToken."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for BearerToken."""
        return {
            "type": "string",
            "format": "bearer-token",
            "pattern": cls._pattern.pattern,
            "description": "An HTTP Bearer token (RFC 6750)",
            "examples": ["Bearer eyJhbGciOiJIUzI1NiIs..."],
            "title": "BearerToken",
        }
