#!/bin/bash
# MindLab Health - Docker Compose Setup with Persistent Volumes
# This script ensures the database and application are run with persistent storage

echo "🔧 MindLab Health - Setting up with persistent volumes..."

# Stop any existing standalone containers
echo "📦 Stopping existing containers..."
podman stop mindlab-health-v59 2>/dev/null || true
podman rm mindlab-health-v59 2>/dev/null || true

# Create volume directories if they don't exist
echo "📁 Creating volume directories..."
mkdir -p volumes/postgres_data
mkdir -p volumes/app_logs

# Set proper permissions for PostgreSQL volume
echo "🔐 Setting permissions..."
sudo chown -R 999:999 volumes/postgres_data 2>/dev/null || chown -R 999:999 volumes/postgres_data

# Build and start the stack
echo "🚀 Starting Docker Compose stack..."
podman-compose down 2>/dev/null || docker-compose down 2>/dev/null || true
podman-compose build
podman-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Checking service status..."
podman-compose ps

echo ""
echo "✅ Setup complete! Services available at:"
echo "   🌐 MindLab Health App: http://localhost:8000"
echo "   🗄️  PostgreSQL: localhost:5432"
echo "   📂 Database files: $(pwd)/volumes/postgres_data"
echo "   📝 Application logs: $(pwd)/volumes/app_logs"
echo ""
echo "📋 To manage the stack:"
echo "   • View logs: podman-compose logs -f"
echo "   • Stop services: podman-compose down"
echo "   • Start services: podman-compose up -d"
echo "   • Rebuild: podman-compose build && podman-compose up -d"
echo ""
echo "💾 Your database is now persistent! Data will survive container restarts."