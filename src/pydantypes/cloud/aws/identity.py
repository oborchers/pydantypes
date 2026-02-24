"""AWS identity types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_ACCOUNT_ID_RE = re.compile(r"^\d{12}$")
_COGNITO_USER_POOL_ID_RE = re.compile(r"^[\w-]+_[0-9a-zA-Z]+$")


def _validate_account_id(v: str) -> str:
    """Validate an AWS account ID format."""
    if not _ACCOUNT_ID_RE.match(v):
        raise PydanticCustomError(
            "aws_account_id",
            "Invalid AWS Account ID: must be a 12-digit string. Got: {value}",
            {"value": v},
        )
    return v


def _validate_cognito_user_pool_id(v: str) -> str:
    """Validate a Cognito User Pool ID format."""
    if len(v) > 55:
        raise PydanticCustomError(
            "cognito_user_pool_id",
            "Invalid Cognito User Pool ID: exceeds 55 characters. Got: {value}",
            {"value": v},
        )
    if not _COGNITO_USER_POOL_ID_RE.match(v):
        raise PydanticCustomError(
            "cognito_user_pool_id",
            "Invalid Cognito User Pool ID: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-identifiers.html
AccountId = Annotated[
    str,
    AfterValidator(_validate_account_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^\d{12}$",
            "description": "A 12-digit AWS Account ID",
            "examples": ["123456789012"],
            "title": "AccountId",
            "minLength": 12,
            "maxLength": 12,
        }
    ),
]
"""A 12-digit AWS Account ID (e.g. `123456789012`)."""

# Source: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateUserPool.html
CognitoUserPoolId = Annotated[
    str,
    AfterValidator(_validate_cognito_user_pool_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[\w-]+_[0-9a-zA-Z]+$",
            "description": "An AWS Cognito User Pool ID",
            "examples": ["us-east-1_AbCdEfGhI"],
            "title": "CognitoUserPoolId",
            "maxLength": 55,
        }
    ),
]
"""An AWS Cognito User Pool ID (e.g. `us-east-1_AbCdEfGhI`)."""
