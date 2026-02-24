"""Azure container types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_CONTAINER_REGISTRY_NAME_RE = re.compile(r"^[a-zA-Z0-9]{5,50}$")


def _validate_container_registry_name(v: str) -> str:
    """Validate an Azure Container Registry name format."""
    if not _CONTAINER_REGISTRY_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_container_registry_name",
            "Invalid Azure Container Registry name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftcontainerregistry
ContainerRegistryName = Annotated[
    str,
    AfterValidator(_validate_container_registry_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9]{5,50}$",
            "description": "Azure Container Registry name.",
            "examples": ["mycontainerregistry"],
            "title": "ContainerRegistryName",
            "minLength": 5,
            "maxLength": 50,
        }
    ),
]
"""Azure Container Registry name (e.g. `mycontainerregistry`)."""
