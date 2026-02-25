#!/bin/bash

# Grafana-Ha Plugin Setup Script
echo "Grafana-Ha Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - GF_DATABASE_TYPE"
echo "  - GF_DATABASE_HOST"
echo "  - GF_DATABASE_NAME"
echo "  - GF_DATABASE_USER"
echo "  - GF_DATABASE_PASSWORD"
echo "  - GF_SESSION_PROVIDER"
echo "  - GF_SESSION_PROVIDER_CONFIG"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9110/health"
echo "4. View metrics: curl http://localhost:9110/metrics"
