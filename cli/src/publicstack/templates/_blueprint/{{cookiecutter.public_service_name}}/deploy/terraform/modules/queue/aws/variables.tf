variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "allowed_security_group_ids" {
  type    = list(string)
  default = []
}

variable "node_type" {
  description = "ElastiCache node type. cache.t4g.micro is the cheapest viable."
  type        = string
  default     = "cache.t4g.micro"
}

variable "num_cache_clusters" {
  description = "Replicas (incl. primary). 1 = single node; 2+ enables auto-failover + multi-AZ."
  type        = number
  default     = 1
}

variable "transit_encryption_enabled" {
  type    = bool
  default = false
}

variable "auth_token" {
  description = "Required when transit_encryption_enabled=true."
  type        = string
  sensitive   = true
  default     = null
}

variable "apply_immediately" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
