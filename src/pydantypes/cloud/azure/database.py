"""Azure database types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_COSMOS_DB_ACCOUNT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,42}[a-z0-9]$")
_SQL_SERVER_NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_REDIS_CACHE_NAME_RE = re.compile(r"^[a-zA-Z0-9](?!.*--)[a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$")
_DATA_FACTORY_NAME_RE = re.compile(r"^[a-zA-Z0-9](?!.*--)[a-zA-Z0-9-]{1,61}[a-zA-Z0-9]$")
_DATABRICKS_WORKSPACE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$")


def _validate_cosmos_db_account_name(v: str) -> str:
    """Validate an Azure Cosmos DB account name format."""
    if not _COSMOS_DB_ACCOUNT_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_cosmos_db_account_name",
            "Invalid Azure Cosmos DB account name: {value}",
            {"value": v},
        )
    return v


def _validate_sql_server_name(v: str) -> str:
    """Validate an Azure SQL Server name format."""
    if not _SQL_SERVER_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_sql_server_name",
            "Invalid Azure SQL Server name: {value}",
            {"value": v},
        )
    return v


def _validate_redis_cache_name(v: str) -> str:
    """Validate an Azure Redis Cache name format."""
    if not _REDIS_CACHE_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_redis_cache_name",
            "Invalid Azure Redis Cache name: {value}",
            {"value": v},
        )
    return v


def _validate_data_factory_name(v: str) -> str:
    """Validate an Azure Data Factory name format."""
    if not _DATA_FACTORY_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_data_factory_name",
            "Invalid Azure Data Factory name: {value}",
            {"value": v},
        )
    return v


def _validate_databricks_workspace_name(v: str) -> str:
    """Validate an Azure Databricks workspace name format."""
    if not _DATABRICKS_WORKSPACE_NAME_RE.match(v):
        raise PydanticCustomError(
            "azure_databricks_workspace_name",
            "Invalid Azure Databricks workspace name: {value}",
            {"value": v},
        )
    return v


# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftdocumentdb
CosmosDbAccountName = Annotated[
    str,
    AfterValidator(_validate_cosmos_db_account_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z0-9][a-z0-9-]{1,42}[a-z0-9]$",
            "description": "Azure Cosmos DB account name.",
            "examples": ["my-cosmos-account"],
            "title": "CosmosDbAccountName",
        }
    ),
]
"""Azure Cosmos DB account name (e.g. `my-cosmos-account`)."""

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftsql
SqlServerName = Annotated[
    str,
    AfterValidator(_validate_sql_server_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$",
            "description": "Azure SQL Server name.",
            "examples": ["my-sql-server"],
            "title": "SqlServerName",
        }
    ),
]
"""Azure SQL Server name (e.g. `my-sql-server`)."""

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftcache
RedisCacheName = Annotated[
    str,
    AfterValidator(_validate_redis_cache_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9](?!.*--)[a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$",
            "description": "Azure Redis Cache name.",
            "examples": ["my-redis-cache"],
            "title": "RedisCacheName",
        }
    ),
]
"""Azure Redis Cache name (e.g. `my-redis-cache`)."""

# Source: https://learn.microsoft.com/en-us/azure/data-factory/naming-rules
DataFactoryName = Annotated[
    str,
    AfterValidator(_validate_data_factory_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9](?!.*--)[a-zA-Z0-9-]{1,61}[a-zA-Z0-9]$",
            "description": "Azure Data Factory name.",
            "examples": ["my-data-factory"],
            "title": "DataFactoryName",
        }
    ),
]
"""Azure Data Factory name (e.g. `my-data-factory`)."""

# Source: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftdatabricks
DatabricksWorkspaceName = Annotated[
    str,
    AfterValidator(_validate_databricks_workspace_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$",
            "description": "Azure Databricks workspace name.",
            "examples": ["my-databricks-ws"],
            "title": "DatabricksWorkspaceName",
        }
    ),
]
"""Azure Databricks workspace name (e.g. `my-databricks-ws`)."""
