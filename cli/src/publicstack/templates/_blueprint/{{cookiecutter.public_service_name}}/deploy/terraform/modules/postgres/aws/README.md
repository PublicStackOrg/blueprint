# `modules/postgres/aws/`

RDS Postgres 16 with the [PublicStack module contract](../README.md): same
outputs as every other `modules/postgres/<cloud>/`.

Defaults:

- `db.t4g.micro` (cheapest viable for PostgreSQL 16)
- 20 GB gp3 storage with autoscaling up to 100 GB
- Single-AZ (flip `multi_az = true` for prod)
- 7-day automated backups
- Encryption at rest (AWS-managed key)
- Private subnets only (no public IP)

## Inputs

| Variable | Required | Default | Notes |
|---|---|---|---|
| `name_prefix` | yes | — | usually `<ps>-<env>`, e.g. `parking-prod` |
| `vpc_id` | yes | — | |
| `private_subnet_ids` | yes | — | ≥2 subnets in different AZs if multi-AZ |
| `allowed_security_group_ids` | no | `[]` | typically the compute SG |
| `master_password` | yes | — | rotate via your secret manager; never commit |

## Outputs

| Output | Type |
|---|---|
| `connection_url` | string (sensitive); `postgresql+asyncpg://…` |
| `reader_url` | string (sensitive); same as connection_url for single-instance |
| `port` | number |
| `database_name` | string |
| `security_group_id` | string |
| `endpoint` | string |

## Cost (us-east-1, on-demand, May 2026)

- `db.t4g.micro` ≈ $13/mo
- 20 GB gp3 ≈ $2.30/mo
- 7-day backups ≈ free up to size of allocated storage

≈ **$15-16/mo** for a dev/staging deployment.

For prod, bump to `db.t4g.small` (≈ $26/mo) and `multi_az = true`
(doubles compute cost; dramatically reduces RPO).
