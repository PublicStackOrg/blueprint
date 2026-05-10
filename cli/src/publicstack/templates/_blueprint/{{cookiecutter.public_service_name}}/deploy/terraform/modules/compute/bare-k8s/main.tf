# {{ cookiecutter.public_service_name }} — compute on Kubernetes, via the
# PublicStack Helm chart at deploy/k8s/.

terraform {
  required_version = ">= 1.6"
  required_providers {
    helm = { source = "hashicorp/helm", version = "~> 2.13" }
  }
}

variable "name_prefix" { type = string }
variable "region" {
  type    = string
  default = ""
}
variable "vpc_id" {
  type    = string
  default = ""
}
variable "public_subnet_ids" {
  type    = list(string)
  default = []
}
variable "private_subnet_ids" {
  type    = list(string)
  default = []
}
variable "image_prefix" { type = string }
variable "image_tag" {
  type    = string
  default = "latest"
}
variable "api_cpu" {
  type    = string
  default = "500m"
}
variable "api_memory" {
  type    = string
  default = "1Gi"
}
variable "api_desired_count" {
  type    = number
  default = 2
}
variable "worker_cpu" {
  type    = string
  default = "250m"
}
variable "worker_memory" {
  type    = string
  default = "512Mi"
}
variable "worker_desired_count" {
  type    = number
  default = 1
}
variable "alb_certificate_arn" {
  type    = string
  default = null
}
variable "namespace" {
  type    = string
  default = "{{ cookiecutter.python_package }}"
}
variable "public_hostname" {
  type = string
}
variable "ingress_class_name" {
  type    = string
  default = "nginx"
}
variable "environment" {
  type    = map(string)
  default = {}
}
variable "secrets" {
  type    = map(string)
  default = {}
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "helm_release" "ps" {
  name       = var.name_prefix
  namespace  = var.namespace
  chart      = "${path.module}/../../../../k8s"
  version    = "0.1.0"

  set {
    name  = "imagePrefix"
    value = var.image_prefix
  }
  set {
    name  = "imageTag"
    value = var.image_tag
  }
  set {
    name  = "publicHostname"
    value = var.public_hostname
  }
  set {
    name  = "api.replicaCount"
    value = var.api_desired_count
  }
  set {
    name  = "worker.replicaCount"
    value = var.worker_desired_count
  }
  set {
    name  = "ingress.className"
    value = var.ingress_class_name
  }
  set {
    name  = "postgresql.enabled"
    value = "false"  # postgres comes from a sibling module
  }
  set {
    name  = "redis.enabled"
    value = "false"
  }

  dynamic "set" {
    for_each = var.environment
    content {
      name  = "extraEnv.${set.key}"
      value = set.value
    }
  }

  timeout = 600
}

output "service_endpoint" {
  description = "Public hostname; matches publicHostname so ingress traffic lands here."
  value       = var.public_hostname
}

output "internal_dns_name" {
  description = "ClusterIP service for the api Deployment."
  value       = "${helm_release.ps.name}-api.${var.namespace}.svc.cluster.local"
}

output "task_role_arn" {
  description = "Unused on bare-k8s (Pods use a ServiceAccount, not an IAM role); shape parity."
  value       = ""
}

output "alb_arn" {
  value = ""
}

output "alb_zone_id" {
  value = ""
}

output "tasks_security_group_id" {
  value = ""
}

output "cluster_name" {
  description = "Unused on bare-k8s (the cluster is whatever your kubectx points at); shape parity."
  value       = ""
}

output "migrator_task_definition_arn" {
  description = "Migrator runs as a Helm hook Job; no separate task ARN."
  value       = ""
}
