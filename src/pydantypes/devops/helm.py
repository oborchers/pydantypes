"""Validated types for Helm chart references."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_HELM_CHART_NAME_RE = re.compile(r"^[a-z0-9][-a-z0-9]*$")


def _validate_helm_chart_name(v: str) -> str:
    """Validate a Helm chart name format."""
    if not _HELM_CHART_NAME_RE.match(v):
        raise PydanticCustomError(
            "helm_chart_name",
            "Invalid Helm chart name: {value}",
            {"value": v},
        )
    return v


# Source: https://helm.sh/docs/chart_best_practices/conventions/
HelmChartName = Annotated[
    str,
    AfterValidator(_validate_helm_chart_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": _HELM_CHART_NAME_RE.pattern,
            "description": "A valid Helm chart name.",
            "examples": ["nginx", "cert-manager"],
            "title": "HelmChartName",
        }
    ),
]
