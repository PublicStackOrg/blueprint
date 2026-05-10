locals {
  _redis_url = format(
    "redis%s://%s%s:%s/0",
    var.transit_encryption_enabled ? "s" : "",
    var.transit_encryption_enabled && var.auth_token != null ? format(":%s@", var.auth_token) : "",
    aws_elasticache_replication_group.this.primary_endpoint_address,
    aws_elasticache_replication_group.this.port,
  )
}

output "redis_url" {
  description = "Redis URL the api/worker services use as REDIS_URL."
  value       = local._redis_url
  sensitive   = true
}

output "queue_url" {
  description = "Alias for redis_url; kept for parity with non-Redis (SQS-style) queue modules."
  value       = local._redis_url
  sensitive   = true
}

output "endpoint" {
  value = aws_elasticache_replication_group.this.primary_endpoint_address
}

output "security_group_id" {
  value = aws_security_group.this.id
}
