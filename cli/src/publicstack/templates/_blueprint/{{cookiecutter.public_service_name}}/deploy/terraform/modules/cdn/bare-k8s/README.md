# `modules/cdn/bare-k8s/`

bare-k8s doesn't have CloudFront. The functional equivalent is the
cluster's Ingress controller (nginx-ingress / Traefik / ALB-ingress)
plus cert-manager for HTTPS. This module creates a cert-manager
`ClusterIssuer` for Let's Encrypt against `nginx` ingress class.

Outputs match `modules/cdn/aws/` (with shape-only fields zeroed when
they don't apply on K8s).

## Prerequisites

- nginx-ingress controller installed in the cluster
- cert-manager installed (≥1.13)
- DNS pointing the public hostname at the ingress LB

## Why no real CDN

Adding a real CDN on bare-k8s usually means contracting with one
(Cloudflare, Fastly, Bunny). That's a per-customer decision rather
than a Terraform module choice. If you want CDN behavior in front of
your bare-k8s install, point your domain at Cloudflare's proxy and let
it cache; the underlying Helm chart's Ingress stays the origin.
