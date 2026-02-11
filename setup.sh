#!/bin/bash

echo "🚀 Setting up Google Photos to Immich Import"
echo "=========================================="

# Check if docker and docker-compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create data directory if it doesn't exist
mkdir -p data/logs

echo "📁 Created data directory"

# Build and start services
echo "🏗️  Building and starting services..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if [ "$(docker ps -q -f name=google-photos-to-immich-import-web-1)" ]; then
    echo "✅ Web service is running"
    echo ""
    echo "🎉 Setup complete!"
    echo "=================="
    echo "🌐 Web UI: http://localhost:8000"
    echo "📊 Immich: http://localhost:2283 (if running)"
    echo ""
    echo "To view logs: docker compose logs -f"
    echo "To stop: docker compose down"
else
    echo "❌ Web service failed to start. Check logs with: docker compose logs"
    exit 1
fi