# {{ cookiecutter.public_service_name }} — "CDN" on bare Kubernetes.
#
# bare-k8s doesn't have CloudFront. The closest equivalent is nginx-ingress
# (already installed in most clusters) + cert-manager for HTTPS. This module
# creates a cert-manager ClusterIssuer for Let's Encrypt and exposes the
# expected outputs as the Helm chart's Ingress hostname.

terraform {
  required_version = ">= 1.6"
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
  }
}

variable "name_prefix" { type = string }
variable "alb_dns_name" {
  description = "Unused on bare-k8s; shape parity."
  type        = string
  default     = ""
}
variable "s3_static_origin_domain" {
  type    = string
  default = ""
}
variable "aliases" {
  type    = list(string)
  default = []
}
variable "cloudfront_certificate_arn" {
  type    = string
  default = ""
}
variable "price_class" {
  type    = string
  default = ""
}
variable "letsencrypt_email" {
  description = "Email used for Let's Encrypt account registration."
  type        = string
  default     = "ops@example.org"
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "kubernetes_manifest" "letsencrypt_issuer" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "ClusterIssuer"
    metadata = {
      name = "${var.name_prefix}-letsencrypt"
    }
    spec = {
      acme = {
        email  = var.letsencrypt_email
        server = "https://acme-v02.api.letsencrypt.org/directory"
        privateKeySecretRef = {
          name = "${var.name_prefix}-letsencrypt-account"
        }
        solvers = [
          {
            http01 = {
              ingress = {
                class = "nginx"
              }
            }
          }
        ]
      }
    }
  }
}

output "distribution_domain_name" {
  description = "On bare-k8s the public hostname IS the distribution domain. Match the Helm chart's publicHostname / Ingress host."
  value       = length(var.aliases) > 0 ? var.aliases[0] : ""
}

output "distribution_id" {
  description = "Unused on bare-k8s; shape parity with aws/."
  value       = ""
}

output "origin_endpoint" {
  value = var.alb_dns_name
}

output "hosted_zone_id" {
  description = "Unused on bare-k8s; shape parity."
  value       = ""
}
