resource "aws_secretsmanager_secret" "frontend" {
  for_each = toset(var.envs)
  name     = "nextgen/${each.key}/frontend-env"
}

resource "aws_secretsmanager_secret_version" "frontend_values" {
  for_each = toset(var.envs)

  secret_id     = aws_secretsmanager_secret.frontend[each.key].id
  secret_string = jsonencode({
    NEXT_PUBLIC_API_HOST     = "https://api.example.com",
    NEXT_PUBLIC_POSTHOG_KEY  = "replace-me",
    NEXT_PUBLIC_POSTHOG_HOST = "https://us.i.posthog.com"
  })
}
