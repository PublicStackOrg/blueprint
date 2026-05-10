# {{ cookiecutter.public_service_name }} — prod environment.
#
# Default cloud is AWS. Override via `terraform apply -var cloud=bare-k8s`
# (or any other cloud once its modules are filled in).

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 5.0"
      configuration_aliases = [aws.us_east_1]
    }
  }
}

provider "aws" {
  region = var.region
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

locals {
  name_prefix = "{{ cookiecutter.python_package }}-${var.environment}"

  common_tags = merge({
    Project     = "{{ cookiecutter.public_service_name }}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }, var.tags)
}

module "postgres" {
  source = "../../modules/postgres/${var.cloud}"

  name_prefix                = local.name_prefix
  vpc_id                     = var.vpc_id
  private_subnet_ids         = var.private_subnet_ids
  allowed_security_group_ids = [module.compute.tasks_security_group_id]
  instance_class             = var.postgres_instance_class
  multi_az                   = var.postgres_multi_az
  master_password            = var.postgres_master_password
  deletion_protection        = var.environment == "prod"
  tags                       = local.common_tags
}

module "object_storage" {
  source = "../../modules/object_storage/${var.cloud}"

  bucket_name         = "${local.name_prefix}-documents"
  allowed_origins     = var.aliases
  deletion_protection = var.environment == "prod"
  tags                = local.common_tags
}

module "static_origin" {
  source = "../../modules/object_storage/${var.cloud}"

  bucket_name         = "${local.name_prefix}-static"
  allowed_origins     = var.aliases
  deletion_protection = var.environment == "prod"
  tags                = local.common_tags
}

module "queue" {
  source = "../../modules/queue/${var.cloud}"

  name_prefix                = local.name_prefix
  vpc_id                     = var.vpc_id
  private_subnet_ids         = var.private_subnet_ids
  allowed_security_group_ids = [module.compute.tasks_security_group_id]
  node_type                  = var.queue_node_type
  num_cache_clusters         = var.queue_num_cache_clusters
  tags                       = local.common_tags
}

module "compute" {
  source = "../../modules/compute/${var.cloud}"

  name_prefix         = local.name_prefix
  region              = var.region
  vpc_id              = var.vpc_id
  public_subnet_ids   = var.public_subnet_ids
  private_subnet_ids  = var.private_subnet_ids
  image_prefix        = var.image_prefix
  image_tag           = var.image_tag
  alb_certificate_arn = var.alb_certificate_arn
  api_desired_count   = var.api_desired_count
  worker_desired_count = var.worker_desired_count
  environment = {
    ENVIRONMENT              = var.environment
    LOG_LEVEL                = var.log_level
    AUTH_MODE                = var.auth_mode
    DATABASE_URL             = module.postgres.connection_url
    REDIS_URL                = module.queue.redis_url
    AUDIT_BACKEND            = "postgres"
    DOCUMENT_STORAGE_BACKEND = "s3"
    DOCUMENT_STORAGE_S3_BUCKET = module.object_storage.bucket_name
    DOCUMENT_STORAGE_S3_REGION = module.object_storage.region
    NOTIFICATIONS_BACKEND    = "log_only"
    PAYMENTS_BACKEND         = "log_only"
    ACCESSIBILITY_BACKEND    = "in_memory"
    OTEL_SDK_DISABLED        = "false"
    OTEL_EXPORTER_OTLP_ENDPOINT = var.otel_exporter_endpoint
    CORS_ORIGINS             = join(",", formatlist("https://%s", var.aliases))
  }
  tags = local.common_tags
}

module "cdn" {
  source = "../../modules/cdn/${var.cloud}"

  name_prefix              = local.name_prefix
  alb_dns_name             = module.compute.service_endpoint
  s3_static_origin_domain  = module.static_origin.endpoint
  aliases                  = var.aliases
  cloudfront_certificate_arn = var.cloudfront_certificate_arn
  price_class              = var.cdn_price_class
  tags                     = local.common_tags
}
