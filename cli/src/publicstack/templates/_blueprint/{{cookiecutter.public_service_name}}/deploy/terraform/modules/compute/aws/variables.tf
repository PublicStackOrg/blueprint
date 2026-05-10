variable "name_prefix" {
  type = string
}

variable "region" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  description = "Public subnets where the ALB lives."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnets where ECS tasks run."
  type        = list(string)
}

variable "image_prefix" {
  description = "Image prefix without the per-service suffix; e.g. ghcr.io/publicstackorg/parking"
  type        = string
}

variable "image_tag" {
  description = "Image tag (git-<sha> for reproducibility, or 'latest' for rolling)."
  type        = string
  default     = "latest"
}

variable "api_cpu" {
  type    = string
  default = "512"
}

variable "api_memory" {
  type    = string
  default = "1024"
}

variable "api_desired_count" {
  description = "Number of api tasks. ≥2 for prod (HA across AZs)."
  type        = number
  default     = 2
}

variable "worker_cpu" {
  type    = string
  default = "256"
}

variable "worker_memory" {
  type    = string
  default = "512"
}

variable "worker_desired_count" {
  type    = number
  default = 1
}

variable "alb_certificate_arn" {
  description = "ACM cert ARN. Must be in the SAME region as the ALB. Set null to skip HTTPS listener."
  type        = string
  default     = null
}

variable "environment" {
  description = "Plain env vars for all three task definitions (api/worker/migrator)."
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Map of env-var-name → SSM Parameter Store / Secrets Manager ARN. Injected at task start."
  type        = map(string)
  default     = {}
}

variable "tags" {
  type    = map(string)
  default = {}
}
