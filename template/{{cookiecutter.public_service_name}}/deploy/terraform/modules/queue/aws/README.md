# `modules/queue/aws/`

ElastiCache Redis cluster — keeps the template's RQ-on-Redis adapter
working without code changes. Set `REDIS_URL=$(terraform output -raw
redis_url)` on the api + worker services and the existing Grid
queue adapter just works.

For a future SQS-backed adapter, swap to a `modules/queue/aws-sqs/`
variant (not in v0.4.0). The `queue_url` output exists for parity
with that future SQS contract.

Defaults:

- `cache.t4g.micro` — cheapest viable
- Single node (no replica) — flip `num_cache_clusters = 2` for prod to
  enable auto-failover + multi-AZ
- Encryption at rest (AWS-managed key)
- Transit encryption off by default; turn on for prod with an `auth_token`

## Inputs

| Variable | Required | Default |
|---|---|---|
| `name_prefix` | yes | — |
| `vpc_id` | yes | — |
| `private_subnet_ids` | yes | — |
| `node_type` | no | `cache.t4g.micro` |
| `num_cache_clusters` | no | 1 |
| `transit_encryption_enabled` | no | false |
| `auth_token` | conditional | — required when transit encryption is on |

## Outputs

| Output | Type |
|---|---|
| `redis_url` | string (sensitive) |
| `queue_url` | string (sensitive); alias for redis_url |
| `endpoint` | string |
| `security_group_id` | string |

## Cost

`cache.t4g.micro` ≈ $13/mo on-demand. Cluster mode (2+ nodes) doubles
that. Most small-city PSes run on one node.
