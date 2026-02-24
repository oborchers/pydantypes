"""Tests for Terraform resource identifier types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from pydantic_core import PydanticCustomError

from pydantypes.devops.terraform import TerraformResourceAddress


class TfModel(BaseModel):
    addr: TerraformResourceAddress


def test_valid_terraform_resource_address_aws_instance() -> None:
    addr = TerraformResourceAddress("aws_instance.web")
    assert addr.resource_type == "aws_instance"
    assert addr.resource_name == "web"


def test_valid_terraform_resource_address_google_compute() -> None:
    addr = TerraformResourceAddress("google_compute_instance.default")
    assert addr.resource_type == "google_compute_instance"
    assert addr.resource_name == "default"


def test_valid_terraform_resource_address_null_resource() -> None:
    addr = TerraformResourceAddress("null_resource.this")
    assert addr.resource_type == "null_resource"
    assert addr.resource_name == "this"


def test_terraform_resource_address_pydantic_model() -> None:
    m = TfModel(addr="aws_instance.web")
    assert isinstance(m.addr, TerraformResourceAddress)


@pytest.mark.parametrize("value", ["", "no-dot", ".starts-with-dot", "1invalid.name", "type."])
def test_invalid_terraform_resource_address(value: str) -> None:
    with pytest.raises(PydanticCustomError):
        TerraformResourceAddress(value)
