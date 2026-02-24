"""Validated types for Kubernetes resource names and namespaces."""

from __future__ import annotations

import re
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, GetCoreSchemaHandler, GetJsonSchemaHandler, WithJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, PydanticCustomError

from pydantypes._internal import _str_type_core_schema

_K8S_NAMESPACE_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_K8S_RESOURCE_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]{0,251}[a-z0-9])?$")
_K8S_LABEL_VALUE_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]{0,61}[a-zA-Z0-9])?$")


def _validate_k8s_namespace_name(v: str) -> str:
    """Validate a Kubernetes namespace name format."""
    if not _K8S_NAMESPACE_RE.match(v):
        raise PydanticCustomError(
            "k8s_namespace_name",
            "Invalid Kubernetes namespace name: {value}",
            {"value": v},
        )
    return v


# Source: https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/
K8sNamespaceName = Annotated[
    str,
    AfterValidator(_validate_k8s_namespace_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _K8S_NAMESPACE_RE.pattern,
            "description": "A valid Kubernetes namespace name (RFC 1123 DNS label).",
            "examples": ["default", "kube-system"],
            "title": "K8sNamespaceName",
        }
    ),
]


def _validate_k8s_resource_name(v: str) -> str:
    """Validate a Kubernetes resource name format."""
    if not _K8S_RESOURCE_RE.match(v):
        raise PydanticCustomError(
            "k8s_resource_name",
            "Invalid Kubernetes resource name: {value}",
            {"value": v},
        )
    if ".." in v:
        raise PydanticCustomError(
            "k8s_resource_name",
            "Invalid Kubernetes resource name (consecutive dots): {value}",
            {"value": v},
        )
    return v


# Source: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#dns-subdomain-names
K8sResourceName = Annotated[
    str,
    AfterValidator(_validate_k8s_resource_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _K8S_RESOURCE_RE.pattern,
            "description": (
                "A valid Kubernetes resource name (RFC 1123 DNS subdomain, max 253 chars)."
            ),
            "examples": ["my-deployment", "nginx-pod"],
            "title": "K8sResourceName",
        }
    ),
]


# Source: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set
class K8sLabelKey(str):
    """A valid Kubernetes label key with optional prefix and name."""

    _pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?:(?P<prefix>[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?)/)"
        r"?(?P<name>[a-zA-Z0-9](?:[-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9])?)$"
    )

    prefix: str | None
    name: str

    def __new__(cls, value: str) -> K8sLabelKey:
        """Create and validate a new K8sLabelKey instance."""
        m = cls._pattern.match(value)
        if not m:
            raise PydanticCustomError(
                "k8s_label_key",
                "Invalid Kubernetes label key: {value}",
                {"value": value},
            )
        instance = str.__new__(cls, value)
        instance.prefix = m.group("prefix")
        instance.name = m.group("name")
        return instance

    @classmethod
    def _validate(cls, value: str) -> K8sLabelKey:
        """Validate a string as a Kubernetes label key."""
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Return the Pydantic core schema for K8sLabelKey."""
        return _str_type_core_schema(cls, source_type, handler)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return the JSON schema for K8sLabelKey."""
        return {
            "type": "string",
            "format": "k8s-label-key",
            "pattern": cls._pattern.pattern,
            "description": "A valid Kubernetes label key with optional prefix and name.",
            "examples": ["app.kubernetes.io/name", "version", "my-label"],
            "title": "K8sLabelKey",
        }


def _validate_k8s_label_value(v: str) -> str:
    """Validate a Kubernetes label value format."""
    if v == "":
        return v
    if not _K8S_LABEL_VALUE_RE.match(v):
        raise PydanticCustomError(
            "k8s_label_value",
            "Invalid Kubernetes label value: {value}",
            {"value": v},
        )
    return v


# Source: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set
K8sLabelValue = Annotated[
    str,
    AfterValidator(_validate_k8s_label_value),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _K8S_LABEL_VALUE_RE.pattern,
            "description": "A valid Kubernetes label value (max 63 chars, empty allowed).",
            "examples": ["v1.0", "production", ""],
            "title": "K8sLabelValue",
        }
    ),
]
