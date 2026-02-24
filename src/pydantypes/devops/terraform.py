"""Validated types for Terraform resource identifiers."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema


# Source: https://developer.hashicorp.com/terraform/cli/state/resource-addressing
class TerraformResourceAddress(str):
    """A Terraform resource address like aws_instance.web."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<resource_type>[a-zA-Z_][a-zA-Z0-9_-]*)\.(?P<resource_name>[a-zA-Z_][a-zA-Z0-9_-]*)$"
    )

    resource_type: str
    resource_name: str

    def __new__(cls, value: str) -> TerraformResourceAddress:
        """Create and validate a new TerraformResourceAddress instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "terraform_resource_address",
                "Invalid Terraform resource address: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.resource_type = m.group("resource_type")
        instance.resource_name = m.group("resource_name")
        return instance

    @classmethod
    def _validate(cls, value: str) -> TerraformResourceAddress:
        """Validate a string as a Terraform resource address."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for TerraformResourceAddress."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for TerraformResourceAddress."""
        return {
            "type": "string",
            "format": "terraform-resource-address",
            "pattern": cls._pattern.pattern,
            "description": "A Terraform resource address like aws_instance.web.",
            "examples": [
                "aws_instance.web",
                "google_compute_instance.default",
            ],
            "title": "TerraformResourceAddress",
        }
