"""Tests for HTTP authentication types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.web.auth import BearerToken


class BearerTokenModel(BaseModel):
    auth: BearerToken


@pytest.mark.parametrize(
    ("value", "expected_token"),
    [
        ("Bearer abc123", "abc123"),
        (
            "Bearer eyJhbGciOiJIUzI1NiIs.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig",
            "eyJhbGciOiJIUzI1NiIs.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig",
        ),
        ("Bearer token+with/special~chars._ok", "token+with/special~chars._ok"),
        ("Bearer abc123==", "abc123=="),
        ("Bearer a", "a"),
        (
            "Bearer ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        ),
    ],
)
def test_valid_bearer_token(value: str, expected_token: str) -> None:
    model = BearerTokenModel(auth=value)
    assert str(model.auth) == value
    assert model.auth.token == expected_token


@pytest.mark.parametrize(
    "value",
    [
        "",
        "bearer abc123",
        "BEARER abc123",
        "Bearer ",
        "Bearer",
        "Bearer  abc123",
        "Basic dXNlcjpwYXNz",
        "abc123",
        "Bearer @invalid",
        "Bearer has space",
    ],
)
def test_invalid_bearer_token(value: str) -> None:
    with pytest.raises(ValidationError):
        BearerTokenModel(auth=value)


def test_bearer_token_serialization() -> None:
    model = BearerTokenModel(auth="Bearer mytoken123")
    assert model.model_dump() == {"auth": "Bearer mytoken123"}
    json_str = model.model_dump_json()
    restored = BearerTokenModel.model_validate_json(json_str)
    assert restored.auth == model.auth
    assert restored.auth.token == "mytoken123"


def test_bearer_token_existing_instance() -> None:
    bt = BearerToken("Bearer mytoken123")
    model = BearerTokenModel(auth=bt)
    assert model.auth is bt


def test_bearer_token_json_schema() -> None:
    schema = BearerTokenModel.model_json_schema()
    field_schema = schema["properties"]["auth"]
    assert field_schema["type"] == "string"
    assert field_schema["format"] == "bearer-token"
