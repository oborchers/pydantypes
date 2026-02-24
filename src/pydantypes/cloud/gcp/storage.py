"""GCP storage types."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema
from pydantypes.cloud._base import CloudStorageUri

_GCS_BUCKET_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$")


def _validate_gcs_bucket_name(v: str) -> str:
    """Validate a GCS bucket name format."""
    if not _GCS_BUCKET_NAME_RE.match(v):
        raise PydanticCustomError(
            "gcs_bucket_name",
            "Invalid GCS bucket name: {value}",
            {"value": v},
        )
    if ".." in v:
        raise PydanticCustomError(
            "gcs_bucket_name",
            "Invalid GCS bucket name: must not contain consecutive dots. Got: {value}",
            {"value": v},
        )
    if "-." in v or ".-" in v:
        raise PydanticCustomError(
            "gcs_bucket_name",
            "Invalid GCS bucket name: must not mix adjacent dots and hyphens. Got: {value}",
            {"value": v},
        )
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", v):
        raise PydanticCustomError(
            "gcs_bucket_name",
            "Invalid GCS bucket name: must not be formatted as an IP address. Got: {value}",
            {"value": v},
        )
    if v.startswith("goog") or "google" in v:
        raise PydanticCustomError(
            "gcs_bucket_name",
            "Invalid GCS bucket name: must not start with 'goog' or contain 'google'. Got: {value}",
            {"value": v},
        )
    return v


# Source: https://cloud.google.com/storage/docs/naming-buckets
GcsBucketName = Annotated[
    str,
    AfterValidator(_validate_gcs_bucket_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _GCS_BUCKET_NAME_RE.pattern,
            "description": "A GCP Cloud Storage bucket name.",
            "examples": ["my-bucket"],
            "title": "GcsBucketName",
            "minLength": 3,
            "maxLength": 63,
        }
    ),
]
"""A GCP Cloud Storage bucket name (e.g. `my-bucket`)."""


# Source: https://cloud.google.com/storage/docs/request-endpoints
class GcsUri(CloudStorageUri):
    """A validated Google Cloud Storage URI (gs://bucket/key)."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^gs://([a-z0-9][a-z0-9._-]{1,61}[a-z0-9])(?:/(.*))?$"
    )

    def __new__(cls, value: str) -> GcsUri:
        """Create and validate a new GcsUri instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError("gcs_uri", "Invalid GCS URI: {value}", {"value": value})
        bucket = m.group(1)
        _validate_gcs_bucket_name(bucket)
        instance = str.__new__(cls, value)
        instance.bucket = bucket
        instance.key = m.group(2) or ""
        return instance

    @classmethod
    def _validate(cls, value: str) -> GcsUri:
        """Validate a string as a GCS URI."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for GcsUri."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for GcsUri."""
        return {
            "type": "string",
            "format": "gcs-uri",
            "pattern": cls._pattern.pattern,
            "description": "A Google Cloud Storage URI (gs://bucket/key).",
            "examples": ["gs://my-bucket/path/to/file.csv"],
            "title": "GcsUri",
        }
