#!/usr/bin/env python3
"""
ServiceNow Integration Processor
Connects to ServiceNow instance and exports ITSM metrics to Prometheus
"""

import json
import time
import requests
import yaml
import os
from datetime import datetime, timedelta
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServiceNowConnector:
    def __init__(self, config_file='/config/config.yml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.base_url = self.config['servicenow']['instance_url']
        self.username = self.config['servicenow']['username']
        self.password = self.config['servicenow']['password']
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        self.metrics = defaultdict(int)
        self.field_mappings = self.config.get('field_mappings', {})
        
    def fetch_table_data(self, table_config):
        """Fetch data from a ServiceNow table"""
        try:
            table_name = table_config['table']
            fields = ','.join(table_config['fields'])
            filters = table_config.get('filters', '')
            
            url = urljoin(self.base_url, f'/api/now/table/{table_name}')
            params = {
                'sysparm_fields': fields,
                'sysparm_query': filters,
                'sysparm_limit': 1000
            }
            
            start_time = time.time()
            response = self.session.get(url, params=params, timeout=self.config['servicenow']['timeout_seconds'])
            response_time = time.time() - start_time
            
            self.metrics['servicenow_api_response_time'] = int(response_time * 1000)  # Convert to milliseconds
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Fetched {len(data.get('result', []))} records from {table_name}")
                return data.get('result', [])
            else:
                logger.error(f"Error fetching {table_name}: {response.status_code} - {response.text}")
                self.metrics['servicenow_api_errors_total'] += 1
                return []
                
        except Exception as e:
            logger.error(f"Exception fetching {table_config['table']}: {e}")
            self.metrics['servicenow_api_errors_total'] += 1
            return []
    
    def process_incidents(self):
        """Process incident data and update metrics"""
        incidents = self.fetch_table_data(self.config['servicenow']['tables']['incidents'])
        
        self.metrics['servicenow_incidents_total'] = len(incidents)
        
        # Reset priority and state counters
        priority_counts = defaultdict(int)
        state_counts = defaultdict(int)
        
        for incident in incidents:
            priority = incident.get('priority', 'Unknown')
            state = incident.get('state', 'Unknown')
            
            # Map priority and state to human-readable names
            priority_name = self.field_mappings.get('incident_priorities', {}).get(priority, f'Priority_{priority}')
            state_name = self.field_mappings.get('incident_states', {}).get(state, f'State_{state}')
            
            priority_counts[priority_name] += 1
            state_counts[state_name] += 1
        
        # Update metrics
        for priority, count in priority_counts.items():
            self.metrics[f'servicenow_incidents_priority_{priority.lower().replace(" ", "_")}_total'] = count
            
        for state, count in state_counts.items():
            self.metrics[f'servicenow_incidents_state_{state.lower().replace(" ", "_")}_total'] = count
    
    def process_change_requests(self):
        """Process change request data and update metrics"""
        changes = self.fetch_table_data(self.config['servicenow']['tables']['change_requests'])
        
        self.metrics['servicenow_change_requests_total'] = len(changes)
        
        # Count by state
        state_counts = defaultdict(int)
        risk_counts = defaultdict(int)
        
        for change in changes:
            state = change.get('state', 'Unknown')
            risk = change.get('risk', 'Unknown')
            
            state_name = self.field_mappings.get('change_states', {}).get(state, f'State_{state}')
            state_counts[state_name] += 1
            risk_counts[risk] += 1
        
        # Update metrics
        for state, count in state_counts.items():
            self.metrics[f'servicenow_changes_state_{state.lower().replace(" ", "_")}_total'] = count
            
        for risk, count in risk_counts.items():
            self.metrics[f'servicenow_changes_risk_{risk.lower()}_total'] = count
    
    def process_problems(self):
        """Process problem data and update metrics"""
        problems = self.fetch_table_data(self.config['servicenow']['tables']['problems'])
        
        self.metrics['servicenow_problems_total'] = len(problems)
        
        # Count by priority and state
        priority_counts = defaultdict(int)
        state_counts = defaultdict(int)
        
        for problem in problems:
            priority = problem.get('priority', 'Unknown')
            state = problem.get('state', 'Unknown')
            
            priority_name = self.field_mappings.get('incident_priorities', {}).get(priority, f'Priority_{priority}')
            state_name = self.field_mappings.get('incident_states', {}).get(state, f'State_{state}')
            
            priority_counts[priority_name] += 1
            state_counts[state_name] += 1
        
        # Update metrics
        for priority, count in priority_counts.items():
            self.metrics[f'servicenow_problems_priority_{priority.lower().replace(" ", "_")}_total'] = count
    
    def process_service_catalog(self):
        """Process service catalog request data"""
        requests_data = self.fetch_table_data(self.config['servicenow']['tables']['service_catalog'])
        
        self.metrics['servicenow_service_requests_total'] = len(requests_data)
        
        # Count by state
        state_counts = defaultdict(int)
        for request in requests_data:
            state = request.get('state', 'Unknown')
            state_counts[state] += 1
        
        for state, count in state_counts.items():
            self.metrics[f'servicenow_service_requests_state_{state}_total'] = count
    
    def collect_all_metrics(self):
        """Collect metrics from all ServiceNow tables"""
        try:
            logger.info("Collecting ServiceNow metrics...")
            
            self.process_incidents()
            self.process_change_requests()
            self.process_problems()
            self.process_service_catalog()
            
            logger.info("ServiceNow metrics collection completed")
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            self.metrics['servicenow_api_errors_total'] += 1
    
    def get_metrics(self):
        """Return Prometheus-formatted metrics"""
        metrics_output = []
        
        for metric_name, value in self.metrics.items():
            metrics_output.append(f"# HELP {metric_name} ServiceNow metric")
            metrics_output.append(f"# TYPE {metric_name} gauge")
            metrics_output.append(f"{metric_name} {value}")
        
        # Add timestamp
        metrics_output.append(f"# HELP servicenow_last_collection_timestamp Last collection timestamp")
        metrics_output.append(f"# TYPE servicenow_last_collection_timestamp gauge")
        metrics_output.append(f"servicenow_last_collection_timestamp {int(datetime.utcnow().timestamp())}")
        
        return "\n".join(metrics_output)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, connector, *args, **kwargs):
        self.connector = connector
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.connector.get_metrics().encode())
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
    connector = ServiceNowConnector()
    
    # Start metrics server
    port = int(os.environ.get('METRICS_PORT', 9142))
    
    def handler(*args, **kwargs):
        return MetricsHandler(connector, *args, **kwargs)
    
    httpd = HTTPServer(('0.0.0.0', port), handler)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"ServiceNow connector started on port {port}")
    
    # Main collection loop
    poll_interval = connector.config['metrics']['poll_interval_seconds']
    
    while True:
        try:
            connector.collect_all_metrics()
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down ServiceNow connector")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == '__main__':
    main()
