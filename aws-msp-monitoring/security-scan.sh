#!/usr/bin/env bash
# CSE / internal security scan for Operations in a Box (core monitoring stack).
# Requires Docker (Colima on macOS: colima start).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "${ROOT}/.." && pwd)"
STACK="${ROOT}/customer-monitoring-stack"
OUT="${SECURITY_SCAN_OUT:-/tmp/operations-in-a-box-security-scan}"
SCAN_PLUGINS="${SCAN_PLUGINS:-0}"
DOCKER_HOST="${DOCKER_HOST:-unix://${HOME}/.colima/default/docker.sock}"
export DOCKER_HOST
export DOCKER_CONFIG="${DOCKER_CONFIG:-/tmp/docker-nocreds}"
mkdir -p "$OUT" "$DOCKER_CONFIG"
[[ -f "${DOCKER_CONFIG}/config.json" ]] || printf '%s\n' '{"auths":{}}' > "${DOCKER_CONFIG}/config.json"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker unavailable (start Colima: colima start)" >&2
  exit 1
fi

scan_path() {
  local label="$1"
  local rel="$2"
  local path="${REPO}/${rel}"
  if [[ ! -e "$path" ]]; then
    echo "WARN: missing ${path} — skip ${label}" >&2
    return 0
  fi

  echo "=== Trivy (${label}) ===" | tee "$OUT/latest-trivy-${label}.txt"
  docker run --rm \
    -v "${REPO}:/repo:ro" \
    -w /repo \
    aquasec/trivy:0.71.2 fs \
    --scanners secret,misconfig \
    --severity HIGH,CRITICAL,MEDIUM,LOW \
    "$rel" 2>&1 | tee -a "$OUT/latest-trivy-${label}.txt" || true
}

echo "=== Gitleaks (git history) ===" | tee "$OUT/latest-gitleaks.txt"
docker run --rm \
  -v "${REPO}:/repo:ro" \
  -w /repo \
  -v "${REPO}/.gitleaks.toml:/repo/.gitleaks.toml:ro" \
  zricethezav/gitleaks:v8.30.1 \
  detect --redact --source /repo --config /repo/.gitleaks.toml 2>&1 | tee -a "$OUT/latest-gitleaks.txt" || true

scan_path core-stack aws-msp-monitoring/customer-monitoring-stack/docker-compose.yml
scan_path api aws-msp-monitoring/customer-monitoring-stack/api
scan_path installer-py aws-msp-monitoring

if [[ "$SCAN_PLUGINS" == "1" ]]; then
  scan_path plugin-templates aws-msp-monitoring/customer-monitoring-stack/plugins
else
  echo "SKIP plugin template scan (set SCAN_PLUGINS=1 to include)" | tee "$OUT/latest-trivy-plugin-templates.txt"
fi

if command -v hadolint >/dev/null 2>&1; then
  echo "=== hadolint (api Dockerfile) ===" | tee "$OUT/latest-hadolint.txt"
  hadolint "${STACK}/api/Dockerfile" 2>&1 | tee -a "$OUT/latest-hadolint.txt" || true
else
  echo "SKIP hadolint (brew install hadolint)" | tee "$OUT/latest-hadolint.txt"
fi

if command -v shellcheck >/dev/null 2>&1; then
  echo "=== shellcheck ===" | tee "$OUT/latest-shellcheck.txt"
  find "${ROOT}" -name '*.sh' -print0 | xargs -0 shellcheck -x 2>&1 | tee -a "$OUT/latest-shellcheck.txt" || true
else
  echo "SKIP shellcheck (brew install shellcheck)" | tee "$OUT/latest-shellcheck.txt"
fi

echo "=== Runtime security validator ===" | tee "$OUT/latest-security-validator.txt"
if [[ ! -f "${STACK}/.env" ]]; then
  echo "Generating ${STACK}/.env via bootstrap-env.sh ..." | tee -a "$OUT/latest-security-validator.txt"
  "${STACK}/scripts/bootstrap-env.sh" >>"$OUT/latest-security-validator.txt" 2>&1
fi
python3 "${ROOT}/aws_msp_security_validator.py" --install-dir "${STACK}" 2>&1 | tee -a "$OUT/latest-security-validator.txt" || true

echo ""
echo "Reports in ${OUT}"
echo "Documented exceptions: aws-msp-monitoring/SECURITY-EXCEPTIONS.md"
