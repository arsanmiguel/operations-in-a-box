#!/bin/bash

# Aws-Discovery Plugin Setup Script
echo "🔧 Aws-Discovery Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "✅ Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - AWS_REGION"
echo "  - AWS_ACCESS_KEY_ID"
echo "  - AWS_SECRET_ACCESS_KEY"
echo "  - DISCOVERY_INTERVAL"
echo "  - DISCOVERY_SERVICES"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9118/health"
echo "4. View metrics: curl http://localhost:9118/metrics"
