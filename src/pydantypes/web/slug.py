"""Validated type for URL slugs."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

_SLUG_MAX_LENGTH = 128


def _validate_slug(v: str) -> str:
    """Validate a URL slug format."""
    if len(v) > _SLUG_MAX_LENGTH:
        raise PydanticCustomError(
            "slug",
            "Invalid slug: must be at most {max_length} characters. Got: {value}",
            {"value": v, "max_length": _SLUG_MAX_LENGTH},
        )
    if not _SLUG_RE.match(v):
        raise PydanticCustomError(
            "slug",
            "Invalid slug: must be lowercase alphanumeric with hyphens. Got: {value}",
            {"value": v},
        )
    return v


# Source: https://python-validators.github.io/validators/reference/slug/
Slug = Annotated[
    str,
    AfterValidator(_validate_slug),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z0-9]+(-[a-z0-9]+)*$",
            "description": "A URL-friendly slug: lowercase alphanumeric with hyphens",
            "examples": ["my-blog-post", "hello-world", "pydantic-types-101"],
            "title": "Slug",
            "maxLength": 128,
        }
    ),
]
