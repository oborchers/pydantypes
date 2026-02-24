"""GCP compute types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_CLOUD_RUN_SERVICE_NAME_RE = re.compile(r"^[a-z]([a-z0-9-]{0,47}[a-z0-9])?$")
_COMPUTE_RESOURCE_NAME_RE = re.compile(r"^[a-z]([-a-z0-9]{0,61}[a-z0-9])?$")
_CLOUD_FUNCTION_NAME_RE = re.compile(r"^[a-z]([-a-z0-9]{0,47}[a-z0-9])?$")


def _validate_cloud_run_service_name(v: str) -> str:
    """Validate a Cloud Run service name format."""
    if not _CLOUD_RUN_SERVICE_NAME_RE.match(v):
        raise PydanticCustomError(
            "gcp_cloud_run_service_name",
            "Invalid GCP Cloud Run service name: {value}",
            {"value": v},
        )
    return v


def _validate_compute_resource_name(v: str) -> str:
    """Validate a Compute Engine resource name format."""
    if not _COMPUTE_RESOURCE_NAME_RE.match(v):
        raise PydanticCustomError(
            "gcp_compute_resource_name",
            "Invalid GCP Compute resource name: {value}",
            {"value": v},
        )
    return v


def _validate_cloud_function_name(v: str) -> str:
    """Validate a Cloud Function name format."""
    if not _CLOUD_FUNCTION_NAME_RE.match(v):
        raise PydanticCustomError(
            "gcp_cloud_function_name",
            "Invalid GCP Cloud Function name: {value}",
            {"value": v},
        )
    return v


# Source: https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services
CloudRunServiceName = Annotated[
    str,
    AfterValidator(_validate_cloud_run_service_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _CLOUD_RUN_SERVICE_NAME_RE.pattern,
            "description": "A GCP Cloud Run service name (1-49 lowercase chars).",
            "examples": ["my-service"],
            "title": "CloudRunServiceName",
        }
    ),
]
"""A GCP Cloud Run service name (1-49 lowercase chars) (e.g. `my-service`)."""

# Source: https://cloud.google.com/compute/docs/naming-resources
ComputeResourceName = Annotated[
    str,
    AfterValidator(_validate_compute_resource_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _COMPUTE_RESOURCE_NAME_RE.pattern,
            "description": "A GCP Compute Engine resource name (1-63 lowercase chars).",
            "examples": ["my-vm-instance"],
            "title": "ComputeResourceName",
        }
    ),
]
"""A GCP Compute Engine resource name (1-63 lowercase chars) (e.g. `my-vm-instance`)."""

# Source: https://cloud.google.com/functions/docs/reference/rest/v2/projects.locations.functions
CloudFunctionName = Annotated[
    str,
    AfterValidator(_validate_cloud_function_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _CLOUD_FUNCTION_NAME_RE.pattern,
            "description": "A GCP Cloud Function name (1-49 lowercase chars).",
            "examples": ["my-function"],
            "title": "CloudFunctionName",
        }
    ),
]
"""A GCP Cloud Function name (1-49 lowercase chars) (e.g. `my-function`)."""
