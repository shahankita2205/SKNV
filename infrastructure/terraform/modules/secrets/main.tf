resource "aws_secretsmanager_secret" "secrets" {
  for_each = toset(var.envs)
  name = "nextgen/${each.key}/env"
}

resource "aws_secretsmanager_secret_version" "secret_values" {
  for_each = toset(var.envs)
  secret_id     = aws_secretsmanager_secret.secrets[each.key].id
  secret_string = jsonencode({
    DJANGO_SECRET_KEY       = "replace-me",
    MYSKNV_DB_ENGINE        = "django.db.backends.mysql",
    MYSKNV_DB_NAME          = "mypc4",
    MYSKNV_DB_USER          = "mypc",
    MYSKNV_DB_PASSWORD      = "replace-me",
    MYSKNV_DB_HOST          = "mysknv-new.cul8gghbdlme.us-east-1.rds.amazonaws.com",
    MYSKNV_DB_PORT          = "3306",
    FRED_DB_ENGINE          = "django.db.backends.postgresql",
    FRED_DB_NAME            = "fred_preprod",
    FRED_DB_USER            = "fred",
    FRED_DB_PASSWORD        = "replace-me",
    FRED_DB_HOST            = "freddev-new.cul8gghbdlme.us-east-1.rds.amazonaws.com",
    FRED_DB_PORT            = "5432",
    FRED_API                = "https://api.fred.sknv.dev",
    AWS_ACCESS_KEY_ID       = "replace-me",
    AWS_SECRET_ACCESS_KEY   = "replace-me",
    AWS_STORAGE_BUCKET_NAME = "sknv-nextgen-${each.key}",
    AWS_S3_REGION_NAME      = "us-east-1",
    TWILIO_ACCOUNT_SID      = "replace-me",
    TWILIO_AUTH_TOKEN       = "replace-me",
    DB_NAME                 = "nextgen",
    DB_HOST                 = var.db_endpoints[each.key]
  })
}
