output "connection_url" {
  description = "Async DSN for the api/worker services (uses asyncpg driver)."
  value = format(
    "postgresql+asyncpg://%s:%s@%s:%s/%s",
    var.master_username,
    var.master_password,
    aws_db_instance.this.address,
    aws_db_instance.this.port,
    var.database_name,
  )
  sensitive = true
}

output "reader_url" {
  description = "Reader DSN. RDS exposes a reader endpoint only for clusters; for single-instance we expose the same endpoint."
  value = format(
    "postgresql+asyncpg://%s:%s@%s:%s/%s",
    var.master_username,
    var.master_password,
    aws_db_instance.this.address,
    aws_db_instance.this.port,
    var.database_name,
  )
  sensitive = true
}

output "port" {
  value = aws_db_instance.this.port
}

output "database_name" {
  value = aws_db_instance.this.db_name
}

output "security_group_id" {
  description = "RDS security group; the compute layer needs to be allowed in via this."
  value       = aws_security_group.this.id
}

output "endpoint" {
  value = aws_db_instance.this.address
}
