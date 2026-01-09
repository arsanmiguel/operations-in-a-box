#!/bin/bash

# Servicenow Plugin Setup Script
echo "🔧 Servicenow Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "✅ Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - SERVICENOW_INSTANCE_URL"
echo "  - SERVICENOW_USERNAME"
echo "  - SERVICENOW_PASSWORD"
echo "  - SERVICENOW_POLL_INTERVAL"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9142/health"
echo "4. View metrics: curl http://localhost:9142/metrics"
