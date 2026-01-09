# Neo4J Plugin

This plugin provides neo4j integration for the monitoring stack.

## Features

- ✅ **Production-ready configuration** with comprehensive templates
- ✅ **Environment-based configuration** via .env files
- ✅ **Health monitoring** with built-in health checks
- ✅ **Metrics export** to Prometheus format
- ✅ **Interactive setup** with guided configuration

## Quick Start

### 1. Configure Environment
```bash
# Copy template and customize
cp .env.template .env
# Edit .env with your actual values

# Or use interactive setup
./setup.sh
```

### 2. Start Service
```bash
docker-compose up -d
```

### 3. Verify Operation
```bash
# Check service health
curl http://localhost:9205/health

# View metrics
curl http://localhost:9205/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `SERVICE_NAME`: neo4j
- `SERVICE_ENABLED`: true

### Service Configuration
Edit `neo4j-config.yml` for advanced configuration options.

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'neo4j'
    static_configs:
      - targets: ['localhost:9205']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for neo4j metrics visualization.

## Troubleshooting

### Common Issues
1. **Service won't start**: Check .env configuration
2. **No metrics**: Verify service is running and port is accessible
3. **Authentication errors**: Check credentials in .env file

### Useful Commands
```bash
# View service status
docker-compose ps

# Check service logs
docker-compose logs neo4j

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Support
- Configuration: Edit `neo4j-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
