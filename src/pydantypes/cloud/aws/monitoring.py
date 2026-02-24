"""AWS monitoring types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_CLOUDWATCH_LOG_GROUP_NAME_RE = re.compile(r"^[.\-_/#A-Za-z0-9]{1,512}$")


def _validate_cloudwatch_log_group_name(v: str) -> str:
    """Validate a CloudWatch log group name format."""
    if not _CLOUDWATCH_LOG_GROUP_NAME_RE.match(v):
        raise PydanticCustomError(
            "cloudwatch_log_group_name",
            "Invalid CloudWatch Log Group name: {value}",
            {"value": v},
        )
    if v.startswith("aws/"):
        raise PydanticCustomError(
            "cloudwatch_log_group_name",
            "Invalid CloudWatch Log Group name: must not start with 'aws/'. Got: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateLogGroup.html
CloudWatchLogGroupName = Annotated[
    str,
    AfterValidator(_validate_cloudwatch_log_group_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[.\-_/#A-Za-z0-9]{1,512}$",
            "description": "An AWS CloudWatch Log Group name",
            "examples": ["/my-app/production"],
            "title": "CloudWatchLogGroupName",
            "maxLength": 512,
        }
    ),
]
"""An AWS CloudWatch Log Group name (e.g. `/my-app/production`)."""
