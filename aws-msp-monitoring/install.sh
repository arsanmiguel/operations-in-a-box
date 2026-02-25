#!/bin/bash
echo "AWS MSP Monitoring Stack Installer"
echo "==================================="
echo ""

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Attempting to install..."
    
    # Try to install Python based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "🍺 Installing Python via Homebrew..."
            brew install python3
        else
            echo "Please install Python 3.7+ from python.org or install Homebrew first"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo "🐧 Installing Python via apt..."
            sudo apt-get update && sudo apt-get install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            echo "🎩 Installing Python via yum..."
            sudo yum install -y python3 python3-pip
        else
            echo "Please install Python 3.7+ using your system package manager"
            exit 1
        fi
    else
        echo "Unsupported OS. Please install Python 3.7+ manually"
        exit 1
    fi
    
    # Verify installation
    if ! command -v python3 &> /dev/null; then
        echo "Python installation failed. Please install manually"
        exit 1
    fi
fi

echo "Python 3 found"

# The main installer will handle Docker installation automatically
echo "Starting installation (Docker will be installed automatically if needed)..."

# Run the installer
python3 aws_msp_monitoring_stack.py --install-dir customer-monitoring-stack
if [ $? -ne 0 ]; then
    echo ""
    echo "Installation failed. Check the error messages above."
    exit 1
fi

echo ""
echo "Installation completed successfully!"
echo "🌐 Access Grafana at: http://localhost:3000"
echo "🔑 Check customer-monitoring-stack/CREDENTIALS.md for login information"
echo "🔑 Check CREDENTIALS.md for login information"
