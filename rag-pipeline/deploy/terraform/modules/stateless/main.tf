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

variable "network" {
  type        = string
  description = "VPC network name"
  default     = "default"
}

variable "subnetwork" {
  type        = string
  description = "Subnet name"
  default     = "default"
}

resource "google_container_cluster" "rag_gke_cluster" {
  name     = "gke-rag-${var.environment}-${var.region}"
  location = var.region
  project  = var.project_id

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = var.network
  subnetwork = var.subnetwork

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  ip_allocation_policy {}

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
}

resource "google_container_node_pool" "rag_primary_nodes" {
  name       = "np-primary-${var.environment}"
  location   = var.region
  cluster    = google_container_cluster.rag_gke_cluster.name
  project    = var.project_id

  autoscaling {
    min_node_count = 2
    max_node_count = var.environment == "prod" ? 10 : 4
  }

  node_config {
    preemptible  = var.environment == "dev"
    machine_type = "e2-standard-4"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = var.environment
      role        = "rag-worker"
    }
  }
}

output "cluster_name" {
  value = google_container_cluster.rag_gke_cluster.name
}

output "cluster_endpoint" {
  value = google_container_cluster.rag_gke_cluster.endpoint
}
