terraform {
  required_version = ">= 1.6, < 2.0"
}

variable "revision" {
  type    = number
  default = 1
}

variable "generation" {
  type    = number
  default = 1
}

# Built-in lifecycle-only resource: no cloud provider or provisioner.
resource "terraform_data" "lesson" {
  input            = { revision = var.revision }
  triggers_replace = var.generation
}

output "selected_revision" {
  value = terraform_data.lesson.output.revision
}
