# `modules/postgres/gcp/` — STUB

Cloud SQL Postgres on GCP. Not implemented in blueprint v0.4.0.

## Contract

Same outputs as `modules/postgres/aws/`:

| Output | Type |
|---|---|
| `connection_url` | string (sensitive); `postgresql+asyncpg://...` |
| `reader_url` | string (sensitive) |
| `port` | number |
| `database_name` | string |
| `endpoint` | string |
| `security_group_id` | string (`""` on GCP — use `gcp_network_id` instead) |

## To implement

1. Create a Cloud SQL instance via `google_sql_database_instance`.
2. Create the database via `google_sql_database` and a user via
   `google_sql_user`.
3. Compose `connection_url` with `${user}:${password}@${private_ip}:5432/${db}`.
4. Surface the instance's authorized network or VPC peering ID via
   `security_group_id` shape parity (or rename to `network_id` and
   adjust the contract — your call).

PRs welcome.
