# Dev environment defaults: smaller instance sizes, single AZ, no
# deletion protection. Identical shape to prod/variables.tf — only
# defaults differ.

variable "cloud" {
  type    = string
  default = "aws"
  validation {
    condition     = contains(["aws", "bare-k8s", "gcp", "hetzner", "r2"], var.cloud)
    error_message = "var.cloud must be one of: aws, bare-k8s, gcp, hetzner, r2."
  }
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }

variable "image_prefix" {
  type    = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "aliases" {
  type    = list(string)
  default = []
}

variable "cloudfront_certificate_arn" {
  type = string
}

variable "alb_certificate_arn" {
  type    = string
  default = null
}

variable "cdn_price_class" {
  type    = string
  default = "PriceClass_100"
}

variable "postgres_instance_class" {
  type    = string
  default = "db.t4g.micro"   # cheapest for dev
}

variable "postgres_multi_az" {
  type    = bool
  default = false   # dev doesn't need HA
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
  default = 1   # single-node Redis
}

variable "api_desired_count" {
  type    = number
  default = 1   # single api task in dev
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
  default = "DEBUG"
}

variable "otel_exporter_endpoint" {
  type    = string
  default = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
