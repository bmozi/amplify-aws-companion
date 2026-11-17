terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.69.1"
    }
  }
}

variable "aws_region" {
  description = "Choose and review a Region before any future deployment."
  type        = string
}

variable "bucket_name" {
  description = "Globally unique lowercase bucket name for a private artifact bucket."
  type        = string

  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63 && can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.bucket_name))
    error_message = "Use 3-63 lowercase letters, digits, periods or hyphens, starting and ending with a letter or digit."
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "release_artifacts" {
  bucket        = var.bucket_name
  force_destroy = false

  tags = {
    Purpose = "learning-example"
  }
}

resource "aws_s3_bucket_public_access_block" "release_artifacts" {
  bucket                  = aws_s3_bucket.release_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "release_artifacts" {
  bucket = aws_s3_bucket.release_artifacts.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "release_artifacts" {
  bucket = aws_s3_bucket.release_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_name" {
  value = aws_s3_bucket.release_artifacts.id
}
