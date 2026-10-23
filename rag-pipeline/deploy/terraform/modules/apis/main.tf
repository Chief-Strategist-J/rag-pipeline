variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "services" {
  type        = list(string)
  description = "List of GCP APIs to enable"
  default = [
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudkms.googleapis.com",
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ]
}

resource "google_project_service" "enabled_apis" {
  for_each                   = toset(var.services)
  project                    = var.project_id
  service                    = each.key
  disable_dependent_services = false
  disable_on_destroy         = false
}

output "enabled_services" {
  value = [for s in google_project_service.enabled_apis : s.service]
}
