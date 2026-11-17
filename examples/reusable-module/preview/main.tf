terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}

module "exhibit" {
  source     = "../modules/exhibit/v1"
  owner      = "preview-team"
  collection = "preview-exhibit"
}

output "record" {
  value = module.exhibit.record
}
