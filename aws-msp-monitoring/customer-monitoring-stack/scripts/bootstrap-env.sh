#!/bin/bash
# Generate local-only secrets for docker compose. Never commit the resulting .env file.
set -euo pipefail

STACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${STACK_DIR}/.env"
TEMPLATE_FILE="${STACK_DIR}/.env.template"

require_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to generate secure credentials."
    exit 1
  fi
}

env_has_placeholders() {
  [[ -f "${ENV_FILE}" ]] || return 0
  grep -qE '^(GRAFANA_ADMIN_PASSWORD|GRAFANA_SECRET_KEY|API_KEY)=change-me$' "${ENV_FILE}"
}

generate_env() {
  require_python
  python3 - <<'PY' > "${ENV_FILE}.tmp"
import secrets

print(f"GRAFANA_ADMIN_PASSWORD={secrets.token_urlsafe(24)}")
print(f"GRAFANA_SECRET_KEY={secrets.token_urlsafe(32)}")
print(f"API_KEY={secrets.token_urlsafe(32)}")
PY
  mv "${ENV_FILE}.tmp" "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
}

ensure_env() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    if [[ -f "${TEMPLATE_FILE}" ]]; then
      cp "${TEMPLATE_FILE}" "${ENV_FILE}"
      chmod 600 "${ENV_FILE}"
    fi
    generate_env
    echo "Created ${ENV_FILE} with generated credentials."
    return
  fi

  if env_has_placeholders; then
    generate_env
    echo "Replaced placeholder values in ${ENV_FILE} with generated credentials."
  fi
}

ensure_env
