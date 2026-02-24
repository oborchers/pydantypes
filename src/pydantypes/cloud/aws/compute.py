"""AWS compute types."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, WithJsonSchema
from pydantic_core import PydanticCustomError

_EC2_INSTANCE_ID_RE = re.compile(r"^i-[0-9a-f]{8,17}$")
_LAMBDA_FUNCTION_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]{1,64}$")
_AMI_ID_RE = re.compile(r"^ami-[0-9a-f]{8,17}$")
_ECS_CLUSTER_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,255}$")
_EKS_CLUSTER_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}$")


def _validate_ec2_instance_id(v: str) -> str:
    """Validate an EC2 instance ID format."""
    if not _EC2_INSTANCE_ID_RE.match(v):
        raise PydanticCustomError(
            "ec2_instance_id",
            "Invalid EC2 Instance ID: {value}",
            {"value": v},
        )
    return v


def _validate_lambda_function_name(v: str) -> str:
    """Validate a Lambda function name format."""
    if not _LAMBDA_FUNCTION_NAME_RE.match(v):
        raise PydanticCustomError(
            "lambda_function_name",
            "Invalid Lambda function name: {value}",
            {"value": v},
        )
    return v


def _validate_ami_id(v: str) -> str:
    """Validate an AMI ID format."""
    if not _AMI_ID_RE.match(v):
        raise PydanticCustomError(
            "ami_id",
            "Invalid AMI ID: {value}",
            {"value": v},
        )
    return v


def _validate_ecs_cluster_name(v: str) -> str:
    """Validate an ECS cluster name format."""
    if not _ECS_CLUSTER_NAME_RE.match(v):
        raise PydanticCustomError(
            "ecs_cluster_name",
            "Invalid ECS cluster name: {value}",
            {"value": v},
        )
    return v


def _validate_eks_cluster_name(v: str) -> str:
    """Validate an EKS cluster name format."""
    if not _EKS_CLUSTER_NAME_RE.match(v):
        raise PydanticCustomError(
            "eks_cluster_name",
            "Invalid EKS cluster name: {value}",
            {"value": v},
        )
    return v


# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
Ec2InstanceId = Annotated[
    str,
    AfterValidator(_validate_ec2_instance_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^i-[0-9a-f]{8,17}$",
            "description": "An AWS EC2 instance ID",
            "examples": ["i-1234567890abcdef0"],
            "title": "Ec2InstanceId",
        }
    ),
]
"""An AWS EC2 instance ID (e.g. `i-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/lambda/latest/api/API_CreateFunction.html
LambdaFunctionName = Annotated[
    str,
    AfterValidator(_validate_lambda_function_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9._-]{1,64}$",
            "description": "An AWS Lambda function name",
            "examples": ["my-function"],
            "title": "LambdaFunctionName",
            "maxLength": 64,
        }
    ),
]
"""An AWS Lambda function name (e.g. `my-function`)."""

# Source: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resource-ids.html
AmiId = Annotated[
    str,
    AfterValidator(_validate_ami_id),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^ami-[0-9a-f]{8,17}$",
            "description": "An AWS AMI ID",
            "examples": ["ami-1234567890abcdef0"],
            "title": "AmiId",
        }
    ),
]
"""An AWS AMI ID (e.g. `ami-1234567890abcdef0`)."""

# Source: https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_CreateCluster.html
EcsClusterName = Annotated[
    str,
    AfterValidator(_validate_ecs_cluster_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9_-]{1,255}$",
            "description": "An AWS ECS cluster name",
            "examples": ["my-ecs-cluster"],
            "title": "EcsClusterName",
            "maxLength": 255,
        }
    ),
]
"""An AWS ECS cluster name (e.g. `my-ecs-cluster`)."""

# Source: https://docs.aws.amazon.com/eks/latest/APIReference/API_CreateCluster.html
EksClusterName = Annotated[
    str,
    AfterValidator(_validate_eks_cluster_name),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}$",
            "description": "An AWS EKS cluster name",
            "examples": ["my-eks-cluster"],
            "title": "EksClusterName",
            "maxLength": 100,
        }
    ),
]
"""An AWS EKS cluster name (e.g. `my-eks-cluster`)."""
