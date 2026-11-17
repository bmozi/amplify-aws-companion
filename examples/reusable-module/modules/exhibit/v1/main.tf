terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}

variable "owner" {
  type = string
}

variable "collection" {
  type = string
}

# This records a teaching contract; it creates no AWS object.
resource "terraform_data" "contract" {
  input = {
    owner               = var.owner
    collection          = var.collection
    publication_enabled = false
    schema_version      = 1
  }
}

output "record" {
  value = terraform_data.contract.output
}
