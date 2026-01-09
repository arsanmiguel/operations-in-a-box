# Prometheus Federation Plugin

This plugin provides prometheus-federation integration for the monitoring stack.

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
curl http://localhost:9109/health

# View metrics
curl http://localhost:9109/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `PROMETHEUS_FEDERATION_TARGETS`: prometheus1:9090,prometheus2:9090
- `PROMETHEUS_RETENTION_TIME`: 15d
- `PROMETHEUS_STORAGE_PATH`: /prometheus
- `PROMETHEUS_WEB_EXTERNAL_URL`: http://localhost:9109

### Service Configuration
Edit `prometheus-federation-config.yml` for advanced configuration options.

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'prometheus-federation'
    static_configs:
      - targets: ['localhost:9109']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for prometheus-federation metrics visualization.

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
docker-compose logs prometheus_federation

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Support
- Configuration: Edit `prometheus-federation-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
