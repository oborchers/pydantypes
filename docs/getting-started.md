# Getting Started

## Installation

<!-- termynal -->

```
$ pip install pydantypes
---> 100%
Successfully installed pydantypes
```

## Basic Usage

Import types from the domain that matches your use case:

```python
# Cloud providers
from pydantypes.cloud.aws import S3Uri, Arn, Region
from pydantypes.cloud.azure import BlobStorageUri, ResourceId, SubscriptionId
from pydantypes.cloud.gcp import GcsUri, ProjectId, ServiceAccountEmail

# DevOps tooling
from pydantypes.devops import DockerImageRef, GitCommitSha, K8sResourceName

# Web standards
from pydantypes.web import Jwt, MimeType, Host, Fqdn, BearerToken

# Data engineering
from pydantypes.data import TableIdentifier, SqlIdentifier, KafkaTopicName

# AI / ML labels
from pydantypes.ai import LabelEnum, Label
```

## Type Patterns

pydantypes uses four patterns depending on what the type needs to do.

### Pattern A: str Subclass (Parsed Properties)

Types that parse the validated string into structured components. Use these when you need
to extract parts of the value after validation.

```python
from pydantypes.cloud.aws import S3Uri

uri = S3Uri("s3://my-bucket/data/input.parquet")
uri.bucket  # "my-bucket"
uri.key     # "data/input.parquet"
uri.name    # "input.parquet"
uri.suffix  # ".parquet"
```

Other examples: `Arn`, `IamRoleArn`, `DockerImageRef`, `Jwt`, `MimeType`, `Host`, `Fqdn`, `Urn`,
`GcsUri`, `BlobStorageUri`, `ResourceId`, `GitSshUrl`, `GitHttpsUrl`.

### Pattern B: Annotated Type (Simple Validation)

Types that validate format without extracting components — accept or reject.

```python
from pydantypes.cloud.aws import Ec2InstanceId

# Valid — passes validation
instance_id: Ec2InstanceId = "i-1234567890abcdef0"

# Invalid — raises ValidationError
instance_id: Ec2InstanceId = "not-an-instance-id"
```

Other examples: `AccountId`, `S3BucketName`, `SecurityGroupId`, `VpcId`,
`K8sResourceName`, `K8sDnsLabel`, `Sha256Hex`, `SqlIdentifier`.

### Pattern C: StrEnum (Fixed Value Sets)

Enumerated sets of valid string values, such as cloud regions.

```python
from pydantypes.cloud.aws import Region

region = Region.US_EAST_1  # "us-east-1"
```

### Pattern D: LabelEnum (Classification Labels with Lifecycle)

Classification labels for AI/ML projects with built-in lifecycle management:
deprecation warnings, retirement enforcement, and alias resolution.

```python
from pydantypes.ai import LabelEnum, Label

class Sentiment(LabelEnum):
    POSITIVE = Label("positive", description="Expresses approval or satisfaction")
    NEGATIVE = Label("negative", description="Expresses disapproval or frustration")
    NEUTRAL  = Label("neutral",  description="No clear emotional signal")

    MIXED = Label(
        "mixed",
        deprecated=True,
        successor="NEUTRAL",
        description="Contradictory signals",
    )

Sentiment.active_labels()      # [POSITIVE, NEGATIVE, NEUTRAL]
Sentiment.deprecated_labels()  # [MIXED]
```

## Using with Pydantic Models

All types work as standard Pydantic field types:

```python
from pydantic import BaseModel
from pydantypes.cloud.aws import S3Uri, Region, AccountId
from pydantypes.devops import DockerImageRef

class DeploymentConfig(BaseModel):
    artifact: S3Uri
    image: DockerImageRef
    region: Region
    account: AccountId

config = DeploymentConfig(
    artifact="s3://deploy-bucket/releases/v1.2.3.tar.gz",
    image="ghcr.io/myorg/myapp:v1.2.3",
    region="us-east-1",
    account="123456789012",
)

# Parsed properties are available on validated fields
config.artifact.bucket  # "deploy-bucket"
config.artifact.key     # "releases/v1.2.3.tar.gz"
config.image.registry   # "ghcr.io"
config.image.tag        # "v1.2.3"
```

## JSON Schema

All types generate clean JSON Schema output. This makes them compatible with OpenAI
structured outputs, LangChain `with_structured_output`, and any framework that relies
on Pydantic's JSON Schema generation.

```python
from pydantic import BaseModel
from pydantypes.cloud.aws import S3Uri

class Config(BaseModel):
    source: S3Uri

print(Config.model_json_schema())
```

```json
{
  "properties": {
    "source": {
      "description": "An S3 URI in the format s3://bucket/key",
      "examples": ["s3://my-bucket/path/to/file.csv"],
      "format": "s3-uri",
      "pattern": "^s3://([a-z0-9][a-z0-9.\\-]{1,61}[a-z0-9])(/(.*))?$",
      "title": "S3Uri",
      "type": "string"
    }
  },
  "required": ["source"],
  "title": "Config",
  "type": "object"
}
```
