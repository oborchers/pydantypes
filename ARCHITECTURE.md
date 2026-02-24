# Architecture

This document codifies the conventions, patterns, and design decisions of the pydantypes codebase. All contributors (human and AI) should follow these conventions when adding or modifying types.

## Type Patterns

Every type in pydantypes uses one of four patterns. The choice depends on what the type needs to do.

### Pattern A: str Subclass (Parsed Properties)

Use when the validated string has **extractable components** (e.g., bucket + key from an S3 URI, partition + service + region from an ARN).

```python
# Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-bucket-intro.html
class S3Uri(CloudStorageUri):
    """An S3 URI like s3://bucket/key with parsed properties."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^s3://([a-z0-9][a-z0-9.\-]{1,61}[a-z0-9])(/(.*))?$"
    )

    def __new__(cls, value: str) -> S3Uri:
        """Create and validate a new S3Uri instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError("s3_uri", "Invalid S3 URI: {value}", {"value": value})
        instance = str.__new__(cls, value)
        instance.bucket = m.group(1)
        instance.key = m.group(3) or ""
        return instance

    @classmethod
    def _validate(cls, value: str) -> S3Uri:
        """Validate a string as an S3 URI."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for S3Uri."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for S3Uri."""
        return {
            "type": "string",
            "format": "s3-uri",
            "pattern": cls._pattern.pattern,
            "description": "An S3 URI in the format s3://bucket/key",
            "examples": ["s3://my-bucket/path/to/file.csv"],
            "title": "S3Uri",
        }
```

Key rules:
- Cloud storage URI types inherit from `CloudStorageUri`; other Pattern A types inherit from `str`
- Regex lives on the class as `_pattern: ClassVar[re.Pattern[str]]`
- Parsed properties are set as instance attributes in `__new__`
- `_validate` is a one-liner that delegates to `__new__`
- `__get_pydantic_core_schema__` delegates to `_str_type_core_schema` from `_internal.py`
- `__get_pydantic_json_schema__` returns a dict with `type`, `format`, `pattern`, `description`, `examples`, `title`
- All five methods (`__new__`, `_validate`, `__get_pydantic_core_schema__`, `__get_pydantic_json_schema__`) have one-line docstrings
- `# Source:` comment on the line directly above the class definition

### Pattern B: Annotated Type (Simple Validation)

Use when the type only needs **validation without parsed properties** — just accept/reject.

```python
_EC2_INSTANCE_ID_RE = re.compile(r"^i-[0-9a-f]{8,17}$")


def _validate_ec2_instance_id(v: str) -> str:
    """Validate an EC2 instance ID format."""
    if not _EC2_INSTANCE_ID_RE.match(v):
        raise PydanticCustomError(
            "ec2_instance_id",
            "Invalid EC2 Instance ID: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resources.html
Ec2InstanceId = Annotated[
    str,
    AfterValidator(_validate_ec2_instance_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^i-[0-9a-f]{8,17}$",
            "description": "An AWS EC2 instance ID",
            "examples": ["i-1234567890abcdef0"],
            "title": "Ec2InstanceId",
        }
    ),
]
```

Key rules:
- Regex lives at **module level** as `_UPPER_CASE_RE = re.compile(...)`
- Validator function named `_validate_<type_name>` with a one-line docstring
- `# Source:` comment directly above the `Annotated[...]` assignment
- `WithJsonSchema` dict includes `type`, `pattern`, `description`, `examples`, `title`
- Optional: `minLength`, `maxLength` when applicable

### Pattern C: StrEnum (Enumerated Values)

Use for **fixed sets of valid values** like regions or zones.

```python
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class Region(StrEnum):
    """AWS region identifiers.

    Source: https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html
    """

    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2"
    # ...
```

Key rules:
- Python 3.10 compatibility shim at top of file
- Class docstring includes `Source:` URL
- Member names are UPPER_SNAKE_CASE
- Member values are the actual string identifiers

### Pattern D: LabelEnum (Classification Labels with Lifecycle)

Use for **AI/ML classification labels** that need metadata, deprecation, and alias resolution.

```python
class Sentiment(LabelEnum):
    POSITIVE = Label("positive", description="Expresses approval or satisfaction")
    NEGATIVE = Label("negative", description="Expresses disapproval or frustration")
    OLD_LABEL = Label("old", deprecated=True, successor="POSITIVE", aliases=["legacy"])
```

Key rules:
- Extends `LabelEnum` base class from `pydantypes.ai.labels`
- Members are `Label(...)` objects or plain strings
- Lifecycle states: active, deprecated (warns), retired (rejects)
- Alias resolution has priority over retired values

## Regex Placement

The placement depends on the pattern:

| Pattern | Where | Example |
|---------|-------|---------|
| **A** (str subclass) | `ClassVar` on the class | `_pattern: ClassVar[re.Pattern[str]] = re.compile(...)` |
| **B** (Annotated) | Module level | `_EC2_INSTANCE_ID_RE = re.compile(...)` |

Module-level regexes use the naming convention `_UPPER_SNAKE_CASE_RE`. The `_RE` suffix is mandatory — `_PATTERN` is prohibited.

### Why Python `re` Instead of Pydantic's Rust Regex

Pydantic v2 uses the Rust `regex` crate internally for `Field(pattern=...)` constraints — faster, with linear-time guarantees. We use Python's `re.compile` instead for two reasons:

- **Pattern A types need capture groups.** Our `__new__` methods extract parsed properties (`.bucket`, `.key`, etc.) from match groups. Pydantic's Rust regex only does accept/reject — it cannot return match groups to Python.
- **Custom error messages.** `AfterValidator` + `PydanticCustomError` gives us control over error codes and messages. Pydantic's built-in `pattern` constraint produces generic errors.

This is not a performance concern. Our regexes are simple (anchored, no backtracking risk), and the Python function call overhead already dominates over the regex match itself.

## Source URL References

Every type must have a `# Source:` comment on the line directly above its definition, linking to the official documentation. This applies uniformly to all patterns — no source URLs inside docstrings.

```python
# Pattern A (str subclass):
# Source: https://docs.aws.amazon.com/...
class S3Uri(str):
    """An S3 URI like s3://bucket/key with parsed properties."""

# Pattern B (Annotated):
# Source: https://docs.aws.amazon.com/...
Ec2InstanceId = Annotated[...]

# Pattern C (StrEnum):
# Source: https://docs.aws.amazon.com/...
class Region(StrEnum):
    """AWS region identifiers."""
```

Rules:
- URL must be verified to load and be the correct reference for the type
- Prefer official provider docs (AWS, Azure, GCP), RFCs, or specification documents
- Never put source URLs inside docstrings

## Docstrings

Every module, class, and function has a docstring. No exceptions.

- **Module:** `"""AWS storage types."""` — short, descriptive
- **Pattern A class:** `"""An S3 URI like s3://bucket/key with parsed properties."""` — one-liner
- **Pattern A methods:** Every `__new__`, `_validate`, `__get_pydantic_core_schema__`, and `__get_pydantic_json_schema__` must have a one-line docstring. Templates:
  - `__new__`: `"""Create and validate a new {ClassName} instance."""`
  - `_validate`: `"""Validate a string as a {description}."""`
  - `__get_pydantic_core_schema__`: `"""Return the Pydantic core schema for {ClassName}."""`
  - `__get_pydantic_json_schema__`: `"""Return the JSON schema for {ClassName}."""`
- **Pattern B validator:** Every `_validate_*` function must have a one-line docstring: `"""Validate a {type description} format."""`
- **Pattern C class:** `"""AWS region identifiers."""` — one-liner
- **`__init__.py`:** `"""AWS cloud resource types."""` — descriptive module docstring
- **Test module:** `"""Tests for AWS storage types."""`

## Module Organization

### Source Files

```
src/pydantypes/cloud/<provider>/<domain>.py
```

Each file groups related types by domain (storage, compute, network, etc.). Within a file:

- `from __future__ import annotations` first
- Standard library imports
- Third-party imports (pydantic)
- Local imports (`from pydantypes._internal import _str_type_core_schema`)
- Module-level regexes (Pattern B)
- Validator functions (Pattern B)
- Type aliases (Pattern B) or classes (Pattern A)

### `__init__.py` Exports

```python
"""AWS cloud resource types."""

from pydantypes.cloud.aws.arn import Arn, IamRoleArn, SnsTopicArn
from pydantypes.cloud.aws.compute import AmiId, Ec2InstanceId, EcsClusterName

__all__ = [
    "AccountId",
    "AmiId",
    "Arn",
    # ... alphabetically sorted
]
```

Rules:
- Explicit imports, no star imports
- `__all__` is **alphabetically sorted**
- Every public type is listed in `__all__`

## Error Handling

All validation errors use `PydanticCustomError`:

```python
raise PydanticCustomError(
    "s3_bucket_name",                    # snake_case error code
    "Invalid S3 bucket name: {value}",   # template message
    {"value": v},                        # context dict
)
```

- Error codes are snake_case, named after the type
- Messages include `{value}` placeholder for the rejected input
- Specific constraint violations get descriptive messages:
  ```python
  "Invalid S3 bucket name: must not contain consecutive dots. Got: {value}"
  ```
- Always use exception chaining when wrapping: `raise Error(...) from e`

## JSON Schema

### Format Naming

```
<provider>-<type-name>    # "aws-arn", "gcs-uri", "gcp-project-id"
<type-name>               # "jwt", "mime-type", "docker-image-ref"
```

### Schema Dict

Pattern A returns from `__get_pydantic_json_schema__`:
```python
{"type": "string", "format": "...", "pattern": "...", "description": "...", "examples": [...], "title": "..."}
```

Pattern B uses `WithJsonSchema(...)`:
```python
{"type": "string", "pattern": "...", "description": "...", "examples": [...], "title": "...", "minLength": N, "maxLength": N}
```

Pattern A includes `format`. Pattern B omits it (the `title` serves as identifier). Both always include `pattern`, `description`, `examples`, and `title`.

## Internal Helper

`_internal.py` exports a single function:

```python
def _str_type_core_schema(cls, source_type, handler) -> CoreSchema:
```

This builds the Pydantic core schema for all Pattern A types. It handles:
- JSON deserialization → validates via `cls._validate`
- Python instantiation → passes through existing instances of `cls`, otherwise validates
- Serialization → plain `str(v)`

All Pattern A types delegate to this in `__get_pydantic_core_schema__`.

## Test Conventions

### File Structure

Mirror source: `src/pydantypes/cloud/aws/storage.py` → `tests/cloud/aws/test_storage.py`

One test file per source file. Module docstring: `"""Tests for AWS storage types."""`

All tests use flat parametrized functions — class-based test grouping (`TestFooValid`, `TestFooInvalid`) is prohibited.

### Test Model

Each type gets a simple wrapper model:

```python
class S3UriModel(BaseModel):
    uri: S3Uri
```

### Required Test Cases

Every type must have these tests:

- **Valid values** — parametrized, assert roundtrip `str(model.field) == value`
- **Invalid values** — parametrized, assert `ValidationError`
- **Serialization** — `model.model_dump()["field"] == value`
- **JSON schema** — verify `type`, `format` (Pattern A) or `pattern` (Pattern B)
- **Existing instance identity** — `TypeName(value)` passed to model yields same object (`is`)
- **Parsed properties** (Pattern A only) — verify each extracted attribute

### Naming

```
test_valid_<type_name>
test_invalid_<type_name>
test_<type_name>_properties
test_<type_name>_serialization
test_<type_name>_json_schema
test_<type_name>_existing_instance
```

### Parametrization

```python
@pytest.mark.parametrize("value", ["valid-1", "valid-2"])
def test_valid_ec2_instance_id(value: str) -> None:
    m = Ec2Model(instance=value)
    assert m.instance == value

@pytest.mark.parametrize("value", ["bad-1", "bad-2", ""])
def test_invalid_ec2_instance_id(value: str) -> None:
    with pytest.raises(ValidationError):
        Ec2Model(instance=value)
```

## Python Version Compatibility

- Target: Python 3.10+
- Use `from __future__ import annotations` in every file
- Use modern syntax: `str | None`, `list[str]`, `dict[str, Any]`
- StrEnum compatibility shim for Python 3.10 (inline in files that need it)
- No lazy imports — everything at file top

## Delegation Pattern

When a URI type contains a component that has its own standalone type, the URI validator **delegates** to the component's validator. This avoids duplicating rules.

```python
# S3Uri.__new__ delegates bucket validation:
bucket = m.group(1)
_validate_s3_bucket_name(bucket)  # reuse S3BucketName's validator

# GcsUri.__new__ delegates bucket validation:
bucket = m.group(1)
_validate_gcs_bucket_name(bucket)  # reuse GcsBucketName's validator
```

## CloudStorageUri Base Class

All cloud storage URI types (`S3Uri`, `GcsUri`, `BlobStorageUri`) inherit from `CloudStorageUri` (`cloud/_base.py`), which provides:

- **Unified interface** — `.bucket` and `.key` across all providers
- **Path helpers** — `.name`, `.suffix`, `.stem`, `.parent_key`, `.suffixes`, `.parts`
- **Heuristic helpers** — `.is_file`, `.is_folder` (based on key naming conventions)

Path helpers delegate to `PurePosixPath(self.key)` internally.

### Attribute Naming

| Concept | Unified name | Provider-specific aliases |
|---------|-------------|--------------------------|
| Bucket/container | `.bucket` | Azure: `.container` |
| Object path | `.key` | Azure: `.blob_path` |

S3Uri and GcsUri use only the unified names. BlobStorageUri exposes both unified names (from base class) and Azure-specific aliases (`.account_name`, `.container`, `.blob_path`).

### Subclass Contract

Subclasses must set `bucket` and `key` as instance attributes in `__new__`. The base class does not define `__new__` — each provider has its own regex and validation. Pydantic integration (`__get_pydantic_core_schema__`, `__get_pydantic_json_schema__`) remains on each subclass.
