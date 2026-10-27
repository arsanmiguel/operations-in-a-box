#!/bin/bash
set -euo pipefail

STACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${STACK_DIR}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker Desktop or the docker engine first."
  exit 1
fi

"${STACK_DIR}/scripts/bootstrap-env.sh"

mkdir -p data/prometheus data/grafana
chmod 750 data data/prometheus data/grafana 2>/dev/null || true

echo "Building and starting monitoring stack..."
docker compose up -d --build

echo "Waiting for services..."
ready=0
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:9090/-/healthy >/dev/null 2>&1 \
    && curl -fsS http://127.0.0.1:3000/api/health >/dev/null 2>&1 \
    && curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done

if [[ "${ready}" -ne 1 ]]; then
  echo "Services did not become healthy in time. Check: docker compose logs"
  exit 1
fi

API_KEY="$(grep '^API_KEY=' .env | cut -d= -f2-)"
curl -fsS -X POST http://127.0.0.1:8080/api/metrics \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"app_name":"operations-in-a-box","metric_name":"install_heartbeat","value":1}' >/dev/null

echo ""
echo "Install complete."
echo "- Grafana:    http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- API:        http://localhost:8080"
echo "- Login:      admin / see GRAFANA_ADMIN_PASSWORD in ${STACK_DIR}/.env"
echo "- Dashboard:  Operations in a Box - Overview (default home dashboard)"
