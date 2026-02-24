"""GCP database types."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

_BIGQUERY_DATASET_ID_RE = re.compile(r"^[a-zA-Z0-9_]{1,1024}$")
_CLOUD_SQL_INSTANCE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
_SPANNER_INSTANCE_ID_RE = re.compile(r"^[a-z][-a-z0-9]{0,62}[a-z0-9]$")
_SPANNER_DATABASE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*[a-z0-9]$")


def _validate_bigquery_dataset_id(v: str) -> str:
    """Validate a BigQuery dataset ID format."""
    if not _BIGQUERY_DATASET_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_bigquery_dataset_id",
            "Invalid GCP BigQuery dataset ID: {value}",
            {"value": v},
        )
    return v


def _validate_cloud_sql_instance_id(v: str) -> str:
    """Validate a Cloud SQL instance ID format."""
    if len(v) > 84:
        raise PydanticCustomError(
            "gcp_cloud_sql_instance_id",
            "Invalid GCP Cloud SQL instance ID: exceeds 84 characters. Got: {value}",
            {"value": v},
        )
    if not _CLOUD_SQL_INSTANCE_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_cloud_sql_instance_id",
            "Invalid GCP Cloud SQL instance ID: {value}",
            {"value": v},
        )
    return v


def _validate_spanner_instance_id(v: str) -> str:
    """Validate a Spanner instance ID format."""
    if len(v) < 2 or len(v) > 64:
        raise PydanticCustomError(
            "gcp_spanner_instance_id",
            "Invalid GCP Spanner instance ID: must be 2-64 characters. Got: {value}",
            {"value": v},
        )
    if not _SPANNER_INSTANCE_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_spanner_instance_id",
            "Invalid GCP Spanner instance ID: {value}",
            {"value": v},
        )
    return v


def _validate_spanner_database_id(v: str) -> str:
    """Validate a Spanner database ID format."""
    if len(v) < 2 or len(v) > 30:
        raise PydanticCustomError(
            "gcp_spanner_database_id",
            "Invalid GCP Spanner database ID: must be 2-30 characters. Got: {value}",
            {"value": v},
        )
    if not _SPANNER_DATABASE_ID_RE.match(v):
        raise PydanticCustomError(
            "gcp_spanner_database_id",
            "Invalid GCP Spanner database ID: {value}",
            {"value": v},
        )
    return v


# Source: https://cloud.google.com/bigquery/docs/datasets
BigQueryDatasetId = Annotated[
    str,
    AfterValidator(_validate_bigquery_dataset_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _BIGQUERY_DATASET_ID_RE.pattern,
            "description": "A GCP BigQuery dataset ID.",
            "examples": ["my_dataset"],
            "title": "BigQueryDatasetId",
        }
    ),
]
"""A GCP BigQuery dataset ID (e.g. `my_dataset`)."""

# Source: https://cloud.google.com/sql/docs/mysql/instance-settings
CloudSqlInstanceId = Annotated[
    str,
    AfterValidator(_validate_cloud_sql_instance_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _CLOUD_SQL_INSTANCE_ID_RE.pattern,
            "description": "A GCP Cloud SQL instance ID (max 84 chars).",
            "examples": ["my-sql-instance"],
            "title": "CloudSqlInstanceId",
        }
    ),
]
"""A GCP Cloud SQL instance ID (max 84 chars) (e.g. `my-sql-instance`)."""


# Source: https://cloud.google.com/bigquery/docs/tables
class BigQueryTableId(str):
    """A validated BigQuery fully-qualified table ID."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^([a-z][a-z0-9-]{4,28}[a-z0-9]|\d+)[.:]([a-zA-Z0-9_]{1,1024})\.([a-zA-Z0-9_]{1,1024})$"
    )

    project_id: str
    dataset_id: str
    table_id: str

    def __new__(cls, value: str) -> BigQueryTableId:
        """Create and validate a new BigQueryTableId instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "gcp_bigquery_table_id",
                "Invalid BigQuery table ID: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.project_id = m.group(1)
        instance.dataset_id = m.group(2)
        instance.table_id = m.group(3)
        return instance

    @classmethod
    def _validate(cls, value: str) -> BigQueryTableId:
        """Validate a string as a BigQuery table ID."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for BigQueryTableId."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for BigQueryTableId."""
        return {
            "type": "string",
            "format": "gcp-bigquery-table-id",
            "pattern": cls._pattern.pattern,
            "description": (
                "A fully-qualified BigQuery table ID"
                " (project.dataset.table or project:dataset.table)."
            ),
            "examples": ["my-project.my_dataset.my_table"],
            "title": "BigQueryTableId",
        }


# Source: https://cloud.google.com/spanner/docs/reference/rest/v1/projects.instances
SpannerInstanceId = Annotated[
    str,
    AfterValidator(_validate_spanner_instance_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _SPANNER_INSTANCE_ID_RE.pattern,
            "description": "A GCP Spanner instance ID (2-64 chars).",
            "examples": ["my-spanner-instance"],
            "title": "SpannerInstanceId",
            "minLength": 2,
            "maxLength": 64,
        }
    ),
]
"""A GCP Spanner instance ID (2-64 chars) (e.g. `my-spanner-instance`)."""

# Source: https://cloud.google.com/spanner/docs/reference/rest/v1/projects.instances.databases
SpannerDatabaseId = Annotated[
    str,
    AfterValidator(_validate_spanner_database_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _SPANNER_DATABASE_ID_RE.pattern,
            "description": "A GCP Spanner database ID (2-30 chars).",
            "examples": ["my-spanner-db"],
            "title": "SpannerDatabaseId",
            "minLength": 2,
            "maxLength": 30,
        }
    ),
]
"""A GCP Spanner database ID (2-30 chars) (e.g. `my-spanner-db`)."""
