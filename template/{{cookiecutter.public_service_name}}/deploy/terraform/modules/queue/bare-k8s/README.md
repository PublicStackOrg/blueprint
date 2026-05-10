# `modules/queue/bare-k8s/`

Redis on Kubernetes via the Bitnami helm chart. Same outputs as
`modules/queue/aws/`. Architecture switches to `replication` when
`num_cache_clusters > 1`.

Inputs match the AWS variant's surface (vpc/subnet/security-group
fields are silently ignored for shape parity).
