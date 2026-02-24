# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pydantypes — The missing types for Pydantic. Validated, constrained types for cloud (AWS/Azure/GCP), DevOps, web, data, and AI engineering identifiers.

**Repo**: https://github.com/oborchers/pydantypes | **Python**: 3.10+ | **Pydantic**: v2.0+

## Quick Start

```bash
make init        # Full setup: env + install + pre-commit
make check       # Run all: lint + typecheck + tests
```

## Development Commands

```bash
# Setup: env, install, init, sync
# Quality: format, format-check, lint, lint-fix, typecheck
# Testing: test, test-cov
# Build: build, clean
# All: check (lint+typecheck+tests)
```

### Pre-commit Hooks

**Auto** (every commit): ruff lint with `--fix`, ruff format, file hygiene (trailing whitespace, end-of-file, yaml/toml check, large files, merge conflicts, debug statements). Typecheck and tests run in CI only — too slow for pre-commit. Run `make check` locally before pushing.

## Critical Rules

### Always Use UV

```bash
# Correct
uv run python script.py
uv run pytest tests/ -v
make test

# Wrong — never use python/pip directly
python script.py
pip install pydantypes
```

### Always Analyze Codebase Before Making Changes

Check existing patterns first, never invent new ones. The `cloud/` modules are the exemplar — all other modules (devops/, web/, data/, ai/) must follow the same conventions. See [ARCHITECTURE.md](ARCHITECTURE.md) for the canonical reference on type patterns (A/B/C/D), regex placement, docstring conventions, error handling, JSON schema, and test structure.

```bash
tree src/pydantypes/
grep -r "class.*Type" src/ --include="*.py" | head -20
```

### Avoid Lazy Imports

All imports at file top — ONLY exception is circular imports.

### Every Type Must Have a `# Source:` Comment

Every type definition must have a `# Source: <url>` comment on the line directly above it, linking to the official documentation for the format being validated. No exceptions for any pattern (class, Annotated, StrEnum). The URL must be verified to load and be the correct reference. Never put source URLs inside docstrings.

### Never Reference Removed Code in Comments

Comments describe what code DOES, not what it USED TO DO. Git tracks history.

### Makefile Is the Single Source of Truth

All commands — CI, pre-commit, developer workflow — use `make` targets. Never run raw tool commands in CI or docs; always wrap them in a Makefile target. `make check` runs the full quality gate (format-check + lint + typecheck + test).

### All Types Are `str`-Based

Every type uses `str` as its base — even when the format is a well-known type like UUID. Azure `SubscriptionId` is `Annotated[str, ...]`, not `Annotated[UUID, ...]`. Consistency over cleverness: string in, string out. See [ARCHITECTURE.md](ARCHITECTURE.md) "All Types Are str-Based" for rationale.

### Never Overlap with Pydantic or pydantic-extra-types

Before adding any new type, verify it does not duplicate functionality already provided by Pydantic core or pydantic-extra-types. See [ARCHITECTURE.md](ARCHITECTURE.md) "No-Overlap Rule" for the explicit inventory. pydantypes fills gaps — it never reimplements what already exists.

### Check Before Creating Files

Prefer editing existing files. Never proactively create docs. Check structure first.

## Project Structure

```
src/pydantypes/
  __init__.py          # Package root, version import
  py.typed             # PEP 561 marker
  cloud/
    aws/               # S3 URIs, IAM ARNs, EC2 IDs, ...
    azure/             # Blob URIs, resource IDs, ...
    gcp/               # GCS URIs, project IDs, ...
  devops/              # Docker refs, semver, cron, ...
  web/                 # Endpoints, headers, MIME types, ...
  data/                # SQL identifiers, connection strings, ...
  ai/                  # LLM classification labels
tests/                 # Mirrors src structure
```

## Python and Formatting

**Ruff**: 100 chars, double quotes, 4-space indent, rules: E/F/UP/B/SIM/I/PLC/RUF/PT/N

### Modern Type Syntax (3.10+)

```python
# Correct — use built-in generics and union syntax
def process(val: str | int) -> str | None:
    items: list[dict[str, Any]] = []

# Wrong — old typing imports
from typing import Union, Optional, Dict, List
```

### Pydantic Patterns

Use `BaseModel` for all models. Avoid dataclasses.

```python
from pydantic import BaseModel, Field, field_validator

class Config(BaseModel):
    key: str = Field(..., min_length=1)

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("must start with sk-")
        return v
```

### StrEnum for Constants

```python
from enum import StrEnum

class CloudProvider(StrEnum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
```

## Error Handling

```python
# Exception chaining (B904)
raise CustomError("msg") from e

# Unused loop variables: prefix with _
for name, _value in items:
    pass

# Flatten nested conditions (SIM102)
if c1 and c2 and c3:
    pass
```

## Testing

### Organization

Mirror src structure: `src/pydantypes/cloud/aws/s3.py` -> `tests/cloud/aws/test_s3.py`

1 test file per source file. Use fixtures in `conftest.py`, parametrize for multiple cases.

### Coverage: 90%+ Target

**Priority**: models -> validation errors -> happy path -> edge cases

```python
# Use dirty-equals for flexible assertions
from dirty_equals import IsStr, IsInstance

# Use real values in mocks, not Mock()
mock_settings.threshold = 0.5
```

## Versioning

Git tags `0.0.0` (no 'v' prefix) via hatch-vcs. `_version.py` is auto-generated at build time, never committed.

## Important Guidelines

- **UV only**: `uv run` for all Python execution
- **Quality**: Run `make format` / `make check` frequently
- **Git**: NEVER `git push` (user only), stage+commit only, meaningful messages
- **Files**: Avoid creating new files, prefer editing, NEVER proactive docs
- Use bullet lists, not numbered lists in documentation
