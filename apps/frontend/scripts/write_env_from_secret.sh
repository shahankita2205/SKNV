#!/bin/bash

set -euo pipefail

TARGET_DIR="${1:-/var/app/current}"
ENV_FILE="${TARGET_DIR}/.env"
TEMP_ENV_FILE=""

cleanup() {
  if [[ -n "${TEMP_ENV_FILE:-}" && -f "$TEMP_ENV_FILE" ]]; then
    rm -f "$TEMP_ENV_FILE"
  fi
}

trap cleanup EXIT

REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"

CONFIG_JSON=$(/opt/elasticbeanstalk/bin/get-config environment)
SECRET_ARN=$(echo "$CONFIG_JSON" | jq -r '.ENV_SECRET_ARN // empty')

if [[ -z "$SECRET_ARN" ]]; then
  echo "Error: ENV_SECRET_ARN is not set in the environment configuration"
  exit 1
fi

echo "Fetching environment secret from ${SECRET_ARN} for ${TARGET_DIR}..."
SECRET_VALUE=$(aws secretsmanager get-secret-value \
  --secret-id "$SECRET_ARN" \
  --region "$REGION" \
  --output json)

TEMP_ENV_FILE=$(mktemp)

echo "Rendering .env file..."
echo "$SECRET_VALUE" | jq -re '
  .SecretString as $s
  | (try ($s | fromjson) catch $s)
  | if type=="object" then . else error("SecretString is not a JSON object") end
  | to_entries
  | .[] | "\(.key)=\(.value|tostring)"
' > "$TEMP_ENV_FILE"

if [[ ! -s "$TEMP_ENV_FILE" ]]; then
  echo "Error: Rendered .env file is empty"
  exit 1
fi

sudo mkdir -p "$TARGET_DIR"
sudo mv -f "$TEMP_ENV_FILE" "$ENV_FILE"
sudo chown webapp:webapp "$ENV_FILE"
sudo chmod 640 "$ENV_FILE"

echo ".env written to $ENV_FILE (values redacted)"
