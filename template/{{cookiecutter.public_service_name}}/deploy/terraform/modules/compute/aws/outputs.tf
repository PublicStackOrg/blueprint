output "service_endpoint" {
  description = "Public-facing ALB DNS name. Front this with CloudFront via the cdn module."
  value       = aws_lb.this.dns_name
}

output "internal_dns_name" {
  description = "ALB DNS for internal references (CloudFront origin, etc.)."
  value       = aws_lb.this.dns_name
}

output "task_role_arn" {
  description = "IAM role ARN attached to ECS tasks. Grant additional policies (S3 bucket access, etc.) here."
  value       = aws_iam_role.task.arn
}

output "alb_arn" {
  value = aws_lb.this.arn
}

output "alb_zone_id" {
  description = "Hosted zone ID of the ALB (for Route 53 alias records)."
  value       = aws_lb.this.zone_id
}

output "tasks_security_group_id" {
  description = "Security group attached to ECS tasks. Allow this SG into your RDS / ElastiCache SGs."
  value       = aws_security_group.tasks.id
}

output "cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "migrator_task_definition_arn" {
  description = "Run via `aws ecs run-task` after each deploy."
  value       = aws_ecs_task_definition.migrator.arn
}
