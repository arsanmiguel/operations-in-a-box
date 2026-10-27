#!/bin/bash
set -euo pipefail

STACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${STACK_DIR}"

"${STACK_DIR}/scripts/bootstrap-env.sh"

mkdir -p data/prometheus data/grafana

echo "Starting Secure Monitoring Stack..."
docker compose up -d
echo "Services started!"
echo ""
echo "Access URLs:"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- API: http://localhost:8080"
echo ""
echo "Credentials are in .env (not printed)."
