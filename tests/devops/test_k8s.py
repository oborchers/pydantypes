"""Tests for Kubernetes resource types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticCustomError

from pydantypes.devops.k8s import (
    K8sDnsLabel,
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


class DnsLabelModel(BaseModel):
    label: K8sDnsLabel


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


# ---------------------------------------------------------------------------
# K8sDnsLabel (RFC 1035)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["nginx", "my-container", "a", "a" + "b" * 62])
def test_valid_k8s_dns_label(value: str) -> None:
    m = DnsLabelModel(label=value)
    assert m.label == value


@pytest.mark.parametrize("value", ["1starts-with-digit", "-starts", "UPPER", "", "a" * 64])
def test_invalid_k8s_dns_label(value: str) -> None:
    with pytest.raises(ValidationError):
        DnsLabelModel(label=value)


# ---------------------------------------------------------------------------
# Serialization / JSON schema
# ---------------------------------------------------------------------------


def test_k8s_namespace_serialization() -> None:
    m = NsModel(ns="default")
    json_str = m.model_dump_json()
    restored = NsModel.model_validate_json(json_str)
    assert restored.ns == m.ns


def test_k8s_namespace_json_schema() -> None:
    schema = NsModel.model_json_schema()
    field = schema["properties"]["ns"]
    assert field["type"] == "string"
    assert field["title"] == "K8sNamespaceName"


def test_k8s_resource_serialization() -> None:
    m = ResModel(name="my-deployment")
    json_str = m.model_dump_json()
    restored = ResModel.model_validate_json(json_str)
    assert restored.name == m.name


def test_k8s_resource_json_schema() -> None:
    schema = ResModel.model_json_schema()
    field = schema["properties"]["name"]
    assert field["type"] == "string"
    assert field["title"] == "K8sResourceName"


def test_k8s_label_key_serialization() -> None:
    m = LabelKeyModel(key="version")
    json_str = m.model_dump_json()
    restored = LabelKeyModel.model_validate_json(json_str)
    assert restored.key == m.key


def test_k8s_label_key_json_schema() -> None:
    schema = LabelKeyModel.model_json_schema()
    field = schema["properties"]["key"]
    assert field["type"] == "string"
    assert field["title"] == "K8sLabelKey"


def test_k8s_label_value_serialization() -> None:
    m = LabelValueModel(val="v1.0")
    json_str = m.model_dump_json()
    restored = LabelValueModel.model_validate_json(json_str)
    assert restored.val == m.val


def test_k8s_label_value_json_schema() -> None:
    schema = LabelValueModel.model_json_schema()
    field = schema["properties"]["val"]
    assert field["type"] == "string"
    assert field["title"] == "K8sLabelValue"


def test_k8s_dns_label_serialization() -> None:
    m = DnsLabelModel(label="nginx")
    json_str = m.model_dump_json()
    restored = DnsLabelModel.model_validate_json(json_str)
    assert restored.label == m.label


def test_k8s_dns_label_json_schema() -> None:
    schema = DnsLabelModel.model_json_schema()
    field = schema["properties"]["label"]
    assert field["type"] == "string"
    assert field["title"] == "K8sDnsLabel"
