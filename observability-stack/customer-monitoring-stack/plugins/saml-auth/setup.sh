#!/bin/bash

# Saml-Auth Plugin Setup Script
echo "Saml-Auth Plugin Configuration"
echo "=================================================="

# Check if .env file exists
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.template "$ENV_FILE"
    echo "Created .env file from template"
fi

echo ""
echo "Please configure the following settings in .env:"
echo "  - SAML_IDP_URL"
echo "  - SAML_ENTITY_ID"
echo "  - SAML_CERT_PATH"
echo "  - SAML_KEY_PATH"

echo ""
echo "After configuration:"
echo "1. Edit .env with your actual values"
echo "2. Start the service: docker-compose up -d"
echo "3. Check health: curl http://localhost:9114/health"
echo "4. View metrics: curl http://localhost:9114/metrics"
