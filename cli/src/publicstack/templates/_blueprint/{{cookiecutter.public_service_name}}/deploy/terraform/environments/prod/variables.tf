variable "cloud" {
  description = "Cloud target. AWS is the default and complete; bare-k8s is also complete; gcp/hetzner/r2 are stubs."
  type        = string
  default     = "aws"
  validation {
    condition     = contains(["aws", "bare-k8s", "gcp", "hetzner", "r2"], var.cloud)
    error_message = "var.cloud must be one of: aws, bare-k8s, gcp, hetzner, r2."
  }
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "region" {
  description = "AWS region (or equivalent for non-AWS clouds)."
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "VPC the infra lives in. Out of scope for this module — bring your own."
  type        = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "image_prefix" {
  description = "Image prefix (no service suffix). e.g. ghcr.io/publicstackorg/{{ cookiecutter.python_package }}"
  type        = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "aliases" {
  description = "Public domain names attached to CloudFront."
  type        = list(string)
  default     = []
}

variable "cloudfront_certificate_arn" {
  description = "ACM cert ARN — MUST be in us-east-1."
  type        = string
}

variable "alb_certificate_arn" {
  description = "ACM cert ARN in the same region as the ALB."
  type        = string
  default     = null
}

variable "cdn_price_class" {
  type    = string
  default = "PriceClass_100"
}

variable "postgres_instance_class" {
  type    = string
  default = "db.t4g.small"
}

variable "postgres_multi_az" {
  type    = bool
  default = true
}

variable "postgres_master_password" {
  type      = string
  sensitive = true
}

variable "queue_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "queue_num_cache_clusters" {
  type    = number
  default = 2
}

variable "api_desired_count" {
  type    = number
  default = 2
}

variable "worker_desired_count" {
  type    = number
  default = 1
}

variable "auth_mode" {
  type    = string
  default = "none"
}

variable "log_level" {
  type    = string
  default = "INFO"
}

variable "otel_exporter_endpoint" {
  description = "OTLP collector endpoint (HTTP). Empty = no traces exported."
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
