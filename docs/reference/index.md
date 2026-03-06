# API Reference

pydantypes provides validated types organized by domain. Each domain is a Python package
that you can import from directly.

| Domain | Module | Types | Description |
|--------|--------|------:|-------------|
| AWS | [`pydantypes.cloud.aws`](cloud/aws.md) | 33 | S3 URIs, IAM ARNs, EC2 IDs, Lambda, DynamoDB, VPC, ... |
| Azure | [`pydantypes.cloud.azure`](cloud/azure.md) | 23 | Blob Storage, Key Vault, Resource IDs, AKS, Cosmos DB, ... |
| GCP | [`pydantypes.cloud.gcp`](cloud/gcp.md) | 24 | GCS URIs, Project IDs, Cloud Run, Spanner, BigQuery, ... |
| DevOps | [`pydantypes.devops`](devops.md) | 13 | Docker, Helm, K8s, Terraform, Git |
| Web | [`pydantypes.web`](web.md) | 11 | JWT, MIME, hashes, FQDN, Bearer tokens, URNs |
| Data | [`pydantypes.data`](data.md) | 3 | SQL identifiers, Kafka topics |
| AI | [`pydantypes.ai`](ai.md) | 2 | LabelEnum, Label |
