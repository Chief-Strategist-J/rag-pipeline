variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP primary region"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
}

resource "google_storage_bucket" "artifacts_bucket" {
  name                        = "bkt-rag-artifacts-${var.environment}-${var.project_id}"
  location                    = var.region
  project                     = var.project_id
  uniform_bucket_level_access = true
  force_destroy               = var.environment != "prod"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 3
      with_state         = "ARCHIVED"
    }
  }
}

output "bucket_name" {
  value = google_storage_bucket.artifacts_bucket.name
}

output "bucket_url" {
  value = google_storage_bucket.artifacts_bucket.url
}
