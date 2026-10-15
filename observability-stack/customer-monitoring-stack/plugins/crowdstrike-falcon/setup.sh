#!/bin/bash

# Crowdstrike-Falcon Plugin Setup Script
echo "Crowdstrike-Falcon Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - FALCON_CLIENT_ID"
echo "  - FALCON_CLIENT_SECRET"
echo "  - FALCON_CLOUD"
echo "  - FALCON_CID"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9135/health"
echo "4. View metrics: curl http://localhost:9135/metrics"
