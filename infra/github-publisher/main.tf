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
  description = "The reviewed AWS account that owns the Amplify app."
  validation {
    condition     = can(regex("^[0-9]{12}$", var.account_id))
    error_message = "Supply a confirmed 12-digit AWS account ID."
  }
}

variable "region" {
  type        = string
  description = "Region containing the manually deployed Amplify app."
  default     = "us-east-2"
}

variable "amplify_app_id" {
  type        = string
  description = "Exact existing Amplify Hosting app to publish."
  validation {
    condition     = can(regex("^d[a-z0-9]+$", var.amplify_app_id))
    error_message = "Supply the exact Amplify app ID."
  }
}

variable "amplify_branch" {
  type        = string
  description = "Exact existing manual-deploy branch to publish."
  validation {
    condition     = length(var.amplify_branch) > 0 && !can(regex("[?*]", var.amplify_branch))
    error_message = "Use one exact branch name without IAM wildcards."
  }
}

variable "budget_name" {
  type        = string
  description = "Exact existing monthly cost budget that must have room before publication."
  validation {
    condition     = length(var.budget_name) > 0
    error_message = "Supply the exact existing AWS Budget name."
  }
}

variable "github_owner" {
  type        = string
  description = "GitHub owner name; kept with IDs for readable trust review."
}

variable "github_owner_id" {
  type        = string
  description = "Immutable numeric GitHub owner ID used in this repo's OIDC subject."
  validation {
    condition     = can(regex("^[0-9]+$", var.github_owner_id))
    error_message = "Supply the numeric owner ID from GitHub repository metadata."
  }
}

variable "github_repository" {
  type        = string
  description = "GitHub repository name, without its owner."
}

variable "github_repository_id" {
  type        = string
  description = "Immutable numeric GitHub repository ID used in this repo's OIDC subject."
  validation {
    condition     = can(regex("^[0-9]+$", var.github_repository_id))
    error_message = "Supply the numeric repository ID from GitHub repository metadata."
  }
}

variable "github_oidc_provider_arn" {
  type        = string
  description = "Verified existing account-level provider ARN; leave empty only when the provider does not exist."
  default     = ""
  validation {
    condition     = var.github_oidc_provider_arn == "" || can(regex("^arn:aws:iam::[0-9]{12}:oidc-provider/token.actions.githubusercontent.com$", var.github_oidc_provider_arn))
    error_message = "Use the verified GitHub OIDC provider ARN or leave empty to create it."
  }
}

variable "github_branch" {
  type        = string
  description = "Only this source branch may request the AWS role."
  default     = "main"
}

provider "aws" {
  region              = var.region
  allowed_account_ids = [var.account_id]
  default_tags {
    tags = {
      Project   = "personal-amplify-lab"
      Purpose   = "Static Amplify Hosting publication only"
      ManagedBy = "Terraform"
    }
  }
}

# One account-level GitHub provider can be shared by multiple deliberately
# scoped roles. Supply its ARN when another stack already owns it; otherwise
# this Terraform root creates it.
resource "aws_iam_openid_connect_provider" "github" {
  count          = var.github_oidc_provider_arn == "" ? 1 : 0
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]

  # This provider is account-wide. A publisher-root destroy or forced
  # replacement must stop until its other role dependencies are reviewed.
  lifecycle {
    prevent_destroy = true
  }
}

locals {
  github_subject = "repo:${var.github_owner}@${var.github_owner_id}/${var.github_repository}@${var.github_repository_id}:ref:refs/heads/${var.github_branch}"
  # Each OIDC job gets a separate role and the exact name claim it expects.
  # A workflow name can be copied; repository write review remains essential.
  publisher_workflow_name    = "Publish the Amplify lab frontend"
  probe_workflow_name        = "Probe the Amplify reader identity without deploying"
  publisher_job_workflow_ref = "${var.github_owner}/${var.github_repository}/.github/workflows/reusable-amplify-publish.yml@refs/heads/${var.github_branch}"
  branch_arn                 = "arn:aws:amplify:${var.region}:${var.account_id}:apps/${var.amplify_app_id}/branches/${var.amplify_branch}"
  github_oidc_provider_arn   = var.github_oidc_provider_arn != "" ? var.github_oidc_provider_arn : aws_iam_openid_connect_provider.github[0].arn
}

data "aws_iam_policy_document" "github_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.github_oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [local.github_subject]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:workflow"
      values   = [local.publisher_workflow_name]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:job_workflow_ref"
      values   = [local.publisher_job_workflow_ref]
    }
  }
}

data "aws_iam_policy_document" "probe_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.github_oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [local.github_subject]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:workflow"
      values   = [local.probe_workflow_name]
    }
  }
}

resource "aws_iam_role" "publisher" {
  name                 = "AmplifyLabGitHubPublisher"
  assume_role_policy   = data.aws_iam_policy_document.github_trust.json
  max_session_duration = 3600
  description          = "Publishes built static files to one Amplify app branch from one GitHub branch."

  lifecycle {
    precondition {
      condition     = var.github_oidc_provider_arn == "" || var.github_oidc_provider_arn == "arn:aws:iam::${var.account_id}:oidc-provider/token.actions.githubusercontent.com"
      error_message = "The supplied GitHub OIDC provider must belong to the configured AWS account."
    }
  }
}

data "aws_iam_policy_document" "publish" {
  statement {
    sid       = "CreateAndStartDeploymentForOneBranch"
    effect    = "Allow"
    actions   = ["amplify:CreateDeployment", "amplify:StartDeployment"]
    resources = [local.branch_arn]
  }

  statement {
    sid       = "ReadJobsForOneBranch"
    effect    = "Allow"
    actions   = ["amplify:GetJob"]
    resources = ["${local.branch_arn}/jobs/*"]
  }

  # Free Tier does not offer resource-level ARNs for this read-only action.
  # The workflow fails closed before publication when it cannot check credits.
  statement {
    sid       = "ReadCurrentFreePlanForPublicationGate"
    effect    = "Allow"
    actions   = ["freetier:GetAccountPlanState"]
    resources = ["*"]
  }

  statement {
    sid       = "ReadOneMonthlyCostBudgetForPublicationGate"
    effect    = "Allow"
    actions   = ["budgets:ViewBudget"]
    resources = ["arn:aws:budgets::${var.account_id}:budget/${var.budget_name}"]
  }
}

resource "aws_iam_role_policy" "publish" {
  name   = "PublishOneAmplifyBranch"
  role   = aws_iam_role.publisher.id
  policy = data.aws_iam_policy_document.publish.json
}

resource "aws_iam_role" "probe" {
  name                 = "AmplifyLabGitHubProbeReader"
  assume_role_policy   = data.aws_iam_policy_document.probe_trust.json
  max_session_duration = 3600
  description          = "Reads one Amplify branch, the Free plan and one budget from the named GitHub probe workflow."

  lifecycle {
    precondition {
      condition     = var.github_oidc_provider_arn == "" || var.github_oidc_provider_arn == "arn:aws:iam::${var.account_id}:oidc-provider/token.actions.githubusercontent.com"
      error_message = "The supplied GitHub OIDC provider must belong to the configured AWS account."
    }
  }
}

data "aws_iam_policy_document" "probe_read" {
  statement {
    sid       = "ReadJobsForOneBranch"
    effect    = "Allow"
    actions   = ["amplify:GetJob"]
    resources = ["${local.branch_arn}/jobs/*"]
  }

  # AWS Free Tier defines no resource-level ARN for this read action.
  statement {
    sid       = "ReadCurrentFreePlan"
    effect    = "Allow"
    actions   = ["freetier:GetAccountPlanState"]
    resources = ["*"]
  }

  statement {
    sid       = "ReadOneMonthlyCostBudget"
    effect    = "Allow"
    actions   = ["budgets:ViewBudget"]
    resources = ["arn:aws:budgets::${var.account_id}:budget/${var.budget_name}"]
  }
}

resource "aws_iam_role_policy" "probe_read" {
  name   = "ReadOneAmplifyBranchAndCostGates"
  role   = aws_iam_role.probe.id
  policy = data.aws_iam_policy_document.probe_read.json
}

output "publisher_role_arn" {
  description = "Set as the protected GitHub repository variable only after review and role verification."
  value       = aws_iam_role.publisher.arn
}

output "probe_role_arn" {
  description = "Exact read-only probe role to verify before enabling the GitHub probe workflow."
  value       = aws_iam_role.probe.arn
}

output "github_oidc_provider_arn" {
  description = "Shared account-level provider used by the trust policy."
  value       = local.github_oidc_provider_arn
}

output "github_oidc_subject" {
  description = "Exact GitHub subject claim the trust policy accepts."
  value       = local.github_subject
}

output "amplify_branch_resource" {
  description = "The only branch resource this publisher policy can change."
  value       = local.branch_arn
}
