# {{ cookiecutter.public_service_name }} — MinIO on Kubernetes (S3-compatible).

terraform {
  required_version = ">= 1.6"
  required_providers {
    helm       = { source = "hashicorp/helm", version = "~> 2.13" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
    random     = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

variable "bucket_name" { type = string }
variable "namespace" {
  type    = string
  default = "{{ cookiecutter.python_package }}"
}
variable "noncurrent_version_expiration_days" {
  type    = number
  default = 30
}
variable "allowed_origins" {
  type    = list(string)
  default = []
}
variable "deletion_protection" {
  type    = bool
  default = false
}
variable "storage_gb" {
  type    = number
  default = 50
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "random_password" "root" {
  length  = 24
  special = false
}

resource "kubernetes_secret_v1" "credentials" {
  metadata {
    name      = "${var.bucket_name}-minio"
    namespace = var.namespace
  }
  data = {
    "root-user"     = "ps-admin"
    "root-password" = random_password.root.result
  }
}

resource "helm_release" "minio" {
  name       = var.bucket_name
  namespace  = var.namespace
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "minio"

  set {
    name  = "auth.existingSecret"
    value = kubernetes_secret_v1.credentials.metadata[0].name
  }
  set {
    name  = "defaultBuckets"
    value = var.bucket_name
  }
  set {
    name  = "persistence.size"
    value = "${var.storage_gb}Gi"
  }
}

locals {
  endpoint = "${var.bucket_name}.${var.namespace}.svc.cluster.local"
}

output "bucket_name" {
  value = var.bucket_name
}

output "bucket_arn" {
  description = "MinIO doesn't surface ARN; here for shape parity with aws/."
  value       = "minio://${var.namespace}/${var.bucket_name}"
}

output "endpoint" {
  value = "${local.endpoint}:9000"
}

output "region" {
  description = "MinIO uses 'us-east-1' as the default region label."
  value       = "us-east-1"
}
