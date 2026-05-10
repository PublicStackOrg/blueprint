# Hosting {{ cookiecutter.public_service_name }}

Three on-ramps, ordered by cheapness and friction. Pick the one that
fits your team — you can always swap later.

| On-ramp | Best for | Floor cost | Doc |
|---|---|---|---|
| **VPS docker-compose** | Cities self-hosting; small-city Parking-style workloads | $10–20/mo | [§1](#1-single-vps-docker-compose) |
| **Helm chart** | Operators with an existing K8s cluster (EKS / GKE / AKS) | already-paid cluster + ~$20/mo | [§2](#2-helm-chart) |
| **AWS Terraform** | Managed hosting (e.g. PublicStack hosts this for a city) | ~$130-250/mo | [§3](#3-aws-terraform-default) |

PublicStack itself defaults to **AWS** for managed deployments because
the `*aws/` Terraform modules are the most production-hardened path
in v0.4.0. Cities that prefer self-hosting use the VPS or Helm paths.

---

## 1. Single-VPS docker-compose

The cheapest path. One Linux VPS, one config file, one command.

See **[`compose/README.md`](compose/README.md)** for the full
runbook. Highlights:

- **Prereqs:** Ubuntu 22.04+ VPS with ≥2 GB RAM, a DNS A record
  pointing at the VPS, Docker Engine + Compose v2.
- **Cost floor:** Hetzner CX21 (~€5/mo), Vultr 2 GB regular (~$12/mo),
  DigitalOcean basic-2gb ($12/mo). See
  [`docs/cost-floor.md`](../../../blueprint/docs/cost-floor.md) for
  details.
- **Stack:** Caddy + Postgres 16 + Redis + migrator + api + worker.
  Caddy auto-acquires a Let's Encrypt cert on first boot.

```bash
git clone https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.public_service_name }}.git
cd {{ cookiecutter.public_service_name }}
cp deploy/compose/.env.prod.example .env.prod
vi .env.prod   # PUBLIC_HOSTNAME, secrets, AUTH_MODE
# Build Flutter web first (see compose/README.md §3)
docker compose -f deploy/compose/prod.yml --env-file .env.prod up -d
curl -fsSL "https://${PUBLIC_HOSTNAME}/health"
```

When this on-ramp runs out of headroom (sustained CPU > 60%, > 500
concurrent residents, dataset > 10 GB), step up to §2 or §3.

---

## 2. Helm chart

For operators with an existing K8s cluster.

See **[`k8s/README.md`](k8s/README.md)** for the full runbook.
Highlights:

- **Prereqs:** A K8s cluster (EKS / GKE / AKS / kind / on-prem), `helm`
  v3.12+, an Ingress controller (nginx-ingress by default), cert-manager
  for HTTPS.
- **Subcharts:** Bitnami Postgres + Redis bundled and conditionally
  enabled. Disable both and point at managed services (RDS, Cloud SQL,
  ElastiCache, MemoryStore) for prod.
- **Migrator-as-Job:** runs as a Helm hook before each install/upgrade.

```bash
helm dep update ./deploy/k8s
helm install {{ cookiecutter.public_service_slug }} ./deploy/k8s \
  --set publicHostname={{ cookiecutter.public_service_slug }}.example.org \
  --set postgresPassword=$(openssl rand -hex 32) \
  --set redisPassword=$(openssl rand -hex 32)
kubectl rollout status deploy/{{ cookiecutter.public_service_slug }}-api
```

For prod, override `values.yaml` with cluster-specific Ingress
annotations (ALB-ingress, GCE-ingress, ...) and crank `api.replicaCount`
+ `autoscaling.enabled`.

---

## 3. AWS Terraform (default)

Managed-hosting path. ECS Fargate + RDS + ElastiCache + S3 + CloudFront
+ ALB. Default `var.cloud = "aws"`.

```bash
cd deploy/terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
vi terraform.tfvars   # vpc_id, subnets, image_prefix, cert ARN, password
terraform init
terraform apply
terraform output cdn_distribution_domain_name   # → d12345.cloudfront.net
```

Point your DNS at `cdn_distribution_domain_name` (Route 53 alias to
the CloudFront distribution; `output.hosted_zone_id` from the cdn
module gives you the zone for the alias).

### Module shape

```
deploy/terraform/
├── modules/
│   ├── postgres/{aws,bare-k8s,gcp,hetzner,r2}/
│   ├── object_storage/{aws,bare-k8s,gcp,r2}/
│   ├── queue/{aws,bare-k8s,gcp,hetzner}/
│   ├── compute/{aws,bare-k8s,gcp,hetzner}/
│   └── cdn/{aws,bare-k8s,gcp,r2}/
└── environments/
    ├── dev/      # 1× api task, db.t4g.micro single-AZ, log_level=DEBUG
    ├── staging/  # 2× api task, db.t4g.micro single-AZ
    └── prod/     # 2× api task, db.t4g.small multi-AZ, deletion protection
```

Every `modules/<resource>/<cloud>/` exposes the same outputs (see
`postgres/aws/README.md` for the field list). Environments reference
modules via `source = "../../modules/<resource>/${var.cloud}"` so
swapping clouds is a single var flip.

### Prerequisites

- AWS account + an IAM user/role with permissions for RDS, S3, ECS,
  ELB, CloudFront, ACM, CloudWatch Logs, ElastiCache, IAM (for the
  ECS task roles).
- A VPC with public + private subnets across ≥2 AZs.
- An ACM cert in **us-east-1** for the CloudFront distribution
  (CloudFront requirement; rest of the infra can live in any region).
- Optional: an OTLP collector if you want to ship traces.

### CI publishes the images

`template/{{…}}/.github/workflows/ci.yml`'s `docker-push` job pushes
api/worker/migrator images to GHCR on every push to `main`. The
`image_prefix` tfvar references those tags. Pin to `git-${SHA}` in
prod for reproducible deploys; `latest` for cheap rolling.

### Migrations

After each `terraform apply` (which updates the migrator task
definition with the new image), trigger a one-shot run:

```bash
aws ecs run-task \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task-definition $(terraform output -raw migrator_task_definition_arn) \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[...], securityGroups=[...]}"
```

### Cost

See [`docs/cost-floor.md`](../../../blueprint/docs/cost-floor.md). dev
~$60/mo, staging ~$80/mo, prod ~$130-250/mo before traffic charges.

---

## Swapping to another cloud

Every Terraform module exposes the same output contract; flip
`var.cloud`:

```bash
# bare-k8s: complete in v0.4.0 (in-cluster Postgres / Redis / MinIO / Helm + Ingress)
terraform apply -var cloud=bare-k8s

# gcp / hetzner / r2: stubs in v0.4.0 — fail fast with a "PRs welcome" message
terraform apply -var cloud=gcp   # → plan fails with module's README pointer
```

The `bare-k8s` path runs the same Helm chart from §2 via the helm
provider; it's the right swap when you already have a cluster and
want everything in one Terraform apply.

---

## Compliance suite

Whichever path you pick, run the compliance suite against the
generated PS:

```bash
publicstack-compliance run --strict
```

Phase 5 ships six checks (`data_export`, `contract_compat`,
`grid_integration`, `security`, `observability`, `accessibility`)
against the v0.3.0+ template. A freshly-generated PS exits 0; the
hosting paths above don't introduce new compliance failures.

---

## See also

- [`compose/README.md`](compose/README.md) — VPS runbook
- [`k8s/README.md`](k8s/README.md) — Helm runbook
- [`terraform/modules/<resource>/<cloud>/README.md`](terraform/) — per-module contracts
- [`../docs/cost-floor.md`](../../../blueprint/docs/cost-floor.md) — design budget table
- [`../../../blueprint/docs/SPIKES.md`](../../../blueprint/docs/SPIKES.md) — open hard problems (cost-floor benchmark, identity provider, etc.)
