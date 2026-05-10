output "distribution_domain_name" {
  description = "CloudFront domain (e.g. d1234abc.cloudfront.net). Point your DNS CNAME / Route 53 alias here."
  value       = aws_cloudfront_distribution.this.domain_name
}

output "distribution_id" {
  value = aws_cloudfront_distribution.this.id
}

output "origin_endpoint" {
  description = "ALB DNS name behind CloudFront (kept for parity with non-AWS cdn modules)."
  value       = var.alb_dns_name
}

output "hosted_zone_id" {
  description = "CloudFront's hosted zone ID — for Route 53 alias records pointing at the distribution."
  value       = aws_cloudfront_distribution.this.hosted_zone_id
}
