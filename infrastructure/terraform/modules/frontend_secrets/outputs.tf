output "secret_arns" {
  description = "ARNs of the frontend secrets"
  value = {
    for env, secret in aws_secretsmanager_secret.frontend : env => secret.arn
  }
}
