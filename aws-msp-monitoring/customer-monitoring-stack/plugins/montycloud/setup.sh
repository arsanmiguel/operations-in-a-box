#!/bin/bash

# Montycloud Plugin Setup Script
echo "Montycloud Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - MONTYCLOUD_API_KEY"
echo "  - MONTYCLOUD_TENANT_ID"
echo "  - MONTYCLOUD_REGION"
echo "  - GOVERNANCE_POLICIES"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9120/health"
echo "4. View metrics: curl http://localhost:9120/metrics"
