"""Cryptographic hash hex digest types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_SHA1_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_MD5_RE = re.compile(r"^[0-9a-fA-F]{32}$")


def _validate_sha256_hex(v: str) -> str:
    """Validate a SHA-256 hex digest format."""
    if not _SHA256_RE.match(v):
        raise PydanticCustomError(
            "sha256_hex",
            "Invalid SHA-256 hex digest: expected 64 hex characters. Got: {value}",
            {"value": v},
        )
    return v.lower()


def _validate_sha1_hex(v: str) -> str:
    """Validate a SHA-1 hex digest format."""
    if not _SHA1_RE.match(v):
        raise PydanticCustomError(
            "sha1_hex",
            "Invalid SHA-1 hex digest: expected 40 hex characters. Got: {value}",
            {"value": v},
        )
    return v.lower()


def _validate_md5_hex(v: str) -> str:
    """Validate an MD5 hex digest format."""
    if not _MD5_RE.match(v):
        raise PydanticCustomError(
            "md5_hex",
            "Invalid MD5 hex digest: expected 32 hex characters. Got: {value}",
            {"value": v},
        )
    return v.lower()


# Source: https://datatracker.ietf.org/doc/html/rfc6234
Sha256Hex = Annotated[
    str,
    AfterValidator(_validate_sha256_hex),
    WithJsonSchema(
        {
            "type": "string",
            "format": "sha256-hex",
            "pattern": r"^[0-9a-fA-F]{64}$",
            "description": "A SHA-256 hex digest (64 hex characters, normalized to lowercase)",
            "examples": ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
            "title": "Sha256Hex",
            "minLength": 64,
            "maxLength": 64,
        }
    ),
]

# Source: https://datatracker.ietf.org/doc/html/rfc3174
Sha1Hex = Annotated[
    str,
    AfterValidator(_validate_sha1_hex),
    WithJsonSchema(
        {
            "type": "string",
            "format": "sha1-hex",
            "pattern": r"^[0-9a-fA-F]{40}$",
            "description": "A SHA-1 hex digest (40 hex characters, normalized to lowercase)",
            "examples": ["da39a3ee5e6b4b0d3255bfef95601890afd80709"],
            "title": "Sha1Hex",
            "minLength": 40,
            "maxLength": 40,
        }
    ),
]

# Source: https://datatracker.ietf.org/doc/html/rfc1321
Md5Hex = Annotated[
    str,
    AfterValidator(_validate_md5_hex),
    WithJsonSchema(
        {
            "type": "string",
            "format": "md5-hex",
            "pattern": r"^[0-9a-fA-F]{32}$",
            "description": "An MD5 hex digest (32 hex characters, normalized to lowercase)",
            "examples": ["d41d8cd98f00b204e9800998ecf8427e"],
            "title": "Md5Hex",
            "minLength": 32,
            "maxLength": 32,
        }
    ),
]
