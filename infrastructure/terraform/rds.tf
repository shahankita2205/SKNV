module "rds" {
  source   = "terraform-aws-modules/rds/aws"
  version  = "~> 6.13"
  for_each = toset(var.envs)

  identifier        = "nextgen-${each.key}"
  engine            = "postgres"
  engine_version    = "15"
  family            = "postgres15"
  instance_class    = "db.t4g.medium"
  allocated_storage = 20

  db_name  = "nextgen"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds[each.key].id]
  subnet_ids             = local.rds_subnets
  multi_az               = true
  publicly_accessible    = false
  skip_final_snapshot    = true
  create_db_subnet_group = true
}

resource "aws_security_group" "rds" {
  for_each    = toset(var.envs)
  name        = "nextgen-rds-${each.key}"
  description = "Security group for RDS Postgres ${each.key} environment"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Note: Consider restricting this to specific IP ranges in production
  }
}
