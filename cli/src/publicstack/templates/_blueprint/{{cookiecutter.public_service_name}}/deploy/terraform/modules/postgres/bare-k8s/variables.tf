variable "name_prefix" { type = string }
variable "namespace" {
  type    = string
  default = "{{ cookiecutter.python_package }}"
}
variable "vpc_id" {
  description = "Unused on bare-k8s; here for shape parity with the aws/ variant."
  type        = string
  default     = ""
}
variable "private_subnet_ids" {
  description = "Unused on bare-k8s; shape parity only."
  type        = list(string)
  default     = []
}
variable "allowed_security_group_ids" {
  description = "Unused on bare-k8s; shape parity only."
  type        = list(string)
  default     = []
}
variable "instance_class" {
  description = "Unused on bare-k8s; shape parity only."
  type        = string
  default     = ""
}
variable "allocated_storage_gb" {
  description = "Alias for storage_gb. Unused; shape parity."
  type        = number
  default     = 20
}
variable "storage_gb" {
  type    = number
  default = 20
}
variable "max_allocated_storage_gb" {
  type    = number
  default = 100
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
  type      = string
  sensitive = true
  default   = null
}
variable "multi_az" {
  type    = bool
  default = false
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
variable "chart_version" {
  type    = string
  default = "16.x.x"
}
variable "tags" {
  type    = map(string)
  default = {}
}
