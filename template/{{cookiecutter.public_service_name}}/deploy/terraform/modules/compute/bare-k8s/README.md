# `modules/compute/bare-k8s/`

Wraps the PublicStack Helm chart at `deploy/k8s/` via the Terraform
helm provider. Same outputs as `modules/compute/aws/` (with shape-only
fields zeroed where they don't apply: task_role_arn, alb_*, cluster_
name, migrator_task_definition_arn).

Postgres and Redis subcharts are disabled by default — provision them
via the sibling `modules/postgres/bare-k8s/` and `modules/queue/
bare-k8s/` modules so the environments/<env>/ wiring stays uniform.
