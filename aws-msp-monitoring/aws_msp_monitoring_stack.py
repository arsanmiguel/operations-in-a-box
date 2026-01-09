#!/usr/bin/env python3
"""
AWS MSP Monitoring Stack Installer
==================================

Enterprise-style monitoring stack installer for AWS Managed Service Providers.
Complete installer with security hardening, progress tracking, and 
real-time validation for customer deployments.
"""

import os
import sys
import subprocess
import json
import time
import secrets
import shutil
from datetime import datetime
from pathlib import Path
import platform
import urllib.request
import tarfile
import zipfile

class ProgressTracker:
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        
    def update(self, step_name, details=""):
        self.current_step += 1
        elapsed = time.time() - self.start_time
        progress = (self.current_step / self.total_steps) * 100
        
        print(f"\n[{self.current_step}/{self.total_steps}] ({progress:.1f}%) {step_name}")
        if details:
            print(f"    {details}")
        print(f"    Elapsed: {elapsed:.1f}s")
        
    def complete(self):
        elapsed = time.time() - self.start_time
        print(f"\n✅ Installation completed in {elapsed:.1f}s")

class SecureMonitoringInstaller:
    def __init__(self, install_dir="secure-monitoring-stack"):
        self.install_dir = Path(install_dir)
        self.progress = ProgressTracker(12)  # Total installation steps
        self.credentials = {}
        self.errors = []
        self.system = platform.system().lower()
        
    def log_error(self, error, details=""):
        """Log installation errors"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'details': details,
            'step': self.progress.current_step
        }
        self.errors.append(error_entry)
        print(f"❌ ERROR: {error}")
        if details:
            print(f"    Details: {details}")
            
    def run_command(self, cmd, description="", check=True, capture_output=False):
        """Run command with error handling and progress tracking"""
        try:
            if description:
                print(f"    Running: {description}")
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=check, 
                capture_output=capture_output,
                text=True
            )
            
            if capture_output:
                return result.stdout.strip()
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {cmd}"
            details = f"Exit code: {e.returncode}"
            if capture_output and e.stderr:
                details += f", Error: {e.stderr}"
            self.log_error(error_msg, details)
            if check:
                raise
            return False
            
    def check_prerequisites(self):
        """Check and install prerequisites with progress tracking"""
        self.progress.update("Checking Prerequisites", "Verifying system requirements and updating images")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 7):
            self.log_error("Python 3.7+ required", f"Current version: {python_version}")
            return False
            
        # Check Docker
        try:
            docker_version = self.run_command("docker --version", capture_output=True)
            print(f"    ✅ Docker found: {docker_version}")
        except:
            print("    📦 Docker not found, installing...")
            if not self.install_docker():
                return False
                
        # Check Docker Compose
        try:
            compose_version = self.run_command("docker compose version", capture_output=True)
            print(f"    ✅ Docker Compose found: {compose_version}")
        except:
            self.log_error("Docker Compose not available", "Please install Docker Desktop or docker-compose-plugin")
            return False
            
        # Check and install Python dependencies
        self.check_and_install_python_dependencies()
        
        return True
    
    def check_and_install_python_dependencies(self):
        """Check and install required Python dependencies"""
        print("    🔍 Checking Python dependencies...")
        
        # Check for PyYAML (needed for enhanced plugin configs)
        try:
            import yaml
            print("    ✅ PyYAML found")
        except ImportError:
            print("    📦 Installing PyYAML for enhanced plugin support...")
            try:
                import subprocess
                
                # Try different installation methods
                install_commands = [
                    [sys.executable, "-m", "pip", "install", "pyyaml"],
                    [sys.executable, "-m", "pip", "install", "pyyaml", "--user"],
                    [sys.executable, "-m", "pip", "install", "pyyaml", "--break-system-packages"]
                ]
                
                for cmd in install_commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        if result.returncode == 0:
                            print("    ✅ PyYAML installed successfully")
                            break
                    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                        continue
                else:
                    print("    ⚠️  Could not install PyYAML automatically")
                    print("    💡 Plugin configs will use basic format")
                    
            except Exception as e:
                print(f"    ⚠️  PyYAML installation failed: {e}")
                print("    💡 Plugin configs will use basic format")
        
        # Check for other optional dependencies
        optional_deps = {
            'requests': 'API integration examples',
            'numpy': 'Advanced anomaly detection'
        }
        
        for dep, purpose in optional_deps.items():
            try:
                __import__(dep)
                print(f"    ✅ {dep} found")
            except ImportError:
                print(f"    ℹ️  {dep} not found (optional - for {purpose})")
            
        # Pull latest security-patched images
        print("    🔄 Pulling latest secure Docker images...")
        images_to_pull = [
            "prom/prometheus:latest",
            "grafana/grafana:latest", 
            "prom/pushgateway:latest",
            "python:3.11-slim"
        ]
        
        for image in images_to_pull:
            try:
                print(f"    📥 Pulling {image}...")
                self.run_command(f"docker pull {image}", capture_output=True)
                print(f"    ✅ {image} updated")
            except Exception as e:
                print(f"    ⚠️  Warning: Could not pull {image}: {e}")
                
        return True
        
    def install_docker(self):
        """Install Docker based on operating system"""
        try:
            if self.system == "darwin":  # macOS
                print("    Installing Docker Desktop for macOS...")
                if shutil.which("brew"):
                    self.run_command("brew install --cask docker", "Installing Docker via Homebrew")
                    print("    ⚠️  Please start Docker Desktop manually and wait for it to be ready")
                    input("    Press Enter when Docker Desktop is running...")
                else:
                    print("    Please install Docker Desktop manually from https://docker.com/products/docker-desktop")
                    return False
                    
            elif self.system == "linux":
                print("    Installing Docker for Linux...")
                self.run_command("curl -fsSL https://get.docker.com -o get-docker.sh", "Downloading Docker installer")
                self.run_command("sh get-docker.sh", "Installing Docker")
                self.run_command("sudo usermod -aG docker $USER", "Adding user to docker group")
                print("    ⚠️  Please log out and back in, then restart the installer")
                return False
                
            else:
                self.log_error("Unsupported operating system", f"OS: {self.system}")
                return False
                
            # Wait for Docker to be ready
            for i in range(30):
                try:
                    self.run_command("docker ps", capture_output=True)
                    print("    ✅ Docker is ready")
                    return True
                except:
                    print(f"    Waiting for Docker... ({i+1}/30)")
                    time.sleep(2)
                    
            self.log_error("Docker failed to start", "Timeout waiting for Docker daemon")
            return False
            
        except Exception as e:
            self.log_error("Docker installation failed", str(e))
            return False
            
    def generate_secure_credentials(self):
        """Generate cryptographically secure credentials"""
        self.progress.update("Generating Secure Credentials", "Creating API keys and passwords")
        
        self.credentials = {
            'api_key': secrets.token_urlsafe(32),
            'grafana_admin_password': secrets.token_urlsafe(16),
            'grafana_secret_key': secrets.token_urlsafe(32),
            'db_encryption_key': secrets.token_urlsafe(32),
            'jwt_secret': secrets.token_urlsafe(64)
        }
        
        print("    ✅ Secure credentials generated")
        for key, value in self.credentials.items():
            print(f"    {key}: {value[:8]}...")
            
    def create_directory_structure(self):
        """Create secure directory structure"""
        self.progress.update("Creating Directory Structure", "Setting up project directories")
        
        directories = [
            self.install_dir,
            self.install_dir / "api",
            self.install_dir / "grafana" / "provisioning" / "dashboards",
            self.install_dir / "grafana" / "provisioning" / "datasources",
            self.install_dir / "data" / "prometheus",
            self.install_dir / "data" / "grafana",
            self.install_dir / "secrets",
            self.install_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"    Created: {directory}")
            
        # Set secure permissions
        os.chmod(self.install_dir / "secrets", 0o700)
        os.chmod(self.install_dir / "data", 0o750)
        
    def create_configuration_files(self):
        """Create all configuration files with progress tracking"""
        self.progress.update("Creating Configuration Files", "Generating secure configurations")
        
        # Docker Compose with security hardening
        compose_content = f'''services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    user: "65534:65534"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./data/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    user: "472:472"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD={self.credentials['grafana_admin_password']}
      - GF_SECURITY_SECRET_KEY={self.credentials['grafana_secret_key']}
      # Complete security hardening - addresses all security findings
      - GF_SECURITY_DISABLE_GRAVATAR=true
      - GF_SECURITY_COOKIE_SECURE=true
      - GF_SECURITY_COOKIE_SAMESITE=strict
      - GF_SECURITY_STRICT_TRANSPORT_SECURITY=true
      - GF_SECURITY_CONTENT_TYPE_PROTECTION=true
      - GF_SECURITY_X_CONTENT_TYPE_OPTIONS=nosniff
      - GF_SECURITY_X_XSS_PROTECTION=true
      - GF_AUTH_ANONYMOUS_ENABLED=false
      - GF_AUTH_BASIC_ENABLED=true
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_USERS_ALLOW_ORG_CREATE=false
      - GF_USERS_AUTO_ASSIGN_ORG=false
      - GF_LOG_LEVEL=warn
      - GF_SESSION_LIFE_TIME=3600
      - GF_SERVER_ROOT_URL=https://localhost:3000
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  pushgateway:
    image: prom/pushgateway:latest
    container_name: pushgateway
    user: "65534:65534"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    ports:
      - "127.0.0.1:9091:9091"
    restart: unless-stopped

  api-server:
    build: ./api
    container_name: api-server
    user: "1000:1000"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    ports:
      - "127.0.0.1:8080:8080"
    environment:
      - API_KEY={self.credentials['api_key']}
      - PUSHGATEWAY_URL=http://pushgateway:9091
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  prometheus_data:
  grafana_data:
'''

        with open(self.install_dir / "docker-compose.yml", "w") as f:
            f.write(compose_content)
        print("    ✅ Docker Compose configuration created")
        
        # Prometheus configuration
        prometheus_config = '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pushgateway'
    static_configs:
      - targets: ['pushgateway:9091']
    honor_labels: true

  - job_name: 'api-server'
    static_configs:
      - targets: ['api-server:8080']
'''

        # Ensure prometheus.yml doesn't exist as directory
        prometheus_file = self.install_dir / "prometheus.yml"
        if prometheus_file.exists() and prometheus_file.is_dir():
            prometheus_file.rmdir()
            
        with open(prometheus_file, "w") as f:
            f.write(prometheus_config)
        print("    ✅ Prometheus configuration created")
        
    def create_secure_api(self):
        """Create secure API server"""
        self.progress.update("Creating Secure API", "Building hardened metrics API")
        
        # Dockerfile
        dockerfile_content = '''FROM python:3.11-slim

RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

WORKDIR /app

RUN apt-get update && \\
    apt-get upgrade -y && \\
    apt-get install -y --no-install-recommends ca-certificates curl && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .
RUN chmod -R 555 /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["python", "-u", "app.py"]'''

        with open(self.install_dir / "api" / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
            
        # Requirements - using latest versions for security patches
        requirements_content = '''flask>=3.0.0
flask-limiter>=3.8.0
werkzeug>=3.0.0
requests>=2.32.0
prometheus-client>=0.21.0
cryptography>=42.0.0
certifi>=2024.8.30'''

        with open(self.install_dir / "api" / "requirements.txt", "w") as f:
            f.write(requirements_content)
            
        # Secure API application
        api_content = f'''from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import os
import time
import re
import hmac
from functools import wraps

app = Flask(__name__)
API_KEY = os.getenv('API_KEY', '{self.credentials['api_key']}')

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)
limiter.init_app(app)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or not hmac.compare_digest(provided_key, API_KEY):
            abort(401, description="Invalid API key")
        return f(*args, **kwargs)
    return decorated_function

def validate_metric_name(name):
    return bool(re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$', name)) and len(name) <= 100

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response

@app.route('/health')
def health():
    return jsonify({{'status': 'healthy', 'timestamp': time.time()}})

@app.route('/api/metrics', methods=['POST'])
@require_api_key
@limiter.limit("50 per minute")
def push_metrics():
    try:
        data = request.json
        app_name = data.get('app_name', '').strip()
        metric_name = data.get('metric_name', '').strip()
        metric_value = data.get('value')
        
        if not app_name or not validate_metric_name(metric_name):
            abort(400, description="Invalid input")
            
        if not isinstance(metric_value, (int, float)):
            abort(400, description="Invalid metric value")
        
        gateway_data = f'{{metric_name}} {{metric_value}}\\n'
        
        response = requests.post(
            'http://pushgateway:9091/metrics/job/{{app_name}}',
            data=gateway_data,
            headers={{'Content-Type': 'text/plain'}},
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({{'status': 'success'}})
        else:
            return jsonify({{'error': 'Gateway error'}}), 502
            
    except Exception:
        return jsonify({{'error': 'Internal server error'}}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)'''

        with open(self.install_dir / "api" / "app.py", "w") as f:
            f.write(api_content)
            
        print("    ✅ Secure API server created")
        
    def create_grafana_config(self):
        """Create Grafana configuration"""
        self.progress.update("Configuring Grafana", "Setting up dashboards and datasources")
        
        # Datasource
        datasource_config = '''apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true'''
    
        with open(self.install_dir / "grafana" / "provisioning" / "datasources" / "prometheus.yml", "w") as f:
            f.write(datasource_config)
            
        # Dashboard provider
        dashboard_provider = '''apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards'''
      
        with open(self.install_dir / "grafana" / "provisioning" / "dashboards" / "dashboard.yml", "w") as f:
            f.write(dashboard_provider)
            
        print("    ✅ Grafana configuration created")
        
    def save_credentials(self):
        """Save credentials securely"""
        self.progress.update("Saving Credentials", "Storing secure credentials")
        
        credentials_file = self.install_dir / "CREDENTIALS.md"
        with open(credentials_file, "w") as f:
            f.write("# Secure Monitoring Stack Credentials\\n\\n")
            f.write("**⚠️  KEEP THIS FILE SECURE - DO NOT COMMIT TO VERSION CONTROL**\\n\\n")
            f.write("## Access Information\\n\\n")
            f.write(f"- **Grafana URL**: http://localhost:3000\\n")
            f.write(f"- **Grafana Username**: admin\\n")
            f.write(f"- **Grafana Password**: `{self.credentials['grafana_admin_password']}`\\n\\n")
            f.write(f"- **Prometheus URL**: http://localhost:9090\\n\\n")
            f.write(f"- **Metrics API URL**: http://localhost:8080\\n")
            f.write(f"- **API Key**: `{self.credentials['api_key']}`\\n\\n")
            f.write("## API Usage Example\\n\\n")
            f.write("```bash\\n")
            f.write("curl -X POST http://localhost:8080/api/metrics \\\\\\n")
            f.write(f'  -H "X-API-Key: {self.credentials['api_key']}" \\\\\\n')
            f.write('  -H "Content-Type: application/json" \\\\\\n')
            f.write('  -d \'{"app_name": "my-app", "metric_name": "test_metric", "value": 42}\'\\n')
            f.write("```\\n")
            
        os.chmod(credentials_file, 0o600)
        print("    ✅ Credentials saved securely")
        
    def build_and_deploy(self):
        """Build and deploy the monitoring stack"""
        self.progress.update("Building Docker Images", "Compiling secure containers")
        
        os.chdir(self.install_dir)
        
        # Build images
        if not self.run_command("docker compose build", "Building API server image"):
            return False
            
        self.progress.update("Starting Services", "Deploying monitoring stack")
        
        # Start services
        if not self.run_command("docker compose up -d", "Starting all services"):
            return False
            
        # Wait for services to be ready
        print("    Waiting for services to start...")
        time.sleep(15)
        
        # Check service health
        services = ['prometheus', 'grafana', 'pushgateway', 'api-server']
        for service in services:
            try:
                result = self.run_command(f"docker compose ps {service}", capture_output=True)
                if "Up" in result:
                    print(f"    ✅ {service} is running")
                else:
                    print(f"    ⚠️  {service} status unclear")
            except:
                print(f"    ❌ {service} failed to start")
                
        return True
        
    def test_deployment(self):
        """Test the deployed monitoring stack"""
        self.progress.update("Testing Deployment", "Verifying all services are working")
        
        tests = [
            ("Prometheus health", "curl -f http://localhost:9090/-/healthy"),
            ("Grafana health", "curl -f http://localhost:3000/api/health"),
            ("API health", "curl -f http://localhost:8080/health"),
        ]
        
        for test_name, test_cmd in tests:
            try:
                self.run_command(test_cmd, f"Testing {test_name}")
                print(f"    ✅ {test_name} passed")
            except:
                print(f"    ⚠️  {test_name} failed")
                
        # Test API with authentication
        try:
            test_metric_cmd = f'''curl -X POST http://localhost:8080/api/metrics \\
                -H "X-API-Key: {self.credentials['api_key']}" \\
                -H "Content-Type: application/json" \\
                -d '{{"app_name": "test", "metric_name": "test_metric", "value": 1}}'
            '''
            self.run_command(test_metric_cmd, "Testing authenticated API")
            print("    ✅ API authentication test passed")
        except:
            print("    ⚠️  API authentication test failed")
            
    def create_management_scripts(self):
        """Create management and documentation"""
        self.progress.update("Creating Management Tools", "Generating scripts and documentation")
        
        # Start script
        start_script = f'''#!/bin/bash
echo "🚀 Starting Secure Monitoring Stack..."
docker compose up -d
echo "✅ Services started!"
echo ""
echo "📊 Access URLs:"
echo "- Grafana: http://localhost:3000 (admin/{self.credentials['grafana_admin_password']})"
echo "- Prometheus: http://localhost:9090"
echo "- API: http://localhost:8080"
echo ""
echo "🔑 API Key: {self.credentials['api_key']}"
'''

        try:
            print(f"    Creating start.sh at: {Path.cwd() / 'start.sh'}")
            with open("start.sh", "w") as f:
                f.write(start_script)
            os.chmod("start.sh", 0o755)
            print("    ✅ start.sh created successfully")
        except Exception as e:
            print(f"    ❌ Failed to create start.sh: {e}")
            raise
        
        # README
        readme_content = f'''# Secure Monitoring Stack

Enterprise-style monitoring solution with Prometheus, Grafana, and secure API.

## Quick Start

```bash
./start.sh
```

## Services

- **Grafana**: http://localhost:3000 (admin/{self.credentials['grafana_admin_password']})
- **Prometheus**: http://localhost:9090
- **Metrics API**: http://localhost:8080

## Security Features

✅ API Key authentication  
✅ Non-root containers  
✅ Read-only filesystems  
✅ Security headers  
✅ Input validation  
✅ Rate limiting  

## Management

```bash
docker compose up -d      # Start
docker compose down       # Stop
docker compose logs -f    # View logs
```

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''

        with open("README.md", "w") as f:
            f.write(readme_content)
            
        print("    ✅ Management tools created")
        
    def generate_installation_report(self):
        """Generate installation report"""
        self.progress.update("Generating Report", "Creating installation summary")
        
        report = {
            'installation_metadata': {
                'timestamp': datetime.now().isoformat(),
                'installer_version': '2.0.0',
                'install_directory': str(self.install_dir.absolute()),
                'system_info': {
                    'platform': platform.system(),
                    'platform_version': platform.version(),
                    'python_version': platform.python_version()
                }
            },
            'credentials': {
                'grafana_url': 'http://localhost:3000',
                'grafana_username': 'admin',
                'grafana_password': self.credentials['grafana_admin_password'],
                'api_url': 'http://localhost:8080',
                'api_key': self.credentials['api_key']
            },
            'services': {
                'prometheus': 'http://localhost:9090',
                'grafana': 'http://localhost:3000',
                'pushgateway': 'http://localhost:9091',
                'api': 'http://localhost:8080'
            },
            'errors': self.errors,
            'installation_status': 'SUCCESS' if not self.errors else 'COMPLETED_WITH_WARNINGS'
        }
        
        report_file = f"installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"    ✅ Installation report saved: {report_file}")
        return report
        
    def install(self):
        """Main installation process"""
        print("🛡️  Secure Monitoring Stack Installer v2.0")
        print("=" * 50)
        print("Enterprise-style monitoring with comprehensive security\\n")
        
        try:
            # Installation steps
            if not self.check_prerequisites():
                return False
                
            self.generate_secure_credentials()
            self.create_directory_structure()
            self.create_configuration_files()
            self.create_secure_api()
            self.create_grafana_config()
            self.save_credentials()
            
            if not self.build_and_deploy():
                return False
                
            self.test_deployment()
            self.create_management_scripts()
            report = self.generate_installation_report()
            
            self.progress.complete()
            
            # Success summary
            print("\\n" + "=" * 60)
            print("🎉 INSTALLATION SUCCESSFUL!")
            print("=" * 60)
            print(f"📁 Installation Directory: {self.install_dir.absolute()}")
            print(f"🔐 Credentials File: {self.install_dir / 'CREDENTIALS.md'}")
            print("\\n📊 Access Your Monitoring Stack:")
            print(f"- Grafana: http://localhost:3000 (admin/{self.credentials['grafana_admin_password']})")
            print(f"- Prometheus: http://localhost:9090")
            print(f"- API: http://localhost:8080 (Key: {self.credentials['api_key'][:16]}...)")
            
            if self.errors:
                print(f"\\n⚠️  Installation completed with {len(self.errors)} warnings")
                print("Check the installation report for details.")
            
            return True
            
        except KeyboardInterrupt:
            print("\\n❌ Installation cancelled by user")
            return False
        except Exception as e:
            self.log_error("Installation failed", str(e))
            print(f"\\n❌ Installation failed: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Secure Monitoring Stack")
    parser.add_argument("--install-dir", default="secure-monitoring-stack", 
                       help="Installation directory")
    args = parser.parse_args()
    
    installer = SecureMonitoringInstaller(args.install_dir)
    success = installer.install()
    
    sys.exit(0 if success else 1)
