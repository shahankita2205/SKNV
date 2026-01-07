variable "aws_region" {
  default = "us-east-1"
}

variable "db_username" {}
variable "db_password" {}

variable "envs" {
  description = "List of environments to create"
  type        = list(string)
  default     = []
}

variable "kafka_version" {
  description = "Apache Kafka version to provision in the MSK cluster"
  type        = string
  default     = "3.6.0"
}

variable "kafka_broker_instance_type" {
  description = "Instance type for MSK broker nodes"
  type        = string
  default     = "kafka.t3.small"
}

variable "kafka_broker_volume_size" {
  description = "EBS storage size (GiB) for each MSK broker node"
  type        = number
  default     = 100
}
