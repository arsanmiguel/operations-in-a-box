#!/bin/bash
echo "AWS MSP Plugin Installer"
echo "=========================="
echo ""

cd "$(dirname "$0")"

# Check if base monitoring stack exists
if [ ! -f "customer-monitoring-stack/docker-compose.yml" ]; then
    echo "Base monitoring stack not found!"
    echo "Please run the main installer first:"
    echo "  ./install.sh"
    exit 1
fi

echo "Base monitoring stack found"
echo ""

# Show available plugins
echo "Available Plugin Categories:"
python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack categories
echo ""

echo "Plugin Management Commands:"
echo ""
echo "🔍 Browse plugins:"
echo "  python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list"
echo "  python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list --category \"Cloud Integration\""
echo ""
echo "ℹ️  Get plugin info:"
echo "  python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack info aws-cloudwatch"
echo ""
echo "Install plugins:"
echo "  python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install aws-cloudwatch"
echo ""
echo "Uninstall plugins:"
echo "  python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack uninstall aws-cloudwatch"
echo ""
echo "View installed plugins:"
echo "  python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list --installed"
echo ""

# Interactive plugin selection
echo "Quick Plugin Installation:"
echo ""
echo "Popular plugin combinations:"
echo "1. AWS Integration Pack (CloudWatch + Auto-Discovery + Cost Optimization)"
echo "2. Security Enhancement Pack (SAML Auth + Certificate Auth)"
echo "3. Analytics Pack (Business Intelligence + Log Aggregation + APM)"
echo "4. AI/ML Pack (Anomaly Detection + Predictive Alerts)"
echo "5. DevOps Pack (CI/CD Monitoring + GitOps + Infrastructure as Code)"
echo "6. Enterprise Scale Pack (Prometheus Federation + Grafana HA + Auto-Scaling)"
echo "7. Custom selection"
echo "8. Exit"
echo ""

read -p "Select a pack (1-8): " choice

case $choice in
    1)
        echo "Installing AWS Integration Pack..."
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install aws-cloudwatch
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install aws-discovery
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install cost-optimization
        ;;
    2)
        echo "Installing Security Enhancement Pack..."
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install saml-auth
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install cert-auth
        ;;
    3)
        echo "Installing Analytics Pack..."
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install business-intelligence
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install log-aggregation
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install apm-monitoring
        ;;
    4)
        echo "Installing AI/ML Pack..."
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install anomaly-detection
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install predictive-alerts
        ;;
    5)
        echo "Installing DevOps Pack..."
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install cicd-monitoring
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install gitops-deployment
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install infrastructure-as-code
        ;;
    6)
        echo "🏢 Installing Enterprise Scale Pack..."
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install prometheus-federation
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install grafana-ha
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install auto-scaling
        ;;
    7)
        echo "Custom Plugin Selection:"
        echo ""
        python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list
        echo ""
        read -p "Enter plugin ID to install (or 'exit'): " plugin_id
        if [ "$plugin_id" != "exit" ]; then
            python3 ../aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install "$plugin_id"
        fi
        ;;
    8)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "🔄 Restart your monitoring stack to activate new plugins:"
echo "  cd customer-monitoring-stack"
echo "  docker compose down && docker compose up -d"
echo ""
echo "Plugin documentation will be available at:"
echo "  customer-monitoring-stack/plugins/[plugin-name]/"
