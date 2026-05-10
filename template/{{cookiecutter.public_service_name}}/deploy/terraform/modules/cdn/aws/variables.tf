variable "name_prefix" {
  type = string
}

variable "alb_dns_name" {
  description = "ALB DNS name from the compute module."
  type        = string
}

variable "s3_static_origin_domain" {
  description = "S3 bucket regional domain that holds the Flutter web builds."
  type        = string
}

variable "aliases" {
  description = "Custom domain names attached to the distribution. Match the ACM cert."
  type        = list(string)
  default     = []
}

variable "cloudfront_certificate_arn" {
  description = "ACM cert ARN. MUST be in us-east-1 (CloudFront requirement). Pass via aws.us_east_1 provider when creating the cert."
  type        = string
}

variable "price_class" {
  description = "PriceClass_100 = US/CA/EU only (cheapest); _200 adds Asia/Africa; _All is global."
  type        = string
  default     = "PriceClass_100"
}

variable "tags" {
  type    = map(string)
  default = {}
}
