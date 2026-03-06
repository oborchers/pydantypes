"""Tests for hash types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.web.hash import Md5Hex, Sha1Hex, Sha256Hex


class Sha256Model(BaseModel):
    digest: Sha256Hex


class Sha1Model(BaseModel):
    digest: Sha1Hex


class Md5Model(BaseModel):
    digest: Md5Hex


def test_valid_sha256() -> None:
    value = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    model = Sha256Model(digest=value)
    assert model.digest == value


def test_sha256_normalizes_to_lowercase() -> None:
    upper = "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
    model = Sha256Model(digest=upper)
    assert model.digest == upper.lower()


@pytest.mark.parametrize("value", ["abc", "g" * 64, "a" * 63, "a" * 65, ""])
def test_invalid_sha256(value: str) -> None:
    with pytest.raises(ValidationError):
        Sha256Model(digest=value)


def test_sha256_serialization() -> None:
    value = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    model = Sha256Model(digest=value)
    json_str = model.model_dump_json()
    restored = Sha256Model.model_validate_json(json_str)
    assert restored.digest == model.digest


def test_sha256_json_schema() -> None:
    schema = Sha256Model.model_json_schema()
    field_schema = schema["properties"]["digest"]
    assert field_schema["type"] == "string"
    assert field_schema["format"] == "sha256-hex"


def test_valid_sha1() -> None:
    value = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    model = Sha1Model(digest=value)
    assert model.digest == value


def test_sha1_normalizes_to_lowercase() -> None:
    upper = "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709"
    model = Sha1Model(digest=upper)
    assert model.digest == upper.lower()


@pytest.mark.parametrize("value", ["abc", "g" * 40, "a" * 39, "a" * 41, ""])
def test_invalid_sha1(value: str) -> None:
    with pytest.raises(ValidationError):
        Sha1Model(digest=value)


def test_valid_md5() -> None:
    value = "d41d8cd98f00b204e9800998ecf8427e"
    model = Md5Model(digest=value)
    assert model.digest == value


def test_md5_normalizes_to_lowercase() -> None:
    upper = "D41D8CD98F00B204E9800998ECF8427E"
    model = Md5Model(digest=upper)
    assert model.digest == upper.lower()


@pytest.mark.parametrize("value", ["abc", "g" * 32, "a" * 31, "a" * 33, ""])
def test_invalid_md5(value: str) -> None:
    with pytest.raises(ValidationError):
        Md5Model(digest=value)


def test_md5_scientific_notation_lookalike() -> None:
    """Regression: pydantic#9621 — MD5 with 'e' parsed as inf."""
    value = "20862292665203397e00089319024245"
    # Pad to 32 chars — the original issue value is 31 chars
    value = value.ljust(32, "0")
    model = Md5Model(digest=value)
    assert model.digest == value


def test_md5_rejects_inf() -> None:
    """The corrupted output from pydantic#9621 must be rejected."""
    with pytest.raises(ValidationError):
        Md5Model(digest="inf")


def test_md5_serialization() -> None:
    value = "d41d8cd98f00b204e9800998ecf8427e"
    model = Md5Model(digest=value)
    json_str = model.model_dump_json()
    restored = Md5Model.model_validate_json(json_str)
    assert restored.digest == model.digest


def test_sha1_serialization() -> None:
    value = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    model = Sha1Model(digest=value)
    json_str = model.model_dump_json()
    restored = Sha1Model.model_validate_json(json_str)
    assert restored.digest == model.digest
