#!/bin/bash

set -euo pipefail

cd /var/app/staging

if ! command -v corepack >/dev/null 2>&1; then
  npm install -g corepack
fi

sudo -u webapp bash -lc 'corepack enable && rm -rf "$HOME/.cache/yarn/v6" && yarn install --immutable'
