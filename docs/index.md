# pydantypes

**The missing types for Pydantic** — cloud, DevOps, web, data, and AI engineering.

pydantypes provides validated, constrained Pydantic types for identifiers, ARNs, URIs,
resource names, and classification labels that appear everywhere in modern infrastructure
and AI code. Catch invalid values at parse time, not at deploy time.

## Installation

<!-- termynal -->

```
$ pip install pydantypes
---> 100%
Successfully installed pydantypes
```

## Quick Examples

Every type validates **and** parses — you get structured properties, not just accept/reject.

```python
from pydantic import BaseModel
from pydantypes.cloud.aws import S3Uri, IamRoleArn

class PipelineConfig(BaseModel):
    source: S3Uri
    execution_role: IamRoleArn

config = PipelineConfig(
    source="s3://my-bucket/data/input.parquet",
    execution_role="arn:aws:iam::123456789012:role/pipeline-role",
)
config.source.bucket             # "my-bucket"
config.source.key                # "data/input.parquet"
config.execution_role.role_name  # "pipeline-role"
```

## Domains

| Domain | Package | What You Get |
|--------|---------|--------------|
| **AWS** | `pydantypes.cloud.aws` | S3 URIs, IAM ARNs, Lambda names, EC2/ECS/EKS IDs, account IDs, regions |
| **Azure** | `pydantypes.cloud.azure` | Blob Storage URIs, resource IDs, Key Vault names, subscription IDs |
| **GCP** | `pydantypes.cloud.gcp` | GCS URIs, project IDs, service account emails, Cloud Run services |
| **DevOps** | `pydantypes.devops` | Docker image refs, Git SHAs/refs/URLs, K8s names/labels, Helm charts, Terraform addresses |
| **Web** | `pydantypes.web` | Hosts, URNs, slugs, JWTs, MIME types, FQDNs, port ranges, Bearer tokens, hashes |
| **Data** | `pydantypes.data` | SQL identifiers, Kafka topics, connection strings, column names |
| **AI** | `pydantypes.ai` | Classification labels with lifecycle, deprecation, alias resolution |

## Types You Won't Find Anywhere Else

### Parse cloud resources into structured components

```python
from pydantypes.cloud.aws import Arn
from pydantypes.cloud.azure import ResourceId

arn = Arn("arn:aws:iam::123456789012:role/pipeline-role")
arn.service      # "iam"
arn.account_id   # "123456789012"
arn.resource     # "role/pipeline-role"

rid = ResourceId(
    "/subscriptions/12345678-1234-1234-1234-123456789012"
    "/resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines/myVM"
)
rid.subscription_id     # "12345678-1234-1234-1234-123456789012"
rid.resource_group      # "myRG"
rid.provider_namespace  # "Microsoft.Compute"
rid.resource_type       # "virtualMachines"
rid.resource_name       # "myVM"
```

### Decompose Docker refs and Git URLs

```python
from pydantypes.devops import DockerImageRef, GitSshUrl

img = DockerImageRef("ghcr.io/owner/app:v2.1@sha256:abcdef1234567890")
img.registry    # "ghcr.io"
img.repository  # "owner/app"
img.tag         # "v2.1"
img.digest      # "sha256:abcdef1234567890"

url = GitSshUrl("git@github.com:torvalds/linux.git")
url.host   # "github.com"
url.owner  # "torvalds"
url.repo   # "linux"
```

### Validate web identifiers with RFC-compliant parsing

```python
from pydantypes.web import Host, Urn, Jwt, MimeType

host = Host("[2001:db8::1]")
host.host_type  # "ipv6"

host = Host("api.example.com")
host.host_type  # "domain"

urn = Urn("urn:isbn:0451450523")
urn.nid  # "isbn"
urn.nss  # "0451450523"

jwt = Jwt("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NSJ9.signature")
jwt.header   # {"alg": "HS256"}
jwt.payload  # {"sub": "12345"}

mime = MimeType("application/json;charset=utf-8")
mime.type        # "application"
mime.subtype     # "json"
mime.parameters  # {"charset": "utf-8"}
```

### Manage classification label lifecycles

Nothing like this exists in the Pydantic ecosystem. `LabelEnum` gives you **typed classification labels** for LLM and ML projects — with descriptions, deprecation warnings, retirement enforcement, and alias resolution built in. Compatible with OpenAI structured outputs, LangChain `with_structured_output`, and all Pydantic-based LLM frameworks.

```python
from pydantic import BaseModel
from pydantypes.ai import LabelEnum, Label

class Sentiment(LabelEnum):
    POSITIVE = Label("positive", description="Expresses approval or satisfaction")
    NEGATIVE = Label("negative", description="Expresses disapproval or frustration")
    NEUTRAL  = Label("neutral",  description="No clear emotional signal")

    # Taxonomy evolves — deprecate old labels without breaking existing data
    MIXED = Label(
        "mixed",
        deprecated=True,
        successor="NEUTRAL",
        description="Contradictory signals",
    )

    # Retired labels are rejected outright, but aliases still resolve
    AMBIGUOUS = Label(
        "ambiguous",
        retired=True,
        successor="NEUTRAL",
        aliases=["unclear", "unknown"],
    )

class Result(BaseModel):
    sentiment: Sentiment

# Active labels work normally
result = Result(sentiment="positive")
result.sentiment.description  # "Expresses approval or satisfaction"

# Deprecated labels still parse but emit a DeprecationWarning
result = Result(sentiment="mixed")  # warns: "Label 'mixed' is deprecated. Use 'NEUTRAL' instead."

# Retired labels are rejected — forces migration
Result(sentiment="ambiguous")  # -> ValidationError

# Aliases silently resolve to their target
result = Result(sentiment="unclear")  # resolves to AMBIGUOUS's alias -> handled
```

In any classification project, your label taxonomy *will* change. Labels get merged, split, renamed. Without lifecycle management you end up with dead labels in your schema, silent data quality regressions, and no migration path. `LabelEnum` makes taxonomy evolution a first-class concern.

```python
# Introspect your taxonomy programmatically
Sentiment.active_labels()      # [POSITIVE, NEGATIVE, NEUTRAL]
Sentiment.deprecated_labels()  # [MIXED]
Sentiment.retired_labels()     # [AMBIGUOUS]
Sentiment.schema_values()      # ["positive", "negative", "neutral", "mixed"] (excludes retired)
Sentiment.alias_map()          # {"unclear": AMBIGUOUS, "unknown": AMBIGUOUS}
```

## Real-World Examples

### Cloud config with Pydantic Settings

```python
from pydantic_settings import BaseSettings
from pydantypes.cloud.aws import S3BucketName, Region, AccountId

class AppConfig(BaseSettings):
    model_config = {"env_prefix": "APP_"}

    data_bucket: S3BucketName
    region: Region
    account_id: AccountId

# Reads from APP_DATA_BUCKET, APP_REGION, APP_ACCOUNT_ID
config = AppConfig()
```

### FastAPI route with validated slugs

```python
from fastapi import FastAPI
from pydantypes.web import Slug

app = FastAPI()

@app.get("/articles/{slug}")
async def get_article(slug: Slug):
    # slug is guaranteed to match [a-z0-9]+(-[a-z0-9]+)*
    return {"slug": slug}
```

### Kubernetes manifest builder

```python
from pydantic import BaseModel
from pydantypes.devops import DockerImageRef, K8sNamespaceName, K8sLabelValue

class K8sDeployment(BaseModel):
    namespace: K8sNamespaceName
    image: DockerImageRef
    app_label: K8sLabelValue

deploy = K8sDeployment(
    namespace="production",
    image="ghcr.io/myorg/api:v2.1.0",
    app_label="my-api",
)
deploy.image.registry  # "ghcr.io"
deploy.image.tag       # "v2.1.0"
```

### Data pipeline validation

```python
from pydantic import BaseModel
from pydantypes.cloud.gcp import ProjectId, BigQueryDatasetId
from pydantypes.data import KafkaTopicName

class PipelineStep(BaseModel):
    source_topic: KafkaTopicName
    dest_project: ProjectId
    dest_dataset: BigQueryDatasetId

step = PipelineStep(
    source_topic="events.user-signups",
    dest_project="analytics-prod-123",
    dest_dataset="raw_events",
)
```

### Secure API client config

```python
from pydantic import BaseModel, SecretStr
from pydantypes.web import Fqdn, BearerToken
from pydantypes.cloud.aws import Arn

class ApiClientConfig(BaseModel):
    endpoint: Fqdn
    auth_token: BearerToken
    role_arn: Arn

config = ApiClientConfig(
    endpoint="api.example.com",
    auth_token="Bearer eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhcGkifQ.sig",
    role_arn="arn:aws:iam::123456789012:role/api-consumer",
)
config.auth_token.token  # "eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhcGkifQ.sig"
config.role_arn.service   # "iam"
```

## Compatibility

pydantypes is designed as a complement to [pydantic-extra-types](https://github.com/pydantic/pydantic-extra-types).
While pydantic-extra-types covers general-purpose types (colors, phone numbers, payment cards),
pydantypes focuses on infrastructure and engineering identifiers.

- Requires **Pydantic v2.5+**
- Supports **Python 3.10--3.13**

## Next Steps

- [Getting Started](getting-started.md) — installation and basic usage
- [API Reference](reference/index.md) — full type documentation by domain
