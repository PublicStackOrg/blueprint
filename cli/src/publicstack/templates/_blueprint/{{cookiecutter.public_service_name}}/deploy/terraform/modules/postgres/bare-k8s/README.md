# `modules/postgres/bare-k8s/`

Postgres on a generic Kubernetes cluster via the Bitnami `postgresql`
Helm chart. Same outputs as `modules/postgres/aws/`.

Required: `name_prefix`. Optional: `namespace`, `master_password` (auto-
generated if null), `storage_gb`, `chart_version`, `database_name`,
`master_username`.

Outputs `connection_url` formatted as
`postgresql+asyncpg://<u>:<p>@<release>-postgresql.<ns>.svc.cluster.local:5432/<db>`.

For prod-grade Postgres on K8s prefer cloudnative-pg (HA + automated
backups). Swap by creating a parallel module `bare-k8s-cnpg/` and
flipping `var.cloud` semantics.
