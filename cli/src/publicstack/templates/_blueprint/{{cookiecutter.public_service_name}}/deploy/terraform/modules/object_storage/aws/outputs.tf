output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}

output "endpoint" {
  description = "Regional S3 endpoint hostname; the document_storage adapter targets this."
  value       = "${aws_s3_bucket.this.bucket}.s3.${aws_s3_bucket.this.region}.amazonaws.com"
}

output "region" {
  value = aws_s3_bucket.this.region
}
