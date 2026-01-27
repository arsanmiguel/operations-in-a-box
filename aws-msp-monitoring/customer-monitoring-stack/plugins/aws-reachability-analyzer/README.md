# AWS Reachability Analyzer Plugin

This plugin provides AWS VPC Reachability Analyzer integration for the monitoring stack, enabling automated network path analysis and connectivity verification.

## Features

- ✅ **Production-ready configuration** with comprehensive templates
- ✅ **Environment-based configuration** via .env files
- ✅ **Health monitoring** with built-in health checks
- ✅ **Metrics export** to Prometheus format
- ✅ **Interactive setup** with guided configuration
- ✅ **Automated path analysis** - Verify network connectivity between resources
- ✅ **Configuration validation** - Detect misconfigurations in security groups, NACLs, route tables
- ✅ **Continuous monitoring** - Schedule recurring reachability checks
- ✅ **Alert integration** - Notify on connectivity failures

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
curl http://localhost:9216/health

# View metrics
curl http://localhost:9216/metrics

# Check logs
docker-compose logs -f
```

## Configuration

### Environment Variables
- `SERVICE_NAME`: aws-reachability-analyzer
- `SERVICE_ENABLED`: true
- `AWS_REGION`: AWS region for Reachability Analyzer
- `CHECK_INTERVAL`: Interval for recurring reachability checks (seconds)
- `ALERT_ON_FAILURE`: Enable alerting on connectivity failures

### Service Configuration
Edit `reachability-analyzer-config.yml` for advanced configuration options.

## Use Cases

### Network Troubleshooting
- Verify connectivity between EC2 instances
- Diagnose why traffic isn't reaching a target
- Validate VPN and Direct Connect configurations
- Test connectivity to AWS services (S3, DynamoDB, etc.)

### Configuration Validation
- Detect security group misconfigurations
- Identify NACL blocking rules
- Verify route table configurations
- Validate network ACL rules

### Continuous Monitoring
- Schedule recurring connectivity checks
- Monitor critical network paths
- Alert on connectivity failures
- Track network configuration changes

### Compliance & Auditing
- Verify network segmentation
- Validate security controls
- Document network connectivity
- Audit access paths

## Integration

### Prometheus Configuration
Add this job to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'aws-reachability-analyzer'
    static_configs:
      - targets: ['localhost:9216']
    scrape_interval: 60s
```

### Grafana Dashboard
Import dashboard for Reachability Analyzer metrics visualization:
- Reachability check success/failure rates
- Network path analysis results
- Configuration issue detection
- Historical connectivity trends

## Metrics Exposed

- `reachability_check_success_total` - Total successful reachability checks
- `reachability_check_failure_total` - Total failed reachability checks
- `reachability_check_duration_seconds` - Duration of reachability analysis
- `reachability_path_hops` - Number of hops in network path
- `reachability_blocking_components` - Components blocking connectivity

## Troubleshooting

### Common Issues
1. **Service won't start**: Check .env configuration and AWS credentials
2. **No metrics**: Verify IAM permissions for Reachability Analyzer
3. **Authentication errors**: Check IAM permissions
4. **Analysis failures**: Verify source/destination resources exist

### Required IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInsightsPath",
        "ec2:CreateNetworkInsightsAnalysis",
        "ec2:DescribeNetworkInsightsPaths",
        "ec2:DescribeNetworkInsightsAnalyses",
        "ec2:DeleteNetworkInsightsPath",
        "ec2:DeleteNetworkInsightsAnalysis",
        "ec2:DescribeInstances",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeRouteTables",
        "ec2:DescribeNetworkAcls",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets"
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
docker-compose logs aws_reachability_analyzer

# Restart service
docker-compose restart

# Update configuration
docker-compose down && docker-compose up -d
```

## Example Reachability Checks

### EC2 to EC2 Connectivity
```yaml
checks:
  - name: web-to-db
    source: i-1234567890abcdef0
    destination: i-0987654321fedcba0
    protocol: tcp
    port: 3306
```

### EC2 to Internet Gateway
```yaml
checks:
  - name: instance-to-internet
    source: i-1234567890abcdef0
    destination: igw-12345678
    protocol: tcp
    port: 443
```

### Cross-VPC Connectivity
```yaml
checks:
  - name: vpc-peering-check
    source: i-1234567890abcdef0
    destination: i-abcdef1234567890
    protocol: tcp
    port: 22
```

## Support
- Configuration: Edit `reachability-analyzer-config.yml`
- Environment: Edit `.env` file
- Setup: Run `./setup.sh` for guided configuration
