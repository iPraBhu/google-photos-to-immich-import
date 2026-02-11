@echo off
echo 🚀 Setting up Google Photos to Immich Import
echo ==========================================
echo.

REM Check if docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

echo ✅ Docker is available

REM Create data directory if it doesn't exist
if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs

echo 📁 Created data directory

REM Build and start services
echo 🏗️  Building and starting services...
docker compose up -d --build

if errorlevel 1 (
    echo ❌ Failed to start services. Check Docker installation.
    pause
    exit /b 1
)

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker ps -q -f name=google-photos-to-immich-import-web-1 >nul 2>&1
if errorlevel 1 (
    echo ❌ Web service failed to start. Check logs with: docker compose logs
    pause
    exit /b 1
)

echo ✅ Web service is running
echo.
echo 🎉 Setup complete!
echo ==================
echo 🌐 Web UI: http://localhost:8000
echo 📊 Immich: http://localhost:2283 (if running)
echo.
echo To view logs: docker compose logs -f
echo To stop: docker compose down
echo.
pause