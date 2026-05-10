# `deploy/`

Deployment artifacts for **{{ cookiecutter.public_service_name }}**.
Three on-ramps, ordered by cheapness and friction:

- `compose/` — single-VPS docker-compose. The cheapest path. Target:
  $10–20/mo VPS for a small-city deploy.
- `k8s/` — Helm chart for operators with a K8s cluster.
- `terraform/` — per-cloud Terraform modules (AWS / GCP / Hetzner /
  K8s) under `terraform/modules/`, with environments under
  `terraform/environments/`.

Filled in during **Phase 6** of `blueprint`'s plan, including
`HOSTING.md` with copy-pasteable runbooks.

Cloud-agnostic from day one. Hosting is a per-deployer decision, not
declared by this repo.
