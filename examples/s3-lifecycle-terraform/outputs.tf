output "bucket_name" {
  description = "Name of the bucket that would be created if this example were applied."
  value       = aws_s3_bucket.lifecycle_lab.id
}

output "lifecycle_scope" {
  description = "Only keys beginning with this prefix are in scope for the example rule."
  value       = "temporary/"
}
