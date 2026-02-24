"""Tests for Helm chart reference types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.devops.helm import HelmChartName


class HelmModel(BaseModel):
    name: HelmChartName


@pytest.mark.parametrize("value", ["nginx", "cert-manager", "0-start-with-num"])
def test_valid_helm_chart_name(value: str) -> None:
    m = HelmModel(name=value)
    assert m.name == value


@pytest.mark.parametrize(
    "value",
    ["", "-starts", "UPPER", "has spaces", "has.dots"],
)
def test_invalid_helm_chart_name(value: str) -> None:
    with pytest.raises(ValidationError):
        HelmModel(name=value)
