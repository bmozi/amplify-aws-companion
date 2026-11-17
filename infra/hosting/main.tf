terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.100.0"
    }
  }
}

variable "account_id" {
  type        = string
  description = "Reviewed target AWS account; deliberately has no default."
  validation {
    condition     = can(regex("^[0-9]{12}$", var.account_id))
    error_message = "Supply the confirmed 12-digit AWS account ID."
  }
}

variable "region" {
  type        = string
  description = "Reviewed AWS Region; deliberately has no default."
}

variable "resource_owner" {
  type        = string
  description = "Person or team responsible for the adapted resource lifecycle; no default."
}

provider "aws" {
  region              = var.region
  allowed_account_ids = [var.account_id]
  default_tags {
    tags = {
      Project   = "amplify-learning-lab"
      Owner     = var.resource_owner
      ManagedBy = "Terraform"
      Purpose   = "Learning"
    }
  }
}

# Terraform owns Hosting; Amplify Gen 2 owns the deployed backend. Git integration is a separate exercise.
resource "aws_amplify_app" "lab" {
  name     = "amplify-learning-lab"
  platform = "WEB"
}

resource "aws_amplify_branch" "lab" {
  app_id            = aws_amplify_app.lab.id
  branch_name       = "lab"
  stage             = "DEVELOPMENT"
  enable_auto_build = false
}

output "app_id" {
  value = aws_amplify_app.lab.id
}

output "hosting_domain" {
  description = "Hosting domain; does not prove content has been deployed."
  value       = "${aws_amplify_branch.lab.branch_name}.${aws_amplify_app.lab.default_domain}"
}
