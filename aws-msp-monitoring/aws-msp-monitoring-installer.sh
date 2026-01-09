#!/bin/bash
# Secure Monitoring Stack - No Interactive Prompts
# Creates secure deployment and validates security controls

set -euo pipefail

echo "🛡️  Secure Monitoring Stack Deployment"
echo "======================================"
echo ""
echo "Creating enterprise-style monitoring stack with all security controls..."
echo ""

INSTALL_DIR="secure-monitoring-stack"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --install-dir DIR    Installation directory (default: secure-monitoring-stack)"
            echo "  --help              Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "📋 Configuration:"
echo "   Installation Directory: $INSTALL_DIR"
echo ""

# Step 1: Create secure deployment
echo "🚀 Step 1: Creating Secure Deployment"
echo "====================================="
echo ""

if python3 aws_msp_monitoring_stack.py --install-dir "$INSTALL_DIR"; then
    echo ""
    echo "✅ Secure deployment created successfully!"
    echo ""
else
    echo ""
    echo "❌ Deployment creation failed!"
    exit 1
fi

# Step 2: Validate security controls
echo "🔒 Step 2: Validating Security Controls"
echo "======================================"
echo ""

if python3 aws_msp_security_validator.py --install-dir "$INSTALL_DIR"; then
    echo ""
    echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "====================================="
    echo ""
    echo "📁 Your secure monitoring stack is ready at: $(pwd)/$INSTALL_DIR"
    echo ""
    echo "🔗 Quick Start:"
    echo "   cd $INSTALL_DIR"
    echo "   ./start.sh"
    echo ""
    echo "📖 Access Information:"
    echo "   - Grafana: http://localhost:3000"
    echo "   - Prometheus: http://localhost:9090"
    echo "   - API: http://localhost:8080"
    echo "   - Credentials: See CREDENTIALS.md"
    echo ""
    echo "🛡️  Security Features Enabled:"
    echo "   ✅ Secure credentials (no defaults)"
    echo "   ✅ API key authentication"
    echo "   ✅ Non-root containers"
    echo "   ✅ Localhost-only binding"
    echo "   ✅ Security headers"
    echo "   ✅ Input validation"
    echo "   ✅ Rate limiting"
    echo "   ✅ Session timeouts"
    echo "   ✅ Container hardening"
    echo ""
else
    echo ""
    echo "❌ Security validation failed!"
    echo "Some security controls may not be properly configured."
    echo "Check the validation output above for details."
    exit 1
fi
