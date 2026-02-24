"""Azure compute types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_FUNCTION_APP_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,58}[a-zA-Z0-9]$")
_APP_SERVICE_NAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,57}[a-zA-Z0-9])?$")
_AKS_CLUSTER_NAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9_-]{0,61}[a-zA-Z0-9])?$")
_CONTAINER_APP_NAME_RE = re.compile(r"^[a-z]([a-z0-9-]{0,29}[a-z0-9])?$")
_LOG_ANALYTICS_WORKSPACE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]{2,61}[a-zA-Z0-9]$")
_API_MANAGEMENT_NAME_RE = re.compile(r"^[a-zA-Z]([a-zA-Z0-9-]{0,48}[a-zA-Z0-9])?$")


def _validate_function_app_name(v: str) -> str:
    """Validate an Azure Function App name format."""
    if not _FUNCTION_APP_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_function_app_name",
            "Invalid Azure Function App name: {value}",
            {"value": v},
        )
    return v


def _validate_app_service_name(v: str) -> str:
    """Validate an Azure App Service name format."""
    if not _APP_SERVICE_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_app_service_name",
            "Invalid Azure App Service name: {value}",
            {"value": v},
        )
    return v


def _validate_aks_cluster_name(v: str) -> str:
    """Validate an Azure AKS cluster name format."""
    if not _AKS_CLUSTER_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_aks_cluster_name",
            "Invalid Azure AKS cluster name: {value}",
            {"value": v},
        )
    return v


def _validate_container_app_name(v: str) -> str:
    """Validate an Azure Container App name format."""
    if not _CONTAINER_APP_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_container_app_name",
            "Invalid Azure Container App name: {value}",
            {"value": v},
        )
    return v


def _validate_log_analytics_workspace_name(v: str) -> str:
    """Validate an Azure Log Analytics workspace name format."""
    if not _LOG_ANALYTICS_WORKSPACE_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_log_analytics_workspace_name",
            "Invalid Azure Log Analytics workspace name: {value}",
            {"value": v},
        )
    return v


def _validate_api_management_name(v: str) -> str:
    """Validate an Azure API Management name format."""
    if not _API_MANAGEMENT_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_api_management_name",
            "Invalid Azure API Management name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftweb
FunctionAppName = Annotated[
    str,
    AfterValidator(_validate_function_app_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,58}[a-zA-Z0-9]$",
            "description": "Azure Function App name.",
            "examples": ["my-function-app"],
            "title": "FunctionAppName",
        }
    ),
]

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftweb
AppServiceName = Annotated[
    str,
    AfterValidator(_validate_app_service_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,57}[a-zA-Z0-9])?$",
            "description": "Azure App Service name.",
            "examples": ["my-app-service"],
            "title": "AppServiceName",
        }
    ),
]

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftcontainerservice
AksClusterName = Annotated[
    str,
    AfterValidator(_validate_aks_cluster_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9]([a-zA-Z0-9_-]{0,61}[a-zA-Z0-9])?$",
            "description": "Azure AKS cluster name.",
            "examples": ["my-aks-cluster"],
            "title": "AksClusterName",
        }
    ),
]

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftapp
ContainerAppName = Annotated[
    str,
    AfterValidator(_validate_container_app_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z]([a-z0-9-]{0,29}[a-z0-9])?$",
            "description": "Azure Container App name.",
            "examples": ["my-container-app"],
            "title": "ContainerAppName",
        }
    ),
]

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftoperationalinsights
LogAnalyticsWorkspaceName = Annotated[
    str,
    AfterValidator(_validate_log_analytics_workspace_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9-]{2,61}[a-zA-Z0-9]$",
            "description": "Azure Log Analytics workspace name.",
            "examples": ["my-log-analytics"],
            "title": "LogAnalyticsWorkspaceName",
        }
    ),
]

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftapimanagement
ApiManagementName = Annotated[
    str,
    AfterValidator(_validate_api_management_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z]([a-zA-Z0-9-]{0,48}[a-zA-Z0-9])?$",
            "description": "Azure API Management name.",
            "examples": ["my-apim"],
            "title": "ApiManagementName",
        }
    ),
]
