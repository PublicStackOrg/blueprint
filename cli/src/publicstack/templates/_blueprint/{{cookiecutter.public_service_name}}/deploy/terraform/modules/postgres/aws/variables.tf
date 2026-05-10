variable "name_prefix" {
  description = "Prefix for resource names; usually `<ps>-<env>`."
  type        = string
}

variable "vpc_id" {
  description = "VPC the RDS instance lives in."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs (multi-AZ requires ≥2)."
  type        = list(string)
}

variable "allowed_security_group_ids" {
  description = "Security groups permitted to reach Postgres on 5432."
  type        = list(string)
  default     = []
}

variable "instance_class" {
  description = "RDS instance class. db.t4g.micro is the cheapest viable for PostgreSQL 16."
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage_gb" {
  type    = number
  default = 20
}

variable "max_allocated_storage_gb" {
  description = "Storage autoscaling cap; 0 disables."
  type        = number
  default     = 100
}

variable "database_name" {
  type    = string
  default = "{{ cookiecutter.python_package }}"
}

variable "master_username" {
  type    = string
  default = "{{ cookiecutter.python_package }}"
}

variable "master_password" {
  description = "Master password. Provide via tfvars + a secret manager; do NOT commit."
  type        = string
  sensitive   = true
}

variable "multi_az" {
  description = "Enable multi-AZ for prod; off in dev/staging to save cost."
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  type    = number
  default = 7
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "apply_immediately" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
