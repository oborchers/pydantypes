"""Azure storage types."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema
from pydantypes.cloud._base import CloudStorageUri

_STORAGE_ACCOUNT_NAME_RE = re.compile(r"^[a-z0-9]{3,24}$")


def _validate_storage_account_name(v: str) -> str:
    """Validate an Azure Storage account name format."""
    if not _STORAGE_ACCOUNT_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_storage_account_name",
            "Invalid Azure Storage account name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftstorage
StorageAccountName = Annotated[
    str,
    AfterValidator(_validate_storage_account_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z0-9]{3,24}$",
            "description": "Azure Storage account name.",
            "examples": ["mystorageaccount"],
            "title": "StorageAccountName",
            "minLength": 3,
            "maxLength": 24,
        }
    ),
]
"""Azure Storage account name (e.g. `mystorageaccount`)."""


# Source: https://learn.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata
class BlobStorageUri(CloudStorageUri):
    """Azure Blob Storage URI (https://{account}.blob.core.windows.net/{container}/{blob})."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^https://([a-z0-9]{3,24})\.blob\.core\.windows\.net"
        r"/([a-z0-9][a-z0-9-]{1,61}[a-z0-9])(?:/(.+))?$"
    )

    account_name: str
    container: str
    blob_path: str

    def __new__(cls, value: str) -> BlobStorageUri:
        """Create and validate a new BlobStorageUri instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "azure_blob_storage_uri",
                "Invalid Azure Blob Storage URI: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.account_name = m.group(1)
        instance.container = m.group(2)
        instance.bucket = m.group(2)
        instance.blob_path = m.group(3) or ""
        instance.key = m.group(3) or ""
        return instance

    @classmethod
    def _validate(cls, value: str) -> BlobStorageUri:
        """Validate a string as a Blob Storage URI."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for BlobStorageUri."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for BlobStorageUri."""
        return {
            "type": "string",
            "format": "azure-blob-storage-uri",
            "pattern": cls._pattern.pattern,
            "description": "Azure Blob Storage URI.",
            "examples": ["https://myaccount.blob.core.windows.net/mycontainer/path/to/blob"],
            "title": "BlobStorageUri",
        }
