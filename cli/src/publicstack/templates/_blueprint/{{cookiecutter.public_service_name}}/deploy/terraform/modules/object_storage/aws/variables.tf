variable "bucket_name" {
  description = "Globally-unique S3 bucket name. Convention: <ps>-<env>-documents."
  type        = string
}

variable "noncurrent_version_expiration_days" {
  description = "Days to keep old object versions before expiring."
  type        = number
  default     = 30
}

variable "allowed_origins" {
  description = "CORS-allowed origins (CloudFront domain, custom domain, etc.). Empty = no CORS rule."
  type        = list(string)
  default     = []
}

variable "deletion_protection" {
  description = "If true, terraform destroy refuses to delete the bucket."
  type        = bool
  default     = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
