#!/bin/bash

# AWS VPC Flow Logs Plugin Setup Script
echo "AWS VPC Flow Logs Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - AWS_REGION: AWS region for VPC Flow Logs"
echo "  - LOG_GROUP_NAME: CloudWatch Logs group name"
echo "  - SERVICE_NAME"
echo "  - SERVICE_ENABLED"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9215/health"
echo "4. View metrics: curl http://localhost:9215/metrics"
