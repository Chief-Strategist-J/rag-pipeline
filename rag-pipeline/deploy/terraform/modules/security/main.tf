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
  description = "Target environment (dev, staging, prod)"
}

resource "google_kms_key_ring" "rag_keyring" {
  name     = "kr-rag-${var.environment}-${var.region}"
  location = var.region
  project  = var.project_id
}

resource "google_kms_crypto_key" "rag_storage_key" {
  name            = "ck-rag-storage-${var.environment}"
  key_ring        = google_kms_key_ring.rag_keyring.id
  rotation_period = "7776000s"
}

output "keyring_id" {
  value = google_kms_key_ring.rag_keyring.id
}

output "crypto_key_id" {
  value = google_kms_crypto_key.rag_storage_key.id
}
