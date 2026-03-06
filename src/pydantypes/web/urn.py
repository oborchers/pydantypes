"""Validated type for Uniform Resource Names (URNs)."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

# ---------------------------------------------------------------------------
# Pattern A: Urn
# ---------------------------------------------------------------------------

# RFC 8141 Section 2 — ABNF for URN syntax:
#   namestring    = assigned-name [ rq-components ] [ "#" f-component ]
#   assigned-name = "urn" ":" NID ":" NSS
#   NID           = (alphanum) 0*30(ldh) (alphanum)   → 2-32 chars
#   NSS           = pchar *( pchar / "/" )
#   rq-components = [ "?+" r-component ] [ "?=" q-component ]
#
# We capture NID, NSS, and optional ?+r / ?=q / #f components.
_URN_RE = re.compile(
    r"^(?i:urn)"  # case-insensitive "urn" prefix
    r":(?P<nid>[a-zA-Z0-9][a-zA-Z0-9-]{0,30}[a-zA-Z0-9])"
    r":(?P<nss>[a-zA-Z0-9()+,\-./:=@;$_!*'~&%]+)"
    r"(?:\?\+(?P<r_component>(?:(?!\?=)(?!#).)+))?"
    r"(?:\?=(?P<q_component>[^#]+))?"
    r"(?:#(?P<f_component>.+))?$"
)


# Source: https://datatracker.ietf.org/doc/html/rfc8141
class Urn(str):
    """A Uniform Resource Name like urn:isbn:0451450523 with parsed NID and NSS."""

    _pattern: ClassVar[re.Pattern[str]] = _URN_RE

    nid: str
    nss: str
    r_component: str | None
    q_component: str | None
    f_component: str | None

    def __new__(cls, value: str) -> Urn:
        """Create and validate a new Urn instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "urn",
                "Invalid URN: {value}",
                {"value": value},
            )
        nid = m.group("nid")
        if nid.lower().startswith("urn-"):
            raise PydanticCustomError(
                "urn",
                "Invalid URN: NID must not start with 'urn-'. Got: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.nid = nid.lower()
        instance.nss = m.group("nss")
        instance.r_component = m.group("r_component")
        instance.q_component = m.group("q_component")
        instance.f_component = m.group("f_component")
        return instance

    @classmethod
    def _validate(cls, value: str) -> Urn:
        """Validate a string as a Uniform Resource Name."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for Urn."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for Urn."""
        return {
            "type": "string",
            "format": "urn",
            "pattern": cls._pattern.pattern,
            "description": "A Uniform Resource Name (RFC 8141) in the format urn:NID:NSS",
            "examples": ["urn:isbn:0451450523", "urn:ietf:rfc:2648", "urn:oid:2.16.840"],
            "title": "Urn",
        }
