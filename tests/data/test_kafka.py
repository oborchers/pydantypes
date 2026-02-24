"""Tests for Apache Kafka identifier types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.data.kafka import KafkaTopicName


class KafkaTopicModel(BaseModel):
    topic: KafkaTopicName


@pytest.mark.parametrize(
    "value",
    [
        "my-topic",
        "events.user.created",
        "topic_v2",
        "a",
        "A",
        "0",
        "my.topic-name_v2",
        "a" * 249,
        "test-topic.with.dots-and_underscores",
    ],
)
def test_valid_kafka_topic_name(value: str) -> None:
    m = KafkaTopicModel(topic=value)
    assert m.topic == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        ".",
        "..",
        "a" * 250,
        "topic with spaces",
        "topic/slash",
        "topic@at",
        "topic!bang",
        "topic#hash",
    ],
)
def test_invalid_kafka_topic_name(value: str) -> None:
    with pytest.raises(ValidationError):
        KafkaTopicModel(topic=value)


def test_kafka_topic_name_serialization() -> None:
    m = KafkaTopicModel(topic="my-topic")
    assert m.model_dump() == {"topic": "my-topic"}
    json_str = m.model_dump_json()
    restored = KafkaTopicModel.model_validate_json(json_str)
    assert restored.topic == m.topic


def test_kafka_topic_name_json_schema() -> None:
    schema = KafkaTopicModel.model_json_schema()
    field = schema["properties"]["topic"]
    assert field["type"] == "string"
    assert field["title"] == "KafkaTopicName"
    assert field["minLength"] == 1
    assert field["maxLength"] == 249
