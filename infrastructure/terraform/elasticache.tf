resource "aws_elasticache_subnet_group" "valkey_cache_subnet_group" {
  for_each = toset(var.envs)

  name       = "valkey-cache-subnet-group-${each.value}"
  subnet_ids = ["subnet-76355a13"] # Using the same subnet as Elastic Beanstalk
}

resource "aws_security_group" "valkey_cache_sg" {
  for_each = toset(var.envs)

  name_prefix = "valkey-cache-sg-${each.value}"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eb_ec2[each.value].id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "valkey-cache-sg-${each.value}"
    Environment = each.value
  }
}

resource "aws_elasticache_parameter_group" "valkey_cache_params" {
  for_each = toset(var.envs)

  family = "redis7"
  name   = "valkey-cache-params-${each.value}"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
}

resource "aws_elasticache_replication_group" "valkey_cache" {
  for_each = toset(var.envs)

  replication_group_id       = "valkey-cache-${each.value}"
  description                = "ValKey cache cluster for ${each.value} environment"
  node_type                  = each.value == "prod" ? "cache.t3.medium" : "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = aws_elasticache_parameter_group.valkey_cache_params[each.value].name
  automatic_failover_enabled = each.value == "prod" ? true : false
  num_cache_clusters         = each.value == "prod" ? 2 : 1
  security_group_ids         = [aws_security_group.valkey_cache_sg[each.value].id]
  subnet_group_name          = aws_elasticache_subnet_group.valkey_cache_subnet_group[each.value].name
  engine                     = "redis"
  engine_version             = "7.0"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name        = "valkey-cache-${each.value}"
    Environment = each.value
  }
}
