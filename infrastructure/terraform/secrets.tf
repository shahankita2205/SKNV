module "secrets" {
  source = "./modules/secrets"
  envs   = var.envs
  db_endpoints = {
    for env in var.envs : env => module.rds[env].db_instance_endpoint
  }
}

module "frontend_secrets" {
  source = "./modules/frontend_secrets"
  envs   = var.envs
}
