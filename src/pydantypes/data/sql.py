"""SQL data types."""

from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema


# Source: https://www.iso.org/standard/76583.html
class TableIdentifier(str):
    """A SQL table identifier like schema.table or catalog.schema.table."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?:(?P<catalog>[a-zA-Z_][a-zA-Z0-9_]*)\.)?(?P<schema>[a-zA-Z_][a-zA-Z0-9_]*)\.(?P<table>[a-zA-Z_][a-zA-Z0-9_]*)$"
    )

    catalog: str | None
    schema_name: str
    table_name: str

    def __new__(cls, value: str) -> TableIdentifier:
        """Create and validate a new TableIdentifier instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "table_identifier",
                "Invalid SQL table identifier: expected"
                " 'schema.table' or 'catalog.schema.table'."
                " Got: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.catalog = m.group("catalog")
        instance.schema_name = m.group("schema")
        instance.table_name = m.group("table")
        return instance

    @classmethod
    def _validate(cls, value: str) -> TableIdentifier:
        """Validate a string as a SQL table identifier."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for TableIdentifier."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for TableIdentifier."""
        return {
            "type": "string",
            "format": "sql-table-identifier",
            "pattern": cls._pattern.pattern,
            "description": "A SQL table identifier (schema.table or catalog.schema.table)",
            "examples": ["public.users", "my_catalog.my_schema.my_table"],
            "title": "TableIdentifier",
        }
