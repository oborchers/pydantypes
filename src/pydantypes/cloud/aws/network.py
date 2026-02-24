"""AWS network types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_VPC_ID_RE = re.compile(r"^vpc-[0-9a-f]{8,17}$")
_SUBNET_ID_RE = re.compile(r"^subnet-[0-9a-f]{8,17}$")
_SECURITY_GROUP_ID_RE = re.compile(r"^sg-[0-9a-f]{8,17}$")
_NAT_GATEWAY_ID_RE = re.compile(r"^nat-[0-9a-f]{8,17}$")
_INTERNET_GATEWAY_ID_RE = re.compile(r"^igw-[0-9a-f]{8,17}$")
_ELASTIC_IP_ALLOCATION_ID_RE = re.compile(r"^eipalloc-[0-9a-f]{8,17}$")
_ENI_ID_RE = re.compile(r"^eni-[0-9a-f]{8,17}$")
_CLOUDFRONT_DISTRIBUTION_ID_RE = re.compile(r"^E[A-Z0-9]{10,16}$")
_ROUTE53_HOSTED_ZONE_ID_RE = re.compile(r"^Z[A-Z0-9]{1,31}$")


def _validate_vpc_id(v: str) -> str:
    """Validate a VPC ID format."""
    if not _VPC_ID_RE.match(v):
        raise PydanticCustomError("vpc_id", "Invalid VPC ID: {value}", {"value": v})
    return v


def _validate_subnet_id(v: str) -> str:
    """Validate a Subnet ID format."""
    if not _SUBNET_ID_RE.match(v):
        raise PydanticCustomError("subnet_id", "Invalid Subnet ID: {value}", {"value": v})
    return v


def _validate_security_group_id(v: str) -> str:
    """Validate a Security Group ID format."""
    if not _SECURITY_GROUP_ID_RE.match(v):
        raise PydanticCustomError(
            "security_group_id", "Invalid Security Group ID: {value}", {"value": v}
        )
    return v


def _validate_nat_gateway_id(v: str) -> str:
    """Validate a NAT Gateway ID format."""
    if not _NAT_GATEWAY_ID_RE.match(v):
        raise PydanticCustomError("nat_gateway_id", "Invalid NAT Gateway ID: {value}", {"value": v})
    return v


def _validate_internet_gateway_id(v: str) -> str:
    """Validate an Internet Gateway ID format."""
    if not _INTERNET_GATEWAY_ID_RE.match(v):
        raise PydanticCustomError(
            "internet_gateway_id", "Invalid Internet Gateway ID: {value}", {"value": v}
        )
    return v


def _validate_elastic_ip_allocation_id(v: str) -> str:
    """Validate an Elastic IP allocation ID format."""
    if not _ELASTIC_IP_ALLOCATION_ID_RE.match(v):
        raise PydanticCustomError(
            "elastic_ip_allocation_id",
            "Invalid Elastic IP Allocation ID: {value}",
            {"value": v},
        )
    return v


def _validate_eni_id(v: str) -> str:
    """Validate an ENI ID format."""
    if not _ENI_ID_RE.match(v):
        raise PydanticCustomError("eni_id", "Invalid ENI ID: {value}", {"value": v})
    return v


def _validate_cloudfront_distribution_id(v: str) -> str:
    """Validate a CloudFront distribution ID format."""
    if not _CLOUDFRONT_DISTRIBUTION_ID_RE.match(v):
        raise PydanticCustomError(
            "cloudfront_distribution_id",
            "Invalid CloudFront Distribution ID: {value}",
            {"value": v},
        )
    return v


def _validate_route53_hosted_zone_id(v: str) -> str:
    """Validate a Route53 hosted zone ID format."""
    if not _ROUTE53_HOSTED_ZONE_ID_RE.match(v):
        raise PydanticCustomError(
            "route53_hosted_zone_id",
            "Invalid Route53 Hosted Zone ID: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
VpcId = Annotated[
    str,
    AfterValidator(_validate_vpc_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^vpc-[0-9a-f]{8,17}$",
            "description": "An AWS VPC ID",
            "examples": ["vpc-1234567890abcdef0"],
            "title": "VpcId",
        }
    ),
]
"""An AWS VPC ID (e.g. `vpc-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
SubnetId = Annotated[
    str,
    AfterValidator(_validate_subnet_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^subnet-[0-9a-f]{8,17}$",
            "description": "An AWS Subnet ID",
            "examples": ["subnet-1234567890abcdef0"],
            "title": "SubnetId",
        }
    ),
]
"""An AWS Subnet ID (e.g. `subnet-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
SecurityGroupId = Annotated[
    str,
    AfterValidator(_validate_security_group_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^sg-[0-9a-f]{8,17}$",
            "description": "An AWS Security Group ID",
            "examples": ["sg-1234567890abcdef0"],
            "title": "SecurityGroupId",
        }
    ),
]
"""An AWS Security Group ID (e.g. `sg-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
NatGatewayId = Annotated[
    str,
    AfterValidator(_validate_nat_gateway_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^nat-[0-9a-f]{8,17}$",
            "description": "An AWS NAT Gateway ID",
            "examples": ["nat-1234567890abcdef0"],
            "title": "NatGatewayId",
        }
    ),
]
"""An AWS NAT Gateway ID (e.g. `nat-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
InternetGatewayId = Annotated[
    str,
    AfterValidator(_validate_internet_gateway_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^igw-[0-9a-f]{8,17}$",
            "description": "An AWS Internet Gateway ID",
            "examples": ["igw-1234567890abcdef0"],
            "title": "InternetGatewayId",
        }
    ),
]
"""An AWS Internet Gateway ID (e.g. `igw-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
ElasticIpAllocationId = Annotated[
    str,
    AfterValidator(_validate_elastic_ip_allocation_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^eipalloc-[0-9a-f]{8,17}$",
            "description": "An AWS Elastic IP Allocation ID",
            "examples": ["eipalloc-1234567890abcdef0"],
            "title": "ElasticIpAllocationId",
        }
    ),
]
"""An AWS Elastic IP Allocation ID (e.g. `eipalloc-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
EniId = Annotated[
    str,
    AfterValidator(_validate_eni_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^eni-[0-9a-f]{8,17}$",
            "description": "An AWS ENI (Elastic Network Interface) ID",
            "examples": ["eni-1234567890abcdef0"],
            "title": "EniId",
        }
    ),
]
"""An AWS ENI (Elastic Network Interface) ID (e.g. `eni-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_Distribution.html
CloudFrontDistributionId = Annotated[
    str,
    AfterValidator(_validate_cloudfront_distribution_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^E[A-Z0-9]{10,16}$",
            "description": "An AWS CloudFront Distribution ID",
            "examples": ["E1A2B3C4D5E6F7"],
            "title": "CloudFrontDistributionId",
        }
    ),
]
"""An AWS CloudFront Distribution ID (e.g. `E1A2B3C4D5E6F7`)."""

# Source: https://docs.aws.amazon.com/Route53/latest/APIReference/API_HostedZone.html
Route53HostedZoneId = Annotated[
    str,
    AfterValidator(_validate_route53_hosted_zone_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^Z[A-Z0-9]{1,31}$",
            "description": "An AWS Route53 Hosted Zone ID",
            "examples": ["Z1234567890ABC"],
            "title": "Route53HostedZoneId",
        }
    ),
]
"""An AWS Route53 Hosted Zone ID (e.g. `Z1234567890ABC`)."""
