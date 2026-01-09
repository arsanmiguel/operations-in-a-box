#!/usr/bin/env python3
"""
Comprehensive Plugin Validator and Enhancer
Installs, configures, and validates all 45 plugins
"""

import subprocess
import os
import yaml
import json
from pathlib import Path

class PluginEnhancer:
    def __init__(self):
        self.base_dir = Path("customer-monitoring-stack/plugins")
        self.port_counter = 9109  # Start after our AWS plugins (9106-9108)
        self.results = {
            'success': [],
            'failed': [],
            'enhanced': []
        }
        
        # Port assignments for different service types
        self.service_ports = {
            'prometheus-federation': 9109,
            'grafana-lb': 9110,
            'grafana-node-1': 9111,
            'grafana-node-2': 9112,
            'scaling-controller': 9113,
            'auth-proxy': 9114,
            'cert-manager': 9115,
            'network-monitor': 9116,
            'vpn-gateway': 9117,
            'aws-discovery': 9118,
            'cost-analyzer': 9119,
            'montycloud-connector': 9120,
            'ml-detector': 9121,
            'model-trainer': 9122,
            'predictor': 9123,
            'remediation-engine': 9124,
            'bi-engine': 9125,
            'data-warehouse': 9126,
            'elasticsearch': 9127,
            'logstash': 9128,
            'kibana': 9129,
            'jaeger': 9130,
            'apm-collector': 9131,
            'terraform-monitor': 9132,
            'pipeline-monitor': 9133,
            'gitops-controller': 9134,
            'falcon-exporter': 9135,
            'prisma-exporter': 9136,
            'alertlogic-exporter': 9137,
            'splunk-forwarder': 9138,
            'splunk-metrics': 9139,
            'sumologic-collector': 9140,
            'datadog-agent': 9141,
            'servicenow-connector': 9142,
            'bmc-connector': 9143,
            'jira-connector': 9144,
            'aws-support-connector': 9145,
            'zendesk-connector': 9146,
            'freshworks-connector': 9147,
            'linear-connector': 9148,
            'duo-connector': 9149,
            'okta-connector': 9150,
            'redis': 9151,
            'mongodb': 9152,
            'confluent': 9153,
            'influxdb': 9154,
            'clickhouse': 9155,
            'neo4j': 9156,
            'databricks-connector': 9157,
            'snowflake-connector': 9158
        }
    
    def get_all_plugins(self):
        """Get list of all available plugins"""
        try:
            result = subprocess.run([
                'python3', 'aws_msp_plugin_manager.py', 
                '--install-dir', 'customer-monitoring-stack', 
                'list'
            ], capture_output=True, text=True)
            
            plugins = []
            for line in result.stdout.split('\n'):
                if '⬜ Available' in line:
                    plugin_name = line.split('|')[0].strip()
                    if plugin_name and plugin_name not in ['aws-cloudwatch', 'aws-cloudtrail', 'aws-config']:
                        plugins.append(plugin_name)
            
            return plugins
        except Exception as e:
            print(f"Error getting plugin list: {e}")
            return []
    
    def install_plugin(self, plugin_name):
        """Install a single plugin"""
        try:
            result = subprocess.run([
                'python3', 'aws_msp_plugin_manager.py',
                '--install-dir', 'customer-monitoring-stack',
                'install', plugin_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Installed: {plugin_name}")
                return True
            else:
                print(f"❌ Failed to install: {plugin_name}")
                print(f"   Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Exception installing {plugin_name}: {e}")
            return False
    
    def enhance_plugin(self, plugin_name):
        """Enhance plugin with proper configuration"""
        plugin_dir = self.base_dir / plugin_name
        if not plugin_dir.exists():
            return False
        
        try:
            # Fix docker-compose.yml
            self.fix_docker_compose(plugin_dir, plugin_name)
            
            # Add basic configuration files
            self.add_basic_config(plugin_dir, plugin_name)
            
            # Add README
            self.add_readme(plugin_dir, plugin_name)
            
            print(f"🔧 Enhanced: {plugin_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enhance {plugin_name}: {e}")
            return False
    
    def fix_docker_compose(self, plugin_dir, plugin_name):
        """Fix docker-compose.yml with proper ports and networks"""
        compose_file = plugin_dir / "docker-compose.yml"
        if not compose_file.exists():
            return
        
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            # Fix networks and add ports
            for service_name, service_config in compose_data.get('services', {}).items():
                # Fix network reference
                if 'networks' in service_config:
                    if 'monitoring' in service_config['networks']:
                        service_config['networks'] = ['default']
                
                # Add port mapping if service has a known port
                if service_name in self.service_ports:
                    port = self.service_ports[service_name]
                    service_config['ports'] = [f"{port}:{port}"]
                    
                    # Add health check
                    service_config['healthcheck'] = {
                        'test': ['CMD', 'wget', '--no-verbose', '--tries=1', '--spider', f'http://localhost:{port}/health'],
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 3,
                        'start_period': '40s'
                    }
            
            # Remove version (deprecated)
            if 'version' in compose_data:
                del compose_data['version']
            
            # Write back
            with open(compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False)
                
        except Exception as e:
            print(f"   Warning: Could not fix docker-compose for {plugin_name}: {e}")
    
    def add_basic_config(self, plugin_dir, plugin_name):
        """Add basic configuration files"""
        # Create config.yml
        config_file = plugin_dir / "config.yml"
        if not config_file.exists():
            config = {
                'name': plugin_name.replace('-', ' ').title(),
                'enabled': True,
                'version': '1.0.0',
                'description': f'Configuration for {plugin_name} plugin'
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        
        # Create .env template
        env_file = plugin_dir / ".env.template"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write(f"# Environment variables for {plugin_name}\n")
                f.write(f"# Copy this to .env and customize\n\n")
                f.write(f"PLUGIN_NAME={plugin_name}\n")
                f.write(f"PLUGIN_ENABLED=true\n")
                
                # Add service-specific variables
                if 'aws' in plugin_name:
                    f.write("AWS_REGION=us-east-1\n")
                    f.write("# AWS_ACCESS_KEY_ID=your-key\n")
                    f.write("# AWS_SECRET_ACCESS_KEY=your-secret\n")
    
    def add_readme(self, plugin_dir, plugin_name):
        """Add basic README for the plugin"""
        readme_file = plugin_dir / "README.md"
        if not readme_file.exists():
            with open(readme_file, 'w') as f:
                f.write(f"# {plugin_name.replace('-', ' ').title()} Plugin\n\n")
                f.write(f"This plugin provides {plugin_name} integration for the monitoring stack.\n\n")
                f.write("## Quick Start\n\n")
                f.write("1. Copy `.env.template` to `.env` and customize\n")
                f.write("2. Edit `config.yml` as needed\n")
                f.write("3. Start the service: `docker-compose up -d`\n\n")
                f.write("## Configuration\n\n")
                f.write("See `config.yml` for available configuration options.\n\n")
                f.write("## Health Check\n\n")
                
                if plugin_name in self.service_ports:
                    port = self.service_ports[plugin_name]
                    f.write(f"Service health: `curl http://localhost:{port}/health`\n")
                    f.write(f"Metrics: `curl http://localhost:{port}/metrics`\n")
    
    def validate_plugin(self, plugin_name):
        """Validate plugin docker-compose configuration"""
        plugin_dir = self.base_dir / plugin_name
        compose_file = plugin_dir / "docker-compose.yml"
        
        if not compose_file.exists():
            return False
        
        try:
            # Test docker-compose config
            result = subprocess.run([
                'docker-compose', 'config'
            ], cwd=plugin_dir, capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def run_full_validation(self):
        """Run complete validation and enhancement"""
        print("🔌 Starting comprehensive plugin validation...")
        print("=" * 60)
        
        plugins = self.get_all_plugins()
        print(f"Found {len(plugins)} plugins to process")
        
        for i, plugin in enumerate(plugins, 1):
            print(f"\n[{i}/{len(plugins)}] Processing: {plugin}")
            print("-" * 40)
            
            # Install plugin
            if self.install_plugin(plugin):
                self.results['success'].append(plugin)
                
                # Enhance plugin
                if self.enhance_plugin(plugin):
                    self.results['enhanced'].append(plugin)
                    
                    # Validate plugin
                    if self.validate_plugin(plugin):
                        print(f"✅ Validated: {plugin}")
                    else:
                        print(f"⚠️  Validation issues: {plugin}")
                else:
                    print(f"⚠️  Enhancement failed: {plugin}")
            else:
                self.results['failed'].append(plugin)
        
        self.print_summary()
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully installed: {len(self.results['success'])}")
        print(f"🔧 Enhanced: {len(self.results['enhanced'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        
        if self.results['failed']:
            print(f"\n❌ Failed plugins:")
            for plugin in self.results['failed']:
                print(f"  - {plugin}")
        
        print(f"\n✅ Port assignments:")
        for service, port in sorted(self.service_ports.items()):
            print(f"  - {service}: {port}")

if __name__ == '__main__':
    enhancer = PluginEnhancer()
    enhancer.run_full_validation()
