"""Azure identity types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

_RESOURCE_GROUP_RE = re.compile(r"^[a-zA-Z0-9_\-.()]{1,90}$")


def _validate_subscription_id(v: str) -> str:
    """Validate an Azure subscription ID format."""
    if not _UUID_RE.match(v):
        raise PydanticCustomError(
            "azure_subscription_id",
            "Invalid Azure Subscription ID: {value}",
            {"value": v},
        )
    return v.lower()


# Source: https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id
SubscriptionId = Annotated[
    str,
    AfterValidator(_validate_subscription_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "description": "Azure Subscription ID (UUID).",
            "examples": ["12345678-1234-1234-1234-123456789012"],
            "title": "SubscriptionId",
        }
    ),
]
"""Azure Subscription ID (UUID) (e.g. `12345678-1234-1234-1234-123456789012`)."""


def _validate_tenant_id(v: str) -> str:
    """Validate an Azure tenant ID format."""
    if not _UUID_RE.match(v):
        raise PydanticCustomError(
            "azure_tenant_id",
            "Invalid Azure Tenant ID: {value}",
            {"value": v},
        )
    return v.lower()


# Source: https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id
TenantId = Annotated[
    str,
    AfterValidator(_validate_tenant_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "description": "Azure Tenant ID (UUID).",
            "examples": ["12345678-1234-1234-1234-123456789012"],
            "title": "TenantId",
        }
    ),
]
"""Azure Tenant ID (UUID) (e.g. `12345678-1234-1234-1234-123456789012`)."""


def _validate_resource_group_name(v: str) -> str:
    """Validate an Azure resource group name format."""
    if not _RESOURCE_GROUP_RE.match(v) or v.endswith("."):
        raise PydanticCustomError(
            "azure_resource_group_name",
            "Invalid Azure Resource Group name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftresources
ResourceGroupName = Annotated[
    str,
    AfterValidator(_validate_resource_group_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9_\-.()]{1,90}$",
            "description": "Azure Resource Group name.",
            "examples": ["my-resource-group"],
            "title": "ResourceGroupName",
        }
    ),
]
"""Azure Resource Group name (e.g. `my-resource-group`)."""
