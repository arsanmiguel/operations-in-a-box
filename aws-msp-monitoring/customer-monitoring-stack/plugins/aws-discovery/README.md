# Aws Discovery Plugin

This plugin provides aws-discovery integration for the monitoring stack.

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
curl http://localhost:9118/health

# View metrics
curl http://localhost:9118/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `AWS_REGION`: us-east-1
- `AWS_ACCESS_KEY_ID`: your-access-key
- `AWS_SECRET_ACCESS_KEY`: your-secret-key
- `DISCOVERY_INTERVAL`: 300
- `DISCOVERY_SERVICES`: ec2,rds,elb,lambda

### Service Configuration
Edit `aws-discovery-config.yml` for advanced configuration options.

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'aws-discovery'
    static_configs:
      - targets: ['localhost:9118']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for aws-discovery metrics visualization.

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
docker-compose logs aws_discovery

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Support
- Configuration: Edit `aws-discovery-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
