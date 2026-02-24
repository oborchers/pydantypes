"""Azure Key Vault types."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import (
    AfterValidator,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    WithJsonSchema,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

_KEY_VAULT_NAME_RE = re.compile(r"^[a-zA-Z](?!.*--)[a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$")
_KEY_VAULT_SECRET_NAME_RE = re.compile(r"^[a-zA-Z0-9-]{1,127}$")


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftkeyvault
class KeyVaultUri(str):
    """Azure Key Vault URI (https://{vault_name}.vault.azure.net/)."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^https://([a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9])\.vault\.azure\.net/?$"
    )

    vault_name: str

    def __new__(cls, value: str) -> KeyVaultUri:
        """Create and validate a new KeyVaultUri instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "azure_key_vault_uri",
                "Invalid Azure Key Vault URI: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.vault_name = m.group(1)
        return instance

    @classmethod
    def _validate(cls, value: str) -> KeyVaultUri:
        """Validate a string as a Key Vault URI."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for KeyVaultUri."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for KeyVaultUri."""
        return {
            "type": "string",
            "format": "azure-key-vault-uri",
            "pattern": cls._pattern.pattern,
            "description": "Azure Key Vault URI.",
            "examples": ["https://my-vault.vault.azure.net/"],
            "title": "KeyVaultUri",
        }


def _validate_key_vault_name(v: str) -> str:
    """Validate an Azure Key Vault name format."""
    if not _KEY_VAULT_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_key_vault_name",
            "Invalid Azure Key Vault name: {value}",
            {"value": v},
        )
    return v


def _validate_key_vault_secret_name(v: str) -> str:
    """Validate an Azure Key Vault secret name format."""
    if not _KEY_VAULT_SECRET_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_key_vault_secret_name",
            "Invalid Azure Key Vault secret name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftkeyvault
KeyVaultName = Annotated[
    str,
    AfterValidator(_validate_key_vault_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z](?!.*--)[a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$",
            "description": "Azure Key Vault name.",
            "examples": ["my-key-vault"],
            "title": "KeyVaultName",
        }
    ),
]
"""Azure Key Vault name (e.g. `my-key-vault`)."""

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftkeyvault
KeyVaultSecretName = Annotated[
    str,
    AfterValidator(_validate_key_vault_secret_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9-]{1,127}$",
            "description": "Azure Key Vault secret name.",
            "examples": ["my-secret"],
            "title": "KeyVaultSecretName",
            "maxLength": 127,
        }
    ),
]
"""Azure Key Vault secret name (e.g. `my-secret`)."""
