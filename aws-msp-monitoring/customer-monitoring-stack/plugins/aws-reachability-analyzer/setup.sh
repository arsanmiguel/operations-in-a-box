#!/bin/bash

# AWS Reachability Analyzer Plugin Setup Script
echo "🔧 AWS Reachability Analyzer Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "✅ Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - AWS_REGION: AWS region for Reachability Analyzer"
echo "  - CHECK_INTERVAL: Interval for recurring checks (seconds)"
echo "  - ALERT_ON_FAILURE: Enable alerting on failures"
echo "  - SERVICE_NAME"
echo "  - SERVICE_ENABLED"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Configure reachability checks in reachability-analyzer-config.yml"
echo "3. Start the service: docker-compose up -d"
echo "4. Check health: curl http://localhost:9216/health"
echo "5. View metrics: curl http://localhost:9216/metrics"
