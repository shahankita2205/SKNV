provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "sknv-nextgen-terraform-state"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name           = "nextgen-terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

# Output the state bucket and dynamodb table names for reference
output "state_bucket" {
  value = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table" {
  value = aws_dynamodb_table.terraform_locks.name
}
