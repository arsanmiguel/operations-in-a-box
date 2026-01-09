#!/usr/bin/env python3
"""
AWS MSP Demo Data Generator - Fixed Version
Generates realistic monitoring data with correct metric names
"""
import time
import random
import requests
import json
from datetime import datetime

class DemoDataGenerator:
    def __init__(self, api_key, api_url="http://localhost:8080"):
        self.api_key = api_key
        self.api_url = api_url
        
    def send_metric(self, app_name, metric_name, value):
        """Send metric to monitoring API"""
        data = {
            "app_name": app_name,
            "metric_name": metric_name,
            "value": value
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(f"{self.api_url}/api/metrics", 
                                   json=data, headers=headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending metric: {e}")
            return False
    
    def generate_system_metrics(self):
        """Generate standard system metrics"""
        # CPU usage with daily pattern
        hour = datetime.now().hour
        base_cpu = 30 + 20 * (hour / 24)  # Higher during day
        cpu_usage = max(0, min(100, base_cpu + random.gauss(0, 10)))
        
        # Memory usage with gradual increase
        base_memory = 40 + random.gauss(0, 5)
        memory_usage = max(0, min(100, base_memory))
        
        # Response time with occasional spikes
        response_time = random.gauss(150, 30)
        if random.random() < 0.05:  # 5% chance of spike
            response_time *= random.uniform(2, 5)
        
        # Error rate
        error_rate = max(0, random.gauss(2, 1))
        
        return {
            "system_cpu_usage": cpu_usage,
            "system_memory_usage": memory_usage,
            "system_response_time": response_time,
            "system_error_rate": error_rate
        }
    
    def generate_aws_metrics(self):
        """Generate AWS CloudWatch-style metrics"""
        return {
            "aws_ec2_cpu_utilization": random.uniform(20, 80),
            "aws_rds_connections": random.randint(10, 100),
            "aws_lambda_invocations": random.randint(50, 500),
            "aws_s3_requests": random.randint(100, 1000)
        }
    
    def generate_security_metrics(self):
        """Generate security monitoring metrics"""
        return {
            "saml_login_attempts": random.randint(0, 20),
            "saml_login_failures": random.randint(0, 3),
            "cert_expiry_days": random.randint(30, 365),
            "firewall_blocked_requests": random.randint(0, 50)
        }
    
    def run_demo(self, duration_minutes=10):
        """Run demo data generation"""
        print(f"🚀 Starting demo data generation for {duration_minutes} minutes...")
        print("📊 Generating realistic monitoring data...")
        
        end_time = time.time() + (duration_minutes * 60)
        cycle = 0
        
        while time.time() < end_time:
            cycle += 1
            
            # Generate and send system metrics
            system_metrics = self.generate_system_metrics()
            for metric_name, value in system_metrics.items():
                self.send_metric("demo-app", metric_name, value)
            
            # Generate AWS metrics (if aws-cloudwatch plugin installed)
            aws_metrics = self.generate_aws_metrics()
            for metric_name, value in aws_metrics.items():
                self.send_metric("aws-integration", metric_name, value)
            
            # Generate security metrics (if security plugins installed)
            security_metrics = self.generate_security_metrics()
            for metric_name, value in security_metrics.items():
                self.send_metric("security-monitor", metric_name, value)
            
            print(f"Cycle {cycle}: CPU={system_metrics['system_cpu_usage']:.1f}% "
                  f"Memory={system_metrics['system_memory_usage']:.1f}% "
                  f"Response={system_metrics['system_response_time']:.0f}ms")
            
            time.sleep(10)  # Send data every 10 seconds
        
        print(f"✅ Demo completed after {cycle} cycles")

def main():
    # Get API key from credentials
    try:
        with open('CREDENTIALS.md', 'r') as f:
            content = f.read()
            # Extract API key from markdown
            lines = content.split('\n')
            for line in lines:
                if 'API Key' in line and '`' in line:
                    api_key = line.split('`')[1]
                    break
            else:
                raise ValueError("API key not found")
    except Exception as e:
        print(f"❌ Could not read API key: {e}")
        print("💡 Make sure you're in the monitoring stack directory with CREDENTIALS.md")
        return
    
    generator = DemoDataGenerator(api_key)
    
    try:
        generator.run_demo(duration_minutes=5)  # Run for 5 minutes
    except KeyboardInterrupt:
        print("\n🛑 Demo data generation stopped")

if __name__ == "__main__":
    main()
