#!/bin/bash

set -euo pipefail

AGENT_NAME="logdna-agent"
PKG_MGR="dnf"
WEB_LOG="/var/log/web.stdout.log"
WORKER_LOG="/var/log/worker.stdout.log"
CONFIG_ROOT="/etc/mezmo"
ENV_FILE="${EB_APP_STAGING_DIR:-/var/app/staging}/.env"
AGENT_RPM_URL=${MEZMO_AGENT_RPM_URL:-"https://github.com/logdna/logdna-agent/releases/download/2.2.1/logdna-agent-2.2.1-1.x86_64.rpm"}

if ! command -v dnf >/dev/null 2>&1; then
  if command -v yum >/dev/null 2>&1; then
    PKG_MGR="yum"
  else
    echo "Neither dnf nor yum package manager is available"
    exit 1
  fi
fi

load_mezmo_key() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Environment file $ENV_FILE not found"
    return
  fi

  echo "Reading MEZMO_INGESTION_KEY from $ENV_FILE"
  local line
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      MEZMO_INGESTION_KEY=*)
        local raw_value
        raw_value=${line#MEZMO_INGESTION_KEY=}
        raw_value=${raw_value%$'\r'}
        raw_value=${raw_value%\"}
        raw_value=${raw_value#\"}
        MEZMO_INGESTION_KEY="$raw_value"
        return
        ;;
    esac
  done < "$ENV_FILE"
}

load_mezmo_key

if [ -z "${MEZMO_INGESTION_KEY:-}" ]; then
  echo "MEZMO_INGESTION_KEY not set; skipping Mezmo agent setup"
  exit 0
fi

mkdir -p "$CONFIG_ROOT"

install_prereqs() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "Installing curl via $PKG_MGR"
    $PKG_MGR install -y curl
  fi
}

install_agent() {
  if ! rpm -q $AGENT_NAME >/dev/null 2>&1; then
    echo "Installing $AGENT_NAME from $AGENT_RPM_URL"
    local tmp_rpm
    tmp_rpm=$(mktemp /tmp/logdna-agent-XXXXXX.rpm)
    curl -L "$AGENT_RPM_URL" -o "$tmp_rpm"
    $PKG_MGR install -y "$tmp_rpm"
    rm -f "$tmp_rpm"
  else
    echo "$AGENT_NAME already installed"
  fi
}

derive_env_tag() {
  if [ -n "${ENVIRONMENT:-}" ]; then
    echo "$ENVIRONMENT"
    return
  fi

  if [ -n "${EB_ENVIRONMENT_NAME:-}" ]; then
    local suffix="${EB_ENVIRONMENT_NAME##*-}"
    if [ -n "$suffix" ]; then
      echo "$suffix"
      return
    fi
  fi

  echo "unknown"
}

write_config() {
  local name="$1"
  local log_path="$2"
  local tags="$3"
  local file="$CONFIG_ROOT/${name}.conf"

  cat <<EOF > "$file"
key = $MEZMO_INGESTION_KEY
logdir = $log_path
tags = $tags
hostname = ${EB_ENVIRONMENT_NAME:-$(hostname)}
EOF

  echo "$file"
}

create_service_unit() {
  local name="$1"
  local conf_file="$2"
  local unit="/etc/systemd/system/${AGENT_NAME}-${name}.service"
  local agent_bin

  agent_bin=$(command -v $AGENT_NAME)
  if [ -z "$agent_bin" ]; then
    echo "Unable to find $AGENT_NAME binary"
    exit 1
  fi

  cat <<EOF > "$unit"
[Unit]
Description=Mezmo LogDNA Agent ($name)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$agent_bin -c $conf_file
Restart=always
RestartSec=5
Environment=LOGDNA_PLATFORM=elasticbeanstalk

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable "${AGENT_NAME}-${name}.service"
  systemctl restart "${AGENT_NAME}-${name}.service"
}

configure_agents() {
  local env_tag
  env_tag=$(derive_env_tag)

  echo "Detected environment tag: $env_tag"

  systemctl disable --now $AGENT_NAME >/dev/null 2>&1 || true

  local base_tag="nextgen"
  local web_tags="env:${env_tag},service:api,${base_tag}"
  local worker_tags="env:${env_tag},service:celery,${base_tag}"

  local web_conf
  web_conf=$(write_config "api" "$WEB_LOG" "$web_tags")
  echo "Wrote $web_conf"

  local worker_conf
  worker_conf=$(write_config "celery" "$WORKER_LOG" "$worker_tags")
  echo "Wrote $worker_conf"

  create_service_unit "api" "$web_conf"
  create_service_unit "celery" "$worker_conf"
}

install_prereqs
install_agent
configure_agents
