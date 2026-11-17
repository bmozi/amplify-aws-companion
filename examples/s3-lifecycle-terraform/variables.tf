variable "aws_region" {
  description = "Region for a future, separately reviewed lab bucket."
  type        = string
}

variable "bucket_name" {
  description = "Globally unique name for a new, disposable lab bucket."
  type        = string

  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63
    error_message = "The bucket name must contain between 3 and 63 characters."
  }
}

variable "current_version_expiration_days" {
  description = "Example age, in days, when the current temporary object version becomes eligible for expiration."
  type        = number
  default     = 30

  validation {
    condition     = var.current_version_expiration_days >= 1 && floor(var.current_version_expiration_days) == var.current_version_expiration_days
    error_message = "Use a whole number of at least one day."
  }
}

variable "noncurrent_version_expiration_days" {
  description = "Example age, in days, when an older temporary object version becomes eligible for permanent deletion."
  type        = number
  default     = 90

  validation {
    condition     = var.noncurrent_version_expiration_days >= 1 && floor(var.noncurrent_version_expiration_days) == var.noncurrent_version_expiration_days
    error_message = "Use a whole number of at least one day."
  }
}

variable "abort_incomplete_upload_days" {
  description = "Example age, in days, when incomplete multipart uploads under the temporary prefix are aborted."
  type        = number
  default     = 7

  validation {
    condition     = var.abort_incomplete_upload_days >= 1 && floor(var.abort_incomplete_upload_days) == var.abort_incomplete_upload_days
    error_message = "Use a whole number of at least one day."
  }
}

variable "tags" {
  description = "Non-sensitive labels for the disposable lab bucket."
  type        = map(string)
  default     = {}
}
