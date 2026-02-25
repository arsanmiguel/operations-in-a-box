# Managed Services Operations in a Box

<a id="overview"></a>
## Overview

Thousands of AWS MSP partners have asked "how do I get started with monitoring and operations tooling?" This repository addresses that common challenge by providing a reference monitoring and observability stack designed to demonstrate a practical baseline aligned with AWS MSP Program expectations.

Originally built for AWS MSP partners, this stack is now used by customers, system integrators (SIs), ISVs, and enterprises for production monitoring and operations. The "MSP" name reflects its multi-tenant, production-grade design, not a limitation on who can use it.

Note: This is a starting point, not an AWS fully managed or supported production solution. Use this project to understand architecture patterns, accelerate experimentation, and build your own compliant monitoring implementation.

What you get:
- Fill-in-the-blanks templates (no coding required for plugins)
- Enterprise-style monitoring stack (Prometheus, Grafana, API, Pushgateway)
- 49 production-ready plugins with configuration templates
- Interactive setup scripts and web-based plugin GUI
- Dashboard tutorial, API examples, security patterns, demo data generator
- Six detailed guides (dashboard, partner, security, etc.)

Quick links: [Prerequisites](#prerequisites) · [Getting Started](#getting-started) · [Plugin System](#plugin-system) · [Support](#support)

Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Uninstalling](#uninstalling)
- [Next Steps After Installation](#next-steps-after-installation)
- [Plugin System](#plugin-system)
- [Agentic AI Integration](#agentic-ai-integration)
- [Package Contents](#package-contents)
- [Support](#support)

---

<a id="prerequisites"></a>
## Prerequisites

- OS: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- CPU: 4 cores minimum, 8 recommended (16+ for enterprise)
- RAM: 8GB minimum, 16GB recommended (32GB+ for 30+ plugins)
- Disk: 20GB free (base ~5GB, plugins ~100MB each, retention 10-15GB)
- Network: Internet for initial setup
- Python: 3.7+ (PyYAML and requests auto-installed)

Scaling guidelines: Small (1-15 plugins) 4 CPU / 8GB / 20GB disk; Medium (15-30) 8 CPU / 16GB / 50GB; Enterprise (30+) 16+ CPU / 32GB+ / 100GB+.

---

<a id="getting-started"></a>
## Getting Started

### Step 1: Extract the Package
1. Download `AWS_MSP_Monitoring_Stack_Universal_Installer.zip`
2. Extract to any folder
3. Open the `aws-msp-monitoring` directory


### Step 2: Run the Installer

Windows: Double-click `install.bat` and wait for completion. Grafana opens automatically.

macOS/Linux: Open Terminal, `cd path/to/aws-msp-monitoring`, run `./install.sh`. Grafana opens automatically.

### Step 3: Access Your Monitoring
- Grafana: http://localhost:3000
- Login: admin / (password in CREDENTIALS.md)

---

<a id="uninstalling"></a>
## Uninstalling

To remove the monitoring stack and free ~6GB: Windows: double-click `uninstall.bat`. macOS/Linux: run `./uninstall.sh`.

---

<a id="next-steps-after-installation"></a>
## Next Steps After Installation

For beginners: Read `AWS_MSP_DASHBOARD_WALKTHROUGH.md`, create dashboards from the guide, generate demo data with the included generator.

For developers: API integration examples in the dashboard walkthrough; connect apps via the secure REST API; custom metrics and dashboards.

For MSP partners: `AWS_MSP_PARTNER_GUIDE.md`, `AWS_MSP_SECURITY_ANALYSIS.md`, and customer handoff procedures.

---

<a id="plugin-system"></a>
## Plugin System

The monitoring stack supports a modular plugin system (performance, security, cloud, ITSM, data platforms, AI/ML). All 49 plugins include production-ready configuration templates; fill in credentials and start monitoring.

<details>
<summary><strong>Quick Plugin Installation</strong></summary>

```bash
# Option 1: Interactive command-line installer
./install-plugins.sh

# Option 2: Web-based GUI (recommended)
python3 aws_msp_plugin_web_gui.py
# Then open: http://localhost:5000

# Option 3: Direct command-line
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install aws-cloudwatch
```

What you get automatically: comprehensive `.env.template`, production-ready `docker-compose.yml` with health checks, service-specific config files, interactive setup script, and full documentation with examples and troubleshooting.
</details>

<details>
<summary><strong>Available Plugin Categories (49 plugins across 12 categories)</strong></summary>

- Performance & Scale: Federation, HA, Auto-scaling (3)
- Advanced Security: SAML/OAuth, Certificates, Network segmentation (3)
- Cloud Integration: AWS CloudWatch, CloudTrail, Config, VPC Flow Logs, Reachability Analyzer, Auto-Discovery, Cost optimization, MontyCloud (8)
- Security Partner: CrowdStrike, Palo Alto, Alert Logic (3)
- Monitoring Partner: Splunk, Sumo Logic, Datadog (3)
- CMDB/ITSM: ServiceNow, BMC Helix, Jira Service Management (3)
- Ticketing: AWS Support, Zendesk, Freshworks, Linear (4)
- Identity: Duo Security, Okta (2)
- Data Platform: Redis, Elasticsearch, Databricks, Snowflake, MongoDB, Confluent, InfluxDB, ClickHouse, Neo4j (9)
- AI/ML: Anomaly detection, Predictive alerts, Auto-remediation (3)
- Advanced Analytics: BI, ELK stack, APM (3)
- DevOps Automation: CloudFormation, Terraform, IaC, CI/CD, GitOps (5)
</details>

<details>
<summary><strong>Popular Plugin Packs</strong></summary>

- AWS Integration Pack: CloudWatch, CloudTrail, Config, VPC Flow Logs, Reachability Analyzer, Auto-Discovery, Cost Optimization, MontyCloud
- Security Enhancement: SAML Auth + Certificate Auth
- Security Partner: CrowdStrike, Palo Alto, Alert Logic
- Monitoring Partner: Splunk, Sumo Logic, Datadog
- CMDB/ITSM: ServiceNow, BMC Helix, Jira Service Management
- Ticketing: AWS Support, Zendesk, Freshworks, Linear
- Identity: Duo Security, Okta
- Data Platform: Redis, Elasticsearch, Databricks, Snowflake, MongoDB, Confluent, InfluxDB, ClickHouse, Neo4j
- Analytics: BI, Log Aggregation, APM
- AI/ML: Anomaly Detection, Predictive Alerts
- Enterprise Scale: Federation, HA, Auto-Scaling
</details>

<details>
<summary><strong>Getting Started Examples</strong></summary>

Basic AWS MSP Setup:
```bash
# Install base stack
./aws-msp-monitoring-installer.sh

# Add essential AWS integration
python3 aws_msp_plugin_manager.py install aws-cloudwatch
python3 aws_msp_plugin_manager.py install aws-cloudtrail
python3 aws_msp_plugin_manager.py install aws-config
python3 aws_msp_plugin_manager.py install montycloud
```

Security-Focused MSP:
```bash
# Install base + security partners
python3 aws_msp_plugin_manager.py install crowdstrike-falcon
python3 aws_msp_plugin_manager.py install duo-security
python3 aws_msp_plugin_manager.py install okta
```

DevOps-Focused MSP:
```bash
# Install infrastructure monitoring
python3 aws_msp_plugin_manager.py install aws-cloudformation
python3 aws_msp_plugin_manager.py install terraform
python3 aws_msp_plugin_manager.py install cicd-monitoring
```

Data Platform MSP:
```bash
# Install data platform monitoring
python3 aws_msp_plugin_manager.py install redis
python3 aws_msp_plugin_manager.py install elasticsearch
python3 aws_msp_plugin_manager.py install databricks
python3 aws_msp_plugin_manager.py install snowflake
python3 aws_msp_plugin_manager.py install mongodb
python3 aws_msp_plugin_manager.py install confluent
python3 aws_msp_plugin_manager.py install influxdb
python3 aws_msp_plugin_manager.py install clickhouse
python3 aws_msp_plugin_manager.py install neo4j
```

Enterprise MSP with Full Stack:
```bash
# Install comprehensive monitoring
python3 aws_msp_plugin_manager.py install aws-cloudwatch
python3 aws_msp_plugin_manager.py install montycloud
python3 aws_msp_plugin_manager.py install servicenow
python3 aws_msp_plugin_manager.py install splunk-enterprise
python3 aws_msp_plugin_manager.py install anomaly-detection
```
</details>

<details>
<summary><strong>Plugin Management Commands</strong></summary>

```bash
# List all available plugins
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list

# Get plugin information
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack info aws-cloudwatch

# View installed plugins
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list --installed
```
</details>

---

<a id="agentic-ai-integration"></a>
## Agentic AI Integration

<details>
<summary><strong>Optional Bedrock-powered alert triage</strong></summary>

### Agentic AI Integration

Optional Bedrock-powered alert triage agent for intelligent routing and analysis. No plugin changes required.

What it does: receives Prometheus alerts, analyzes context with Claude (Bedrock), determines root cause and severity, routes to multiple systems (AWS Support, ServiceNow, Jira, etc.), triggers auto-remediation when appropriate. Uses your existing plugin APIs.

Key features: ~200 lines of Python between AlertManager and your plugins; multi-system routing; auto-remediation for known issues. Approximately $3/month for 1,000 alerts.

Quick start:
```bash
# Install dependencies
pip install boto3 requests flask

# Configure AlertManager webhook
# See ALERT_TRIAGE_AGENT.md for details

# Run the agent
python3 alert_triage_agent.py
```

Documentation: See `ALERT_TRIAGE_AGENT.md` for full setup, configuration examples, and deployment options.

</details>

---

<a id="package-contents"></a>
## Package Contents

<details>
<summary><strong>Everything included</strong></summary>

- `aws-msp-monitoring-installer.sh` - Main installer (Unix)
- `aws_msp_monitoring_stack.py` - Core installer with PyYAML auto-install
- `aws_msp_universal_installer.py` - Cross-platform installer (Windows/macOS/Linux)
- `aws_msp_security_validator.py` - Security validation
- `aws_msp_plugin_manager.py` - Plugin system (49 plugins across 12 categories)
- `aws_msp_plugin_web_gui.py` - Web-based plugin management interface
- `alert_triage_agent.py` - Bedrock-powered intelligent alert routing (optional)
- `ALERT_TRIAGE_AGENT.md` - Agentic AI integration documentation
- `install-plugins.sh` - Interactive plugin installer
- `install.sh` - Unix installer
- `install.bat` - Windows installer
- `uninstall.sh` - Unix uninstaller
- `uninstall.bat` - Windows uninstaller
- `enhance-all-plugins.py` - Plugin validation and enhancement system
- `enhance-all-templates.py` - Comprehensive template generator
- `AWS_MSP_DASHBOARD_WALKTHROUGH.md` - Complete dashboard guide
- `AWS_MSP_DASHBOARD_QUERY_REFERENCE.md` - Prometheus query reference
- `AWS_MSP_PARTNER_GUIDE.md` - Partner deployment guide
- `AWS_MSP_SECURITY_GUIDE.md` - Security documentation
- `AWS_MSP_SECURITY_ANALYSIS.md` - Security analysis
- `aws_msp_demo_data_generator.py` - Demo data generator (fixed metric names)

</details>

---

<a id="support"></a>
## Support

<details>
<summary><strong>Troubleshooting</strong></summary>

### 1. Verify Prerequisites
```bash
# Check Docker is running
docker --version
docker ps

# Check Python version
python3 --version  # macOS/Linux
python --version   # Windows

# Check available disk space (need 20GB+)
df -h .            # macOS/Linux
dir               # Windows
```

### 2. Service Status Checks
```bash
# Check all containers are running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check container logs for errors
docker logs prometheus
docker logs grafana
docker logs pushgateway
docker logs msp-api

# Check service health
curl -f http://localhost:3000/api/health  # Grafana
curl -f http://localhost:9090/-/healthy  # Prometheus
```

### 3. Network & Port Troubleshooting
```bash
# Verify ports are accessible
netstat -an | grep :3000   # Grafana
netstat -an | grep :9090   # Prometheus
netstat -an | grep :9091   # Pushgateway
netstat -an | grep :8080   # MSP API

# Test connectivity
curl -I http://localhost:3000
curl -I http://localhost:9090
```

### 4. System Resource Checks
```bash
# Check memory usage (need 8GB+ available)
free -h           # Linux
vm_stat           # macOS
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows

# Check CPU usage
top -n 1          # Linux/macOS
wmic cpu get loadpercentage  # Windows
```

### 5. Plugin-Specific Issues
```bash
# List installed plugins
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list --installed

# Check plugin status
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack status

# Reinstall problematic plugin
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack uninstall <plugin-name>
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install <plugin-name>
```

### 6. Log Collection for Support
```bash
# Collect all container logs
mkdir support-logs
docker logs prometheus > support-logs/prometheus.log 2>&1
docker logs grafana > support-logs/grafana.log 2>&1
docker logs pushgateway > support-logs/pushgateway.log 2>&1
docker logs msp-api > support-logs/msp-api.log 2>&1

# System information
docker info > support-logs/docker-info.log
python3 --version > support-logs/python-version.log
uname -a > support-logs/system-info.log  # Unix
systeminfo > support-logs/system-info.log  # Windows
```

### 7. Common Error Solutions

"Port already in use" errors:
```bash
# Find and stop conflicting processes
lsof -i :3000     # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process using port
kill -9 <PID>     # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

"Permission denied" errors:
```bash
# Fix file permissions (Unix)
chmod +x install.sh
chmod +x install-plugins.sh
sudo chown -R $USER:$USER customer-monitoring-stack/

# Run as administrator (Windows)
# Right-click install.bat -> "Run as administrator"
```

"Docker not found" errors:
```bash
# Install Docker Desktop
# macOS: https://docs.docker.com/desktop/mac/install/
# Windows: https://docs.docker.com/desktop/windows/install/
# Linux: https://docs.docker.com/engine/install/

# Start Docker service
sudo systemctl start docker  # Linux
# Or start Docker Desktop application
```

"Module not found" Python errors:
```bash
# Reinstall dependencies
pip3 install --upgrade pip
pip3 install pyyaml requests docker

# Use virtual environment
python3 -m venv monitoring-env
source monitoring-env/bin/activate  # Unix
monitoring-env\Scripts\activate     # Windows
pip install -r requirements.txt
```
</details>

<details>
<summary><strong>Additional Resources</strong></summary>

1. Detailed troubleshooting: `AWS_MSP_DASHBOARD_WALKTHROUGH.md`
2. Security: `AWS_MSP_SECURITY_GUIDE.md`
3. Partner deployment: `AWS_MSP_PARTNER_GUIDE.md`
</details>

Contact: [adrianr.sanmiguel@gmail.com](mailto:adrianr.sanmiguel@gmail.com) for bugs and feature requests.

---

Important: This project is not an official AWS product and does not by itself confer AWS MSP Program compliance. Partners are responsible for validating their own implementations against current AWS MSP Program requirements.
