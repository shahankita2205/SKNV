#!/bin/bash

# Exit on error
set -euo pipefail

# Determine the correct staging directory
APP_STAGING_DIR="${EB_APP_STAGING_DIR:-/var/app/staging}"
ENV_FILE="${APP_STAGING_DIR}/.env"

echo "Debug: Current environment:"
env | sort

# Ensure AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    yum install -y awscli
fi

# Get environment name from EB environment variables
# The environment name is available in several places, try them all
EB_ENV=${EB_ENVIRONMENT_NAME:-${HOSTNAME:-unknown}}
echo "Environment name: $EB_ENV"

# Get secrets from AWS Secrets Manager using the ARN provided in ENV_SECRET_ARN
if [ -z "${ENV_SECRET_ARN:-}" ]; then
    echo "Error: ENV_SECRET_ARN is not set"
    exit 1
fi

# Get the secrets
echo "Retrieving secrets from Secrets Manager..."
echo "Using secret ARN: $ENV_SECRET_ARN"

# First verify we can access AWS
aws sts get-caller-identity || {
    echo "Error: Unable to call AWS. Check instance role and permissions"
    aws sts get-caller-identity --debug
    exit 1
}

# Get the raw secret value
echo "Fetching secret from $ENV_SECRET_ARN..."
SECRET_VALUE=$(aws secretsmanager get-secret-value \
    --secret-id "$ENV_SECRET_ARN" \
    --region us-east-1 \
    --output json) || {
    echo "Error: Failed to fetch secret"
    echo "Command: aws secretsmanager get-secret-value --secret-id \"$ENV_SECRET_ARN\" --region us-east-1"
    aws secretsmanager get-secret-value --secret-id "$ENV_SECRET_ARN" --region us-east-1 --debug
    exit 1
}

echo "Debug: Successfully retrieved secret (value redacted)"

# Extract and parse SecretString into KEY=VALUE lines
# Handles both cases where SecretString is a JSON string (common) or already a JSON object
echo "Debug: Extracting SecretString and converting to .env format..."
ENV_LINES=$(echo "$SECRET_VALUE" | jq -re '
  .SecretString as $s
  | (try ($s | fromjson) catch $s)
  | if type=="object" then . else error("SecretString is not a JSON object") end
  | to_entries
  | .[] | "\(.key)=\(.value)"
')

# Get DB password if DB_SECRET_ARN is set
if [ -n "${DB_SECRET_ARN:-}" ]; then
    echo "Fetching DB password from $DB_SECRET_ARN..."
    DB_SECRET_VALUE=$(aws secretsmanager get-secret-value \
        --secret-id "$DB_SECRET_ARN" \
        --region us-east-1 \
        --output json) || {
        echo "Error: Failed to fetch DB secret"
        exit 1
    }
    
    DB_PASSWORD=$(echo "$DB_SECRET_VALUE" | jq -re '
        .SecretString as $s
        | (try ($s | fromjson) catch $s)
        | if type=="object" then .password else error("SecretString is not a JSON object") end
    ')
    DB_PASSWORD_ESCAPED=$(printf '%s' "$DB_PASSWORD" | sed 's/"/\\"/g')
    
    # Add DB_PASSWORD to ENV_LINES
    ENV_LINES="${ENV_LINES}"$'\n'"DB_PASSWORD=\"${DB_PASSWORD_ESCAPED}\""
fi

echo "Writing secrets to $ENV_FILE..."
# Write the .env file atomically
printf "%s\n" "$ENV_LINES" > "$ENV_FILE"
JQ_EXIT=$?

if [ $JQ_EXIT -ne 0 ]; then
    echo "Error: Failed to parse secrets into environment variables"
    echo "jq exit code: $JQ_EXIT"
    exit 1
fi

# Verify the file was created and has content
if [ ! -s "$ENV_FILE" ]; then
    echo "Error: .env file is empty or was not created"
    exit 1
fi

echo "Successfully created .env file. First few lines (secrets redacted):"
head -n 3 "$ENV_FILE" | sed 's/=.*/=****/'

# Ensure proper permissions
chown webapp:webapp "$ENV_FILE"
chmod 644 "$ENV_FILE"

echo "Successfully created and secured .env file with secrets at $ENV_FILE"
