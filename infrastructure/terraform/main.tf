terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.2"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Use default VPC
data "aws_vpc" "default" {
  default = true
}

# Get public subnets for ELB
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "map-public-ip-on-launch"
    values = [true]
  }
}

# Get private subnets for instances
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "map-public-ip-on-launch"
    values = [false]
  }
}

# Get default VPC subnets and their details
data "aws_subnet" "all" {
  for_each = toset(data.aws_subnets.all.ids)
  id       = each.value
}

data "aws_subnets" "all" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

locals {
  # Group subnets by AZ and get one subnet per AZ
  subnets_by_az = {
    for subnet_id, subnet in data.aws_subnet.all : subnet.availability_zone => subnet_id...
  }

  # Get one subnet from us-east-1a for EC2 instances
  ec2_subnet = [
    for az, subnets in local.subnets_by_az :
    subnets[0] if az == "us-east-1a"
  ]

  # Get one subnet from us-east-1b for ELB
  elb_subnet = [
    for az, subnets in local.subnets_by_az :
    subnets[0] if az == "us-east-1b"
  ]

  # All subnets for RDS (needs multi-AZ)
  rds_subnets = concat(local.ec2_subnet, local.elb_subnet)
}