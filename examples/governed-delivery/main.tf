terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}

variable "owner" { type = string }
variable "module_version" { type = string }
variable "action" { type = string }
variable "resource_scope" { type = string }
variable "pause_auto_builds" { type = bool }

# This is a proposal record, not an AWS IAM policy or an Amplify setting.
resource "terraform_data" "delivery_proposal" {
  input = {
    owner             = var.owner
    module_version    = var.module_version
    action            = var.action
    resource_scope    = var.resource_scope
    pause_auto_builds = var.pause_auto_builds
  }
}
