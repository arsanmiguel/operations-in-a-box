#!/usr/bin/env python3
"""
AWS Config Compliance Monitor and Metrics Exporter
Monitors AWS Config rules and exports compliance metrics to Prometheus
"""

import json
import time
import boto3
import yaml
import os
from datetime import datetime, timedelta
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigComplianceMonitor:
    def __init__(self, config_file='/config/config.yml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.config_client = boto3.client('config', region_name=self.config['aws_region'])
        self.metrics = defaultdict(int)
        self.compliance_details = {}
        
    def check_compliance(self):
        """Check compliance status for all configured rules"""
        try:
            # Get all Config rules
            rules_response = self.config_client.describe_config_rules()
            
            total_rules = len(rules_response['ConfigRules'])
            compliant_rules = 0
            
            self.metrics['config_rules_total'] = total_rules
            
            for rule in rules_response['ConfigRules']:
                rule_name = rule['ConfigRuleName']
                
                try:
                    # Get compliance status for this rule
                    compliance_response = self.config_client.get_compliance_details_by_config_rule(
                        ConfigRuleName=rule_name
                    )
                    
                    self._process_compliance_results(rule_name, compliance_response)
                    
                except Exception as e:
                    logger.error(f"Error checking compliance for rule {rule_name}: {e}")
                    self.metrics['config_errors_total'] += 1
            
            # Calculate overall compliance score
            self._calculate_compliance_score()
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            self.metrics['config_errors_total'] += 1
    
    def _process_compliance_results(self, rule_name, compliance_response):
        """Process compliance results for a specific rule"""
        compliant_count = 0
        non_compliant_count = 0
        
        for result in compliance_response.get('EvaluationResults', []):
            compliance_type = result['ComplianceType']
            resource_type = result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceType']
            resource_id = result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId']
            
            if compliance_type == 'COMPLIANT':
                compliant_count += 1
                self.metrics['config_compliant_resources_total'] += 1
            elif compliance_type == 'NON_COMPLIANT':
                non_compliant_count += 1
                self.metrics['config_non_compliant_resources_total'] += 1
                
                # Log non-compliant resources
                logger.warning(f"Non-compliant resource: {resource_type}/{resource_id} for rule {rule_name}")
                
                # Check severity and update metrics
                rule_config = self._get_rule_config(rule_name)
                if rule_config:
                    severity = rule_config.get('severity', 'medium')
                    self.metrics[f'config_violations_{severity}_total'] += 1
            
            self.metrics['config_evaluation_results_total'] += 1
        
        # Store compliance details for this rule
        self.compliance_details[rule_name] = {
            'compliant': compliant_count,
            'non_compliant': non_compliant_count,
            'total': compliant_count + non_compliant_count
        }
    
    def _get_rule_config(self, rule_name):
        """Get configuration for a specific rule"""
        for rule in self.config['config']['compliance_rules']:
            if rule['rule_name'] == rule_name:
                return rule
        return None
    
    def _calculate_compliance_score(self):
        """Calculate overall compliance score based on weighted violations"""
        total_score = 0
        max_possible_score = 0
        
        scoring = self.config['scoring']
        
        for rule_name, details in self.compliance_details.items():
            rule_config = self._get_rule_config(rule_name)
            if not rule_config:
                continue
                
            severity = rule_config.get('severity', 'medium')
            weight = scoring.get(f'{severity}_weight', 1)
            
            # Calculate score for this rule
            total_resources = details['total']
            if total_resources > 0:
                rule_compliance = details['compliant'] / total_resources
                rule_score = rule_compliance * weight * total_resources
                total_score += rule_score
                max_possible_score += weight * total_resources
        
        # Calculate percentage compliance score
        if max_possible_score > 0:
            compliance_percentage = (total_score / max_possible_score) * 100
            self.metrics['config_compliance_score'] = int(compliance_percentage)
        else:
            self.metrics['config_compliance_score'] = 100
        
        logger.info(f"Overall compliance score: {self.metrics['config_compliance_score']}%")
    
    def check_configuration_changes(self):
        """Check for recent configuration changes"""
        try:
            # Get configuration history for the last hour
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            for resource_type in self.config['resource_types']:
                try:
                    response = self.config_client.get_resource_config_history(
                        resourceType=resource_type,
                        laterTime=start_time,
                        earlierTime=end_time,
                        limit=50
                    )
                    
                    changes = len(response.get('configurationItems', []))
                    if changes > 0:
                        self.metrics['config_configuration_changes_total'] += changes
                        logger.info(f"Found {changes} configuration changes for {resource_type}")
                        
                except Exception as e:
                    # Some resource types might not be available in all regions
                    logger.debug(f"Could not get config history for {resource_type}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking configuration changes: {e}")
            self.metrics['config_errors_total'] += 1
    
    def get_metrics(self):
        """Return Prometheus-formatted metrics"""
        metrics_output = []
        
        for metric_name, value in self.metrics.items():
            metrics_output.append(f"# HELP {metric_name} AWS Config metric")
            metrics_output.append(f"# TYPE {metric_name} gauge")
            metrics_output.append(f"{metric_name} {value}")
        
        # Add detailed compliance metrics per rule
        for rule_name, details in self.compliance_details.items():
            safe_rule_name = rule_name.replace('-', '_').replace('.', '_')
            
            metrics_output.append(f"# HELP config_rule_compliant_resources_{safe_rule_name} Compliant resources for rule")
            metrics_output.append(f"# TYPE config_rule_compliant_resources_{safe_rule_name} gauge")
            metrics_output.append(f"config_rule_compliant_resources_{safe_rule_name} {details['compliant']}")
            
            metrics_output.append(f"# HELP config_rule_non_compliant_resources_{safe_rule_name} Non-compliant resources for rule")
            metrics_output.append(f"# TYPE config_rule_non_compliant_resources_{safe_rule_name} gauge")
            metrics_output.append(f"config_rule_non_compliant_resources_{safe_rule_name} {details['non_compliant']}")
        
        # Add timestamp
        metrics_output.append(f"# HELP config_last_check_timestamp Last check timestamp")
        metrics_output.append(f"# TYPE config_last_check_timestamp gauge")
        metrics_output.append(f"config_last_check_timestamp {int(datetime.utcnow().timestamp())}")
        
        return "\n".join(metrics_output)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, monitor, *args, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.monitor.get_metrics().encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP logging
        pass

def main():
    # Load configuration
    monitor = ConfigComplianceMonitor()
    
    # Start metrics server
    port = int(os.environ.get('METRICS_PORT', 9108))
    
    def handler(*args, **kwargs):
        return MetricsHandler(monitor, *args, **kwargs)
    
    httpd = HTTPServer(('0.0.0.0', port), handler)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"Config compliance monitor started on port {port}")
    
    # Main monitoring loop
    poll_interval = monitor.config['config']['poll_interval_seconds']
    
    while True:
        try:
            logger.info("Checking compliance status...")
            monitor.check_compliance()
            
            logger.info("Checking configuration changes...")
            monitor.check_configuration_changes()
            
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down Config monitor")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == '__main__':
    main()
