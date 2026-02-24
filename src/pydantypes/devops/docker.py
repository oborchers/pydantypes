"""Validated types for Docker image references."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema


# Source: https://github.com/distribution/reference/blob/main/reference.go
class DockerImageRef(str):
    """A Docker/OCI image reference like registry/repo:tag@digest."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^"
        r"(?:(?P<registry>"
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?"
        r"|localhost(?::\d+)?"
        r")/)?"
        r"(?P<repository>[a-z0-9]+(?:[._/-][a-z0-9]+)*)"
        r"(?::(?P<tag>[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}))?"
        r"(?:@(?P<digest>[a-z0-9]+:[a-f0-9]+))?"
        r"$"
    )

    registry: str | None
    repository: str
    tag: str | None
    digest: str | None

    def __new__(cls, value: str) -> DockerImageRef:
        """Create and validate a new DockerImageRef instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "docker_image_ref",
                "Invalid Docker image reference: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.registry = m.group("registry")
        instance.repository = m.group("repository")
        instance.tag = m.group("tag")
        instance.digest = m.group("digest")
        return instance

    @classmethod
    def _validate(cls, value: str) -> DockerImageRef:
        """Validate a string as a Docker image reference."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for DockerImageRef."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for DockerImageRef."""
        return {
            "type": "string",
            "format": "docker-image-ref",
            "pattern": cls._pattern.pattern,
            "description": "A Docker/OCI image reference like registry/repo:tag@digest.",
            "examples": [
                "nginx:latest",
                "ghcr.io/owner/repo:v1.0",
                "registry.example.com/my-app@sha256:abc123",
            ],
            "title": "DockerImageRef",
        }
