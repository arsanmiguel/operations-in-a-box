#!/bin/bash

# Splunk-Enterprise Plugin Setup Script
echo "Splunk-Enterprise Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - SPLUNK_START_ARGS"
echo "  - SPLUNK_PASSWORD"
echo "  - SPLUNK_HEC_TOKEN"
echo "  - SPLUNK_APPS_URL"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9139/health"
echo "4. View metrics: curl http://localhost:9139/metrics"
