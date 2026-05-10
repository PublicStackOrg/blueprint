# {{ cookiecutter.public_service_name }} — Postgres on a generic Kubernetes
# cluster, via the Bitnami postgresql Helm chart.
#
# Assumes the cluster already exists (kubectl context is set up). Use this
# module when bringing the database up alongside the rest of the PS in a
# single Terraform apply against EKS / GKE / AKS / kind / on-prem.

terraform {
  required_version = ">= 1.6"
  required_providers {
    helm       = { source = "hashicorp/helm", version = "~> 2.13" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
    random     = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

resource "random_password" "this" {
  length  = 32
  special = false
}

resource "kubernetes_secret_v1" "credentials" {
  metadata {
    name      = "${var.name_prefix}-pg-credentials"
    namespace = var.namespace
  }
  data = {
    password = var.master_password != null ? var.master_password : random_password.this.result
  }
}

resource "helm_release" "postgresql" {
  name       = "${var.name_prefix}-postgres"
  namespace  = var.namespace
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "postgresql"
  version    = var.chart_version

  set {
    name  = "auth.username"
    value = var.master_username
  }
  set {
    name  = "auth.database"
    value = var.database_name
  }
  set {
    name  = "auth.existingSecret"
    value = kubernetes_secret_v1.credentials.metadata[0].name
  }
  set {
    name  = "auth.secretKeys.userPasswordKey"
    value = "password"
  }
  set {
    name  = "primary.persistence.size"
    value = "${var.storage_gb}Gi"
  }

  depends_on = [kubernetes_secret_v1.credentials]
}

locals {
  password = var.master_password != null ? var.master_password : random_password.this.result
  service_name = "${helm_release.postgresql.name}-postgresql"
  endpoint     = "${local.service_name}.${var.namespace}.svc.cluster.local"
}
