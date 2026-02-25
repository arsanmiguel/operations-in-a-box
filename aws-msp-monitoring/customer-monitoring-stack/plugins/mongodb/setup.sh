#!/bin/bash

# Mongodb Plugin Setup Script
echo "Mongodb Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - MONGODB_URI"
echo "  - MONGODB_DATABASE"
echo "  - MONGODB_USERNAME"
echo "  - MONGODB_PASSWORD"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9152/health"
echo "4. View metrics: curl http://localhost:9152/metrics"
