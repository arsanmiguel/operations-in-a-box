#!/bin/bash

# Plugin Validation Script
# Tests installation and basic configuration for all plugins

echo "Plugin Installation and Configuration Validator"
echo "=================================================="

# Get list of all available plugins
PLUGINS=$(python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list | grep "Available" | grep -v "Installed" | awk '{print $1}')

# Port assignment tracker (starting from 9109 since we used 9106-9108)
PORT=9109
FAILED_PLUGINS=()
SUCCESS_PLUGINS=()

# Test each plugin
for plugin in $PLUGINS; do
    echo ""
    echo "Testing plugin: $plugin"
    echo "----------------------------------------"
    
    # Try to install the plugin
    if python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install $plugin; then
        echo "Installation successful: $plugin"
        
        # Check if docker-compose.yml was created
        PLUGIN_DIR="customer-monitoring-stack/plugins/$plugin"
        if [ -f "$PLUGIN_DIR/docker-compose.yml" ]; then
            echo "Docker compose file created"
            
            # Validate docker-compose syntax
            if cd "$PLUGIN_DIR" && docker-compose config > /dev/null 2>&1; then
                echo "Docker compose syntax valid"
                SUCCESS_PLUGINS+=($plugin)
            else
                echo "Docker compose syntax invalid"
                FAILED_PLUGINS+=($plugin)
            fi
            cd - > /dev/null
        else
            echo "No docker-compose.yml created"
            FAILED_PLUGINS+=($plugin)
        fi
    else
        echo "Installation failed: $plugin"
        FAILED_PLUGINS+=($plugin)
    fi
    
    PORT=$((PORT + 1))
done

echo ""
echo "SUMMARY"
echo "=========="
echo "Successful: ${#SUCCESS_PLUGINS[@]} plugins"
echo "Failed: ${#FAILED_PLUGINS[@]} plugins"

if [ ${#FAILED_PLUGINS[@]} -gt 0 ]; then
    echo ""
    echo "Failed plugins:"
    for plugin in "${FAILED_PLUGINS[@]}"; do
        echo "  - $plugin"
    done
fi

echo ""
echo "Successful plugins:"
for plugin in "${SUCCESS_PLUGINS[@]}"; do
    echo "  - $plugin"
done
