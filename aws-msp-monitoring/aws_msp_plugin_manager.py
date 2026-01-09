#!/usr/bin/env python3
"""
AWS MSP Plugin Manager - Fixed Version
=====================================

Modular plugin system for extending the base monitoring stack.
Partners and customers can pick and choose additional features.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

class PluginManager:
    def __init__(self, install_dir: str = "secure-monitoring-stack"):
        self.install_dir = Path(install_dir)
        self.plugins_dir = self.install_dir / "plugins"
        self.plugins_config = self.install_dir / "plugins.json"
        
        self.available_plugins = {}
        self.installed_plugins = {}
        
        self.load_plugin_registry()
        self.load_installed_plugins()
        
        # Ensure plugins directory exists
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
    
    def load_plugin_registry(self):
        """Load available plugins registry"""
        self.available_plugins = {
            # Performance & Scale
            "prometheus-federation": {
                "name": "Prometheus Federation",
                "category": "Performance & Scale",
                "description": "Multi-node Prometheus federation for enterprise scale",
                "dependencies": ["base"],
                "docker_services": ["prometheus-federation"],
                "config_files": ["federation.yml"],
                "size_mb": 15,
                "complexity": "intermediate"
            },
            "grafana-ha": {
                "name": "Grafana High Availability",
                "category": "Performance & Scale", 
                "description": "Load-balanced Grafana cluster with shared database",
                "dependencies": ["base"],
                "docker_services": ["grafana-lb", "grafana-node-1", "grafana-node-2"],
                "config_files": ["grafana-ha.yml", "nginx-lb.conf"],
                "size_mb": 25,
                "complexity": "advanced"
            },
            "auto-scaling": {
                "name": "Auto-Scaling Monitor",
                "category": "Performance & Scale",
                "description": "Automatic scaling based on metrics volume and load",
                "dependencies": ["base", "prometheus-federation"],
                "docker_services": ["scaling-controller"],
                "config_files": ["scaling-rules.yml"],
                "size_mb": 8,
                "complexity": "advanced"
            },
            
            # Advanced Security
            "saml-auth": {
                "name": "SAML/OAuth Authentication",
                "category": "Advanced Security",
                "description": "Enterprise SSO integration with SAML and OAuth providers",
                "dependencies": ["base"],
                "docker_services": ["auth-proxy"],
                "config_files": ["saml-config.yml", "oauth-providers.json"],
                "size_mb": 12,
                "complexity": "intermediate"
            },
            "cert-auth": {
                "name": "Certificate Authentication",
                "category": "Advanced Security",
                "description": "mTLS certificate-based authentication and authorization",
                "dependencies": ["base"],
                "docker_services": ["cert-manager"],
                "config_files": ["cert-config.yml", "ca-bundle.pem"],
                "size_mb": 5,
                "complexity": "advanced"
            },
            "network-security": {
                "name": "Network Segmentation",
                "category": "Advanced Security",
                "description": "VPN integration and network security monitoring",
                "dependencies": ["base"],
                "docker_services": ["network-monitor", "vpn-gateway"],
                "config_files": ["network-policies.yml"],
                "size_mb": 18,
                "complexity": "expert"
            },
            
            # Cloud Integration
            "aws-cloudwatch": {
                "name": "AWS CloudWatch Integration",
                "category": "Cloud Integration",
                "description": "Native AWS CloudWatch metrics and log integration",
                "dependencies": ["base"],
                "docker_services": ["cloudwatch-exporter"],
                "config_files": ["aws-config.yml", "cloudwatch-metrics.json"],
                "size_mb": 10,
                "complexity": "beginner"
            },
            "aws-discovery": {
                "name": "AWS Auto-Discovery",
                "category": "Cloud Integration", 
                "description": "Automatic discovery of EC2, ECS, EKS, and RDS resources",
                "dependencies": ["base", "aws-cloudwatch"],
                "docker_services": ["aws-discovery"],
                "config_files": ["discovery-rules.yml"],
                "size_mb": 15,
                "complexity": "intermediate"
            },
            "cost-optimization": {
                "name": "Cost Optimization Monitor",
                "category": "Cloud Integration",
                "description": "AWS cost tracking and optimization recommendations",
                "dependencies": ["base", "aws-cloudwatch"],
                "docker_services": ["cost-analyzer"],
                "config_files": ["cost-rules.yml"],
                "size_mb": 12,
                "complexity": "intermediate"
            },
            "montycloud": {
                "name": "MontyCloud Governance",
                "category": "Cloud Integration",
                "description": "MontyCloud multi-cloud governance, compliance, and cost optimization (AWS MSP Program benefit)",
                "dependencies": ["base"],
                "docker_services": ["montycloud-connector"],
                "config_files": ["montycloud-config.yml", "montycloud-api-keys.json"],
                "size_mb": 25,
                "complexity": "intermediate"
            },
            
            # Security Partner Integration
            "crowdstrike-falcon": {
                "name": "CrowdStrike Falcon EDR",
                "category": "Security Partner Integration",
                "description": "CrowdStrike endpoint detection and response metrics integration",
                "dependencies": ["base"],
                "docker_services": ["falcon-exporter"],
                "config_files": ["crowdstrike-config.yml", "falcon-api-keys.json"],
                "size_mb": 18,
                "complexity": "intermediate"
            },
            "palo-alto-prisma": {
                "name": "Palo Alto Prisma Cloud",
                "category": "Security Partner Integration",
                "description": "Palo Alto Networks firewall and cloud security metrics",
                "dependencies": ["base"],
                "docker_services": ["prisma-exporter"],
                "config_files": ["palo-alto-config.yml", "prisma-credentials.json"],
                "size_mb": 22,
                "complexity": "intermediate"
            },
            "alertlogic": {
                "name": "Alert Logic Security",
                "category": "Security Partner Integration",
                "description": "Alert Logic threat detection and security monitoring",
                "dependencies": ["base"],
                "docker_services": ["alertlogic-exporter"],
                "config_files": ["alertlogic-config.yml", "al-api-config.json"],
                "size_mb": 16,
                "complexity": "intermediate"
            },
            
            # Monitoring Partner Integration
            "splunk-enterprise": {
                "name": "Splunk Enterprise",
                "category": "Monitoring Partner Integration",
                "description": "Splunk log analysis and SIEM integration for AWS workloads",
                "dependencies": ["base"],
                "docker_services": ["splunk-forwarder", "splunk-metrics"],
                "config_files": ["splunk-config.yml", "splunk-inputs.conf"],
                "size_mb": 45,
                "complexity": "advanced"
            },
            "sumologic": {
                "name": "Sumo Logic",
                "category": "Monitoring Partner Integration", 
                "description": "Sumo Logic cloud-native analytics and monitoring",
                "dependencies": ["base"],
                "docker_services": ["sumologic-collector"],
                "config_files": ["sumologic-config.yml", "sumo-sources.json"],
                "size_mb": 25,
                "complexity": "intermediate"
            },
            "datadog": {
                "name": "Datadog APM",
                "category": "Monitoring Partner Integration",
                "description": "Datadog application performance monitoring and infrastructure metrics",
                "dependencies": ["base"],
                "docker_services": ["datadog-agent"],
                "config_files": ["datadog-config.yml", "dd-integrations.json"],
                "size_mb": 35,
                "complexity": "intermediate"
            },
            
            # CMDB/ITSM Integration (Configuration Management Database / IT Service Management)
            "servicenow": {
                "name": "ServiceNow ITSM",
                "category": "CMDB/ITSM Integration",
                "description": "ServiceNow incident, change, and configuration management integration",
                "dependencies": ["base"],
                "docker_services": ["servicenow-connector"],
                "config_files": ["servicenow-config.yml", "snow-api-credentials.json"],
                "size_mb": 28,
                "complexity": "intermediate"
            },
            "bmc-helix": {
                "name": "BMC Helix ITSM",
                "category": "CMDB/ITSM Integration",
                "description": "BMC Remedy/Helix change management and CMDB integration",
                "dependencies": ["base"],
                "docker_services": ["bmc-connector"],
                "config_files": ["bmc-helix-config.yml", "remedy-credentials.json"],
                "size_mb": 32,
                "complexity": "advanced"
            },
            "jira-service-mgmt": {
                "name": "Atlassian Jira Service Management",
                "category": "CMDB/ITSM Integration",
                "description": "Jira Service Management incident and change tracking integration",
                "dependencies": ["base"],
                "docker_services": ["jira-connector"],
                "config_files": ["jira-config.yml", "atlassian-api-keys.json"],
                "size_mb": 20,
                "complexity": "beginner"
            },
            
            # Ticketing Platform Integration
            "aws-support": {
                "name": "AWS Support Case Integration",
                "category": "Ticketing Platform Integration",
                "description": "AWS Support case monitoring, response times, and resolution tracking",
                "dependencies": ["base"],
                "docker_services": ["aws-support-connector"],
                "config_files": ["aws-support-config.yml", "aws-support-credentials.json"],
                "size_mb": 12,
                "complexity": "intermediate"
            },
            "zendesk": {
                "name": "Zendesk Support",
                "category": "Ticketing Platform Integration",
                "description": "Zendesk customer support and helpdesk ticket integration",
                "dependencies": ["base"],
                "docker_services": ["zendesk-connector"],
                "config_files": ["zendesk-config.yml", "zendesk-api-keys.json"],
                "size_mb": 22,
                "complexity": "beginner"
            },
            "freshworks": {
                "name": "Freshworks Suite",
                "category": "Ticketing Platform Integration",
                "description": "Freshdesk/Freshservice ticket and customer service integration",
                "dependencies": ["base"],
                "docker_services": ["freshworks-connector"],
                "config_files": ["freshworks-config.yml", "fresh-api-credentials.json"],
                "size_mb": 18,
                "complexity": "beginner"
            },
            "linear": {
                "name": "Linear Issue Tracking",
                "category": "Ticketing Platform Integration",
                "description": "Linear modern issue tracking and project management integration",
                "dependencies": ["base"],
                "docker_services": ["linear-connector"],
                "config_files": ["linear-config.yml", "linear-api-token.json"],
                "size_mb": 15,
                "complexity": "intermediate"
            },
            
            # Identity Management Integration
            "duo-security": {
                "name": "Duo Security MFA",
                "category": "Identity Management Integration",
                "description": "Duo Security multi-factor authentication and access monitoring",
                "dependencies": ["base"],
                "docker_services": ["duo-connector"],
                "config_files": ["duo-config.yml", "duo-api-credentials.json"],
                "size_mb": 16,
                "complexity": "intermediate"
            },
            "okta": {
                "name": "Okta Identity Platform",
                "category": "Identity Management Integration",
                "description": "Okta SSO, MFA, and identity governance integration",
                "dependencies": ["base"],
                "docker_services": ["okta-connector"],
                "config_files": ["okta-config.yml", "okta-api-tokens.json"],
                "size_mb": 24,
                "complexity": "intermediate"
            },
            
            # Data Platform Integration
            "redis": {
                "name": "Redis Data Store",
                "category": "Data Platform Integration",
                "description": "Redis caching, session storage, and real-time data structure monitoring",
                "dependencies": ["base"],
                "docker_services": ["redis-monitor"],
                "config_files": ["redis-config.yml", "redis-cluster-config.json"],
                "size_mb": 14,
                "complexity": "beginner"
            },
            "elasticsearch": {
                "name": "Elasticsearch Data Platform",
                "category": "Data Platform Integration",
                "description": "Elasticsearch cluster monitoring, index health, and search performance tracking",
                "dependencies": ["base"],
                "docker_services": ["elasticsearch-monitor"],
                "config_files": ["elasticsearch-config.yml", "es-cluster-settings.json"],
                "size_mb": 28,
                "complexity": "intermediate"
            },
            "databricks": {
                "name": "Databricks Analytics",
                "category": "Data Platform Integration",
                "description": "Databricks workspace monitoring, job tracking, and cluster performance analysis",
                "dependencies": ["base"],
                "docker_services": ["databricks-connector"],
                "config_files": ["databricks-config.yml", "databricks-api-tokens.json"],
                "size_mb": 32,
                "complexity": "advanced"
            },
            "snowflake": {
                "name": "Snowflake Data Warehouse",
                "category": "Data Platform Integration",
                "description": "Snowflake warehouse monitoring, query performance, and cost tracking",
                "dependencies": ["base"],
                "docker_services": ["snowflake-connector"],
                "config_files": ["snowflake-config.yml", "snowflake-credentials.json"],
                "size_mb": 26,
                "complexity": "intermediate"
            },
            "mongodb": {
                "name": "MongoDB Database",
                "category": "Data Platform Integration",
                "description": "MongoDB cluster monitoring, replica set health, and document store performance",
                "dependencies": ["base"],
                "docker_services": ["mongodb-monitor"],
                "config_files": ["mongodb-config.yml", "mongo-cluster-settings.json"],
                "size_mb": 20,
                "complexity": "intermediate"
            },
            "confluent": {
                "name": "Confluent Kafka Platform",
                "category": "Data Platform Integration",
                "description": "Confluent Kafka event streaming monitoring, topic throughput, and consumer lag tracking",
                "dependencies": ["base"],
                "docker_services": ["confluent-monitor"],
                "config_files": ["confluent-config.yml", "kafka-cluster-config.json"],
                "size_mb": 35,
                "complexity": "advanced"
            },
            "influxdb": {
                "name": "InfluxDB Time Series",
                "category": "Data Platform Integration",
                "description": "InfluxDB time series database monitoring, query performance, and retention tracking",
                "dependencies": ["base"],
                "docker_services": ["influxdb-monitor"],
                "config_files": ["influxdb-config.yml", "influx-retention-policies.json"],
                "size_mb": 18,
                "complexity": "intermediate"
            },
            "clickhouse": {
                "name": "ClickHouse Analytics",
                "category": "Data Platform Integration",
                "description": "ClickHouse OLAP database monitoring, query performance, and real-time analytics tracking",
                "dependencies": ["base"],
                "docker_services": ["clickhouse-monitor"],
                "config_files": ["clickhouse-config.yml", "ch-cluster-settings.json"],
                "size_mb": 24,
                "complexity": "advanced"
            },
            "neo4j": {
                "name": "Neo4j Graph Database",
                "category": "Data Platform Integration",
                "description": "Neo4j graph database monitoring, relationship analysis, and query performance tracking",
                "dependencies": ["base"],
                "docker_services": ["neo4j-monitor"],
                "config_files": ["neo4j-config.yml", "graph-db-settings.json"],
                "size_mb": 22,
                "complexity": "intermediate"
            },
            
            # AI/ML Features
            "anomaly-detection": {
                "name": "AI Anomaly Detection",
                "category": "AI/ML Features",
                "description": "Machine learning-based anomaly detection and alerting",
                "dependencies": ["base"],
                "docker_services": ["ml-detector", "model-trainer"],
                "config_files": ["ml-config.yml", "training-data.json"],
                "size_mb": 45,
                "complexity": "advanced"
            },
            "predictive-alerts": {
                "name": "Predictive Alerting",
                "category": "AI/ML Features",
                "description": "Predictive alerts based on historical patterns",
                "dependencies": ["base", "anomaly-detection"],
                "docker_services": ["predictor"],
                "config_files": ["prediction-models.yml"],
                "size_mb": 30,
                "complexity": "advanced"
            },
            "auto-remediation": {
                "name": "Auto-Remediation",
                "category": "AI/ML Features",
                "description": "Automated issue remediation based on runbooks",
                "dependencies": ["base", "predictive-alerts"],
                "docker_services": ["remediation-engine"],
                "config_files": ["runbooks.yml", "remediation-rules.json"],
                "size_mb": 20,
                "complexity": "expert"
            },
            
            # Advanced Analytics
            "business-intelligence": {
                "name": "Business Intelligence",
                "category": "Advanced Analytics",
                "description": "Custom BI dashboards with advanced analytics",
                "dependencies": ["base"],
                "docker_services": ["bi-engine", "data-warehouse"],
                "config_files": ["bi-config.yml", "dashboard-templates.json"],
                "size_mb": 35,
                "complexity": "intermediate"
            },
            "log-aggregation": {
                "name": "Log Aggregation (ELK)",
                "category": "Advanced Analytics",
                "description": "Elasticsearch, Logstash, Kibana stack for log analysis",
                "dependencies": ["base"],
                "docker_services": ["elasticsearch", "logstash", "kibana"],
                "config_files": ["elk-config.yml", "log-pipelines.json"],
                "size_mb": 80,
                "complexity": "intermediate"
            },
            "apm-monitoring": {
                "name": "Application Performance Monitoring",
                "category": "Advanced Analytics",
                "description": "Distributed tracing and APM with Jaeger/Zipkin",
                "dependencies": ["base"],
                "docker_services": ["jaeger", "apm-collector"],
                "config_files": ["apm-config.yml", "tracing-rules.json"],
                "size_mb": 25,
                "complexity": "intermediate"
            },
            
            # DevOps Automation
            "aws-cloudformation": {
                "name": "AWS CloudFormation",
                "category": "DevOps Automation",
                "description": "AWS CloudFormation stack monitoring, drift detection, and deployment tracking",
                "dependencies": ["base"],
                "docker_services": ["cloudformation-monitor"],
                "config_files": ["cloudformation-config.yml", "cfn-stack-filters.json"],
                "size_mb": 18,
                "complexity": "intermediate"
            },
            "terraform": {
                "name": "Terraform Infrastructure",
                "category": "DevOps Automation",
                "description": "Terraform state monitoring, plan analysis, and infrastructure drift detection",
                "dependencies": ["base"],
                "docker_services": ["terraform-monitor"],
                "config_files": ["terraform-config.yml", "tf-workspace-config.json"],
                "size_mb": 22,
                "complexity": "intermediate"
            },
            "infrastructure-as-code": {
                "name": "Infrastructure as Code",
                "category": "DevOps Automation",
                "description": "Generic IaC monitoring for multiple platforms and deployment tracking",
                "dependencies": ["base"],
                "docker_services": ["iac-monitor"],
                "config_files": ["iac-config.yml", "iac-templates/"],
                "size_mb": 15,
                "complexity": "advanced"
            },
            "cicd-monitoring": {
                "name": "CI/CD Pipeline Monitoring",
                "category": "DevOps Automation",
                "description": "Jenkins, GitHub Actions, GitLab CI pipeline monitoring",
                "dependencies": ["base"],
                "docker_services": ["pipeline-monitor"],
                "config_files": ["cicd-config.yml", "pipeline-templates.json"],
                "size_mb": 18,
                "complexity": "intermediate"
            },
            "gitops-deployment": {
                "name": "GitOps Deployment",
                "category": "DevOps Automation",
                "description": "ArgoCD/Flux integration for GitOps workflows",
                "dependencies": ["base", "cicd-monitoring"],
                "docker_services": ["gitops-controller"],
                "config_files": ["gitops-config.yml", "deployment-templates/"],
                "size_mb": 22,
                "complexity": "advanced"
            }
        }
    
    def load_installed_plugins(self):
        """Load currently installed plugins"""
        if self.plugins_config.exists():
            with open(self.plugins_config) as f:
                self.installed_plugins = json.load(f)
        else:
            self.installed_plugins = {}
    
    def save_installed_plugins(self):
        """Save installed plugins configuration"""
        with open(self.plugins_config, 'w') as f:
            json.dump(self.installed_plugins, f, indent=2)
    
    def install_plugin(self, plugin_id: str, force: bool = False):
        """Install a plugin"""
        plugin = self.available_plugins.get(plugin_id)
        if not plugin:
            print(f"❌ Plugin '{plugin_id}' not found")
            return False
        
        print(f"🔌 Installing plugin: {plugin['name']}")
        print(f"📦 Size: {plugin['size_mb']}MB")
        print(f"🎯 Complexity: {plugin['complexity']}")
        
        # Check dependencies
        missing_deps = self.check_dependencies(plugin_id)
        if missing_deps and not force:
            print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
            return False
        
        # Create plugin directory
        plugin_dir = self.plugins_dir / plugin_id
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate plugin files
        try:
            self._generate_plugin_files(plugin_id, plugin_dir)
        except Exception as e:
            print(f"❌ Failed to generate plugin files: {e}")
            return False
        
        # Mark as installed
        self.installed_plugins[plugin_id] = {
            "name": plugin["name"],
            "version": "1.0.0",
            "installed_at": "2026-01-07T16:43:00Z"
        }
        
        self.save_installed_plugins()
        print(f"✅ Plugin '{plugin['name']}' installed successfully")
        return True
    
    def _generate_plugin_files(self, plugin_id: str, plugin_dir: Path):
        """Generate configuration files for the plugin"""
        if not YAML_AVAILABLE:
            print(f"⚠️  Warning: PyYAML not installed. Creating basic config files.")
            return self._create_basic_configs(plugin_id, plugin_dir)
        
        plugin = self.available_plugins[plugin_id]
        
        # Create docker-compose extension
        compose_content = {
            'version': '3.8',
            'services': {}
        }
        
        for service in plugin.get('docker_services', []):
            compose_content['services'][service] = {
                'image': self._get_default_image(service),
                'container_name': service,
                'restart': 'unless-stopped',
                'networks': ['monitoring']
            }
        
        compose_file = plugin_dir / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            yaml.dump(compose_content, f, default_flow_style=False)
        
        # Create config files
        for config_file in plugin.get('config_files', []):
            self._create_config_file(plugin_dir, config_file, plugin)
        
        print(f"    ✅ Generated configuration files for {plugin_id}")
    
    def _create_basic_configs(self, plugin_id: str, plugin_dir: Path):
        """Create basic configuration files when yaml is not available"""
        plugin = self.available_plugins[plugin_id]
        
        # Create basic docker-compose extension
        compose_content = f"""version: '3.8'
services:
"""
        
        for service in plugin.get('docker_services', []):
            compose_content += f"""  {service}:
    image: {self._get_default_image(service)}
    container_name: {service}
    restart: unless-stopped
    networks:
      - monitoring
"""
        
        compose_file = plugin_dir / "docker-compose.yml"
        compose_file.write_text(compose_content)
        
        # Create basic config files
        for config_file in plugin.get('config_files', []):
            if config_file.endswith('.yml') or config_file.endswith('.yaml'):
                config_path = plugin_dir / config_file
                config_path.parent.mkdir(parents=True, exist_ok=True)
                config_path.write_text(f"# {plugin['name']} Configuration\nversion: 1\n")
            elif config_file.endswith('.json'):
                config_path = plugin_dir / config_file
                config_path.parent.mkdir(parents=True, exist_ok=True)
                config_path.write_text('{"version": 1}')
            elif config_file.endswith('/'):
                # Directory
                dir_path = plugin_dir / config_file
                dir_path.mkdir(parents=True, exist_ok=True)
                (dir_path / "README.md").write_text(f"# {plugin['name']} Templates\n")
        
        print(f"    ✅ Created basic configuration files for {plugin_id}")
        
        # Create dashboard query examples for this plugin
        self._create_dashboard_examples(plugin_id, plugin_dir, plugin)
        
        return True
    
    def _create_dashboard_examples(self, plugin_id: str, plugin_dir: Path, plugin: dict):
        """Create dashboard query examples for the plugin"""
        examples_file = plugin_dir / "dashboard_queries.md"
        
        # Plugin-specific query examples
        query_examples = {
            'aws-cloudwatch': [
                'aws_ec2_cpu_utilization',
                'aws_rds_connections', 
                'aws_lambda_invocations'
            ],
            'montycloud': [
                'montycloud_cost_savings_identified',
                'montycloud_policy_violations',
                'montycloud_compliance_score'
            ],
            'anomaly-detection': [
                'anomaly_score_cpu_usage',
                'anomaly_detected_memory_usage',
                'predicted_response_time'
            ],
            'log-aggregation': [
                'log_error_rate_per_minute',
                'application_log_volume',
                'security_log_alerts'
            ],
            'saml-auth': [
                'saml_login_attempts',
                'saml_login_failures',
                'saml_session_count'
            ],
            'crowdstrike-falcon': [
                'falcon_endpoint_detections',
                'falcon_threat_score',
                'falcon_quarantine_events'
            ],
            'palo-alto-prisma': [
                'prisma_firewall_blocks',
                'prisma_threat_detections',
                'prisma_policy_violations'
            ],
            'alertlogic': [
                'alertlogic_incidents',
                'alertlogic_threat_level',
                'alertlogic_scan_results'
            ],
            'splunk-enterprise': [
                'splunk_search_performance',
                'splunk_index_volume',
                'splunk_alert_count'
            ],
            'sumologic': [
                'sumologic_query_performance',
                'sumologic_data_volume',
                'sumologic_alert_triggers'
            ],
            'datadog': [
                'datadog_apm_traces',
                'datadog_infrastructure_health',
                'datadog_custom_metrics'
            ],
            'servicenow': [
                'servicenow_incident_count',
                'servicenow_change_requests',
                'servicenow_sla_breaches'
            ],
            'bmc-helix': [
                'bmc_remedy_tickets',
                'bmc_change_approvals',
                'bmc_cmdb_updates'
            ],
            'jira-service-mgmt': [
                'jira_service_requests',
                'jira_incident_resolution_time',
                'jira_change_velocity'
            ],
            'aws-support': [
                'aws_support_open_cases',
                'aws_support_response_time_sla',
                'aws_support_resolution_time'
            ],
            'zendesk': [
                'zendesk_ticket_volume',
                'zendesk_resolution_time',
                'zendesk_customer_satisfaction'
            ],
            'freshworks': [
                'freshdesk_open_tickets',
                'freshservice_sla_compliance',
                'freshworks_agent_performance'
            ],
            'linear': [
                'linear_issue_velocity',
                'linear_cycle_time',
                'linear_backlog_health'
            ],
            'duo-security': [
                'duo_authentication_attempts',
                'duo_mfa_success_rate',
                'duo_device_trust_score'
            ],
            'okta': [
                'okta_login_attempts',
                'okta_sso_success_rate',
                'okta_policy_violations'
            ],
            'aws-cloudformation': [
                'cloudformation_stack_status',
                'cloudformation_drift_detected',
                'cloudformation_deployment_time'
            ],
            'terraform': [
                'terraform_state_drift',
                'terraform_plan_changes',
                'terraform_apply_success_rate'
            ],
            'infrastructure-as-code': [
                'iac_deployment_frequency',
                'iac_rollback_rate',
                'iac_compliance_score'
            ],
            'redis': [
                'redis_memory_usage',
                'redis_connected_clients',
                'redis_cache_hit_ratio'
            ],
            'elasticsearch': [
                'elasticsearch_cluster_health',
                'elasticsearch_index_size',
                'elasticsearch_search_latency'
            ],
            'databricks': [
                'databricks_job_success_rate',
                'databricks_cluster_utilization',
                'databricks_notebook_execution_time'
            ],
            'snowflake': [
                'snowflake_warehouse_usage',
                'snowflake_query_performance',
                'snowflake_credit_consumption'
            ],
            'mongodb': [
                'mongodb_connections',
                'mongodb_operations_per_second',
                'mongodb_replica_lag'
            ],
            'confluent': [
                'confluent_topic_throughput',
                'confluent_consumer_lag',
                'confluent_broker_health'
            ],
            'influxdb': [
                'influxdb_query_performance',
                'influxdb_series_cardinality',
                'influxdb_retention_policy_usage'
            ],
            'clickhouse': [
                'clickhouse_query_latency',
                'clickhouse_merge_performance',
                'clickhouse_disk_usage'
            ],
            'neo4j': [
                'neo4j_query_performance',
                'neo4j_relationship_count',
                'neo4j_graph_traversal_time'
            ]
        }
        
        queries = query_examples.get(plugin_id, [f"{plugin_id}_metric_example"])
        
        content = f"""# {plugin['name']} - Dashboard Queries

## Available Metrics
"""
        
        for query in queries:
            content += f"""
### {query}
```
{query}
```
**Usage**: Add this query to a Grafana panel
**Unit**: Depends on metric type
**Panel Type**: Time series recommended
"""
        
        content += f"""
## Dashboard Panel Template
```json
{{
  "type": "timeseries",
  "targets": [
    {{
      "expr": "{queries[0] if queries else 'metric_name'}",
      "legendFormat": "Display Name",
      "refId": "A"
    }}
  ],
  "fieldConfig": {{
    "defaults": {{
      "color": {{"mode": "palette-classic"}},
      "unit": "short"
    }}
  }}
}}
```

## Troubleshooting
1. Verify plugin is active: `docker compose ps`
2. Check metrics exist: `curl "http://localhost:9090/api/v1/label/__name__/values"`
3. Test query: `curl "http://localhost:9090/api/v1/query?query=METRIC_NAME"`
"""
        
        examples_file.write_text(content)
        print(f"    ✅ Created dashboard query examples for {plugin_id}")
    
    def _get_default_image(self, service_name: str) -> str:
        """Get default Docker image for a service"""
        image_map = {
            'prometheus-federation': 'prom/prometheus:latest',
            'grafana-lb': 'nginx:alpine',
            'grafana-node-1': 'grafana/grafana:latest',
            'grafana-node-2': 'grafana/grafana:latest',
            'scaling-controller': 'alpine:latest',
            'auth-proxy': 'nginx:alpine',
            'cert-manager': 'alpine:latest',
            'network-monitor': 'alpine:latest',
            'vpn-gateway': 'alpine:latest',
            'cloudwatch-exporter': 'prom/cloudwatch-exporter:latest',
            'aws-discovery': 'alpine:latest',
            'cost-analyzer': 'alpine:latest',
            'montycloud-connector': 'montycloud/governance-connector:latest',
            'ml-detector': 'tensorflow/tensorflow:latest',
            'model-trainer': 'tensorflow/tensorflow:latest',
            'predictor': 'tensorflow/tensorflow:latest',
            'remediation-engine': 'alpine:latest',
            'bi-engine': 'alpine:latest',
            'data-warehouse': 'postgres:alpine',
            'elasticsearch': 'elasticsearch:8.11.0',
            'logstash': 'logstash:8.11.0',
            'kibana': 'kibana:8.11.0',
            'jaeger': 'jaegertracing/all-in-one:latest',
            'apm-collector': 'alpine:latest',
            'terraform-monitor': 'hashicorp/terraform:latest',
            'pipeline-monitor': 'alpine:latest',
            'gitops-controller': 'alpine:latest',
            # Security Partner Integration
            'falcon-exporter': 'crowdstrike/falcon-sensor:latest',
            'prisma-exporter': 'paloaltonetworks/prisma-cloud:latest',
            'alertlogic-exporter': 'alertlogic/al-agent:latest',
            # Monitoring Partner Integration
            'splunk-forwarder': 'splunk/universalforwarder:latest',
            'splunk-metrics': 'splunk/splunk:latest',
            'sumologic-collector': 'sumologic/collector:latest',
            'datadog-agent': 'datadog/agent:latest',
            # CMDB/ITSM Integration
            'servicenow-connector': 'servicenow/connector:latest',
            'bmc-connector': 'bmc/helix-connector:latest',
            'jira-connector': 'atlassian/jira-connector:latest',
            # Ticketing Platform Integration
            'aws-support-connector': 'amazon/aws-support-connector:latest',
            'zendesk-connector': 'zendesk/connector:latest',
            'freshworks-connector': 'freshworks/connector:latest',
            'linear-connector': 'linear/api-connector:latest',
            # Identity Management Integration
            'duo-connector': 'duo/security-connector:latest',
            'okta-connector': 'okta/identity-connector:latest',
            # DevOps Automation
            'cloudformation-monitor': 'amazon/cloudformation-monitor:latest',
            'terraform-monitor': 'hashicorp/terraform-monitor:latest',
            'iac-monitor': 'alpine:latest',
            # Data Platform Integration
            'redis-monitor': 'redis/redis-exporter:latest',
            'elasticsearch-monitor': 'elasticsearch/elasticsearch-exporter:latest',
            'databricks-connector': 'databricks/monitoring-connector:latest',
            'snowflake-connector': 'snowflake/metrics-connector:latest',
            'mongodb-monitor': 'mongo:latest',
            'confluent-monitor': 'confluentinc/cp-kafka:latest',
            'influxdb-monitor': 'influxdb:2.0',
            'clickhouse-monitor': 'clickhouse/clickhouse-server:latest',
            'neo4j-monitor': 'neo4j:latest'
        }
        return image_map.get(service_name, 'alpine:latest')
    
    def _create_config_file(self, plugin_dir: Path, config_file: str, plugin: dict):
        """Create individual config file"""
        config_path = plugin_dir / config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if config_file.endswith('.yml') or config_file.endswith('.yaml'):
            config_content = {
                'name': plugin['name'],
                'version': '1.0.0',
                'enabled': True
            }
            with open(config_path, 'w') as f:
                yaml.dump(config_content, f, default_flow_style=False)
        elif config_file.endswith('.json'):
            config_content = {
                "name": plugin['name'],
                "version": "1.0.0",
                "enabled": True
            }
            with open(config_path, 'w') as f:
                json.dump(config_content, f, indent=2)
        elif config_file.endswith('/'):
            # Directory
            config_path.mkdir(parents=True, exist_ok=True)
            readme_path = config_path / "README.md"
            readme_path.write_text(f"# {plugin['name']} Templates\n\nConfiguration templates for {plugin['name']}.\n")
        else:
            # Generic file
            config_path.write_text(f"# {plugin['name']} Configuration\n")
    
    def check_dependencies(self, plugin_id: str) -> List[str]:
        """Check if plugin dependencies are satisfied"""
        plugin = self.available_plugins.get(plugin_id)
        if not plugin:
            return []
        
        missing_deps = []
        for dep in plugin.get('dependencies', []):
            if dep == 'base':
                # Check if base monitoring stack exists
                if not (self.install_dir / "docker-compose.yml").exists():
                    missing_deps.append('base monitoring stack')
            elif dep not in self.installed_plugins:
                missing_deps.append(dep)
        
        return missing_deps
    
    def list_available_plugins(self, category: Optional[str] = None):
        """List all available plugins, optionally filtered by category"""
        plugins = self.available_plugins
        if category:
            plugins = {k: v for k, v in plugins.items() if v['category'] == category}
        
        return plugins
    
    def list_categories(self):
        """List all plugin categories"""
        categories = set()
        for plugin in self.available_plugins.values():
            categories.add(plugin['category'])
        return sorted(categories)

def main():
    parser = argparse.ArgumentParser(description='AWS MSP Plugin Manager')
    parser.add_argument('--install-dir', default='secure-monitoring-stack',
                       help='Installation directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available plugins')
    list_parser.add_argument('--category', help='Filter by category')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a plugin')
    install_parser.add_argument('plugin_id', help='Plugin ID to install')
    install_parser.add_argument('--force', action='store_true', help='Force install ignoring dependencies')
    
    # Categories command
    subparsers.add_parser('categories', help='List all categories')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PluginManager(args.install_dir)
    
    if args.command == 'list':
        plugins = manager.list_available_plugins(args.category)
        print(f"\n🔌 Available Plugins ({len(plugins)} total):")
        print("=" * 60)
        
        current_category = None
        for plugin_id, plugin in plugins.items():
            if plugin['category'] != current_category:
                current_category = plugin['category']
                print(f"\n📂 {current_category}")
                print("-" * 40)
            
            status = "✅ Installed" if plugin_id in manager.installed_plugins else "⬜ Available"
            print(f"  {plugin_id:<20} | {plugin['name']:<30} | {status}")
            print(f"  {'':20} | {plugin['description']:<30} | {plugin['size_mb']}MB")
    
    elif args.command == 'install':
        manager.install_plugin(args.plugin_id, args.force)
        print("\n🔄 Restart the monitoring stack to activate the plugin:")
        print(f"  cd {args.install_dir}")
        print("  docker-compose down && docker-compose up -d")
    
    elif args.command == 'categories':
        categories = manager.list_categories()
        print(f"\n📂 Plugin Categories ({len(categories)} total):")
        print("=" * 40)
        for category in categories:
            count = len([p for p in manager.available_plugins.values() if p['category'] == category])
            print(f"  {category:<30} | {count} plugins")

if __name__ == "__main__":
    main()
