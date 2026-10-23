variable "project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "rag-prod-project"
}

variable "region" {
  type        = string
  description = "GCP primary region"
  default     = "us-central1"
}

locals {
  environment = "prod"
}

module "apis" {
  source     = "../../modules/apis"
  project_id = var.project_id
}

module "network" {
  source      = "../../modules/network"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  depends_on  = [module.apis]
}

module "iam" {
  source      = "../../modules/iam"
  project_id  = var.project_id
  environment = local.environment
  depends_on  = [module.apis]
}

module "security" {
  source      = "../../modules/security"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  depends_on  = [module.apis]
}

module "storage" {
  source      = "../../modules/storage"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  depends_on  = [module.apis]
}

module "registry" {
  source      = "../../modules/registry"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  depends_on  = [module.apis]
}

module "stateful" {
  source      = "../../modules/stateful"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  depends_on  = [module.network]
}

module "stateless" {
  source      = "../../modules/stateless"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  network     = module.network.network_name
  subnetwork  = module.network.subnetwork_name
  depends_on  = [module.network, module.iam]
}
