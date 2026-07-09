#!/usr/bin/env python3
"""
AWS CloudTrail Log Processor and Metrics Exporter
Processes CloudTrail logs from S3 and exports Prometheus metrics
"""

import json
import time
import boto3
import gzip
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

class CloudTrailProcessor:
    def __init__(self, config_file='/config/config.yml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.s3_client = boto3.client('s3', region_name=self.config['aws_region'])
        self.metrics = defaultdict(int)
        self.last_processed = datetime.utcnow() - timedelta(hours=1)
        
    def process_logs(self):
        """Process new CloudTrail logs from S3"""
        try:
            bucket = self.config['cloudtrail']['s3_bucket']
            prefix = self.config['cloudtrail']['s3_prefix']
            
            # List objects in S3 bucket
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                StartAfter=self._get_start_key()
            )
            
            if 'Contents' not in response:
                logger.info("No new CloudTrail logs found")
                return
                
            for obj in response['Contents'][:self.config['cloudtrail']['batch_size']]:
                if obj['Key'].endswith('.json.gz'):
                    self._process_log_file(bucket, obj['Key'])
                    
        except Exception as e:
            logger.error(f"Error processing logs: {e}")
            self.metrics['cloudtrail_errors_total'] += 1
    
    def _get_start_key(self):
        """Generate S3 key prefix based on last processed time"""
        # CloudTrail S3 structure: AWSLogs/account-id/CloudTrail/region/YYYY/MM/DD/
        date_str = self.last_processed.strftime('%Y/%m/%d')
        return f"{self.config['cloudtrail']['s3_prefix']}/CloudTrail/{self.config['aws_region']}/{date_str}"
    
    def _process_log_file(self, bucket, key):
        """Process individual CloudTrail log file"""
        try:
            # Download and decompress log file
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            
            if key.endswith('.gz'):
                content = gzip.decompress(response['Body'].read())
            else:
                content = response['Body'].read()
                
            log_data = json.loads(content.decode('utf-8'))
            
            # Process each record
            for record in log_data.get('Records', []):
                self._process_event(record)
                
            logger.info(f"Processed {len(log_data.get('Records', []))} events from {key}")
            
        except Exception as e:
            logger.error(f"Error processing log file {key}: {e}")
            self.metrics['cloudtrail_errors_total'] += 1
    
    def _process_event(self, event):
        """Process individual CloudTrail event"""
        event_name = event.get('eventName', 'Unknown')
        event_source = event.get('eventSource', 'Unknown')
        user_identity = event.get('userIdentity', {})
        
        # Update basic metrics
        self.metrics['cloudtrail_events_total'] += 1
        self.metrics[f'cloudtrail_api_calls_{event_source.replace(".", "_")}_total'] += 1
        
        # Check for security events
        for security_event in self.config['cloudtrail']['security_events']:
            if event_name == security_event['event_name']:
                self.metrics['cloudtrail_security_events_total'] += 1
                self.metrics[f'cloudtrail_{event_name.lower()}_total'] += 1
                
                # Log security event
                logger.warning(f"Security event detected: {security_event['description']} - {event_name}")
        
        # Check for failed logins
        if event_name == 'ConsoleLogin' and event.get('responseElements', {}).get('ConsoleLogin') == 'Failure':
            self.metrics['cloudtrail_failed_logins_total'] += 1
            
        # Check for root account usage
        if user_identity.get('type') == 'Root':
            self.metrics['cloudtrail_root_usage_total'] += 1
            logger.warning(f"Root account usage detected: {event_name}")
    
    def get_metrics(self):
        """Return Prometheus-formatted metrics"""
        metrics_output = []
        
        for metric_name, value in self.metrics.items():
            metrics_output.append(f"# HELP {metric_name} CloudTrail metric")
            metrics_output.append(f"# TYPE {metric_name} counter")
            metrics_output.append(f"{metric_name} {value}")
            
        # Add timestamp
        metrics_output.append(f"# HELP cloudtrail_last_processed_timestamp Last processed timestamp")
        metrics_output.append(f"# TYPE cloudtrail_last_processed_timestamp gauge")
        metrics_output.append(f"cloudtrail_last_processed_timestamp {int(self.last_processed.timestamp())}")
        
        return "\n".join(metrics_output)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, processor, *args, **kwargs):
        self.processor = processor
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.processor.get_metrics().encode())
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
    processor = CloudTrailProcessor()
    
    # Start metrics server
    port = int(os.environ.get('METRICS_PORT', 9107))
    
    def handler(*args, **kwargs):
        return MetricsHandler(processor, *args, **kwargs)
    
    httpd = HTTPServer(('0.0.0.0', port), handler)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"CloudTrail metrics server started on port {port}")
    
    # Main processing loop
    poll_interval = processor.config['cloudtrail']['poll_interval_seconds']
    
    while True:
        try:
            processor.process_logs()
            processor.last_processed = datetime.utcnow()
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down CloudTrail processor")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == '__main__':
    main()
