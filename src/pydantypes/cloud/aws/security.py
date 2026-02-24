"""AWS security types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_KMS_KEY_ID_RE = re.compile(
    r"^(mrk-[0-9a-f]{32}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"
)
_SECRETS_MANAGER_SECRET_NAME_RE = re.compile(r"^[a-zA-Z0-9/_+=.@-]{1,512}$")
_SSM_PARAMETER_NAME_RE = re.compile(r"^[a-zA-Z0-9_./-]+$")


def _validate_kms_key_id(v: str) -> str:
    """Validate a KMS key ID format."""
    if not _KMS_KEY_ID_RE.match(v):
        raise PydanticCustomError(
            "kms_key_id",
            "Invalid KMS Key ID: {value}",
            {"value": v},
        )
    return v


def _validate_secrets_manager_secret_name(v: str) -> str:
    """Validate a Secrets Manager secret name format."""
    if not _SECRETS_MANAGER_SECRET_NAME_RE.match(v):
        raise PydanticCustomError(
            "secrets_manager_secret_name",
            "Invalid Secrets Manager secret name: {value}",
            {"value": v},
        )
    return v


def _validate_ssm_parameter_name(v: str) -> str:
    """Validate an SSM parameter name format."""
    if not _SSM_PARAMETER_NAME_RE.match(v) or len(v) > 1011:
        raise PydanticCustomError(
            "ssm_parameter_name",
            "Invalid SSM Parameter name: {value}",
            {"value": v},
        )
    if v.lower().startswith("aws") or v.lower().startswith("ssm"):
        raise PydanticCustomError(
            "ssm_parameter_name",
            "Invalid SSM Parameter name: must not start with 'aws' or 'ssm'. Got: {value}",
            {"value": v},
        )
    if v.count("/") > 15:
        raise PydanticCustomError(
            "ssm_parameter_name",
            "Invalid SSM Parameter name: exceeds 15 hierarchy levels. Got: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html
KmsKeyId = Annotated[
    str,
    AfterValidator(_validate_kms_key_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": (
                r"^(mrk-[0-9a-f]{32}"
                r"|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"
            ),
            "description": "An AWS KMS key ID (UUID or multi-region key ID)",
            "examples": ["12345678-1234-1234-1234-123456789012"],
            "title": "KmsKeyId",
        }
    ),
]
"""An AWS KMS key ID (UUID or multi-region key ID) (e.g. `12345678-1234-1234-1234-123456789012`)."""

# Source: https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_CreateSecret.html
SecretsManagerSecretName = Annotated[
    str,
    AfterValidator(_validate_secrets_manager_secret_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9/_+=.@-]{1,512}$",
            "description": "An AWS Secrets Manager secret name",
            "examples": ["prod/my-app/db-password"],
            "title": "SecretsManagerSecretName",
            "maxLength": 512,
        }
    ),
]
"""An AWS Secrets Manager secret name (e.g. `prod/my-app/db-password`)."""

# Source: https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_PutParameter.html
SsmParameterName = Annotated[
    str,
    AfterValidator(_validate_ssm_parameter_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9_./-]+$",
            "description": "An AWS SSM Parameter Store parameter name",
            "examples": ["/my-app/config/database-url"],
            "title": "SsmParameterName",
            "maxLength": 1011,
        }
    ),
]
"""An AWS SSM Parameter Store parameter name (e.g. `/my-app/config/database-url`)."""
