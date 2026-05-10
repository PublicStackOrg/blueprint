# Hosting cost floor — design budget

PLAN.md §3 says cheap hosting is a first-class goal: **the
single-VPS docker-compose path should run a small-city Parking
deploy for $10–20/mo**. This doc captures the design budget — the
estimated cost based on resource assumptions, not a measured
benchmark. SPIKES.md #7 stays open until Parking actually deploys to
a real city and we measure the floor; that closes this doc into a
"validated" version.

Numbers are May 2026, on-demand list prices, USD.

## Workload assumptions

For the budget below, "small city" means:

| Metric | Value |
|---|---|
| Population served | < 50,000 |
| Citations issued / year | ~100,000 |
| Concurrent resident sessions (peak) | ~1,000 |
| Concurrent staff sessions (peak) | ~200 |
| Document storage growth | < 1 GB / year |
| Audit log growth | < 5 GB / year |
| Daily database backup size | < 100 MB |

A real Parking deployment will validate or invalidate these. The
synthetic load test plan: 10 RPS sustained, 50 RPS burst, all six
adapters wired (audit on every state change).

## Resource ceiling per service

Estimated steady-state resource use, derived from the template's
default container sizes + Phase 5's compliance baseline (CSP +
HTTPSRedirect + JsonFormatter + OpenTelemetry SDK + FastAPI +
SQLAlchemy async):

| Service | Idle RAM | Peak RAM | Idle CPU | Peak CPU |
|---|---|---|---|---|
| api (FastAPI + Uvicorn) | ~250 MB | ~600 MB | 0.05 vCPU | 0.6 vCPU |
| worker (RQ) | ~150 MB | ~400 MB | 0.02 vCPU | 0.3 vCPU |
| db (Postgres 16) | ~200 MB | ~500 MB | 0.03 vCPU | 0.4 vCPU |
| redis | ~50 MB | ~150 MB | 0.01 vCPU | 0.1 vCPU |
| caddy | ~30 MB | ~80 MB | 0.01 vCPU | 0.1 vCPU |
| **TOTAL (ballpark)** | **~700 MB** | **~1.7 GB** | **~0.12 vCPU** | **~1.5 vCPU** |

Migrator runs once per deploy and exits — not in steady state.

## Single-VPS path (the cheap one)

| Provider / Tier | RAM | vCPU | Storage | Monthly | Headroom |
|---|---|---|---|---|---|
| **Hetzner CX21** | 4 GB | 2 | 40 GB SSD | **€5 (~$5.50)** | comfortable |
| **Hetzner CX31** | 8 GB | 2 | 80 GB SSD | **€11 (~$12)** | generous; recommended for prod |
| **Vultr 2 GB regular** | 2 GB | 1 | 55 GB SSD | $12 | tight at peak; OK for dev |
| **DigitalOcean basic-2gb** | 2 GB | 1 | 60 GB SSD | $12 | tight at peak |
| **DigitalOcean basic-4gb** | 4 GB | 2 | 80 GB SSD | $24 | comfortable |

**Verdict (design):** Hetzner CX21 at €5/mo or DO basic-4gb at $24/mo
hit the PLAN.md §3 target. The VPS path floor is ≈ **$10–25/mo**.

What we don't yet know (SPIKES.md #7):

- Real RAM under sustained citation-volume load
- Postgres dataset growth past year 1
- Whether the OpenTelemetry SDK's overhead is the ~250 MB ballpark or
  meaningfully higher

Once Parking deploys, we benchmark for real and update this doc.

## Helm chart path (existing K8s cluster)

Assumes the cluster is already paid for. Marginal cost = the resources
this PS consumes:

| Resource | Quantity | Notes |
|---|---|---|
| 1 GB RAM, 0.5 vCPU per Pod (api/worker) | 3 Pods | small footprint |
| 10 GB Postgres PVC | 1 | + LB charges if external Postgres |
| 4 GB Redis PVC | 1 | optional persistence |
| Ingress LB | 1 | depends on cluster (NLB, GCE LB, ...) |

**Marginal cost on EKS:** ~$15–20/mo on top of the cluster's $73/mo
control plane. **On GKE Autopilot:** ~$10/mo marginal.

If you don't already pay for a K8s cluster, this path is more
expensive than VPS docker-compose; pick that instead.

## AWS Terraform path (the managed default)

Defaults from `deploy/terraform/environments/{dev,staging,prod}/
terraform.tfvars.example`:

| Service | dev | staging | prod |
|---|---|---|---|
| RDS | db.t4g.micro single-AZ | db.t4g.micro single-AZ | db.t4g.small multi-AZ |
| ElastiCache | cache.t4g.micro × 1 | cache.t4g.micro × 1 | cache.t4g.micro × 2 |
| ECS Fargate api | 1 task × 0.5 vCPU/1 GiB | 2 × 0.5/1 | 2 × 0.5/1 |
| ECS Fargate worker | 1 × 0.25/0.5 | 1 × 0.25/0.5 | 1 × 0.25/0.5 |
| ALB | 1 | 1 | 1 |
| CloudFront | 1 distribution | 1 | 1 |
| S3 (documents + static) | 2 buckets | 2 | 2 |
| Logs | 30/14-day retention | 30/14 | 30/14 |
| **Estimated monthly** | **~$60** | **~$80** | **~$130–250** |

prod range depends on multi-AZ ($26 instance × 2 = $52 vs $26
single), CloudFront traffic, and S3 storage growth. Use FARGATE_SPOT
to cut compute ~70% with restart risk.

us-east-1, on-demand. Reserved Instances / Savings Plans cut RDS
30-50% with a 1- or 3-year commit.

## Cost-floor benchmark plan

When Parking ships into a real city (Phase 8):

1. Run synthetic load against the VPS path (Hetzner CX21) for 7 days
   matching the workload-assumption table.
2. Capture: peak RAM per service, peak CPU per service, sustained
   disk I/O, postgres dataset growth, daily backup size.
3. Update this doc with measured numbers.
4. Close SPIKES.md #7 with a link back here.

Until then, the numbers above are design budget — useful for picking
a tier, not for SLA commitments.

## Out of scope

- Network egress (varies wildly by city traffic shape; CloudFront
  egress is ~$0.085/GB)
- Domain registration + DNS hosting (~$10-15/yr per domain)
- Email sending costs (Notifications adapter, when not log_only)
- Backup off-site shipping (S3 / B2 / Backblaze; ~$0.005/GB-month)
