# `deploy/`

Deployment artifacts for **{{ cookiecutter.public_service_name }}**.
Three on-ramps — see [`HOSTING.md`](HOSTING.md) for the full
walkthrough.

| Path | Best for | Floor |
|---|---|---|
| [`compose/`](compose/) | Cities self-hosting on a VPS | $10–20/mo |
| [`k8s/`](k8s/) | Operators with an existing K8s cluster | already-paid cluster + ~$20/mo |
| [`terraform/`](terraform/) | Managed hosting (default cloud: AWS) | ~$130-250/mo prod |

PublicStack-managed deployments default to the AWS Terraform path;
self-hosting cities pick VPS or Helm. Swap clouds in the Terraform
path via `terraform apply -var cloud=bare-k8s` (or `gcp` / `hetzner` /
`r2` once those modules land).
