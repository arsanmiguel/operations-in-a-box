## Overview

Thousands of AWS MSP partners have asked "how do I get started with monitoring and operations tooling?" This repository addresses that common challenge by providing a reference monitoring and observability stack designed to demonstrate a practical baseline aligned with AWS MSP Program expectations.

While specifically intended for AWS partners operating MSPs, customers, system integrators (SIs), independent software vendors (ISVs), and distributors are welcome to use this as well.

**Note:** This is a starting point—not an AWS fully managed or supported production solution. Use this project to understand architecture patterns, accelerate experimentation, and build your own compliant monitoring implementation.

---

## 📖 **What You Get**

✅ Enterprise-style monitoring stack (Prometheus, Grafana, API, Pushgateway)  
✅ Security patterns and hardening examples (authentication and encryption)  
✅ **47 production-ready plugins** with comprehensive configuration templates  
✅ **Complete dashboard tutorial** (step-by-step beginner to advanced)  
✅ **API integration examples** (Python, JavaScript, curl)  
✅ **Demo data generator** (realistic metrics for testing)  
✅ **Comprehensive documentation** (6 detailed guides)  
✅ **Interactive setup scripts** for guided plugin configuration  
✅ **Fill-in-the-blanks templates** - no coding required for any plugin  

=================================================================


# AWS MSP Monitoring Stack - Universal Installer

## 🚀 **GETTING STARTED** (2 minutes)

### **Step 1: Extract the Package**
1. Download `AWS_MSP_Monitoring_Stack_Universal_Installer.zip`
2. Extract to any folder
3. Open the `aws-msp-monitoring` directory


### **Step 2: Run the Installer**

#### **Windows Users:**
1. **Double-click** `install.bat`
2. **Wait** for installation to complete
3. **Done!** Grafana opens automatically

#### **macOS/Linux Users:**
1. **Open Terminal**
2. **Navigate** to the extracted folder: `cd path/to/aws-msp-monitoring`
3. **Run:** `./install.sh`
4. **Done!** Grafana opens automatically

### **Step 3: Access Your Monitoring**
- **Grafana Dashboard:** http://localhost:3000
- **Login:** admin / (password in CREDENTIALS.md)
- **Start monitoring!**

---

## 📖 **What You Get**


✅ Enterprise-style monitoring stack (Prometheus, Grafana, API, Pushgateway)  
✅ Security patterns and hardening examples (authentication and encryption)  
✅ **45 plugins across 12 categories** (complete ecosystem coverage)  
✅ **Complete dashboard tutorial** (step-by-step beginner to advanced)  
✅ **API integration examples** (Python, JavaScript, curl)  
✅ **Demo data generator** (realistic metrics for testing)  
✅ **Comprehensive documentation** (6 detailed guides)  

---

## 🎯 **Next Steps After Installation**

### **For Beginners:**
1. **Read:** `AWS_MSP_DASHBOARD_WALKTHROUGH.md` - Complete tutorial
2. **Create dashboards** following the step-by-step guide
3. **Generate demo data** using the included generator

### **For Developers:**
1. **API integration** examples in the dashboard walkthrough
2. **Connect your applications** using the secure REST API
3. **Custom metrics** and dashboard creation

### **For MSP Partners:**
1. **Partner guide:** `AWS_MSP_PARTNER_GUIDE.md`
2. **Security analysis:** `AWS_MSP_SECURITY_ANALYSIS.md`
3. **Customer handoff** procedures and documentation

---

## 🔌 Plugin System (Extensible by Design)
The monitoring stack supports a modular plugin system covering performance, security, cloud integration, ITSM, data platforms, and AI/ML use cases. **All 47 plugins come with production-ready configuration templates** - just fill in your credentials and start monitoring!

<details>
<summary><strong>🚀 Quick Plugin Installation</strong></summary>

```bash
# Option 1: Interactive command-line installer
./install-plugins.sh

# Option 2: Web-based GUI (recommended)
python3 aws_msp_plugin_web_gui.py
# Then open: http://localhost:5000

# Option 3: Direct command-line
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install aws-cloudwatch
```

**What you get automatically:**
- ✅ **Comprehensive `.env.template`** with all required variables
- ✅ **Production-ready `docker-compose.yml`** with health checks
- ✅ **Service-specific configuration files** with advanced options
- ✅ **Interactive setup script** for guided configuration
- ✅ **Complete documentation** with examples and troubleshooting
</details>

<details>
<summary><strong>📋 Available Plugin Categories (47 plugins across 12 categories)</strong></summary>

- **🚀 Performance & Scale** - Federation, HA, Auto-scaling (3 plugins)
- **🛡️ Advanced Security** - SAML/OAuth, Certificates, Network segmentation (3 plugins)
- **☁️ Cloud Integration** - AWS CloudWatch, AWS CloudTrail, AWS Config, Auto-Discovery, Cost optimization, MontyCloud (6 plugins)
- **🔒 Security Partner Integration** - CrowdStrike, Palo Alto, Alert Logic (3 plugins)
- **📊 Monitoring Partner Integration** - Splunk, Sumo Logic, Datadog (3 plugins)
- **🎫 CMDB/ITSM Integration** - ServiceNow, BMC Helix, Jira Service Management (3 plugins)
- **🎟️ Ticketing Platform Integration** - AWS Support, Zendesk, Freshworks, Linear (4 plugins)
- **🆔 Identity Management Integration** - Duo Security, Okta (2 plugins)
- **💾 Data Platform Integration** - Redis, Elasticsearch, Databricks, Snowflake, MongoDB, Confluent, InfluxDB, ClickHouse, Neo4j (9 plugins)
- **🤖 AI/ML Features** - Anomaly detection, Predictive alerts, Auto-remediation (3 plugins)
- **📈 Advanced Analytics** - Business intelligence, ELK stack, APM monitoring (3 plugins)
- **🔧 DevOps Automation** - AWS CloudFormation, Terraform, Infrastructure as Code, CI/CD, GitOps (5 plugins)
</details>

<details>
<summary><strong>📦 Popular Plugin Packs</strong></summary>

- **AWS Integration Pack** - AWS CloudWatch + AWS CloudTrail + AWS Config + Auto-Discovery + Cost Optimization + MontyCloud
- **Security Enhancement Pack** - SAML Auth + Certificate Auth
- **Security Partner Pack** - CrowdStrike + Palo Alto + Alert Logic
- **Monitoring Partner Pack** - Splunk + Sumo Logic + Datadog
- **CMDB/ITSM Pack** - ServiceNow + BMC Helix + Jira Service Management
- **Ticketing Platform Pack** - AWS Support + Zendesk + Freshworks + Linear
- **Identity Management Pack** - Duo Security + Okta
- **Data Platform Pack** - Redis + Elasticsearch + Databricks + Snowflake + MongoDB + Confluent + InfluxDB + ClickHouse + Neo4j
- **Analytics Pack** - BI + Log Aggregation + APM
- **AI/ML Pack** - Anomaly Detection + Predictive Alerts
- **Enterprise Scale Pack** - Federation + HA + Auto-Scaling
</details>

<details>
<summary><strong>💡 Getting Started Examples</strong></summary>

**Basic AWS MSP Setup:**
```bash
# Install base stack
./aws-msp-monitoring-installer.sh

# Add essential AWS integration
python3 aws_msp_plugin_manager.py install aws-cloudwatch
python3 aws_msp_plugin_manager.py install aws-cloudtrail
python3 aws_msp_plugin_manager.py install aws-config
python3 aws_msp_plugin_manager.py install montycloud
```

**Security-Focused MSP:**
```bash
# Install base + security partners
python3 aws_msp_plugin_manager.py install crowdstrike-falcon
python3 aws_msp_plugin_manager.py install duo-security
python3 aws_msp_plugin_manager.py install okta
```

**DevOps-Focused MSP:**
```bash
# Install infrastructure monitoring
python3 aws_msp_plugin_manager.py install aws-cloudformation
python3 aws_msp_plugin_manager.py install terraform
python3 aws_msp_plugin_manager.py install cicd-monitoring
```

**Data Platform MSP:**
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

**Enterprise MSP with Full Stack:**
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
<summary><strong>🔧 Plugin Management Commands</strong></summary>

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

## Package Contents

- `aws-msp-monitoring-installer.sh` - Main installer (Unix)
- `aws_msp_monitoring_stack.py` - Core installer with PyYAML auto-install
- `aws_msp_universal_installer.py` - Cross-platform installer (Windows/macOS/Linux)
- `aws_msp_security_validator.py` - Security validation
- `aws_msp_plugin_manager.py` - Plugin system (47 plugins across 12 categories)
- `aws_msp_plugin_web_gui.py` - Web-based plugin management interface
- `install-plugins.sh` - Interactive plugin installer
- `install.sh` - Unix installer
- `install.bat` - Windows installer
- `enhance-all-plugins.py` - Plugin validation and enhancement system
- `enhance-all-templates.py` - Comprehensive template generator
- `AWS_MSP_DASHBOARD_WALKTHROUGH.md` - Complete dashboard guide
- `AWS_MSP_DASHBOARD_QUERY_REFERENCE.md` - Prometheus query reference
- `AWS_MSP_PARTNER_GUIDE.md` - Partner deployment guide
- `AWS_MSP_SECURITY_GUIDE.md` - Security documentation
- `AWS_MSP_SECURITY_ANALYSIS.md` - Security analysis
- `aws_msp_demo_data_generator.py` - Demo data generator (fixed metric names)

## Support

<details>
<summary><strong>🔧 Quick Troubleshooting Steps</strong></summary>

### **1. Verify Prerequisites**
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

### **2. Service Status Checks**
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

### **3. Network & Port Troubleshooting**
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

### **4. System Resource Checks**
```bash
# Check memory usage (need 8GB+ available)
free -h           # Linux
vm_stat           # macOS
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows

# Check CPU usage
top -n 1          # Linux/macOS
wmic cpu get loadpercentage  # Windows
```

### **5. Plugin-Specific Issues**
```bash
# List installed plugins
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack list --installed

# Check plugin status
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack status

# Reinstall problematic plugin
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack uninstall <plugin-name>
python3 aws_msp_plugin_manager.py --install-dir customer-monitoring-stack install <plugin-name>
```

### **6. Log Collection for Support**
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

### **7. Common Error Solutions**

**"Port already in use" errors:**
```bash
# Find and stop conflicting processes
lsof -i :3000     # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process using port
kill -9 <PID>     # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**"Permission denied" errors:**
```bash
# Fix file permissions (Unix)
chmod +x install.sh
chmod +x install-plugins.sh
sudo chown -R $USER:$USER customer-monitoring-stack/

# Run as administrator (Windows)
# Right-click install.bat → "Run as administrator"
```

**"Docker not found" errors:**
```bash
# Install Docker Desktop
# macOS: https://docs.docker.com/desktop/mac/install/
# Windows: https://docs.docker.com/desktop/windows/install/
# Linux: https://docs.docker.com/engine/install/

# Start Docker service
sudo systemctl start docker  # Linux
# Or start Docker Desktop application
```

**"Module not found" Python errors:**
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
<summary><strong>📚 Additional Resources</strong></summary>

1. **Detailed troubleshooting:** `AWS_MSP_DASHBOARD_WALKTHROUGH.md`
2. **Security issues:** `AWS_MSP_SECURITY_GUIDE.md`
3. **Partner deployment:** `AWS_MSP_PARTNER_GUIDE.md`
</details>

### **Contact Support**
- **GitLab Issues:** [Report bugs and feature requests](https://gitlab.aws.dev/adrianrs/managed-services-operations-in-a-box/-/issues)

## Prerequisites

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **CPU**: 4 cores minimum, 8 cores recommended (16+ cores for enterprise deployments)
- **RAM**: 8GB minimum, 16GB recommended (32GB+ for 30+ plugins)
- **Disk**: 20GB free space (base stack: 5GB, plugins: ~100MB each, data retention: 10-15GB)
- **Network**: Internet connection for initial setup
- **Python**: 3.7+ (PyYAML and requests auto-installed during setup)

### Scaling Guidelines
- **Small MSP (1-15 plugins)**: 4 CPU, 8GB RAM, 20GB disk
- **Medium MSP (15-30 plugins)**: 8 CPU, 16GB RAM, 50GB disk  
- **Enterprise MSP (30+ plugins)**: 16+ CPU, 32GB+ RAM, 100GB+ disk

> **Note:** This project is not an official AWS product and does not by itself confer AWS MSP Program compliance. Partners are responsible for validating their own implementations against current AWS MSP Program requirements.

