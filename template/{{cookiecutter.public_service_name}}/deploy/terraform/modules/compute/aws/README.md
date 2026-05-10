# `modules/compute/aws/`

ECS Fargate cluster + ALB + IAM + CloudWatch Logs for the api / worker /
migrator services. The CloudFront distribution sits in front of this
ALB (see `modules/cdn/aws/`).

Layout:

- **`api`** — ECS Service, ≥2 tasks for prod, behind the ALB on
  `/health` health checks.
- **`worker`** — ECS Service, 1 task default. No ALB.
- **`migrator`** — Task Definition only (not a Service). Run on each
  deploy via:

  ```bash
  aws ecs run-task \
    --cluster $(terraform output -raw cluster_name) \
    --task-definition $(terraform output -raw migrator_task_definition_arn) \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[...], securityGroups=[...]}"
  ```

## Inputs

Required: `name_prefix`, `region`, `vpc_id`, `public_subnet_ids`,
`private_subnet_ids`, `image_prefix`. Optional: `image_tag` (default
`latest`), CPU/memory per service, `desired_count` per service,
`alb_certificate_arn` (ACM), `environment` map, `secrets` map (env
var → SSM/Secrets Manager ARN).

## Outputs

| Output | Type |
|---|---|
| `service_endpoint` | string (ALB DNS) |
| `internal_dns_name` | string (same as service_endpoint) |
| `task_role_arn` | string |
| `alb_arn`, `alb_zone_id` | strings (Route 53 alias) |
| `tasks_security_group_id` | string |
| `cluster_name` | string |
| `migrator_task_definition_arn` | string |

## Cost (us-east-1, May 2026)

- 2 × api Fargate at 0.5 vCPU / 1 GiB = 2 × 24h × 30d × ($0.04048 +
  $0.004445) ≈ **$65/mo**
- 1 × worker Fargate at 0.25 vCPU / 0.5 GiB ≈ **$16/mo**
- ALB ≈ $16/mo + LCU charges
- CloudWatch Logs ≈ $1-2/mo for normal volume

≈ **$100/mo** baseline before traffic + CDN. Use `FARGATE_SPOT` capacity
provider via `desired_count` mix to cut compute ~70% with restart risk.
