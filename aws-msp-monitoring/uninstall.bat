@echo off
echo Removing AWS MSP Monitoring Stack...
echo.

REM Stop and remove all containers, networks, and volumes
if exist "customer-monitoring-stack\docker-compose.yml" (
    cd customer-monitoring-stack
    docker-compose down -v --remove-orphans >nul 2>&1
    cd ..
)

REM Remove plugin containers
for /r customer-monitoring-stack\plugins %%i in (docker-compose.yml) do (
    cd "%%~pi"
    docker-compose down -v --remove-orphans >nul 2>&1
    cd /d "%~dp0"
)

REM Clean up Docker system (images, containers, networks, volumes)
echo Cleaning up Docker images and volumes...
docker system prune -f --volumes >nul 2>&1

echo.
echo AWS MSP Monitoring Stack removed successfully!
echo You can now safely delete this folder if desired.
echo.
pause
