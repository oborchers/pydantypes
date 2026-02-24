"""Tests for Kubernetes resource types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticCustomError

from pydantypes.devops.k8s import (
    K8sLabelKey,
    K8sLabelValue,
    K8sNamespaceName,
    K8sResourceName,
)


class NsModel(BaseModel):
    ns: K8sNamespaceName


class ResModel(BaseModel):
    name: K8sResourceName


class LabelKeyModel(BaseModel):
    key: K8sLabelKey


class LabelValueModel(BaseModel):
    val: K8sLabelValue


@pytest.mark.parametrize("value", ["default", "kube-system", "a", "a" * 63])
def test_valid_k8s_namespace_name(value: str) -> None:
    m = NsModel(ns=value)
    assert m.ns == value


@pytest.mark.parametrize("value", ["", "-starts", "ends-", "UPPER", "a" * 64])
def test_invalid_k8s_namespace_name(value: str) -> None:
    with pytest.raises(ValidationError):
        NsModel(ns=value)


@pytest.mark.parametrize("value", ["my-deployment", "a", "sub.domain.name"])
def test_valid_k8s_resource_name(value: str) -> None:
    m = ResModel(name=value)
    assert m.name == value


@pytest.mark.parametrize("value", ["", "-starts", "a" * 254, "has..dots"])
def test_invalid_k8s_resource_name(value: str) -> None:
    with pytest.raises(ValidationError):
        ResModel(name=value)


def test_valid_k8s_label_key_simple_name() -> None:
    k = K8sLabelKey("app")
    assert k.prefix is None
    assert k.name == "app"


def test_valid_k8s_label_key_version() -> None:
    k = K8sLabelKey("version")
    assert k.prefix is None
    assert k.name == "version"


def test_valid_k8s_label_key_prefixed() -> None:
    k = K8sLabelKey("app.kubernetes.io/name")
    assert k.prefix == "app.kubernetes.io"
    assert k.name == "name"


def test_valid_k8s_label_key_with_dash() -> None:
    k = K8sLabelKey("my-label")
    assert k.prefix is None
    assert k.name == "my-label"


def test_k8s_label_key_pydantic_model() -> None:
    m = LabelKeyModel(key="version")
    assert isinstance(m.key, K8sLabelKey)


@pytest.mark.parametrize("value", ["", "/name", "a" * 64])
def test_invalid_k8s_label_key(value: str) -> None:
    with pytest.raises(PydanticCustomError):
        K8sLabelKey(value)


@pytest.mark.parametrize("value", ["v1.0", "production", "", "a", "a" * 63])
def test_valid_k8s_label_value(value: str) -> None:
    m = LabelValueModel(val=value)
    assert m.val == value


@pytest.mark.parametrize("value", ["-starts", "ends-", "a" * 64, "has spaces"])
def test_invalid_k8s_label_value(value: str) -> None:
    with pytest.raises(ValidationError):
        LabelValueModel(val=value)
