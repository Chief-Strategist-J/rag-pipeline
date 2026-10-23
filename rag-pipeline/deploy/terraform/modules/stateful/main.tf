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

variable "database_version" {
  type        = string
  description = "Postgres engine version"
  default     = "POSTGRES_15"
}

variable "tier" {
  type        = string
  description = "Machine tier for database instance"
  default     = "db-custom-2-7680"
}

resource "google_sql_database_instance" "rag_db_instance" {
  name             = "sql-rag-${var.environment}-${var.region}"
  database_version = var.database_version
  region           = var.region
  project          = var.project_id

  settings {
    tier              = var.tier
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_size         = 50
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    backup_configuration {
      enabled            = true
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      ipv4_enabled    = false
      require_ssl     = true
    }
  }

  deletion_protection = var.environment == "prod"
}

resource "google_sql_database" "rag_database" {
  name     = "rag_db"
  instance = google_sql_database_instance.rag_db_instance.name
  project  = var.project_id
}

output "instance_connection_name" {
  value = google_sql_database_instance.rag_db_instance.connection_name
}

output "database_name" {
  value = google_sql_database.rag_database.name
}
