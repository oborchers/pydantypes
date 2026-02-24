# pydantypes

<p align="center">
<a href="https://github.com/oborchers/pydantypes/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/oborchers/pydantypes/ci.yml?branch=main&logo=github&label=CI"></a>
<a href="https://github.com/oborchers/pydantypes/blob/main/LICENSE"><img alt="license" src="https://img.shields.io/github/license/oborchers/pydantypes.svg"></a>
<a href="https://pepy.tech/project/pydantypes"><img alt="Downloads" src="https://pepy.tech/badge/pydantypes"></a>
<a href="https://docs.pydantic.dev"><img alt="Pydantic v2" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json"></a>
<a href="https://github.com/astral-sh/ruff"><img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
<img alt="types" src="https://img.shields.io/badge/types-100%2B-blue">
<img alt="tests" src="https://img.shields.io/badge/tests-1k%2B-brightgreen">
</p>

**The missing types for Pydantic** — cloud, DevOps, web, data, and AI engineering.

pydantypes provides validated, constrained Pydantic types for identifiers, ARNs, URIs, resource names, and classification labels that appear everywhere in modern infrastructure and AI code. Catch invalid values at parse time, not at deploy time.

## Installation

```bash
pip install pydantypes
# or
uv add pydantypes
```

## Quick Example

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

## Compatibility

pydantypes is designed as a complement to [pydantic-extra-types](https://github.com/pydantic/pydantic-extra-types). While pydantic-extra-types covers general-purpose types (colors, phone numbers, payment cards), pydantypes focuses on infrastructure and engineering identifiers.

For **IBAN and BIC** (banking identifiers), use [schwifty](https://github.com/mdomke/schwifty) which provides native Pydantic v2 support with `__get_pydantic_core_schema__`.

- Requires **Pydantic v2.5.2+**
- Supports **Python 3.10–3.13**

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for type patterns, conventions, and design decisions.

## Development

```bash
# Clone and set up
git clone https://github.com/oborchers/pydantypes.git
cd pydantypes
make init

# Run checks
make check        # lint + typecheck + test
make format       # auto-format code
make test-cov     # tests with coverage report
```

## License

MIT
