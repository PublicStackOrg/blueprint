locals {
  _connection_url = format(
    "postgresql+asyncpg://%s:%s@%s:5432/%s",
    var.master_username,
    local.password,
    local.endpoint,
    var.database_name,
  )
}

output "connection_url" {
  value     = local._connection_url
  sensitive = true
}

output "reader_url" {
  value     = local._connection_url
  sensitive = true
}

output "port" {
  value = 5432
}

output "database_name" {
  value = var.database_name
}

output "endpoint" {
  value = local.endpoint
}

output "security_group_id" {
  description = "Unused on bare-k8s; shape parity with the aws/ variant."
  value       = ""
}
