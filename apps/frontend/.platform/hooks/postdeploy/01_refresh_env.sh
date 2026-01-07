#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# Re-create .env inside /var/app/current after the swap to ensure permissions are correct.
bash "${PROJECT_ROOT}/scripts/write_env_from_secret.sh" "/var/app/current"
