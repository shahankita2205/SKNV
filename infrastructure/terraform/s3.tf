locals {
  bucket_mapping = {
    "prod" = ["sknv-nextgen"]
    "test" = ["sknv-nextgen-test", "sknv-nextgen-dev"]
  }
}

module "buckets" {
  source = "terraform-aws-modules/s3-bucket/aws"
  for_each = toset(flatten([
    for env in var.envs : local.bucket_mapping[env]
  ]))
  bucket                   = each.key
  force_destroy            = true
  control_object_ownership = true
  object_ownership         = "BucketOwnerEnforced"
}
