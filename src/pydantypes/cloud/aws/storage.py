"""AWS storage types."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema
from pydantypes.cloud._base import CloudStorageUri

_S3_BUCKET_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
_S3_KEY_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")
_EBS_VOLUME_ID_RE = re.compile(r"^vol-[0-9a-f]{8,17}$")
_EBS_SNAPSHOT_ID_RE = re.compile(r"^snap-[0-9a-f]{8,17}$")


def _validate_s3_bucket_name(v: str) -> str:
    """Validate an S3 bucket name format."""
    if not _S3_BUCKET_NAME_RE.match(v):
        raise PydanticCustomError(
            "s3_bucket_name",
            "Invalid S3 bucket name: {value}",
            {"value": v},
        )
    if ".." in v:
        raise PydanticCustomError(
            "s3_bucket_name",
            "Invalid S3 bucket name: must not contain consecutive dots. Got: {value}",
            {"value": v},
        )
    if "-." in v or ".-" in v:
        raise PydanticCustomError(
            "s3_bucket_name",
            "Invalid S3 bucket name: must not mix adjacent dots and hyphens. Got: {value}",
            {"value": v},
        )
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", v):
        raise PydanticCustomError(
            "s3_bucket_name",
            "Invalid S3 bucket name: must not be formatted as an IP address. Got: {value}",
            {"value": v},
        )
    for prefix in ("xn--", "sthree-", "amzn-s3-demo-"):
        if v.startswith(prefix):
            raise PydanticCustomError(
                "s3_bucket_name",
                "Invalid S3 bucket name: must not start with '{prefix}'. Got: {value}",
                {"prefix": prefix, "value": v},
            )
    for suffix in ("-s3alias", "--ol-s3", ".mrap", "--x-s3", "--table-s3"):
        if v.endswith(suffix):
            raise PydanticCustomError(
                "s3_bucket_name",
                "Invalid S3 bucket name: must not end with '{suffix}'. Got: {value}",
                {"suffix": suffix, "value": v},
            )
    return v


def _validate_ebs_volume_id(v: str) -> str:
    """Validate an EBS volume ID format."""
    if not _EBS_VOLUME_ID_RE.match(v):
        raise PydanticCustomError(
            "ebs_volume_id",
            "Invalid EBS Volume ID: {value}",
            {"value": v},
        )
    return v


def _validate_ebs_snapshot_id(v: str) -> str:
    """Validate an EBS snapshot ID format."""
    if not _EBS_SNAPSHOT_ID_RE.match(v):
        raise PydanticCustomError(
            "ebs_snapshot_id",
            "Invalid EBS Snapshot ID: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
S3BucketName = Annotated[
    str,
    AfterValidator(_validate_s3_bucket_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$",
            "description": "An AWS S3 bucket name",
            "examples": ["my-bucket"],
            "title": "S3BucketName",
            "minLength": 3,
            "maxLength": 63,
        }
    ),
]
"""An AWS S3 bucket name (e.g. `my-bucket`)."""


# Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-bucket-intro.html
class S3Uri(CloudStorageUri):
    """An S3 URI like s3://bucket/key with parsed properties."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^s3://([a-z0-9][a-z0-9.\-]{1,61}[a-z0-9])(/(.*))?$"
    )

    def __new__(cls, value: str) -> S3Uri:
        """Create and validate a new S3Uri instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "s3_uri",
                "Invalid S3 URI: {value}",
                {"value": value},
            )
        bucket = m.group(1)
        _validate_s3_bucket_name(bucket)
        key = m.group(3) or ""
        if len(key.encode("utf-8")) > 1024:
            raise PydanticCustomError(
                "s3_uri",
                "Invalid S3 URI: key must be <= 1024 bytes. Got: {value}",
                {"value": value},
            )
        if _S3_KEY_CONTROL_CHAR_RE.search(key):
            raise PydanticCustomError(
                "s3_uri",
                "Invalid S3 URI: key must not contain control characters. Got: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.bucket = bucket
        instance.key = key
        return instance

    @classmethod
    def _validate(cls, value: str) -> S3Uri:
        """Validate a string as an S3 URI."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for S3Uri."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for S3Uri."""
        return {
            "type": "string",
            "format": "s3-uri",
            "pattern": cls._pattern.pattern,
            "description": "An S3 URI in the format s3://bucket/key",
            "examples": ["s3://my-bucket/path/to/file.csv"],
            "title": "S3Uri",
        }


# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
EbsVolumeId = Annotated[
    str,
    AfterValidator(_validate_ebs_volume_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^vol-[0-9a-f]{8,17}$",
            "description": "An AWS EBS Volume ID",
            "examples": ["vol-1234567890abcdef0"],
            "title": "EbsVolumeId",
        }
    ),
]
"""An AWS EBS Volume ID (e.g. `vol-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
EbsSnapshotId = Annotated[
    str,
    AfterValidator(_validate_ebs_snapshot_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^snap-[0-9a-f]{8,17}$",
            "description": "An AWS EBS Snapshot ID",
            "examples": ["snap-1234567890abcdef0"],
            "title": "EbsSnapshotId",
        }
    ),
]
"""An AWS EBS Snapshot ID (e.g. `snap-1234567890abcdef0`)."""
