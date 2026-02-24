"""Tests for Docker image reference types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticCustomError

from pydantypes.devops.docker import DockerImageRef

_DIGEST = "abcdef1234567890" * 4


class ImageModel(BaseModel):
    ref: DockerImageRef


def test_valid_docker_image_ref_simple() -> None:
    ref = DockerImageRef("nginx")
    assert ref.registry is None
    assert ref.repository == "nginx"
    assert ref.tag is None
    assert ref.digest is None


def test_valid_docker_image_ref_with_tag() -> None:
    ref = DockerImageRef("nginx:latest")
    assert ref.registry is None
    assert ref.repository == "nginx"
    assert ref.tag == "latest"
    assert ref.digest is None


def test_valid_docker_image_ref_library_with_tag() -> None:
    ref = DockerImageRef("library/nginx:1.21")
    assert ref.registry is None
    assert ref.repository == "library/nginx"
    assert ref.tag == "1.21"


def test_valid_docker_image_ref_registry() -> None:
    ref = DockerImageRef("ghcr.io/owner/repo:v1.0")
    assert ref.registry == "ghcr.io"
    assert ref.repository == "owner/repo"
    assert ref.tag == "v1.0"
    assert ref.digest is None


def test_valid_docker_image_ref_registry_with_port() -> None:
    ref = DockerImageRef("registry.example.com:5000/my-app:latest")
    assert ref.registry == "registry.example.com:5000"
    assert ref.repository == "my-app"
    assert ref.tag == "latest"


def test_valid_docker_image_ref_digest_only() -> None:
    ref = DockerImageRef("my-app@sha256:" + _DIGEST)
    assert ref.registry is None
    assert ref.repository == "my-app"
    assert ref.tag is None
    assert ref.digest == "sha256:" + _DIGEST


def test_valid_docker_image_ref_tag_and_digest() -> None:
    ref = DockerImageRef("nginx:latest@sha256:" + _DIGEST)
    assert ref.tag == "latest"
    assert ref.digest == "sha256:" + _DIGEST


def test_docker_image_ref_pydantic_model() -> None:
    m = ImageModel(ref="nginx:latest")
    assert isinstance(m.ref, DockerImageRef)
    assert m.ref.tag == "latest"


def test_invalid_docker_image_ref_empty() -> None:
    with pytest.raises(PydanticCustomError):
        DockerImageRef("")


def test_invalid_docker_image_ref_uppercase_repo() -> None:
    with pytest.raises(PydanticCustomError):
        DockerImageRef("UPPERCASE:latest")


def test_invalid_docker_image_ref_no_repo_tag_only() -> None:
    with pytest.raises(PydanticCustomError):
        DockerImageRef(":tag")


def test_invalid_docker_image_ref_no_repo_digest_only() -> None:
    with pytest.raises(PydanticCustomError):
        DockerImageRef("@sha256:abc")


def test_invalid_docker_image_ref_pydantic_model() -> None:
    with pytest.raises(ValidationError):
        ImageModel(ref="")
