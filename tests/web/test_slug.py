"""Tests for slug types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.web.slug import Slug

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class SlugModel(BaseModel):
    slug: Slug


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "hello-world",
        "my-blog-post",
        "pydantic-types-101",
        "a",
        "a1b2c3",
        "123",
        "x-1-y-2",
    ],
)
def test_valid_slug(value: str) -> None:
    model = SlugModel(slug=value)
    assert model.slug == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Hello-World",
        "UPPER",
        "-leading-hyphen",
        "trailing-hyphen-",
        "double--hyphen",
        "has space",
        "has_underscore",
        "has.dot",
        "special!char",
        "a" * 129,
    ],
)
def test_invalid_slug(value: str) -> None:
    with pytest.raises(ValidationError):
        SlugModel(slug=value)


def test_slug_max_length_boundary() -> None:
    valid = "a" * 128
    model = SlugModel(slug=valid)
    assert model.slug == valid

    with pytest.raises(ValidationError):
        SlugModel(slug="a" * 129)


def test_slug_serialization() -> None:
    model = SlugModel(slug="my-blog-post")
    assert model.model_dump() == {"slug": "my-blog-post"}
    json_str = model.model_dump_json()
    restored = SlugModel.model_validate_json(json_str)
    assert restored.slug == model.slug


def test_slug_json_schema() -> None:
    schema = SlugModel.model_json_schema()
    field_schema = schema["properties"]["slug"]
    assert field_schema["type"] == "string"
    assert field_schema["title"] == "Slug"
    assert field_schema["maxLength"] == 128
    assert "pattern" in field_schema
