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

resource "google_artifact_registry_repository" "docker_repo" {
  provider      = google
  project       = var.project_id
  location      = var.region
  repository_id = "rag-repo-${var.environment}"
  description   = "Docker container registry for RAG pipeline images"
  format        = "DOCKER"

  docker_config {
    immutable_tags = var.environment == "prod"
  }
}

output "repository_id" {
  value = google_artifact_registry_repository.docker_repo.repository_id
}

output "repository_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}
