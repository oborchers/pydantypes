"""Tests for URN types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.web.urn import Urn

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class UrnModel(BaseModel):
    urn: Urn


# ---------------------------------------------------------------------------
# Urn
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "urn:isbn:0451450523",
        "urn:ietf:rfc:2648",
        "urn:oid:2.16.840",
        "urn:example:a123,z456",
        "urn:example:foo-bar",
        "urn:example:resource/sub/path",
        "urn:example:foo~bar",
        "urn:example:foo&bar",
    ],
)
def test_valid_urn(value: str) -> None:
    model = UrnModel(urn=value)
    assert str(model.urn) == value


def test_urn_properties_simple() -> None:
    urn = Urn("urn:isbn:0451450523")
    assert urn.nid == "isbn"
    assert urn.nss == "0451450523"
    assert urn.r_component is None
    assert urn.q_component is None
    assert urn.f_component is None


def test_urn_properties_with_r_component() -> None:
    urn = Urn("urn:example:resource?+res-info")
    assert urn.nid == "example"
    assert urn.nss == "resource"
    assert urn.r_component == "res-info"
    assert urn.q_component is None
    assert urn.f_component is None


def test_urn_properties_with_q_component() -> None:
    urn = Urn("urn:example:resource?=query-info")
    assert urn.nid == "example"
    assert urn.nss == "resource"
    assert urn.r_component is None
    assert urn.q_component == "query-info"
    assert urn.f_component is None


def test_urn_properties_with_fragment() -> None:
    urn = Urn("urn:example:resource#fragment")
    assert urn.nid == "example"
    assert urn.nss == "resource"
    assert urn.r_component is None
    assert urn.q_component is None
    assert urn.f_component == "fragment"


def test_urn_properties_all_components() -> None:
    urn = Urn("urn:example:resource?+res?=query#frag")
    assert urn.nid == "example"
    assert urn.nss == "resource"
    assert urn.r_component == "res"
    assert urn.q_component == "query"
    assert urn.f_component == "frag"


def test_urn_nid_normalized_to_lowercase() -> None:
    urn = Urn("urn:ISBN:0451450523")
    assert urn.nid == "isbn"


def test_urn_r_component_with_question_mark() -> None:
    urn = Urn("urn:example:res?+info?more")
    assert urn.nid == "example"
    assert urn.nss == "res"
    assert urn.r_component == "info?more"


def test_urn_case_insensitive_prefix() -> None:
    urn = Urn("URN:example:resource")
    assert urn.nid == "example"
    assert urn.nss == "resource"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not-a-urn",
        "urn:",
        "urn:a:",
        "urn::nss",
        "http://example.com",
        "urn:urn-reserved:something",
    ],
)
def test_invalid_urn(value: str) -> None:
    with pytest.raises(ValidationError):
        UrnModel(urn=value)


def test_urn_serialization() -> None:
    model = UrnModel(urn="urn:isbn:0451450523")
    assert model.model_dump() == {"urn": "urn:isbn:0451450523"}
    json_str = model.model_dump_json()
    restored = UrnModel.model_validate_json(json_str)
    assert restored.urn == model.urn
    assert restored.urn.nid == "isbn"


def test_urn_existing_instance() -> None:
    urn = Urn("urn:isbn:0451450523")
    model = UrnModel(urn=urn)
    assert model.urn is urn


def test_urn_json_schema() -> None:
    schema = UrnModel.model_json_schema()
    field_schema = schema["properties"]["urn"]
    assert field_schema["type"] == "string"
    assert field_schema["format"] == "urn"
    assert field_schema["title"] == "Urn"
