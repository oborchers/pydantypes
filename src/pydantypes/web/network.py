"""Validated types for network identifiers."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

# ---------------------------------------------------------------------------
# Pattern A: Fqdn
# ---------------------------------------------------------------------------

_FQDN_LABEL_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")


# Source: https://www.rfc-editor.org/rfc/rfc1123
class Fqdn(str):
    """A fully qualified domain name like www.example.com with parsed labels."""

    labels: list[str]
    tld: str

    def __new__(cls, value: str) -> Fqdn:
        """Create and validate a new Fqdn instance."""
        # Strip optional trailing dot (DNS absolute notation)
        normalized = value.rstrip(".")
        if not normalized:
            raise PydanticCustomError(
                "fqdn", "Invalid FQDN: must not be empty. Got: {value}", {"value": value}
            )
        if len(normalized) > 253:
            raise PydanticCustomError(
                "fqdn",
                "Invalid FQDN: total length must be <= 253. Got: {value}",
                {"value": value},
            )
        labels = normalized.split(".")
        if len(labels) < 2:
            raise PydanticCustomError(
                "fqdn",
                "Invalid FQDN: must have at least 2 labels. Got: {value}",
                {"value": value},
            )
        for label in labels:
            if not label or len(label) > 63:
                raise PydanticCustomError(
                    "fqdn",
                    "Invalid FQDN: each label must be 1-63 characters. Got: {value}",
                    {"value": value},
                )
            if not _FQDN_LABEL_RE.match(label):
                raise PydanticCustomError(
                    "fqdn",
                    "Invalid FQDN: label contains invalid characters. Got: {value}",
                    {"value": value},
                )
        normalized = normalized.lower()
        instance = str.__new__(cls, normalized)
        instance.labels = normalized.split(".")
        instance.tld = instance.labels[-1]
        return instance

    @classmethod
    def _validate(cls, value: str) -> Fqdn:
        """Validate a string as a fully qualified domain name."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for Fqdn."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for Fqdn."""
        return {
            "type": "string",
            "format": "fqdn",
            "description": "A fully qualified domain name (RFC 1123, normalized to lowercase)",
            "examples": ["www.example.com", "api.github.com"],
            "title": "Fqdn",
            "maxLength": 253,
        }


# ---------------------------------------------------------------------------
# Pattern A: PortRange
# ---------------------------------------------------------------------------


# Source: https://www.rfc-editor.org/rfc/rfc6335
class PortRange(str):
    """A TCP/UDP port or port range like 443 or 8080-8090 with parsed endpoints."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(r"^(?P<start>\d{1,5})(?:-(?P<end>\d{1,5}))?$")

    start: int
    end: int

    def __new__(cls, value: str) -> PortRange:
        """Create and validate a new PortRange instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "port_range",
                "Invalid port range: {value}",
                {"value": value},
            )
        start = int(m.group("start"))
        end_str = m.group("end")
        end = int(end_str) if end_str else start
        if start > 65535:
            raise PydanticCustomError(
                "port_range",
                "Invalid port range: port must be 0-65535. Got: {value}",
                {"value": value},
            )
        if end > 65535:
            raise PydanticCustomError(
                "port_range",
                "Invalid port range: port must be 0-65535. Got: {value}",
                {"value": value},
            )
        if start > end:
            raise PydanticCustomError(
                "port_range",
                "Invalid port range: start must be <= end. Got: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.start = start
        instance.end = end
        return instance

    @classmethod
    def _validate(cls, value: str) -> PortRange:
        """Validate a string as a port range."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for PortRange."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for PortRange."""
        return {
            "type": "string",
            "format": "port-range",
            "pattern": cls._pattern.pattern,
            "description": "A TCP/UDP port (0-65535) or port range like 8080-8090",
            "examples": ["443", "8080-8090", "0"],
            "title": "PortRange",
        }
