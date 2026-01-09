@echo off
echo AWS MSP Monitoring Stack Installer
echo ===================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Attempting to install...
    echo.
    echo Downloading Python installer...
    
    REM Try to download and install Python
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe'}"
    if errorlevel 1 (
        echo Failed to download Python installer.
        echo Please install Python 3.7+ manually from python.org
        pause
        exit /b 1
    )
    
    echo Installing Python...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    if errorlevel 1 (
        echo Python installation failed.
        echo Please install Python 3.7+ manually from python.org
        pause
        exit /b 1
    )
    
    REM Clean up installer
    del python-installer.exe
    
    REM Refresh PATH
    call refreshenv.cmd 2>nul || echo Please restart your command prompt and run this installer again
    
    REM Check again
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Python installation completed but not found in PATH.
        echo Please restart your command prompt and run this installer again.
        pause
        exit /b 1
    )
)

echo Python found!
echo.

REM The main installer will handle Docker installation automatically
echo Starting installation (Docker will be installed automatically if needed)...
echo.

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
echo Check customer-monitoring-stack\CREDENTIALS.md for login information
pause
)

echo.
echo Installation completed successfully!
echo Access Grafana at: http://localhost:3000
echo Check CREDENTIALS.md for login information
pause
