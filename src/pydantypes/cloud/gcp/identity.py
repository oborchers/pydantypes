"""GCP identity types."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

_PROJECT_ID_RE = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
_PROJECT_NUMBER_RE = re.compile(r"^[1-9]\d+$")
_BILLING_ACCOUNT_ID_RE = re.compile(r"^[A-Z0-9]{6}-[A-Z0-9]{6}-[A-Z0-9]{6}$")
_ORGANIZATION_ID_RE = re.compile(r"^[1-9]\d*$")

_RESERVED_PROJECT_IDS = frozenset({"google", "undefined", "null", "ssl"})


def _validate_project_id(v: str) -> str:
    """Validate a GCP project ID format."""
    if not _PROJECT_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_project_id",
            "Invalid GCP project ID: {value}",
            {"value": v},
        )
    if v in _RESERVED_PROJECT_IDS:
        raise PydanticCustomError(
            "gcp_project_id",
            "Invalid GCP project ID: '{value}' is a reserved word",
            {"value": v},
        )
    return v


def _validate_project_number(v: str) -> str:
    """Validate a GCP project number format."""
    if not _PROJECT_NUMBER_RE.match(v):
        raise PydanticCustomError(
            "gcp_project_number",
            "Invalid GCP project number: {value}",
            {"value": v},
        )
    return v


def _validate_billing_account_id(v: str) -> str:
    """Validate a GCP billing account ID format."""
    if not _BILLING_ACCOUNT_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_billing_account_id",
            "Invalid GCP billing account ID: {value}",
            {"value": v},
        )
    return v


def _validate_organization_id(v: str) -> str:
    """Validate a GCP organization ID format."""
    if not _ORGANIZATION_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_organization_id",
            "Invalid GCP organization ID: {value}",
            {"value": v},
        )
    return v


# Source: https://cloud.google.com/resource-manager/docs/creating-managing-projects
ProjectId = Annotated[
    str,
    AfterValidator(_validate_project_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _PROJECT_ID_RE.pattern,
            "description": "A GCP project ID (6-30 lowercase chars).",
            "examples": ["my-project-123"],
            "title": "ProjectId",
        }
    ),
]
"""A GCP project ID (6-30 lowercase chars) (e.g. `my-project-123`)."""

# Source: https://cloud.google.com/resource-manager/docs/creating-managing-projects
ProjectNumber = Annotated[
    str,
    AfterValidator(_validate_project_number),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _PROJECT_NUMBER_RE.pattern,
            "description": "A GCP project number.",
            "examples": ["123456789012"],
            "title": "ProjectNumber",
        }
    ),
]
"""A GCP project number (e.g. `123456789012`)."""

# Source: https://cloud.google.com/billing/docs/how-to/find-billing-account-id
BillingAccountId = Annotated[
    str,
    AfterValidator(_validate_billing_account_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _BILLING_ACCOUNT_ID_RE.pattern,
            "description": "A GCP billing account ID.",
            "examples": ["01A2B3-C4D5E6-F7G8H9"],
            "title": "BillingAccountId",
        }
    ),
]
"""A GCP billing account ID (e.g. `01A2B3-C4D5E6-F7G8H9`)."""

# Source: https://cloud.google.com/resource-manager/docs/creating-managing-organization
OrganizationId = Annotated[
    str,
    AfterValidator(_validate_organization_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _ORGANIZATION_ID_RE.pattern,
            "description": "A GCP organization ID.",
            "examples": ["123456789012"],
            "title": "OrganizationId",
        }
    ),
]
"""A GCP organization ID (e.g. `123456789012`)."""


# Source: https://cloud.google.com/iam/docs/service-accounts-create
class ServiceAccountEmail(str):
    """A validated GCP service account email."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^([a-z][a-z0-9-]{4,28}[a-z0-9])@([a-z][a-z0-9-]{4,28}[a-z0-9])\.iam\.gserviceaccount\.com$"
    )
    name: str
    project_id: str

    def __new__(cls, value: str) -> ServiceAccountEmail:
        """Create and validate a new ServiceAccountEmail instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "gcp_service_account_email",
                "Invalid GCP service account email: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.name = m.group(1)
        instance.project_id = m.group(2)
        return instance

    @classmethod
    def _validate(cls, value: str) -> ServiceAccountEmail:
        """Validate a string as a service account email."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for ServiceAccountEmail."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for ServiceAccountEmail."""
        return {
            "type": "string",
            "format": "gcp-service-account-email",
            "pattern": cls._pattern.pattern,
            "description": "A GCP service account email.",
            "examples": ["my-service-account@my-project.iam.gserviceaccount.com"],
            "title": "ServiceAccountEmail",
        }
