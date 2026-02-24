"""JSON Web Token (JWT) type with parsed header and payload."""

from __future__ import annotations

import base64
import json
from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema


# Source: https://datatracker.ietf.org/doc/html/rfc7519
class Jwt(str):
    """A JSON Web Token (JWT) string with parsed header and payload."""

    header: dict[str, Any]
    payload: dict[str, Any]

    def __new__(cls, value: str) -> Jwt:
        """Create and validate a new Jwt instance."""
        parts = value.split(".")
        if len(parts) != 3:
            raise PydanticCustomError(
                "jwt",
                "Invalid JWT: expected 3 dot-separated parts. Got: {value}",
                {"value": value},
            )
        try:
            header = cls._decode_part(parts[0])
        except Exception as e:
            raise PydanticCustomError(
                "jwt",
                "Invalid JWT header: could not decode. Got: {value}",
                {"value": value},
            ) from e
        try:
            payload = cls._decode_part(parts[1])
        except Exception as e:
            raise PydanticCustomError(
                "jwt",
                "Invalid JWT payload: could not decode. Got: {value}",
                {"value": value},
            ) from e
        instance = str.__new__(cls, value)
        instance.header = header
        instance.payload = payload
        return instance

    @staticmethod
    def _decode_part(part: str) -> dict[str, Any]:
        padded = part + "=" * (-len(part) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        result: dict[str, Any] = json.loads(decoded)
        return result

    @classmethod
    def _validate(cls, value: str) -> Jwt:
        """Validate a string as a JSON Web Token."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for Jwt."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for Jwt."""
        return {
            "type": "string",
            "format": "jwt",
            "description": (
                "A JSON Web Token (JWT) with three dot-separated base64url-encoded parts"
            ),
            "examples": [
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
            ],
            "title": "Jwt",
        }
