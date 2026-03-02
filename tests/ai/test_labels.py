"""Tests for pydantypes.ai.labels — LabelEnum and Label."""

from __future__ import annotations

import json
import warnings

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.ai import Label, LabelEnum

# ---------------------------------------------------------------------------
# Test fixtures: enum definitions representing different lifecycle phases
# ---------------------------------------------------------------------------


class Sentiment(LabelEnum):
    """Full lifecycle enum for testing."""

    POSITIVE = Label(
        "positive",
        description="Expresses approval, happiness, or satisfaction",
        note="Core label since v1.",
    )
    NEGATIVE = Label(
        "negative",
        description="Expresses disapproval, sadness, or frustration",
    )
    NEUTRAL = Label(
        "neutral",
        description="No clear emotional tone",
        note="Deprecated in Q1 2024. See JIRA-1234.",
        deprecated=True,
        successor="AMBIGUOUS",
    )
    AMBIGUOUS = Label(
        "ambiguous",
        description="Mixed or unclear emotional signals",
        note="Added Q1 2024 to replace neutral.",
        aliases=["neutral_v1"],
    )


class RetiredSentiment(LabelEnum):
    """Enum with a retired label and aliases on the successor."""

    POSITIVE = Label("positive", description="Positive sentiment")
    NEGATIVE = Label("negative", description="Negative sentiment")
    NEUTRAL = Label(
        "neutral",
        description="No clear emotional tone",
        retired=True,
        successor="AMBIGUOUS",
    )
    AMBIGUOUS = Label(
        "ambiguous",
        description="Mixed or unclear emotional signals",
        aliases=["neutral"],
    )


class SimpleLabels(LabelEnum):
    """Plain string labels — no metadata."""

    YES = "yes"
    NO = "no"


class SentimentModel(BaseModel):
    sentiment: Sentiment


class RetiredSentimentModel(BaseModel):
    sentiment: RetiredSentiment


class SimpleModel(BaseModel):
    label: SimpleLabels


# ---------------------------------------------------------------------------
# Active labels
# ---------------------------------------------------------------------------


class TestActiveLabels:
    @pytest.mark.parametrize("value", ["positive", "negative", "ambiguous"])
    def test_valid_active_values(self, value: str) -> None:
        result = SentimentModel(sentiment=value)
        assert result.sentiment.value == value
        assert isinstance(result.sentiment, Sentiment)

    def test_property_access(self) -> None:
        result = SentimentModel(sentiment="positive")
        assert result.sentiment.description == "Expresses approval, happiness, or satisfaction"
        assert result.sentiment.note == "Core label since v1."
        assert result.sentiment.deprecated is False
        assert result.sentiment.retired is False
        assert result.sentiment.successor is None
        assert result.sentiment.aliases == []

    def test_serialization_roundtrip_dict(self) -> None:
        result = SentimentModel(sentiment="positive")
        dumped = result.model_dump()
        assert dumped == {"sentiment": "positive"}
        restored = SentimentModel.model_validate(dumped)
        assert restored.sentiment is Sentiment.POSITIVE

    def test_serialization_roundtrip_json(self) -> None:
        result = SentimentModel(sentiment="positive")
        json_str = result.model_dump_json()
        assert json.loads(json_str) == {"sentiment": "positive"}
        restored = SentimentModel.model_validate_json(json_str)
        assert restored.sentiment is Sentiment.POSITIVE

    def test_invalid_value_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SentimentModel(sentiment="unknown")


# ---------------------------------------------------------------------------
# Deprecated labels
# ---------------------------------------------------------------------------


class TestDeprecatedLabels:
    def test_accepted_with_warning(self) -> None:
        with pytest.warns(DeprecationWarning, match="Label 'neutral' is deprecated"):
            result = SentimentModel(sentiment="neutral")
        assert result.sentiment is Sentiment.NEUTRAL

    def test_warning_includes_successor(self) -> None:
        with pytest.warns(DeprecationWarning, match="Use 'AMBIGUOUS' instead"):
            SentimentModel(sentiment="neutral")

    def test_deprecated_flag(self) -> None:
        assert Sentiment.NEUTRAL.deprecated is True
        assert Sentiment.NEUTRAL.successor == "AMBIGUOUS"

    def test_deprecated_still_in_schema(self) -> None:
        assert "neutral" in Sentiment.schema_values()


# ---------------------------------------------------------------------------
# Retired labels
# ---------------------------------------------------------------------------


class TestRetiredLabels:
    def test_retired_rejected_when_no_alias(self) -> None:
        """A retired label with no alias on the successor is rejected."""

        class WithRetiredNoAlias(LabelEnum):
            OLD = Label("old", retired=True, successor="NEW")
            NEW = Label("new", description="The replacement")

        class M(BaseModel):
            val: WithRetiredNoAlias

        with pytest.raises(ValidationError, match="retired"):
            M(val="old")

    def test_retired_excluded_from_schema(self) -> None:
        assert "neutral" not in RetiredSentiment.schema_values()

    def test_retired_member_accessible_in_python(self) -> None:
        assert RetiredSentiment.NEUTRAL.value == "neutral"
        assert RetiredSentiment.NEUTRAL.retired is True


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------


class TestAliases:
    def test_alias_resolves_silently(self) -> None:
        """Alias resolution should not emit any warnings."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = SentimentModel(sentiment="neutral_v1")
        assert result.sentiment is Sentiment.AMBIGUOUS

    def test_alias_resolves_retired_value_via_successor(self) -> None:
        """In RetiredSentiment, 'neutral' is both a retired member value and an alias on AMBIGUOUS.

        Because aliases are checked before direct member matching, the alias wins and
        resolves to AMBIGUOUS instead of raising a retired error.
        """
        result = RetiredSentimentModel(sentiment="neutral")
        assert result.sentiment is RetiredSentiment.AMBIGUOUS

    def test_alias_map_contents(self) -> None:
        aliases = Sentiment.alias_map()
        assert "neutral_v1" in aliases
        assert aliases["neutral_v1"] is Sentiment.AMBIGUOUS

    def test_alias_map_retired_enum(self) -> None:
        aliases = RetiredSentiment.alias_map()
        assert "neutral" in aliases
        assert aliases["neutral"] is RetiredSentiment.AMBIGUOUS


# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------


class TestJsonSchema:
    def test_schema_structure(self) -> None:
        schema = SentimentModel.model_json_schema()
        sentiment_schema = schema["properties"]["sentiment"]
        assert sentiment_schema["type"] == "string"
        assert "enum" in sentiment_schema
        assert sentiment_schema["title"] == "Sentiment"

    def test_schema_excludes_retired(self) -> None:
        schema = RetiredSentimentModel.model_json_schema()
        sentiment_schema = schema["properties"]["sentiment"]
        assert "neutral" not in sentiment_schema["enum"]
        assert "positive" in sentiment_schema["enum"]
        assert "negative" in sentiment_schema["enum"]
        assert "ambiguous" in sentiment_schema["enum"]

    def test_schema_includes_deprecated(self) -> None:
        schema = SentimentModel.model_json_schema()
        sentiment_schema = schema["properties"]["sentiment"]
        assert "neutral" in sentiment_schema["enum"]

    def test_schema_no_custom_extensions(self) -> None:
        """Schema should only have type, enum, and title — no extras."""
        schema = SentimentModel.model_json_schema()
        sentiment_schema = schema["properties"]["sentiment"]
        allowed_keys = {"type", "enum", "title"}
        assert set(sentiment_schema.keys()) == allowed_keys


# ---------------------------------------------------------------------------
# Introspection methods
# ---------------------------------------------------------------------------


class TestIntrospection:
    def test_active_labels(self) -> None:
        active = Sentiment.active_labels()
        active_values = [m.value for m in active]
        assert "positive" in active_values
        assert "negative" in active_values
        assert "ambiguous" in active_values
        assert "neutral" not in active_values

    def test_deprecated_labels(self) -> None:
        deprecated = Sentiment.deprecated_labels()
        assert len(deprecated) == 1
        assert deprecated[0] is Sentiment.NEUTRAL

    def test_retired_labels(self) -> None:
        retired = RetiredSentiment.retired_labels()
        assert len(retired) == 1
        assert retired[0] is RetiredSentiment.NEUTRAL

    def test_retired_labels_empty_when_none(self) -> None:
        retired = Sentiment.retired_labels()
        assert retired == []

    def test_schema_values(self) -> None:
        values = Sentiment.schema_values()
        assert values == ["positive", "negative", "neutral", "ambiguous"]

    def test_schema_values_excludes_retired(self) -> None:
        values = RetiredSentiment.schema_values()
        assert values == ["positive", "negative", "ambiguous"]

    def test_alias_map(self) -> None:
        aliases = Sentiment.alias_map()
        assert isinstance(aliases, dict)
        assert "neutral_v1" in aliases
        assert aliases["neutral_v1"] is Sentiment.AMBIGUOUS


# ---------------------------------------------------------------------------
# Plain string support
# ---------------------------------------------------------------------------


class TestPlainStringSupport:
    def test_simple_labels_valid(self) -> None:
        result = SimpleModel(label="yes")
        assert result.label is SimpleLabels.YES
        assert result.label.value == "yes"

    def test_simple_labels_invalid(self) -> None:
        with pytest.raises(ValidationError):
            SimpleModel(label="maybe")

    def test_simple_labels_default_metadata(self) -> None:
        assert SimpleLabels.YES.description == ""
        assert SimpleLabels.YES.note == ""
        assert SimpleLabels.YES.deprecated is False
        assert SimpleLabels.YES.retired is False
        assert SimpleLabels.YES.successor is None
        assert SimpleLabels.YES.aliases == []

    def test_simple_labels_serialization(self) -> None:
        result = SimpleModel(label="no")
        dumped = result.model_dump()
        assert dumped == {"label": "no"}

    def test_simple_labels_schema(self) -> None:
        schema = SimpleModel.model_json_schema()
        label_schema = schema["properties"]["label"]
        assert label_schema["enum"] == ["yes", "no"]


# ---------------------------------------------------------------------------
# str() behavior
# ---------------------------------------------------------------------------


class TestStrBehavior:
    def test_str_returns_value(self) -> None:
        assert str(Sentiment.POSITIVE) == "positive"

    def test_str_matches_value_for_all_members(self) -> None:
        for member in Sentiment:
            assert str(member) == member.value

    def test_str_in_fstring(self) -> None:
        label = Sentiment.POSITIVE
        assert f"label: {label}" == "label: positive"

    def test_str_concat(self) -> None:
        label = Sentiment.POSITIVE
        assert "label: " + str(label) == "label: positive"

    def test_simple_labels_str(self) -> None:
        assert str(SimpleLabels.YES) == "yes"
        assert str(SimpleLabels.NO) == "no"


# ---------------------------------------------------------------------------
# Existing instance pass-through
# ---------------------------------------------------------------------------


class TestExistingInstancePassthrough:
    def test_enum_member_accepted_directly(self) -> None:
        """An already-instantiated enum member is accepted without re-validation."""
        result = SentimentModel(sentiment=Sentiment.POSITIVE)
        assert result.sentiment is Sentiment.POSITIVE

    def test_deprecated_member_passthrough_no_warning(self) -> None:
        """Passing an already-instantiated deprecated member should not warn."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = SentimentModel(sentiment=Sentiment.NEUTRAL)
        assert result.sentiment is Sentiment.NEUTRAL
