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

variable "subnet_cidr" {
  type        = string
  description = "Primary subnet CIDR"
  default     = "10.0.0.0/20"
}

variable "pods_cidr" {
  type        = string
  description = "Secondary CIDR for GKE Pods"
  default     = "10.4.0.0/14"
}

variable "services_cidr" {
  type        = string
  description = "Secondary CIDR for GKE Services"
  default     = "10.8.0.0/20"
}

resource "google_compute_network" "vpc_network" {
  name                    = "vpc-rag-${var.environment}"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "subnet" {
  name                     = "sb-rag-${var.environment}-${var.region}"
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.vpc_network.id
  project                  = var.project_id
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }
}

output "network_name" {
  value = google_compute_network.vpc_network.name
}

output "network_id" {
  value = google_compute_network.vpc_network.id
}

output "subnetwork_name" {
  value = google_compute_subnetwork.subnet.name
}

output "subnetwork_id" {
  value = google_compute_subnetwork.subnet.id
}
