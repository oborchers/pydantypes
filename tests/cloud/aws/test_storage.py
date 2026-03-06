"""Tests for AWS storage types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.cloud.aws.storage import EbsSnapshotId, EbsVolumeId, S3BucketName, S3Uri


class S3UriModel(BaseModel):
    uri: S3Uri


class S3BucketModel(BaseModel):
    bucket: S3BucketName


class EbsVolModel(BaseModel):
    vol_id: EbsVolumeId


class EbsSnapModel(BaseModel):
    snap_id: EbsSnapshotId


@pytest.mark.parametrize(
    ("value", "expected_bucket", "expected_key"),
    [
        ("s3://my-bucket/my-key", "my-bucket", "my-key"),
        ("s3://my-bucket/path/to/file.csv", "my-bucket", "path/to/file.csv"),
        ("s3://my-bucket", "my-bucket", ""),
        ("s3://my-bucket/", "my-bucket", ""),
        ("s3://my.dotted.bucket/key", "my.dotted.bucket", "key"),
        ("s3://a1b2c3d4/key", "a1b2c3d4", "key"),
    ],
)
def test_valid_s3_uri(value: str, expected_bucket: str, expected_key: str) -> None:
    model = S3UriModel(uri=value)
    assert str(model.uri) == value
    assert model.uri.bucket == expected_bucket
    assert model.uri.key == expected_key


@pytest.mark.parametrize(
    "value",
    [
        "s3://",
        "s3:///no-bucket",
        "http://bucket/key",
        "s3://UPPER/key",
        "",
        "s3://-invalid/key",
        "not-an-s3-uri",
        "s3://my..bucket/key",
        "s3://xn--mybucket/key",
        "s3://192.168.1.1/key",
    ],
)
def test_invalid_s3_uri(value: str) -> None:
    with pytest.raises(ValidationError):
        S3UriModel(uri=value)


def test_s3_uri_serialization() -> None:
    model = S3UriModel(uri="s3://my-bucket/my-key")
    assert model.model_dump() == {"uri": "s3://my-bucket/my-key"}
    json_str = model.model_dump_json()
    restored = S3UriModel.model_validate_json(json_str)
    assert restored.uri == model.uri
    assert restored.uri.bucket == model.uri.bucket


def test_s3_uri_existing_instance() -> None:
    uri = S3Uri("s3://my-bucket/my-key")
    model = S3UriModel(uri=uri)
    assert model.uri is uri


def test_s3_uri_json_schema() -> None:
    schema = S3UriModel.model_json_schema()
    field_schema = schema["properties"]["uri"]
    assert field_schema["type"] == "string"
    assert field_schema["format"] == "s3-uri"
    assert "pattern" in field_schema


@pytest.mark.parametrize("value", ["my-bucket", "a1b2c3d4", "my.dotted.bucket"])
def test_valid_s3_bucket_name(value: str) -> None:
    model = S3BucketModel(bucket=value)
    assert model.bucket == value


@pytest.mark.parametrize(
    "value",
    [
        "ab",
        "UPPER",
        "my..bucket",
        "my-.bucket",
        "my.-bucket",
        "192.168.1.1",
        "xn--mybucket",
        "sthree-mybucket",
        "amzn-s3-demo-mybucket",
        "mybucket-s3alias",
        "mybucket--ol-s3",
        "mybucket.mrap",
        "mybucket--x-s3",
        "mybucket--table-s3",
    ],
)
def test_invalid_s3_bucket_name(value: str) -> None:
    with pytest.raises(ValidationError):
        S3BucketModel(bucket=value)


def test_s3_bucket_name_serialization() -> None:
    model = S3BucketModel(bucket="my-bucket")
    assert model.model_dump() == {"bucket": "my-bucket"}


@pytest.mark.parametrize("value", ["vol-1234567890abcdef0", "vol-12345678"])
def test_valid_ebs_volume_id(value: str) -> None:
    model = EbsVolModel(vol_id=value)
    assert model.vol_id == value


@pytest.mark.parametrize("value", ["vol-", "vol-UPPER", ""])
def test_invalid_ebs_volume_id(value: str) -> None:
    with pytest.raises(ValidationError):
        EbsVolModel(vol_id=value)


def test_ebs_volume_id_serialization() -> None:
    model = EbsVolModel(vol_id="vol-1234567890abcdef0")
    assert model.model_dump() == {"vol_id": "vol-1234567890abcdef0"}


@pytest.mark.parametrize("value", ["snap-1234567890abcdef0", "snap-12345678"])
def test_valid_ebs_snapshot_id(value: str) -> None:
    model = EbsSnapModel(snap_id=value)
    assert model.snap_id == value


@pytest.mark.parametrize("value", ["snap-", "snap-UPPER", ""])
def test_invalid_ebs_snapshot_id(value: str) -> None:
    with pytest.raises(ValidationError):
        EbsSnapModel(snap_id=value)


def test_s3_uri_key_at_max_length() -> None:
    key = "a" * 1024
    model = S3UriModel(uri=f"s3://my-bucket/{key}")
    assert model.uri.key == key


def test_s3_uri_key_too_long() -> None:
    key = "a" * 1025
    with pytest.raises(ValidationError):
        S3UriModel(uri=f"s3://my-bucket/{key}")


@pytest.mark.parametrize(
    "value",
    [
        "s3://my-bucket/path\twith\ttab",
        "s3://my-bucket/path\x00null",
        "s3://my-bucket/path\x1fcontrol",
        "s3://my-bucket/path\x7fdelete",
    ],
)
def test_s3_uri_rejects_control_chars(value: str) -> None:
    with pytest.raises(ValidationError):
        S3UriModel(uri=value)


def test_s3_uri_is_folder() -> None:
    uri = S3Uri("s3://my-bucket/path/to/folder/")
    assert uri.is_folder is True
    assert uri.is_file is False


def test_s3_uri_is_file() -> None:
    uri = S3Uri("s3://my-bucket/path/to/file.csv")
    assert uri.is_file is True
    assert uri.is_folder is False


def test_s3_uri_name_and_suffix() -> None:
    uri = S3Uri("s3://my-bucket/path/to/file.csv")
    assert uri.name == "file.csv"
    assert uri.suffix == ".csv"


def test_s3_uri_no_key_is_folder() -> None:
    uri = S3Uri("s3://my-bucket")
    assert uri.is_folder is True
    assert uri.name == ""
    assert uri.suffix == ""


def test_ebs_snapshot_id_serialization() -> None:
    model = EbsSnapModel(snap_id="snap-1234567890abcdef0")
    assert model.model_dump() == {"snap_id": "snap-1234567890abcdef0"}
