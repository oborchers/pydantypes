"""Azure messaging types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_SERVICE_BUS_NAMESPACE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]{4,48}[a-zA-Z0-9]$")
_EVENT_HUB_NAMESPACE_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]{4,48}[a-zA-Z0-9]$")


def _validate_service_bus_namespace(v: str) -> str:
    """Validate an Azure Service Bus namespace format."""
    if not _SERVICE_BUS_NAMESPACE_RE.match(v):
        raise PydanticCustomError(
            "azure_service_bus_namespace",
            "Invalid Azure Service Bus namespace: {value}",
            {"value": v},
        )
    return v


def _validate_event_hub_namespace_name(v: str) -> str:
    """Validate an Azure Event Hub namespace name format."""
    if not _EVENT_HUB_NAMESPACE_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_event_hub_namespace_name",
            "Invalid Azure Event Hub namespace name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftservicebus
ServiceBusNamespace = Annotated[
    str,
    AfterValidator(_validate_service_bus_namespace),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z][a-zA-Z0-9-]{4,48}[a-zA-Z0-9]$",
            "description": "Azure Service Bus namespace.",
            "examples": ["my-servicebus-ns"],
            "title": "ServiceBusNamespace",
        }
    ),
]
"""Azure Service Bus namespace (e.g. `my-servicebus-ns`)."""

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsofteventhub
EventHubNamespaceName = Annotated[
    str,
    AfterValidator(_validate_event_hub_namespace_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z][a-zA-Z0-9-]{4,48}[a-zA-Z0-9]$",
            "description": "Azure Event Hub namespace name.",
            "examples": ["my-eventhub-ns"],
            "title": "EventHubNamespaceName",
        }
    ),
]
"""Azure Event Hub namespace name (e.g. `my-eventhub-ns`)."""
