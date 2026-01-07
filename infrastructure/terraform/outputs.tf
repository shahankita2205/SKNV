output "rds_endpoints" {
  value = {
    for env in var.envs : env => module.rds[env].db_instance_endpoint
  }
}

output "s3_buckets" {
  value = [for b in module.buckets : b.s3_bucket_id]
}

output "valkey_cache_endpoints" {
  value = {
    for env in var.envs : env => {
      primary_endpoint = aws_elasticache_replication_group.valkey_cache[env].primary_endpoint_address
      reader_endpoint  = aws_elasticache_replication_group.valkey_cache[env].reader_endpoint_address
    }
  }
  description = "ElastiCache endpoints for each environment"
  sensitive   = true
}

output "kafka_bootstrap_brokers_tls" {
  value = {
    for env in var.envs : env => aws_msk_cluster.kafka[env].bootstrap_brokers_tls
  }
  description = "MSK bootstrap broker string (TLS) for each environment"
  sensitive   = true
}
