terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.83.0, < 7.0.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "lifecycle_lab" {
  bucket        = var.bucket_name
  force_destroy = false

  tags = var.tags
}

resource "aws_s3_bucket_public_access_block" "lifecycle_lab" {
  bucket = aws_s3_bucket.lifecycle_lab.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "lifecycle_lab" {
  bucket = aws_s3_bucket.lifecycle_lab.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_lab" {
  bucket = aws_s3_bucket.lifecycle_lab.id

  rule {
    id     = "temporary-prefix-retention"
    status = "Enabled"

    filter {
      prefix = "temporary/"
    }

    expiration {
      days = var.current_version_expiration_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = var.abort_incomplete_upload_days
    }
  }
}
