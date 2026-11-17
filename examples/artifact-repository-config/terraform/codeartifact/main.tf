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

resource "aws_codeartifact_domain" "learning" {
  domain = "amplify-aws-learning"

  tags = {
    Purpose = "learning-example"
  }
}

resource "aws_codeartifact_repository" "internal_npm" {
  repository  = "internal-npm"
  domain      = aws_codeartifact_domain.learning.domain
  description = "Internal npm packages; no external upstream is configured in this example."

  tags = {
    Purpose = "learning-example"
  }
}

output "repository_name" {
  value = aws_codeartifact_repository.internal_npm.repository
}
