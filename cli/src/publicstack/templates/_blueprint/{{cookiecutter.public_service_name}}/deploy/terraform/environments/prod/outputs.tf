output "cdn_distribution_domain_name" {
  description = "Point your DNS at this hostname."
  value       = module.cdn.distribution_domain_name
}

output "cdn_distribution_id" {
  value = module.cdn.distribution_id
}

output "alb_dns_name" {
  value = module.compute.service_endpoint
}

output "ecs_cluster_name" {
  value = module.compute.cluster_name
}

output "migrator_task_definition_arn" {
  description = "Run via `aws ecs run-task ...` after each deploy."
  value       = module.compute.migrator_task_definition_arn
}

output "documents_bucket_name" {
  value = module.object_storage.bucket_name
}

output "static_bucket_name" {
  description = "Upload Flutter web builds here. CloudFront serves them."
  value       = module.static_origin.bucket_name
}

output "postgres_endpoint" {
  value = module.postgres.endpoint
}
