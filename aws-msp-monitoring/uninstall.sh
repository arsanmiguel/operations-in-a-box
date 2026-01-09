#!/bin/bash

echo "🗑️  Removing AWS MSP Monitoring Stack..."
echo ""

# Stop and remove all containers, networks, and volumes
if [ -f "customer-monitoring-stack/docker-compose.yml" ]; then
    cd customer-monitoring-stack
    docker-compose down -v --remove-orphans 2>/dev/null
    cd ..
fi

# Remove plugin containers
find customer-monitoring-stack/plugins -name "docker-compose.yml" -exec dirname {} \; | while read plugin_dir; do
    if [ -d "$plugin_dir" ]; then
        cd "$plugin_dir"
        docker-compose down -v --remove-orphans 2>/dev/null
        cd - >/dev/null
    fi
done

# Clean up Docker system (images, containers, networks, volumes)
echo "Cleaning up Docker images and volumes..."
docker system prune -f --volumes 2>/dev/null

echo ""
echo "✅ AWS MSP Monitoring Stack removed successfully!"
echo "📁 You can now safely delete this folder if desired."
echo ""
