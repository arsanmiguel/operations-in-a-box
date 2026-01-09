#!/bin/bash

# Prometheus-Federation Plugin Setup Script
echo "🔧 Prometheus-Federation Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "✅ Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - PROMETHEUS_FEDERATION_TARGETS"
echo "  - PROMETHEUS_RETENTION_TIME"
echo "  - PROMETHEUS_STORAGE_PATH"
echo "  - PROMETHEUS_WEB_EXTERNAL_URL"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9109/health"
echo "4. View metrics: curl http://localhost:9109/metrics"
