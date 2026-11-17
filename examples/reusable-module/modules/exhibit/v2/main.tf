terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}

variable "owner" {
  type = string
}

variable "collection" {
  type = string
}

variable "retention_days" {
  type = number
  validation {
    condition     = var.retention_days >= 1 && var.retention_days <= 30 && floor(var.retention_days) == var.retention_days
    error_message = "Choose a whole-day teaching retention from 1 through 30."
  }
}

# The new field is a recorded decision, not an S3 Lifecycle rule.
resource "terraform_data" "contract" {
  input = {
    owner               = var.owner
    collection          = var.collection
    publication_enabled = false
    retention_days      = var.retention_days
    schema_version      = 2
  }
}

output "record" {
  value = terraform_data.contract.output
}
