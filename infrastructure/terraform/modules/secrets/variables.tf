variable "envs" {
  type = list(string)
}

variable "db_endpoints" {
  description = "Map of environment names to their RDS endpoints"
  type        = map(string)
}
