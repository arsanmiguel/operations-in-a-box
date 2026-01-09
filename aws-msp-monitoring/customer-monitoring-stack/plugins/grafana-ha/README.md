# Grafana Ha Plugin

This plugin provides grafana-ha integration for the monitoring stack.

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
curl http://localhost:9110/health

# View metrics
curl http://localhost:9110/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `GF_DATABASE_TYPE`: postgres
- `GF_DATABASE_HOST`: postgres:5432
- `GF_DATABASE_NAME`: grafana
- `GF_DATABASE_USER`: grafana
- `GF_DATABASE_PASSWORD`: your-db-password
- `GF_SESSION_PROVIDER`: redis
- `GF_SESSION_PROVIDER_CONFIG`: addr=redis:6379,pool_size=100

### Service Configuration
Edit `grafana-ha-config.yml` for advanced configuration options.

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'grafana-ha'
    static_configs:
      - targets: ['localhost:9110']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for grafana-ha metrics visualization.

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
docker-compose logs grafana_ha

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Support
- Configuration: Edit `grafana-ha-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
