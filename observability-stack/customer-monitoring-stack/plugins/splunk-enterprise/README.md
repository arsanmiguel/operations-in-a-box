# Splunk Enterprise Plugin

This plugin provides splunk-enterprise integration for the monitoring stack.

## Features

- **Production-ready configuration** with comprehensive templates
- **Environment-based configuration** via .env files
- **Health monitoring** with built-in health checks
- **Metrics export** to Prometheus format
- **Interactive setup** with guided configuration

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
curl http://localhost:9139/health

# View metrics
curl http://localhost:9139/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `SPLUNK_START_ARGS`: --accept-license
- `SPLUNK_PASSWORD`: your-splunk-password
- `SPLUNK_HEC_TOKEN`: your-hec-token
- `SPLUNK_APPS_URL`: https://splunkbase.splunk.com

### Service Configuration
Edit `splunk-enterprise-config.yml` for advanced configuration options.

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'splunk-enterprise'
    static_configs:
      - targets: ['localhost:9139']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for splunk-enterprise metrics visualization.

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
docker-compose logs splunk_enterprise

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Support
- Configuration: Edit `splunk-enterprise-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
