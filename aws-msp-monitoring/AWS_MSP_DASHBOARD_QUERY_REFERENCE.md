# AWS MSP Dashboard Query Reference

## Standard Prometheus Queries for AWS MSP Monitoring Stack

### System Metrics (Always Available)
```
# CPU Usage
system_cpu_usage

# Memory Usage  
system_memory_usage

# Response Time
system_response_time

# Error Rate
system_error_rate
```

### Anomaly Detection Metrics (When anomaly-detection plugin installed)
```
# Anomaly Scores (Z-scores)
anomaly_score_cpu_usage
anomaly_score_memory_usage
anomaly_score_response_time

# Anomaly Detection Flags (0 or 1)
anomaly_detected_cpu_usage
anomaly_detected_memory_usage
anomaly_detected_response_time

# Predictions
predicted_cpu_usage
predicted_memory_usage
predicted_response_time
```

### AWS CloudWatch Metrics (When aws-cloudwatch plugin installed)
```
# EC2 Metrics
aws_ec2_cpu_utilization
aws_ec2_network_in
aws_ec2_network_out

# RDS Metrics
aws_rds_cpu_utilization
aws_rds_connections
aws_rds_free_storage_space

# Lambda Metrics
aws_lambda_invocations
aws_lambda_errors
aws_lambda_duration
```

### MontyCloud Governance Metrics (When montycloud plugin installed)
```
# Cost Optimization
montycloud_cost_savings_identified
montycloud_resource_optimization_opportunities
montycloud_cost_anomaly_detected

# Compliance & Governance
montycloud_policy_violations
montycloud_compliance_score
montycloud_security_findings

# Automation
montycloud_automation_executions
montycloud_remediation_actions
montycloud_workflow_success_rate
```

### Security Metrics (When security plugins installed)
```
# SAML Authentication
saml_login_attempts
saml_login_failures
saml_session_count

# Certificate Status
cert_expiry_days
cert_validation_errors
cert_renewal_alerts

# Security Partner Integration
falcon_endpoint_detections
falcon_threat_score
prisma_firewall_blocks
prisma_threat_detections
alertlogic_incidents
```

### CMDB/ITSM Metrics (When ITSM plugins installed)
```
# ServiceNow Integration
servicenow_incident_count
servicenow_change_requests
servicenow_sla_breaches

# BMC Helix Integration
bmc_remedy_tickets
bmc_change_approvals
bmc_cmdb_updates

# Jira Service Management
jira_service_requests
jira_incident_resolution_time
jira_change_velocity
```

### Monitoring Partner Metrics (When partner plugins installed)
```
# Splunk Integration
splunk_search_performance
splunk_index_volume
splunk_alert_count

# Sumo Logic Integration
sumologic_query_performance
sumologic_data_volume
sumologic_alert_triggers

# Datadog Integration
datadog_apm_traces
datadog_infrastructure_health
datadog_custom_metrics
```

### Performance Metrics (When performance plugins installed)
```
# Prometheus Federation
prometheus_federation_samples_total
prometheus_federation_queries_total

# Grafana HA
grafana_active_sessions
grafana_dashboard_views
grafana_api_requests_total
```

### Ticketing Platform Metrics (When ticketing plugins installed)
```
# AWS Support Integration
aws_support_open_cases
aws_support_case_severity_distribution
aws_support_response_time_sla
aws_support_resolution_time
aws_support_case_status_changes
aws_support_communication_count

# Zendesk Integration
zendesk_ticket_volume
zendesk_resolution_time
zendesk_customer_satisfaction

# Freshworks Integration
freshdesk_open_tickets
freshservice_sla_compliance
freshworks_agent_performance

# Linear Integration
linear_issue_velocity
linear_cycle_time
linear_backlog_health
```

### Identity Management Metrics (When identity plugins installed)
```
# Duo Security Integration
duo_authentication_attempts
duo_mfa_success_rate
duo_device_trust_score
duo_policy_violations
duo_bypass_attempts

# Okta Integration
okta_login_attempts
okta_sso_success_rate
okta_policy_violations
okta_user_provisioning_events
okta_app_access_requests
```

### DevOps Automation Metrics (When DevOps plugins installed)
```
# AWS CloudFormation Integration
cloudformation_stack_status
cloudformation_drift_detected
cloudformation_deployment_time
cloudformation_rollback_events
cloudformation_resource_count

# Terraform Integration
terraform_state_drift
terraform_plan_changes
terraform_apply_success_rate
terraform_workspace_health
terraform_resource_drift

# Infrastructure as Code
iac_deployment_frequency
iac_rollback_rate
iac_compliance_score
iac_security_violations
iac_cost_impact
```

### Data Platform Metrics (When data platform plugins installed)
```
# Redis Integration
redis_memory_usage
redis_connected_clients
redis_cache_hit_ratio
redis_keyspace_hits
redis_evicted_keys

# Elasticsearch Integration
elasticsearch_cluster_health
elasticsearch_index_size
elasticsearch_search_latency
elasticsearch_indexing_rate
elasticsearch_node_disk_usage

# Databricks Integration
databricks_job_success_rate
databricks_cluster_utilization
databricks_notebook_execution_time
databricks_spark_job_duration
databricks_cost_per_workload

# Snowflake Integration
snowflake_warehouse_usage
snowflake_query_performance
snowflake_credit_consumption
snowflake_data_transfer_volume
snowflake_storage_usage

# MongoDB Integration
mongodb_connections
mongodb_operations_per_second
mongodb_replica_lag
mongodb_memory_usage
mongodb_index_efficiency

# Confluent Kafka Integration
confluent_topic_throughput
confluent_consumer_lag
confluent_broker_health
confluent_partition_count
confluent_message_rate

# InfluxDB Integration
influxdb_query_performance
influxdb_series_cardinality
influxdb_retention_policy_usage
influxdb_write_throughput
influxdb_disk_usage

# ClickHouse Integration
clickhouse_query_latency
clickhouse_merge_performance
clickhouse_disk_usage
clickhouse_table_size
clickhouse_insert_rate

# Neo4j Integration
neo4j_query_performance
neo4j_relationship_count
neo4j_graph_traversal_time
neo4j_node_count
neo4j_memory_usage
```

## Dashboard Panel Configuration

### Time Series Panel Template
```json
{
  "type": "timeseries",
  "targets": [
    {
      "expr": "METRIC_NAME_HERE",
      "legendFormat": "Display Name",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "unit": "UNIT_HERE"
    }
  }
}
```

### Stat Panel Template
```json
{
  "type": "stat",
  "targets": [
    {
      "expr": "METRIC_NAME_HERE",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "thresholds": {
        "steps": [
          {"color": "green", "value": null},
          {"color": "yellow", "value": 80},
          {"color": "red", "value": 90}
        ]
      }
    }
  }
}
```

## Common Units
- `percent` - For CPU, memory percentages
- `ms` - For response times, latency
- `bytes` - For memory, storage sizes
- `short` - For counts, rates
- `ops` - For operations per second

## Troubleshooting Dashboard Issues

### No Data Showing
1. Check metric exists: `curl "http://localhost:9090/api/v1/label/__name__/values"`
2. Test query: `curl "http://localhost:9090/api/v1/query?query=METRIC_NAME"`
3. Verify time range in dashboard (use "Last 5 minutes")
4. Check if data source is Prometheus at http://prometheus:9090

### Metrics Not Available
1. Verify plugin is installed: `python3 aws_msp_plugin_manager.py list --installed`
2. Check plugin services running: `docker compose ps`
3. Restart monitoring stack: `docker compose restart`

### Query Errors
1. Use simple metric names (no complex filtering initially)
2. Avoid job labels unless specifically needed
3. Test queries in Prometheus UI first: http://localhost:9090
