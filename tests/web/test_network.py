"""Tests for network types."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from pydantypes.web.network import Fqdn, PortRange

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class FqdnModel(BaseModel):
    domain: Fqdn


class PortModel(BaseModel):
    port: PortRange


# ---------------------------------------------------------------------------
# Fqdn
# ---------------------------------------------------------------------------


def test_valid_fqdn_simple() -> None:
    fqdn = Fqdn("www.example.com")
    assert fqdn.labels == ["www", "example", "com"]
    assert fqdn.tld == "com"


def test_valid_fqdn_api() -> None:
    fqdn = Fqdn("api.github.com")
    assert fqdn.labels == ["api", "github", "com"]
    assert fqdn.tld == "com"


def test_valid_fqdn_multi_label() -> None:
    fqdn = Fqdn("my-host.example.co.uk")
    assert fqdn.labels == ["my-host", "example", "co", "uk"]
    assert fqdn.tld == "uk"


def test_valid_fqdn_minimal() -> None:
    fqdn = Fqdn("a.b")
    assert fqdn.labels == ["a", "b"]
    assert fqdn.tld == "b"


def test_fqdn_normalizes_to_lowercase() -> None:
    fqdn = Fqdn("EXAMPLE.COM")
    assert str(fqdn) == "example.com"
    assert fqdn.labels == ["example", "com"]


def test_fqdn_strips_trailing_dot() -> None:
    fqdn = Fqdn("example.com.")
    assert str(fqdn) == "example.com"
    assert fqdn.labels == ["example", "com"]


def test_fqdn_numeric_label() -> None:
    fqdn = Fqdn("123.example.com")
    assert fqdn.labels == ["123", "example", "com"]


def test_fqdn_pydantic_model() -> None:
    m = FqdnModel(domain="www.example.com")
    assert isinstance(m.domain, Fqdn)
    assert m.domain.tld == "com"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "localhost",
        "-example.com",
        "example-.com",
        "exam ple.com",
        "example..com",
        "." * 3,
        "a." + "x" * 64 + ".com",
    ],
)
def test_invalid_fqdn(value: str) -> None:
    with pytest.raises(ValidationError):
        FqdnModel(domain=value)


def test_invalid_fqdn_too_long() -> None:
    # 254 chars total exceeds 253 limit
    long_domain = ("a" * 63 + ".") * 4 + "com"
    with pytest.raises(ValidationError):
        FqdnModel(domain=long_domain)


def test_fqdn_serialization() -> None:
    m = FqdnModel(domain="www.example.com")
    json_str = m.model_dump_json()
    restored = FqdnModel.model_validate_json(json_str)
    assert restored.domain == m.domain


def test_fqdn_existing_instance() -> None:
    fqdn = Fqdn("www.example.com")
    m = FqdnModel(domain=fqdn)
    assert m.domain is fqdn


def test_fqdn_json_schema() -> None:
    schema = FqdnModel.model_json_schema()
    field = schema["properties"]["domain"]
    assert field["type"] == "string"
    assert field["format"] == "fqdn"
    assert field["title"] == "Fqdn"
    assert field["maxLength"] == 253


# ---------------------------------------------------------------------------
# PortRange
# ---------------------------------------------------------------------------


def test_valid_port_range_single() -> None:
    pr = PortRange("443")
    assert pr.start == 443
    assert pr.end == 443


def test_valid_port_range_range() -> None:
    pr = PortRange("8080-8090")
    assert pr.start == 8080
    assert pr.end == 8090


def test_valid_port_range_zero() -> None:
    pr = PortRange("0")
    assert pr.start == 0
    assert pr.end == 0


def test_valid_port_range_max() -> None:
    pr = PortRange("65535")
    assert pr.start == 65535
    assert pr.end == 65535


def test_valid_port_range_full() -> None:
    pr = PortRange("0-65535")
    assert pr.start == 0
    assert pr.end == 65535


def test_valid_port_range_same_start_end() -> None:
    pr = PortRange("80-80")
    assert pr.start == 80
    assert pr.end == 80


def test_port_range_pydantic_model() -> None:
    m = PortModel(port="443")
    assert isinstance(m.port, PortRange)
    assert m.port.start == 443


@pytest.mark.parametrize(
    "value",
    [
        "",
        "65536",
        "8090-8080",
        "abc",
        "80-",
        "80-90-100",
        "0-65536",
    ],
)
def test_invalid_port_range(value: str) -> None:
    with pytest.raises(ValidationError):
        PortModel(port=value)


def test_port_range_serialization() -> None:
    m = PortModel(port="8080-8090")
    json_str = m.model_dump_json()
    restored = PortModel.model_validate_json(json_str)
    assert restored.port == m.port


def test_port_range_existing_instance() -> None:
    pr = PortRange("443")
    m = PortModel(port=pr)
    assert m.port is pr


def test_port_range_json_schema() -> None:
    schema = PortModel.model_json_schema()
    field = schema["properties"]["port"]
    assert field["type"] == "string"
    assert field["format"] == "port-range"
    assert field["title"] == "PortRange"
