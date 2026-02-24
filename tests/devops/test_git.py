"""Tests for Git reference and URL types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.devops.git import GitCommitSha, GitHttpsUrl, GitRef, GitShortSha, GitSshUrl

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class CommitShaModel(BaseModel):
    sha: GitCommitSha


class ShortShaModel(BaseModel):
    sha: GitShortSha


class RefModel(BaseModel):
    ref: GitRef


class SshUrlModel(BaseModel):
    url: GitSshUrl


class HttpsUrlModel(BaseModel):
    url: GitHttpsUrl


# ---------------------------------------------------------------------------
# GitCommitSha
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
        "0000000000000000000000000000000000000000",
        "abcdef1234567890abcdef1234567890abcdef12",
    ],
)
def test_valid_git_commit_sha(value: str) -> None:
    m = CommitShaModel(sha=value)
    assert m.sha == value.lower()


def test_git_commit_sha_normalizes_to_lowercase() -> None:
    upper = "A94A8FE5CCB19BA61C4C0873D391E987982FBBD3"
    m = CommitShaModel(sha=upper)
    assert m.sha == upper.lower()


@pytest.mark.parametrize(
    "value",
    [
        "",
        "a94a8fe",
        "a" * 39,
        "a" * 41,
        "g" * 40,
        "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3 ",
    ],
)
def test_invalid_git_commit_sha(value: str) -> None:
    with pytest.raises(ValidationError):
        CommitShaModel(sha=value)


def test_git_commit_sha_serialization() -> None:
    value = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
    m = CommitShaModel(sha=value)
    json_str = m.model_dump_json()
    restored = CommitShaModel.model_validate_json(json_str)
    assert restored.sha == m.sha


def test_git_commit_sha_json_schema() -> None:
    schema = CommitShaModel.model_json_schema()
    field = schema["properties"]["sha"]
    assert field["type"] == "string"
    assert field["title"] == "GitCommitSha"
    assert field["minLength"] == 40
    assert field["maxLength"] == 40


# ---------------------------------------------------------------------------
# GitShortSha
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "a94a8fe",
        "a94a8fe5cc",
        "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
        "1234567890",
    ],
)
def test_valid_git_short_sha(value: str) -> None:
    m = ShortShaModel(sha=value)
    assert m.sha == value.lower()


def test_git_short_sha_normalizes_to_lowercase() -> None:
    upper = "ABCDEF1"
    m = ShortShaModel(sha=upper)
    assert m.sha == upper.lower()


@pytest.mark.parametrize(
    "value",
    [
        "",
        "a94a8f",
        "a" * 41,
        "g" * 7,
        "abc def",
    ],
)
def test_invalid_git_short_sha(value: str) -> None:
    with pytest.raises(ValidationError):
        ShortShaModel(sha=value)


def test_git_short_sha_serialization() -> None:
    value = "a94a8fe"
    m = ShortShaModel(sha=value)
    json_str = m.model_dump_json()
    restored = ShortShaModel.model_validate_json(json_str)
    assert restored.sha == m.sha


def test_git_short_sha_json_schema() -> None:
    schema = ShortShaModel.model_json_schema()
    field = schema["properties"]["sha"]
    assert field["type"] == "string"
    assert field["title"] == "GitShortSha"
    assert field["minLength"] == 7
    assert field["maxLength"] == 40


# ---------------------------------------------------------------------------
# GitRef
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "main",
        "develop",
        "feature/my-branch",
        "refs/heads/main",
        "refs/tags/v1.0.0",
        "feature/JIRA-123",
        "v1.0",
        "a",
        "release/2024-01-01",
    ],
)
def test_valid_git_ref(value: str) -> None:
    m = RefModel(ref=value)
    assert m.ref == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "@",
        "feature..branch",
        "/leading-slash",
        "trailing-slash/",
        ".starts-with-dot",
        "ends-with-dot.",
        "main.lock",
        "feature//branch",
        "feature@{branch",
        "feature branch",
        "feature~branch",
        "feature^branch",
        "feature:branch",
        "feature?branch",
        "feature*branch",
        "feature[branch",
        "feature\\branch",
        "refs/heads/.hidden",
        "refs/heads/main.lock",
    ],
)
def test_invalid_git_ref(value: str) -> None:
    with pytest.raises(ValidationError):
        RefModel(ref=value)


def test_git_ref_serialization() -> None:
    value = "feature/my-branch"
    m = RefModel(ref=value)
    json_str = m.model_dump_json()
    restored = RefModel.model_validate_json(json_str)
    assert restored.ref == m.ref


def test_git_ref_json_schema() -> None:
    schema = RefModel.model_json_schema()
    field = schema["properties"]["ref"]
    assert field["type"] == "string"
    assert field["title"] == "GitRef"
    assert field["minLength"] == 1


# ---------------------------------------------------------------------------
# GitSshUrl
# ---------------------------------------------------------------------------


def test_valid_git_ssh_url_scp_with_dotgit() -> None:
    url = GitSshUrl("git@github.com:torvalds/linux.git")
    assert url.host == "github.com"
    assert url.owner == "torvalds"
    assert url.repo == "linux"


def test_valid_git_ssh_url_scp_without_dotgit() -> None:
    url = GitSshUrl("git@github.com:torvalds/linux")
    assert url.host == "github.com"
    assert url.owner == "torvalds"
    assert url.repo == "linux"


def test_valid_git_ssh_url_ssh_scheme() -> None:
    url = GitSshUrl("ssh://git@github.com/torvalds/linux.git")
    assert url.host == "github.com"
    assert url.owner == "torvalds"
    assert url.repo == "linux"


def test_valid_git_ssh_url_ssh_scheme_with_port() -> None:
    url = GitSshUrl("ssh://git@github.com:22/torvalds/linux.git")
    assert url.host == "github.com"
    assert url.owner == "torvalds"
    assert url.repo == "linux"


def test_valid_git_ssh_url_gitlab_subgroups() -> None:
    url = GitSshUrl("git@gitlab.com:group/subgroup/repo.git")
    assert url.host == "gitlab.com"
    assert url.owner == "group/subgroup"
    assert url.repo == "repo"


def test_valid_git_ssh_url_bitbucket() -> None:
    url = GitSshUrl("git@bitbucket.org:team/project.git")
    assert url.host == "bitbucket.org"
    assert url.owner == "team"
    assert url.repo == "project"


def test_valid_git_ssh_url_custom_user() -> None:
    url = GitSshUrl("deploy@git.example.com:company/app.git")
    assert url.host == "git.example.com"
    assert url.owner == "company"
    assert url.repo == "app"


def test_git_ssh_url_pydantic_model() -> None:
    m = SshUrlModel(url="git@github.com:torvalds/linux.git")
    assert isinstance(m.url, GitSshUrl)
    assert m.url.repo == "linux"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "https://github.com/owner/repo.git",
        "git@github.com",
        "github.com:owner/repo.git",
    ],
)
def test_invalid_git_ssh_url(value: str) -> None:
    with pytest.raises(ValidationError):
        SshUrlModel(url=value)


def test_git_ssh_url_serialization() -> None:
    value = "git@github.com:torvalds/linux.git"
    m = SshUrlModel(url=value)
    json_str = m.model_dump_json()
    restored = SshUrlModel.model_validate_json(json_str)
    assert restored.url == m.url


def test_git_ssh_url_existing_instance() -> None:
    url = GitSshUrl("git@github.com:torvalds/linux.git")
    m = SshUrlModel(url=url)
    assert m.url is url


def test_git_ssh_url_json_schema() -> None:
    schema = SshUrlModel.model_json_schema()
    field = schema["properties"]["url"]
    assert field["type"] == "string"
    assert field["format"] == "git-ssh-url"
    assert field["title"] == "GitSshUrl"


# ---------------------------------------------------------------------------
# GitHttpsUrl
# ---------------------------------------------------------------------------


def test_valid_git_https_url_standard() -> None:
    url = GitHttpsUrl("https://github.com/torvalds/linux.git")
    assert url.host == "github.com"
    assert url.owner == "torvalds"
    assert url.repo == "linux"


def test_valid_git_https_url_without_dotgit() -> None:
    url = GitHttpsUrl("https://github.com/torvalds/linux")
    assert url.host == "github.com"
    assert url.owner == "torvalds"
    assert url.repo == "linux"


def test_valid_git_https_url_gitlab_subgroups() -> None:
    url = GitHttpsUrl("https://gitlab.com/group/subgroup/repo.git")
    assert url.host == "gitlab.com"
    assert url.owner == "group/subgroup"
    assert url.repo == "repo"


def test_valid_git_https_url_custom_port() -> None:
    url = GitHttpsUrl("https://git.example.com:8443/team/project.git")
    assert url.host == "git.example.com:8443"
    assert url.owner == "team"
    assert url.repo == "project"


def test_git_https_url_pydantic_model() -> None:
    m = HttpsUrlModel(url="https://github.com/torvalds/linux.git")
    assert isinstance(m.url, GitHttpsUrl)
    assert m.url.repo == "linux"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "http://github.com/owner/repo.git",
        "git@github.com:owner/repo.git",
        "https://github.com",
        "ftp://github.com/owner/repo.git",
    ],
)
def test_invalid_git_https_url(value: str) -> None:
    with pytest.raises(ValidationError):
        HttpsUrlModel(url=value)


def test_git_https_url_serialization() -> None:
    value = "https://github.com/torvalds/linux.git"
    m = HttpsUrlModel(url=value)
    json_str = m.model_dump_json()
    restored = HttpsUrlModel.model_validate_json(json_str)
    assert restored.url == m.url


def test_git_https_url_existing_instance() -> None:
    url = GitHttpsUrl("https://github.com/torvalds/linux.git")
    m = HttpsUrlModel(url=url)
    assert m.url is url


def test_git_https_url_json_schema() -> None:
    schema = HttpsUrlModel.model_json_schema()
    field = schema["properties"]["url"]
    assert field["type"] == "string"
    assert field["format"] == "git-https-url"
    assert field["title"] == "GitHttpsUrl"
