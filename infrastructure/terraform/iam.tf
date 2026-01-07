resource "aws_iam_role" "eb_ec2" {
  name = "nextgen-eb-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "eb_ec2" {
  name = "nextgen-eb-ec2-profile"
  role = aws_iam_role.eb_ec2.name
}

resource "aws_iam_role_policy_attachment" "eb_web_tier" {
  role       = aws_iam_role.eb_ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_role_policy" "secrets_access" {
  name = "nextgen-secrets-access"
  role = aws_iam_role.eb_ec2.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = concat(
          [for env in var.envs :
            "arn:aws:secretsmanager:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:secret:nextgen/${env}/*"
          ],
          [
            "arn:aws:secretsmanager:us-east-1:861005430179:secret:rds!db-b12b15a2-1f54-4318-b20a-7941447467ab-kaBoZD",
            "arn:aws:secretsmanager:us-east-1:861005430179:secret:rds!db-32c26e6d-fc34-4ec8-a4e3-3bcfb732fa04-vXB2AM"
          ]
        )
      }
    ]
  })
}

# Get current region and account ID for ARN construction
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
