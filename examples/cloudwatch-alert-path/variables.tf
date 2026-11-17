variable "enable_resources" {
  description = "False by default; local validation creates nothing. A live run needs a reviewed role, estimate and cleanup plan."
  type        = bool
  default     = false
}

variable "aws_region" {
  description = "Region for a separately authorized single-account experiment."
  type        = string
  default     = "us-east-2"
}

variable "account_id" {
  description = "Expected 12-digit AWS account ID for the topic policy, required only when enabled."
  type        = string
  default     = ""

  validation {
    condition     = !var.enable_resources || can(regex("^[0-9]{12}$", var.account_id))
    error_message = "Set a 12-digit account_id before enabling resources."
  }
}

variable "name_prefix" {
  description = "Unique disposable teaching prefix; do not reuse an existing alarm or dashboard name."
  type        = string
  default     = "amplify-aws-local"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.name_prefix))
    error_message = "Use 3 to 31 lowercase letters, digits or hyphens, starting with a letter."
  }
}

variable "log_retention_days" {
  description = "Example retention only; replace with an approved investigation/handling rule."
  type        = number
  default     = 7
}

variable "notification_email" {
  description = "Optional consenting recipient for a future live run; an SNS email subscription requires confirmation."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Disposable lab ownership and cost attribution tags."
  type        = map(string)
  default = {
    Project = "amplify-aws-lab"
    Purpose = "cloudops-teaching"
  }
}
