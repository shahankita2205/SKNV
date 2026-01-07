#!/bin/bash

set -euo pipefail

APP_DIR="/var/app/current"
ENV_FILE="${APP_DIR}/.env"
TEMP_ENV_FILE=$(mktemp)

# Clean up the temp file on exit
trap 'rm -f "$TEMP_ENV_FILE"' EXIT

ENV_ARN=$(/opt/elasticbeanstalk/bin/get-config environment | jq -r '.ENV_SECRET_ARN')
DB_ARN=$(/opt/elasticbeanstalk/bin/get-config environment | jq -r '.DB_SECRET_ARN')

# Get the raw secret value
echo "Fetching secret from $ENV_ARN..."
SECRET_VALUE=$(aws secretsmanager get-secret-value \
    --secret-id "$ENV_ARN" \
    --region us-east-1 \
    --output json) || {
    echo "Error: Failed to fetch secret"
    echo "Command: aws secretsmanager get-secret-value --secret-id \"$ENV_ARN\" --region us-east-1"
    aws secretsmanager get-secret-value --secret-id "$ENV_ARN" --region us-east-1 --debug
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

if [ -n "${DB_ARN:-}" ]; then
    echo "Fetching DB password from $DB_ARN..."
    DB_SECRET_VALUE=$(aws secretsmanager get-secret-value \
        --secret-id "$DB_ARN" \
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

# Write the new environment file to the temporary location
printf "%s\n" "$ENV_LINES" > "$TEMP_ENV_FILE"
JQ_EXIT=$?

if [ $JQ_EXIT -ne 0 ]; then
    echo "Error: Failed to parse secrets into environment variables"
    echo "jq exit code: $JQ_EXIT"
    exit 1
fi

# Verify the temp file has content
if [ ! -s "$TEMP_ENV_FILE" ]; then
    echo "Error: Temporary .env file is empty or was not created"
    exit 1
fi

# Compare the new .env file with the existing one
if [ -f "$ENV_FILE" ] && cmp -s "$TEMP_ENV_FILE" "$ENV_FILE"; then
    echo "No changes detected in the .env file. Nothing to do."
    exit 0
fi

echo "Changes detected. Updating .env file..."
# Overwrite the existing .env file
sudo mv -f "$TEMP_ENV_FILE" "$ENV_FILE"

# Verify the file was created and has content
if [ ! -s "$ENV_FILE" ]; then
    echo "Error: .env file is empty or was not created"
    exit 1
fi

echo "Successfully created .env file. First few lines (secrets redacted):"
head -n 3 "$ENV_FILE" | sed 's/=.*/=****/'

# Ensure proper permissions
sudo chown webapp:webapp "$ENV_FILE"
sudo chmod 644 "$ENV_FILE"

echo "Restarting web service..."
sudo systemctl restart web.service

echo "Successfully created and secured .env file with secrets at $ENV_FILE"
