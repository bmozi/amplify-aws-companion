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

provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "repair_api" {
  name                 = "repair-api"
  image_tag_mutability = "IMMUTABLE"

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Purpose = "learning-example"
  }
}

output "repository_url" {
  value = aws_ecr_repository.repair_api.repository_url
}
