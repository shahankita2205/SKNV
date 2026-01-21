resource "aws_security_group" "kafka" {
  for_each    = toset(var.envs)
  name        = "nextgen-kafka-${each.key}"
  description = "Security group for MSK cluster in ${each.key}"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "Kafka TLS traffic from Elastic Beanstalk instances"
    from_port       = 9094
    to_port         = 9094
    protocol        = "tcp"
    security_groups = [aws_security_group.eb_ec2[each.key].id]
  }

  ingress {
    description     = "Kafka plaintext traffic from Elastic Beanstalk instances"
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    security_groups = [aws_security_group.eb_ec2[each.key].id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "nextgen-kafka-${each.key}"
    Environment = each.key
  }
}

resource "aws_msk_cluster" "kafka" {
  for_each = toset(var.envs)

  cluster_name           = "nextgen-${each.key}-kafka"
  kafka_version          = var.kafka_version
  number_of_broker_nodes = length(local.rds_subnets)
  enhanced_monitoring    = "DEFAULT"

  broker_node_group_info {
    instance_type  = var.kafka_broker_instance_type
    client_subnets = local.rds_subnets
    security_groups = [
      aws_security_group.kafka[each.key].id
    ]

    storage_info {
      ebs_storage_info {
        volume_size = var.kafka_broker_volume_size
      }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  tags = {
    Name        = "nextgen-${each.key}-kafka"
    Environment = each.key
  }
}
