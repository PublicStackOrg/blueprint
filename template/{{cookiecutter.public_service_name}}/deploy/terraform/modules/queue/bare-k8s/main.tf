# {{ cookiecutter.public_service_name }} — Redis on Kubernetes via Bitnami.

terraform {
  required_version = ">= 1.6"
  required_providers {
    helm       = { source = "hashicorp/helm", version = "~> 2.13" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
    random     = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

variable "name_prefix" { type = string }
variable "namespace" {
  type    = string
  default = "{{ cookiecutter.python_package }}"
}
variable "vpc_id" {
  type    = string
  default = ""
}
variable "private_subnet_ids" {
  type    = list(string)
  default = []
}
variable "allowed_security_group_ids" {
  type    = list(string)
  default = []
}
variable "node_type" {
  type    = string
  default = ""
}
variable "num_cache_clusters" {
  type    = number
  default = 1
}
variable "transit_encryption_enabled" {
  type    = bool
  default = false
}
variable "auth_token" {
  type      = string
  sensitive = true
  default   = null
}
variable "apply_immediately" {
  type    = bool
  default = false
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "random_password" "auth" {
  length  = 32
  special = false
}

resource "kubernetes_secret_v1" "credentials" {
  metadata {
    name      = "${var.name_prefix}-redis"
    namespace = var.namespace
  }
  data = {
    "redis-password" = var.auth_token != null ? var.auth_token : random_password.auth.result
  }
}

resource "helm_release" "redis" {
  name       = "${var.name_prefix}-redis"
  namespace  = var.namespace
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "redis"

  set {
    name  = "auth.existingSecret"
    value = kubernetes_secret_v1.credentials.metadata[0].name
  }
  set {
    name  = "auth.existingSecretPasswordKey"
    value = "redis-password"
  }
  set {
    name  = "architecture"
    value = var.num_cache_clusters > 1 ? "replication" : "standalone"
  }
}

locals {
  password   = var.auth_token != null ? var.auth_token : random_password.auth.result
  endpoint   = "${helm_release.redis.name}-master.${var.namespace}.svc.cluster.local"
  _redis_url = format("redis://:%s@%s:6379/0", local.password, local.endpoint)
}

output "redis_url" {
  value     = local._redis_url
  sensitive = true
}

output "queue_url" {
  value     = local._redis_url
  sensitive = true
}

output "endpoint" {
  value = local.endpoint
}

output "security_group_id" {
  description = "Unused on bare-k8s; shape parity only."
  value       = ""
}
