"""Validated types for Apache Kafka identifiers."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_KAFKA_TOPIC_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]{1,249}$")


def _validate_kafka_topic_name(v: str) -> str:
    """Validate a Kafka topic name format."""
    if not _KAFKA_TOPIC_NAME_RE.match(v):
        raise PydanticCustomError(
            "kafka_topic_name",
            "Invalid Kafka topic name: {value}",
            {"value": v},
        )
    if v in (".", ".."):
        raise PydanticCustomError(
            "kafka_topic_name",
            "Invalid Kafka topic name: '.' and '..' are not allowed. Got: {value}",
            {"value": v},
        )
    return v


# Source: https://github.com/apache/kafka/blob/trunk/clients/src/main/java/org/apache/kafka/common/internals/Topic.java
KafkaTopicName = Annotated[
    str,
    AfterValidator(_validate_kafka_topic_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _KAFKA_TOPIC_NAME_RE.pattern,
            "description": "A valid Apache Kafka topic name.",
            "examples": ["my-topic", "events.user.created", "topic_v2"],
            "title": "KafkaTopicName",
            "minLength": 1,
            "maxLength": 249,
        }
    ),
]
"""A valid Apache Kafka topic name (e.g. `my-topic`)."""
