"""Validated types for Git references and URLs."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

# ---------------------------------------------------------------------------
# Pattern B: GitCommitSha
# ---------------------------------------------------------------------------

_GIT_COMMIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _validate_git_commit_sha(v: str) -> str:
    """Validate a Git commit SHA-1 hash."""
    if not _GIT_COMMIT_SHA_RE.match(v):
        raise PydanticCustomError(
            "git_commit_sha",
            "Invalid Git commit SHA: expected 40 hex characters. Got: {value}",
            {"value": v},
        )
    return v.lower()


# Source: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
GitCommitSha = Annotated[
    str,
    AfterValidator(_validate_git_commit_sha),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _GIT_COMMIT_SHA_RE.pattern,
            "description": "A full 40-character Git commit SHA-1 hash (normalized to lowercase)",
            "examples": ["a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"],
            "title": "GitCommitSha",
            "minLength": 40,
            "maxLength": 40,
        }
    ),
]
"""A full 40-character Git commit SHA-1 hash (normalized to lowercase) (e.g. `a94a8fe5ccb19ba61c4c0873d391e987982fbbd3`)."""

# ---------------------------------------------------------------------------
# Pattern B: GitShortSha
# ---------------------------------------------------------------------------

_GIT_SHORT_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def _validate_git_short_sha(v: str) -> str:
    """Validate a Git short SHA prefix."""
    if not _GIT_SHORT_SHA_RE.match(v):
        raise PydanticCustomError(
            "git_short_sha",
            "Invalid Git short SHA: expected 7-40 hex characters. Got: {value}",
            {"value": v},
        )
    return v.lower()


# Source: https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection
GitShortSha = Annotated[
    str,
    AfterValidator(_validate_git_short_sha),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _GIT_SHORT_SHA_RE.pattern,
            "description": "A Git short SHA prefix (7-40 hex characters, normalized to lowercase)",
            "examples": ["a94a8fe"],
            "title": "GitShortSha",
            "minLength": 7,
            "maxLength": 40,
        }
    ),
]
"""A Git short SHA prefix (7-40 hex characters, normalized to lowercase) (e.g. `a94a8fe`)."""

# ---------------------------------------------------------------------------
# Pattern B: GitRef
# ---------------------------------------------------------------------------

_GIT_REF_FORBIDDEN_RE = re.compile(r"[\x00-\x1f\x7f ~^:?*\[\\]")


def _validate_git_ref(v: str) -> str:
    """Validate a Git ref name per git-check-ref-format rules."""
    if not v:
        raise PydanticCustomError(
            "git_ref", "Invalid Git ref: must not be empty. Got: {value}", {"value": v}
        )
    if v == "@":
        raise PydanticCustomError(
            "git_ref", "Invalid Git ref: must not be single '@'. Got: {value}", {"value": v}
        )
    if ".." in v:
        raise PydanticCustomError(
            "git_ref",
            "Invalid Git ref: must not contain '..'. Got: {value}",
            {"value": v},
        )
    if v.startswith("/") or v.endswith("/"):
        raise PydanticCustomError(
            "git_ref",
            "Invalid Git ref: must not start or end with '/'. Got: {value}",
            {"value": v},
        )
    if "//" in v:
        raise PydanticCustomError(
            "git_ref",
            "Invalid Git ref: must not contain consecutive slashes. Got: {value}",
            {"value": v},
        )
    if v.endswith("."):
        raise PydanticCustomError(
            "git_ref",
            "Invalid Git ref: must not end with '.'. Got: {value}",
            {"value": v},
        )
    if "@{" in v:
        raise PydanticCustomError(
            "git_ref",
            "Invalid Git ref: must not contain '@{{'. Got: {value}",
            {"value": v},
        )
    if _GIT_REF_FORBIDDEN_RE.search(v):
        raise PydanticCustomError(
            "git_ref",
            "Invalid Git ref: contains forbidden characters. Got: {value}",
            {"value": v},
        )
    # Per-component checks: no component may start with '.' or end with '.lock'
    for component in v.split("/"):
        if component.startswith("."):
            raise PydanticCustomError(
                "git_ref",
                "Invalid Git ref: component must not start with '.'. Got: {value}",
                {"value": v},
            )
        if component.endswith(".lock"):
            raise PydanticCustomError(
                "git_ref",
                "Invalid Git ref: component must not end with '.lock'. Got: {value}",
                {"value": v},
            )
    return v


# Source: https://git-scm.com/docs/git-check-ref-format
GitRef = Annotated[
    str,
    AfterValidator(_validate_git_ref),
    WithJsonSchema(
        {
            "type": "string",
            "description": "A valid Git ref name (branch or tag) per git-check-ref-format rules",
            "examples": ["main", "feature/my-branch", "refs/heads/main", "v1.0"],
            "title": "GitRef",
            "minLength": 1,
        }
    ),
]
"""A valid Git ref name (branch or tag) per git-check-ref-format rules (e.g. `main`)."""

# ---------------------------------------------------------------------------
# Pattern A: GitSshUrl
# ---------------------------------------------------------------------------


# Source: https://git-scm.com/docs/git-clone#_git_urls
class GitSshUrl(str):
    """A Git SSH clone URL like git@github.com:owner/repo.git with parsed properties."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?:"
        # SCP-like: user@host:path[.git]
        r"(?P<scp_user>[a-zA-Z0-9_][a-zA-Z0-9_.-]*)@(?P<scp_host>[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?):(?P<scp_path>[a-zA-Z0-9_./-]+?)"
        r"|"
        # ssh://user@host[:port]/path[.git]
        r"ssh://(?P<ssh_user>[a-zA-Z0-9_][a-zA-Z0-9_.-]*)@(?P<ssh_host>[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?)(?::(?P<ssh_port>\d+))?/(?P<ssh_path>[a-zA-Z0-9_./-]+?)"
        r")"
        r"(?:\.git)?$"
    )

    host: str
    owner: str
    repo: str

    def __new__(cls, value: str) -> GitSshUrl:
        """Create and validate a new GitSshUrl instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "git_ssh_url",
                "Invalid Git SSH URL: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        if m.group("scp_host"):
            instance.host = m.group("scp_host")
            path = m.group("scp_path")
        else:
            instance.host = m.group("ssh_host")
            path = m.group("ssh_path")
        parts = path.rsplit("/", 1)
        if len(parts) == 2:
            instance.owner = parts[0]
            instance.repo = parts[1]
        else:
            instance.owner = ""
            instance.repo = parts[0]
        return instance

    @classmethod
    def _validate(cls, value: str) -> GitSshUrl:
        """Validate a string as a Git SSH URL."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for GitSshUrl."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for GitSshUrl."""
        return {
            "type": "string",
            "format": "git-ssh-url",
            "description": "A Git SSH clone URL in SCP-like (git@host:owner/repo.git) or ssh:// format",
            "examples": [
                "git@github.com:torvalds/linux.git",
                "ssh://git@github.com/torvalds/linux.git",
            ],
            "title": "GitSshUrl",
        }


# ---------------------------------------------------------------------------
# Pattern A: GitHttpsUrl
# ---------------------------------------------------------------------------


# Source: https://git-scm.com/docs/git-clone#_git_urls
class GitHttpsUrl(str):
    """A Git HTTPS clone URL like https://github.com/owner/repo.git with parsed properties."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^https://(?P<host>[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?(?::\d+)?)/(?P<path>[a-zA-Z0-9_./-]+?)(?:\.git)?$"
    )

    host: str
    owner: str
    repo: str

    def __new__(cls, value: str) -> GitHttpsUrl:
        """Create and validate a new GitHttpsUrl instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "git_https_url",
                "Invalid Git HTTPS URL: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.host = m.group("host")
        path = m.group("path")
        parts = path.rsplit("/", 1)
        if len(parts) == 2:
            instance.owner = parts[0]
            instance.repo = parts[1]
        else:
            instance.owner = ""
            instance.repo = parts[0]
        return instance

    @classmethod
    def _validate(cls, value: str) -> GitHttpsUrl:
        """Validate a string as a Git HTTPS URL."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for GitHttpsUrl."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for GitHttpsUrl."""
        return {
            "type": "string",
            "format": "git-https-url",
            "description": "A Git HTTPS clone URL like https://github.com/owner/repo.git",
            "examples": [
                "https://github.com/torvalds/linux.git",
                "https://gitlab.com/group/subgroup/repo.git",
            ],
            "title": "GitHttpsUrl",
        }
