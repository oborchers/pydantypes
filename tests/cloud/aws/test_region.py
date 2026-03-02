"""Tests for AWS region types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.cloud.aws.region import Region


class RegionModel(BaseModel):
    region: Region


@pytest.mark.parametrize(
    "value", ["us-east-1", "eu-west-1", "ap-southeast-1", "ap-southeast-5", "mx-central-1"]
)
def test_valid_region(value: str) -> None:
    model = RegionModel(region=value)
    assert model.region == value


@pytest.mark.parametrize("value", ["invalid-region", "US-EAST-1", ""])
def test_invalid_region(value: str) -> None:
    with pytest.raises(ValidationError):
        RegionModel(region=value)


def test_region_str_returns_value() -> None:
    assert str(Region.US_EAST_1) == "us-east-1"
    assert str(Region.EU_WEST_1) == "eu-west-1"


def test_region_serialization() -> None:
    model = RegionModel(region="us-east-1")
    assert model.model_dump() == {"region": "us-east-1"}
    json_str = model.model_dump_json()
    restored = RegionModel.model_validate_json(json_str)
    assert restored.region == model.region
