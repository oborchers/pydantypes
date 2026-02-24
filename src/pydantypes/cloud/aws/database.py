"""AWS database types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_DYNAMODB_TABLE_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,255}$")
_RDS_INSTANCE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,62}$")


def _validate_dynamodb_table_name(v: str) -> str:
    """Validate a DynamoDB table name format."""
    if not _DYNAMODB_TABLE_NAME_RE.match(v):
        raise PydanticCustomError(
            "dynamodb_table_name",
            "Invalid DynamoDB table name: {value}",
            {"value": v},
        )
    return v


def _validate_rds_instance_id(v: str) -> str:
    """Validate an RDS instance identifier format."""
    if not _RDS_INSTANCE_ID_RE.match(v):
        raise PydanticCustomError(
            "rds_instance_id",
            "Invalid RDS instance ID: {value}",
            {"value": v},
        )
    if "--" in v:
        raise PydanticCustomError(
            "rds_instance_id",
            "Invalid RDS instance ID: must not contain consecutive hyphens. Got: {value}",
            {"value": v},
        )
    if v.endswith("-"):
        raise PydanticCustomError(
            "rds_instance_id",
            "Invalid RDS instance ID: must not end with a hyphen. Got: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html
DynamoDbTableName = Annotated[
    str,
    AfterValidator(_validate_dynamodb_table_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9._-]{3,255}$",
            "description": "An AWS DynamoDB table name",
            "examples": ["my-table"],
            "title": "DynamoDbTableName",
            "minLength": 3,
            "maxLength": 255,
        }
    ),
]
"""An AWS DynamoDB table name (e.g. `my-table`)."""

# Source: https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_CreateDBInstance.html
RdsInstanceId = Annotated[
    str,
    AfterValidator(_validate_rds_instance_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-z][a-z0-9-]{0,62}$",
            "description": "An AWS RDS instance identifier (lowercase only)",
            "examples": ["my-db-instance"],
            "title": "RdsInstanceId",
            "maxLength": 63,
        }
    ),
]
"""An AWS RDS instance identifier (lowercase only) (e.g. `my-db-instance`)."""
