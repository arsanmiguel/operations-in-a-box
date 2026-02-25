# AWS VPC Flow Logs Plugin

This plugin provides AWS VPC Flow Logs integration for the monitoring stack, enabling network traffic analysis, security monitoring, and troubleshooting.

## Features

- **Production-ready configuration** with comprehensive templates
- **Environment-based configuration** via .env files
- **Health monitoring** with built-in health checks
- **Metrics export** to Prometheus format
- **Interactive setup** with guided configuration
- **Network traffic analysis** - Monitor accepted/rejected connections
- **Security monitoring** - Detect suspicious traffic patterns
- **Cost optimization** - Identify high-traffic resources
- **Compliance tracking** - Audit network access patterns

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
curl http://localhost:9215/health

# View metrics
curl http://localhost:9215/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `SERVICE_NAME`: aws-vpc-flow-logs
- `SERVICE_ENABLED`: true
- `AWS_REGION`: AWS region for VPC Flow Logs
- `LOG_GROUP_NAME`: CloudWatch Logs group name for flow logs
- `FLOW_LOG_FORMAT`: Custom flow log format (optional)

### Service Configuration
Edit `vpc-flow-logs-config.yml` for advanced configuration options.

## Use Cases

### Network Traffic Analysis
- Monitor traffic patterns across VPCs
- Identify top talkers and bandwidth consumers
- Track connection attempts (accepted/rejected)

### Security Monitoring
- Detect port scanning attempts
- Identify unauthorized access attempts
- Monitor traffic to/from suspicious IPs
- Track security group rule effectiveness

### Troubleshooting
- Diagnose connectivity issues
- Verify security group and NACL rules
- Identify packet loss and network bottlenecks

### Cost Optimization
- Identify high-traffic resources
- Optimize data transfer costs
- Right-size network capacity

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'aws-vpc-flow-logs'
    static_configs:
      - targets: ['localhost:9215']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for VPC Flow Logs metrics visualization:
- Network traffic volume by source/destination
- Top talkers and bandwidth consumers
- Rejected connection attempts
- Security group effectiveness

## Metrics Exposed

- `vpc_flow_logs_bytes_total` - Total bytes transferred
- `vpc_flow_logs_packets_total` - Total packets transferred
- `vpc_flow_logs_connections_total` - Total connections by action (ACCEPT/REJECT)
- `vpc_flow_logs_top_talkers` - Top source/destination IPs by traffic volume

## Troubleshooting

### Common Issues
1. **Service won't start**: Check .env configuration and AWS credentials
2. **No metrics**: Verify VPC Flow Logs are enabled and publishing to CloudWatch
3. **Authentication errors**: Check IAM permissions for CloudWatch Logs access
4. **Missing data**: Verify LOG_GROUP_NAME matches your VPC Flow Logs configuration

### Required IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "ec2:DescribeFlowLogs",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeNetworkInterfaces"
      ],
      "Resource": "*"
    }
  ]
}
```

### Useful Commands
```bash
# View service status
docker-compose ps

# Check service logs
docker-compose logs aws_vpc_flow_logs

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Support
- Configuration: Edit `vpc-flow-logs-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
