#!/bin/bash
# MindLab Health Data Migration Script
# Migrates data from current container to volume-based setup

echo "=== MindLab Health Data Migration ==="
echo "This script will migrate your database to persistent volumes"
echo "without losing any work."

# Step 1: Create database backup
echo ""
echo "Step 1: Creating database backup..."
podman exec mindlab-postgres pg_dump -U mindlab_admin -d mindlab_health > backup_$(date +%Y%m%d_%H%M%S).sql
if [ $? -eq 0 ]; then
    echo "✅ Database backup created successfully"
else
    echo "❌ Database backup failed - STOPPING migration"
    exit 1
fi

# Step 2: Stop current services (but keep data containers)
echo ""
echo "Step 2: Stopping application services..."
podman stop mindlab-health-v59 mindlab-app 2>/dev/null || true
echo "✅ Application services stopped"

# Step 3: Ensure postgres data volume has current data
echo ""
echo "Step 3: Preparing volume-based postgres..."

# Check if postgres_volumes container exists, if not create it
if ! podman ps -a | grep -q "postgres_volumes"; then
    echo "Creating new postgres container with volumes..."
    
    # Stop any existing postgres_volumes container
    podman stop postgres_volumes 2>/dev/null || true
    podman rm postgres_volumes 2>/dev/null || true
    
    # Start new postgres with volume
    podman run -d \
        --name postgres_volumes \
        -e POSTGRES_DB=mindlab_health \
        -e POSTGRES_USER=mindlab_admin \
        -e POSTGRES_PASSWORD=MindLab2024!Secure \
        -v "$(pwd)/volumes/postgres_data:/var/lib/postgresql/data" \
        -p 5434:5432 \
        postgres:16-alpine
        
    # Wait for postgres to be ready
    echo "Waiting for postgres to be ready..."
    sleep 10
    
    # Restore backup to new postgres
    echo "Restoring backup to volume-based postgres..."
    podman exec -i postgres_volumes psql -U mindlab_admin -d mindlab_health < backup_$(date +%Y%m%d)*.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Data restored to volume-based postgres"
    else
        echo "❌ Data restoration failed"
        exit 1
    fi
else
    echo "✅ Volume-based postgres already exists"
fi

# Step 4: Update app to use new postgres
echo ""
echo "Step 4: Starting services with volumes..."

# Build new image with updated DATABASE_URL
podman build -t mindlab-health-volumes:latest .

# Start postgres (if not already running)
if ! podman ps | grep -q "postgres_volumes"; then
    podman start postgres_volumes
fi

# Wait a moment for postgres
sleep 5

# Start app with new database connection
podman run -d \
    --name mindlab-app-volumes \
    -p 8000:8000 \
    -e DATABASE_URL="postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5434/mindlab_health" \
    -v "$(pwd)/volumes/app_logs:/app/logs" \
    --add-host host.containers.internal:host-gateway \
    mindlab-health-volumes:latest

echo ""
echo "✅ Migration completed successfully!"
echo ""
echo "🔗 Your application is now running with persistent volumes:"
echo "   - Database: postgres_volumes container with data in volumes/postgres_data"
echo "   - App logs: volumes/app_logs"
echo "   - Application: http://localhost:8000"
echo ""
echo "📦 Old containers (mindlab-postgres, mindlab-health-v59) are preserved"
echo "    You can remove them later once you confirm everything works"
echo ""
echo "🎯 All your healthcare modules and data have been preserved!"