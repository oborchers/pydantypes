# Contributing to pydantypes

Thanks for your interest in contributing! We welcome bug fixes, new types, and improvements.

For clear bug fixes or typos, just submit a PR. For new features or if there is any doubt on how to approach something, open an issue first to discuss.

## Setup

```bash
git clone https://github.com/oborchers/pydantypes.git
cd pydantypes
make init        # creates venv, installs deps, sets up pre-commit hooks
```

Requires [uv](https://docs.astral.sh/uv/). All commands use `uv run` — never use `python` or `pip` directly.

## Running Checks

```bash
make check       # lint + typecheck + tests (run before every PR)
make format      # auto-format code
make test-cov    # tests with coverage report
```

## Adding a New Type

The most common contribution is adding a validated type. Follow these steps:

- Look at an existing type in the same domain for the pattern (e.g. `src/pydantypes/cloud/aws/storage.py` for AWS types)
- Place the type in the appropriate domain module, or create a new file if it doesn't fit existing ones
- Add the type to the domain's `__init__.py` `__all__` list
- Add tests in the mirror location under `tests/` — one test file per source file
- Run `make check` to verify everything passes

Four type patterns exist in the codebase (A/B/C/D). See [ARCHITECTURE.md](ARCHITECTURE.md) for full details, examples, and conventions for each pattern.

## PR Guidelines

- Keep PRs focused — one type or one fix per PR
- All checks must pass (`make check`)
- New code needs tests — target the existing 95%+ coverage level
- Follow existing code style — Ruff enforces this automatically via pre-commit

## Reporting Issues

Use [GitHub Issues](https://github.com/oborchers/pydantypes/issues). For security vulnerabilities, see [SECURITY.md](SECURITY.md).
