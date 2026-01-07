terraform {
  backend "s3" {
    key = "terraform.tfstate"
    # Other settings like bucket and region will be passed via -backend-config
    # during terraform init to keep environments separate
  }
}
