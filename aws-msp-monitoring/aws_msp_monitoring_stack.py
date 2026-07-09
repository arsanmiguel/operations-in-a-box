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
        print(f"\nInstallation completed in {elapsed:.1f}s")

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
        print(f"ERROR: {error}")
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
            print(f"    Docker found: {docker_version}")
        except:
            print("    Docker not found, installing...")
            if not self.install_docker():
                return False
                
        # Check Docker Compose
        try:
            compose_version = self.run_command("docker compose version", capture_output=True)
            print(f"    Docker Compose found: {compose_version}")
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
            print("    PyYAML found")
        except ImportError:
            print("    Installing PyYAML for enhanced plugin support...")
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
                            print("    PyYAML installed successfully")
                            break
                    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                        continue
                else:
                    print("    ⚠️  Could not install PyYAML automatically")
                    print("    Plugin configs will use basic format")
                    
            except Exception as e:
                print(f"    ⚠️  PyYAML installation failed: {e}")
                print("    Plugin configs will use basic format")
        
        # Check for other optional dependencies
        optional_deps = {
            'requests': 'API integration examples',
            'numpy': 'Advanced anomaly detection'
        }
        
        for dep, purpose in optional_deps.items():
            try:
                __import__(dep)
                print(f"    {dep} found")
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
                print(f"    {image} updated")
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
                    print("    Docker is ready")
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
        
        print("    Secure credentials generated")
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
        
    def copy_bundled_stack_files(self):
        """Copy version-controlled stack assets from the package bundle."""
        bundle_root = Path(__file__).parent / "customer-monitoring-stack"
        if not bundle_root.exists():
            self.log_error("Bundled stack files not found", str(bundle_root))
            return False

        copy_items = [
            "docker-compose.yml",
            "prometheus.yml",
            "start.sh",
            "install.sh",
            ".env.template",
            "README.md",
            "api",
            "grafana",
            "scripts",
        ]

        for item in copy_items:
            src = bundle_root / item
            dst = self.install_dir / item
            if not src.exists():
                continue
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        for script in ("start.sh", "install.sh", "scripts/bootstrap-env.sh"):
            script_path = self.install_dir / script
            if script_path.exists():
                os.chmod(script_path, 0o755)

        print("    Bundled stack files copied")
        return True

    def write_env_file(self):
        """Write local-only credentials for docker compose."""
        self.progress.update("Saving Credentials", "Writing local .env file")

        env_file = self.install_dir / ".env"
        env_content = (
            f"GRAFANA_ADMIN_PASSWORD={self.credentials['grafana_admin_password']}\n"
            f"GRAFANA_SECRET_KEY={self.credentials['grafana_secret_key']}\n"
            f"API_KEY={self.credentials['api_key']}\n"
        )
        with open(env_file, "w") as f:
            f.write(env_content)
        os.chmod(env_file, 0o600)
        print("    Local .env file created")

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
                    print(f"    {service} is running")
                else:
                    print(f"    ⚠️  {service} status unclear")
            except:
                print(f"    {service} failed to start")
                
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
                print(f"    {test_name} passed")
            except:
                print(f"    ⚠️  {test_name} failed")
                
        # Test API with authentication
        try:
            test_metric_cmd = f'''curl -X POST http://localhost:8080/api/metrics \\
                -H "X-API-Key: {self.credentials['api_key']}" \\
                -H "Content-Type: application/json" \\
                -d '{{"app_name": "operations-in-a-box", "metric_name": "install_heartbeat", "value": 1}}'
            '''
            self.run_command(test_metric_cmd, "Testing authenticated API")
            print("    API authentication test passed")
        except:
            print("    ⚠️  API authentication test failed")
            
    def create_management_scripts(self):
        """Bundled scripts are copied with the stack assets."""
        self.progress.update("Creating Management Tools", "Using bundled install scripts")
        print("    install.sh and start.sh ready")

    def generate_installation_report(self):
        """Generate installation report without secrets."""
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
            'services': {
                'prometheus': 'http://localhost:9090',
                'grafana': 'http://localhost:3000',
                'pushgateway': 'http://localhost:9091',
                'api': 'http://localhost:8080'
            },
            'credentials_location': str(self.install_dir / '.env'),
            'errors': self.errors,
            'installation_status': 'SUCCESS' if not self.errors else 'COMPLETED_WITH_WARNINGS'
        }
        
        report_file = f"installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"    Installation report saved: {report_file}")
        return report
        
    def install(self):
        """Main installation process"""
        print("Secure Monitoring Stack Installer v2.0")
        print("=" * 50)
        print("Enterprise-style monitoring with comprehensive security\\n")
        
        try:
            # Installation steps
            if not self.check_prerequisites():
                return False
                
            self.generate_secure_credentials()
            self.create_directory_structure()
            if not self.copy_bundled_stack_files():
                return False
            self.write_env_file()
            
            if not self.build_and_deploy():
                return False
                
            self.test_deployment()
            self.create_management_scripts()
            report = self.generate_installation_report()
            
            self.progress.complete()
            
            # Success summary
            print("\\n" + "=" * 60)
            print("INSTALLATION SUCCESSFUL!")
            print("=" * 60)
            print(f"Installation Directory: {self.install_dir.absolute()}")
            print(f"Credentials File: {self.install_dir / '.env'}")
            print("\\nAccess Your Monitoring Stack:")
            print("- Grafana: http://localhost:3000 (admin / see .env)")
            print("- Prometheus: http://localhost:9090")
            print("- API: http://localhost:8080")
            print("- Default dashboard: Operations in a Box - Overview")
            
            if self.errors:
                print(f"\\n⚠️  Installation completed with {len(self.errors)} warnings")
                print("Check the installation report for details.")
            
            return True
            
        except KeyboardInterrupt:
            print("\\nInstallation cancelled by user")
            return False
        except Exception as e:
            self.log_error("Installation failed", str(e))
            print(f"\\nInstallation failed: {e}")
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
