# Alert Triage Agent - Bedrock Integration

## Overview

Bedrock-powered intelligent agent that analyzes Prometheus alerts and automatically routes them to appropriate ticketing systems using your existing plugin infrastructure.

## Features

✅ **AI-powered analysis** - Uses Claude via Bedrock to understand alert context  
✅ **Multi-system routing** - Routes to multiple ITSM/ticketing systems simultaneously  
✅ **Auto-remediation** - Triggers fixes when appropriate  
✅ **Zero plugin changes** - Uses existing plugin APIs  
✅ **Intelligent decisions** - Determines severity, root cause, and best routing  

## How It Works

```
Prometheus Alert → AlertManager Webhook → Bedrock Agent → Routes to:
                                                          ├─ AWS Support
                                                          ├─ ServiceNow
                                                          ├─ BMC Helix
                                                          ├─ Jira Service Mgmt
                                                          ├─ Zendesk
                                                          ├─ Freshworks
                                                          ├─ Linear
                                                          ├─ AWS Config
                                                          └─ Auto-remediation
```

## Prerequisites

1. **AWS Credentials** with Bedrock access
2. **Existing plugins** configured and running
3. **Python 3.8+** with boto3

## Installation

```bash
pip install boto3 requests
```

## Configuration

### 1. Set up AlertManager webhook

Edit your `alertmanager.yml`:

```yaml
receivers:
  - name: 'bedrock-agent'
    webhook_configs:
      - url: 'http://localhost:5000/webhook/alert'
        send_resolved: true

route:
  receiver: 'bedrock-agent'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
```

### 2. Configure plugin endpoints

Update port numbers in `alert_triage_agent.py` to match your plugin configuration:

```python
# Default ports (adjust as needed)
aws-support: 9217
servicenow: 9218
bmc-helix: 9219
jira-service-mgmt: 9220
zendesk: 9221
freshworks: 9222
linear: 9223
aws-config: 9224
auto-remediation: 9225
```

### 3. Set AWS credentials

```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Usage

### Run as webhook server

```python
from flask import Flask, request, jsonify
from alert_triage_agent import handle_prometheus_alert

app = Flask(__name__)

@app.route('/webhook/alert', methods=['POST'])
def webhook():
    alert_data = request.json
    result = handle_prometheus_alert(alert_data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Test with example alert

```bash
python alert_triage_agent.py
```

## Example Output

```
🤖 Analyzing alert: HighCPUUsage
📊 Analysis complete:
  Root cause: EC2 instance experiencing sustained high CPU load, likely due to runaway process or insufficient capacity
  Severity: critical
  Targets: aws-support, servicenow
  Auto-remediate: false

🚀 Routing alert to 2 system(s)...
✅ aws-support: success
   Ticket ID: case-123456789
✅ servicenow: success
   Ticket ID: INC0012345

✨ Alert triage complete!
```

## Agent Decision Logic

The Bedrock agent analyzes:

1. **Alert severity** - Critical, high, medium, low
2. **Resource type** - AWS resources → AWS Support
3. **Alert type** - Compliance → AWS Config
4. **Historical patterns** - Similar past incidents
5. **Remediation confidence** - Auto-fix if high confidence

## Routing Examples

### Critical AWS Resource Issue
```
Targets: [aws-support, servicenow]
Auto-remediate: false (requires human approval)
```

### Compliance Violation
```
Targets: [aws-config, jira-service-mgmt]
Auto-remediate: true (known fix)
```

### High Severity Application Error
```
Targets: [servicenow, linear]
Auto-remediate: false
```

### Medium Severity Disk Space
```
Targets: [jira-service-mgmt]
Auto-remediate: true (cleanup old logs)
```

## Customization

### Add custom routing rules

Modify the prompt in `analyze_alert()` to include your specific rules:

```python
prompt = f"""...
Custom routing rules:
- Database alerts → Create Jira ticket for DB team
- Security alerts → Create AWS Support case + notify security team
- Cost alerts → Create Linear issue for FinOps team
..."""
```

### Change Bedrock model

```python
agent = AlertTriageAgent(
    bedrock_model="anthropic.claude-3-opus-20240229-v1:0"
)
```

## Cost Estimation

**Per alert analysis:**
- Input tokens: ~500 tokens (alert context)
- Output tokens: ~300 tokens (analysis)
- Cost: ~$0.003 per alert (Claude 3.5 Sonnet)

**Monthly estimate (1000 alerts):**
- ~$3/month for Bedrock API calls

## Troubleshooting

### Agent not routing to plugin
- Check plugin is running: `curl http://localhost:9217/health`
- Verify port numbers match your configuration
- Check plugin logs for errors

### Bedrock API errors
- Verify AWS credentials: `aws sts get-caller-identity`
- Check Bedrock model access in AWS Console
- Ensure region supports Bedrock (us-east-1, us-west-2)

### No tickets created
- Check plugin API responses in agent logs
- Verify plugin credentials are configured
- Test plugin APIs directly with curl

## Integration with Existing Stack

**No changes required to:**
- Prometheus configuration
- Grafana dashboards
- Plugin configurations
- Docker compose setup

**Only additions:**
- AlertManager webhook configuration
- This agent script
- Flask webhook server (optional)

## Next Steps

1. **Test with sample alerts** - Run the example
2. **Configure AlertManager** - Add webhook
3. **Deploy agent** - Run as service or Lambda
4. **Monitor results** - Check ticket creation
5. **Tune prompts** - Adjust routing logic as needed

## Production Deployment

### Option 1: Docker container
```dockerfile
FROM python:3.9-slim
COPY alert_triage_agent.py /app/
RUN pip install boto3 requests flask
CMD ["python", "/app/webhook_server.py"]
```

### Option 2: AWS Lambda
- Package as Lambda function
- Trigger via API Gateway
- Configure AlertManager to call API Gateway URL

### Option 3: Kubernetes pod
- Deploy alongside monitoring stack
- Use service mesh for plugin communication
- Scale based on alert volume
