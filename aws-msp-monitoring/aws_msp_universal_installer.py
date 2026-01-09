#!/usr/bin/env python3
"""
AWS MSP Monitoring Stack - Universal Installer
==============================================

Cross-platform installer for Windows, macOS, and Linux.
Automatically detects OS and installs appropriate dependencies.
"""

import os
import sys
import platform
import subprocess
import shutil
import urllib.request
import zipfile
import tempfile
from pathlib import Path

class UniversalInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.install_dir = Path.cwd() / "aws-msp-monitoring"
        
    def detect_os(self):
        """Detect operating system and architecture"""
        print(f"🔍 Detected OS: {platform.system()} {platform.release()}")
        print(f"🔍 Architecture: {platform.machine()}")
        
        if self.system == "windows":
            return "windows"
        elif self.system == "darwin":
            return "macos"
        elif self.system == "linux":
            return "linux"
        else:
            print(f"❌ Unsupported OS: {self.system}")
            sys.exit(1)
    
    def check_python(self):
        """Verify Python version and install dependencies"""
        version = sys.version_info
        if version < (3, 7):
            print(f"❌ Python 3.7+ required. Current: {version.major}.{version.minor}")
            print("Please install Python 3.7+ and try again.")
            sys.exit(1)
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        
        # Install PyYAML for enhanced plugin support
        self.install_python_dependencies()
    
    def install_python_dependencies(self):
        """Install required Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        dependencies = ["pyyaml", "requests"]
        
        for dep in dependencies:
            try:
                __import__(dep.replace("-", "_"))
                print(f"    ✅ {dep} already installed")
                continue
            except ImportError:
                pass
            
            print(f"    📥 Installing {dep}...")
            
            # Try different installation methods
            install_commands = [
                [sys.executable, "-m", "pip", "install", dep],
                [sys.executable, "-m", "pip", "install", dep, "--user"],
                [sys.executable, "-m", "pip", "install", dep, "--break-system-packages"]
            ]
            
            success = False
            for cmd in install_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        print(f"    ✅ {dep} installed successfully")
                        success = True
                        break
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue
            
            if not success:
                print(f"    ⚠️  Could not install {dep} automatically")
                if dep == "pyyaml":
                    print("    💡 Plugin configs will use basic format")
                elif dep == "requests":
                    print("    💡 API examples may not work without manual installation")
    
    def install_docker_windows(self):
        """Install Docker Desktop on Windows"""
        print("📦 Installing Docker Desktop for Windows...")
        
        # Check if Docker is already installed
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("✅ Docker already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        print("⬇️  Downloading Docker Desktop...")
        docker_url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
        installer_path = Path(tempfile.gettempdir()) / "DockerDesktopInstaller.exe"
        
        try:
            urllib.request.urlretrieve(docker_url, installer_path)
            print("🚀 Running Docker Desktop installer...")
            subprocess.run([str(installer_path), "install", "--quiet"], check=True)
            print("✅ Docker Desktop installed")
            print("⚠️  Please restart your computer and run this installer again")
            return False
        except Exception as e:
            print(f"❌ Failed to install Docker: {e}")
            print("Please install Docker Desktop manually from https://docker.com/products/docker-desktop")
            return False
    
    def install_docker_macos(self):
        """Install Docker Desktop on macOS"""
        print("📦 Installing Docker Desktop for macOS...")
        
        # Check if Docker is already installed
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("✅ Docker already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Try Homebrew first
        try:
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            print("🍺 Installing via Homebrew...")
            subprocess.run(["brew", "install", "--cask", "docker"], check=True)
            print("✅ Docker Desktop installed via Homebrew")
            print("⚠️  Please start Docker Desktop from Applications and run this installer again")
            return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Manual download
        print("⬇️  Downloading Docker Desktop...")
        if "arm" in self.arch or "aarch64" in self.arch:
            docker_url = "https://desktop.docker.com/mac/main/arm64/Docker.dmg"
        else:
            docker_url = "https://desktop.docker.com/mac/main/amd64/Docker.dmg"
        
        installer_path = Path(tempfile.gettempdir()) / "Docker.dmg"
        
        try:
            urllib.request.urlretrieve(docker_url, installer_path)
            print("📀 Mounting Docker.dmg...")
            subprocess.run(["hdiutil", "attach", str(installer_path)], check=True)
            print("📋 Please drag Docker to Applications folder and start it")
            print("⚠️  Then run this installer again")
            return False
        except Exception as e:
            print(f"❌ Failed to download Docker: {e}")
            print("Please install Docker Desktop manually from https://docker.com/products/docker-desktop")
            return False
    
    def install_docker_linux(self):
        """Install Docker on Linux"""
        print("📦 Installing Docker on Linux...")
        
        # Check if Docker is already installed
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            print("✅ Docker already installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Detect Linux distribution
        try:
            with open("/etc/os-release") as f:
                os_info = f.read().lower()
        except FileNotFoundError:
            print("❌ Cannot detect Linux distribution")
            return False
        
        try:
            if "ubuntu" in os_info or "debian" in os_info:
                print("🐧 Installing on Ubuntu/Debian...")
                commands = [
                    ["sudo", "apt-get", "update"],
                    ["sudo", "apt-get", "install", "-y", "apt-transport-https", "ca-certificates", "curl", "gnupg", "lsb-release"],
                    ["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "|", "sudo", "gpg", "--dearmor", "-o", "/usr/share/keyrings/docker-archive-keyring.gpg"],
                    ["sudo", "apt-get", "update"],
                    ["sudo", "apt-get", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"]
                ]
            elif "centos" in os_info or "rhel" in os_info or "fedora" in os_info:
                print("🎩 Installing on CentOS/RHEL/Fedora...")
                commands = [
                    ["sudo", "yum", "install", "-y", "yum-utils"],
                    ["sudo", "yum-config-manager", "--add-repo", "https://download.docker.com/linux/centos/docker-ce.repo"],
                    ["sudo", "yum", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"]
                ]
            else:
                print("❌ Unsupported Linux distribution")
                print("Please install Docker manually: https://docs.docker.com/engine/install/")
                return False
            
            for cmd in commands:
                if "|" in cmd:
                    # Handle piped commands
                    subprocess.run(" ".join(cmd), shell=True, check=True)
                else:
                    subprocess.run(cmd, check=True)
            
            # Start and enable Docker
            subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "docker"], check=True)
            
            # Add user to docker group
            import getpass
            username = getpass.getuser()
            subprocess.run(["sudo", "usermod", "-aG", "docker", username], check=True)
            
            print("✅ Docker installed successfully")
            print("⚠️  Please log out and log back in, then run this installer again")
            return False
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Docker: {e}")
            print("Please install Docker manually: https://docs.docker.com/engine/install/")
            return False
    
    def install_docker(self):
        """Install Docker based on OS"""
        os_type = self.detect_os()
        
        if os_type == "windows":
            return self.install_docker_windows()
        elif os_type == "macos":
            return self.install_docker_macos()
        elif os_type == "linux":
            return self.install_docker_linux()
        
        return False
    
    def create_package_structure(self):
        """Create the monitoring package structure"""
        print("📁 Creating package structure...")
        
        # Create main directory
        self.install_dir.mkdir(exist_ok=True)
        
        # Copy all AWS MSP files
        files_to_copy = [
            "aws-msp-monitoring-installer.sh",
            "aws_msp_monitoring_stack.py",
            "aws_msp_security_validator.py",
            "AWS_MSP_SECURITY_GUIDE.md",
            "AWS_MSP_SECURITY_ANALYSIS.md",
            "AWS_MSP_PARTNER_GUIDE.md",
            "AWS_MSP_DASHBOARD_WALKTHROUGH.md",
            "aws_msp_demo_data_generator.py"
        ]
        
        for file_name in files_to_copy:
            src = Path(file_name)
            if src.exists():
                dst = self.install_dir / file_name
                shutil.copy2(src, dst)
                print(f"  ✅ {file_name}")
            else:
                print(f"  ⚠️  {file_name} not found")
        
        # Make shell script executable on Unix systems
        os_type = self.detect_os()
        if os_type != "windows":
            installer_script = self.install_dir / "aws-msp-monitoring-installer.sh"
            if installer_script.exists():
                installer_script.chmod(0o755)
    
    def create_cross_platform_launcher(self):
        """Create platform-specific launcher scripts"""
        print("🚀 Creating launcher scripts...")
        
        # Windows batch file
        windows_launcher = self.install_dir / "install.bat"
        windows_launcher.write_text(f"""@echo off
echo AWS MSP Monitoring Stack Installer
echo ===================================
echo.

cd /d "{self.install_dir}"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker not found. Please install Docker Desktop from docker.com
    pause
    exit /b 1
)

REM Run the installer
python aws_msp_monitoring_stack.py --install-dir customer-monitoring-stack
if errorlevel 1 (
    echo.
    echo Installation failed. Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo Access Grafana at: http://localhost:3000
echo Check CREDENTIALS.md for login information
pause
""")
        
        # Unix shell script
        unix_launcher = self.install_dir / "install.sh"
        unix_launcher.write_text(f"""#!/bin/bash
echo "AWS MSP Monitoring Stack Installer"
echo "==================================="
echo ""

cd "{self.install_dir}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found. Please install Python 3.7+"
    exit 1
fi

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker not found. Please install Docker"
    exit 1
fi

# Run the installer
python3 aws_msp_monitoring_stack.py --install-dir customer-monitoring-stack
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation failed. Check the error messages above."
    exit 1
fi

echo ""
echo "✅ Installation completed successfully!"
echo "🌐 Access Grafana at: http://localhost:3000"
echo "🔑 Check CREDENTIALS.md for login information"
""")
        
        # Make Unix script executable
        if self.system != "windows":
            unix_launcher.chmod(0o755)
        
        print(f"  ✅ install.bat (Windows)")
        print(f"  ✅ install.sh (macOS/Linux)")
    
    def create_readme(self):
        """Create installation README"""
        readme_content = f"""# AWS MSP Monitoring Stack - Universal Installer

## Quick Start

### Windows
1. Double-click `install.bat`
2. Follow the prompts

### macOS/Linux
1. Open Terminal
2. Navigate to this directory
3. Run: `./install.sh`

## Manual Installation

### Prerequisites
- Python 3.7+
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)

### Install Command
```bash
# Windows
python aws_msp_monitoring_stack.py --install-dir customer-monitoring-stack

# macOS/Linux  
python3 aws_msp_monitoring_stack.py --install-dir customer-monitoring-stack
```

## After Installation

1. **Access Grafana**: http://localhost:3000
2. **Login credentials**: Check `customer-monitoring-stack/CREDENTIALS.md`
3. **Dashboard guide**: See `AWS_MSP_DASHBOARD_WALKTHROUGH.md`
4. **API integration**: Examples in the dashboard walkthrough

## Package Contents

- `aws-msp-monitoring-installer.sh` - Main installer (Unix)
- `aws_msp_monitoring_stack.py` - Core installer
- `aws_msp_security_validator.py` - Security validation
- `AWS_MSP_DASHBOARD_WALKTHROUGH.md` - Complete dashboard guide
- `AWS_MSP_PARTNER_GUIDE.md` - Partner deployment guide
- `AWS_MSP_SECURITY_GUIDE.md` - Security documentation
- `AWS_MSP_SECURITY_ANALYSIS.md` - Security analysis
- `aws_msp_demo_data_generator.py` - Demo data generator

## Support

For issues or questions:
1. Check the troubleshooting section in `AWS_MSP_DASHBOARD_WALKTHROUGH.md`
2. Verify Docker is running: `docker --version`
3. Check Python version: `python --version` (Windows) or `python3 --version` (Unix)

## System Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **Network**: Internet connection for initial setup
"""
        
        readme_file = self.install_dir / "README.md"
        readme_file.write_text(readme_content)
        print("  ✅ README.md")
    
    def run_installation(self):
        """Run the complete installation process"""
        print("🚀 AWS MSP Monitoring Stack - Universal Installer")
        print("=" * 50)
        print()
        
        # Step 1: Check Python
        self.check_python()
        
        # Step 2: Detect OS
        os_type = self.detect_os()
        
        # Step 3: Install Docker if needed
        docker_ready = self.install_docker()
        if not docker_ready:
            print("\n⚠️  Docker installation required. Please restart and run again.")
            return False
        
        # Step 4: Create package structure
        self.create_package_structure()
        
        # Step 5: Create launchers
        self.create_cross_platform_launcher()
        
        # Step 6: Create README
        self.create_readme()
        
        print("\n" + "=" * 50)
        print("🎉 UNIVERSAL INSTALLER PACKAGE CREATED!")
        print("=" * 50)
        print(f"📁 Location: {self.install_dir.absolute()}")
        print()
        print("🚀 To deploy monitoring stack:")
        if os_type == "windows":
            print(f"   cd {self.install_dir}")
            print("   install.bat")
        else:
            print(f"   cd {self.install_dir}")
            print("   ./install.sh")
        print()
        print("📖 Documentation:")
        print("   • README.md - Quick start guide")
        print("   • AWS_MSP_DASHBOARD_WALKTHROUGH.md - Complete tutorial")
        print("   • AWS_MSP_PARTNER_GUIDE.md - Partner information")
        print()
        
        return True

def main():
    """Main entry point"""
    try:
        installer = UniversalInstaller()
        success = installer.run_installation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
