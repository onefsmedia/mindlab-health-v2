# MindLab Health - Quick Start with PostgreSQL
# Run this script to start everything with PostgreSQL

Write-Host "🚀 MindLab Health - PostgreSQL Quick Start" -ForegroundColor Green
Write-Host "=" * 80

# Step 1: Start PostgreSQL
Write-Host "`n📦 Step 1: Starting PostgreSQL..." -ForegroundColor Cyan
$postgresRunning = podman ps --filter "name=mindlab-postgres" --format "{{.Names}}"
if ($postgresRunning -eq "mindlab-postgres") {
    Write-Host "✅ PostgreSQL is already running" -ForegroundColor Green
} else {
    Write-Host "Starting PostgreSQL container..."
    podman run -d `
      --name mindlab-postgres `
      -e POSTGRES_DB=mindlab_health `
      -e POSTGRES_USER=mindlab_admin `
      -e POSTGRES_PASSWORD=MindLab2024!Secure `
      -p 5432:5432 `
      -v mindlab_postgres_data:/var/lib/postgresql/data `
      postgres:16-alpine

    Write-Host "⏳ Waiting for PostgreSQL to be ready (15 seconds)..."
    Start-Sleep -Seconds 15
}

# Step 2: Verify PostgreSQL
Write-Host "`n🔍 Step 2: Verifying PostgreSQL..." -ForegroundColor Cyan
try {
    $result = podman exec mindlab-postgres psql -U mindlab_admin -d mindlab_health -c "SELECT version();" 2>&1
    Write-Host "✅ PostgreSQL is ready!" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL connection failed. Check logs with: podman logs mindlab-postgres" -ForegroundColor Red
    exit 1
}

# Step 3: Migrate data from SQLite (if exists)
Write-Host "`n📊 Step 3: Checking for existing SQLite data..." -ForegroundColor Cyan
if (Test-Path "mindlab_health.db") {
    $migrate = Read-Host "SQLite database found. Migrate data? (y/n)"
    if ($migrate -eq "y") {
        Write-Host "Running migration script..."
        $env:DATABASE_URL = "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5432/mindlab_health"
        python migrate_to_postgres.py
    }
} else {
    Write-Host "⏭️  No SQLite database found. Will start fresh." -ForegroundColor Yellow
}

# Step 4: Build application
Write-Host "`n🔨 Step 4: Building application..." -ForegroundColor Cyan
podman build -t mindlab-health-v2:latest . | Select-String "Successfully"

# Step 5: Stop old container
Write-Host "`n🛑 Step 5: Stopping old container..." -ForegroundColor Cyan
$oldContainers = @("mindlab-health-v3", "mindlab-health-v4", "mindlab-health-v5")
foreach ($container in $oldContainers) {
    $running = podman ps -a --filter "name=$container" --format "{{.Names}}"
    if ($running -eq $container) {
        podman stop $container 2>&1 | Out-Null
        Write-Host "✅ Stopped $container" -ForegroundColor Green
    }
}

# Step 6: Start application with PostgreSQL
Write-Host "`n🚀 Step 6: Starting application with PostgreSQL..." -ForegroundColor Cyan
podman run -d `
  --name mindlab-health-v5 `
  -p 8000:8000 `
  -e DATABASE_URL="postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5432/mindlab_health" `
  mindlab-health-v2:latest

Write-Host "⏳ Waiting for application to start (5 seconds)..."
Start-Sleep -Seconds 5

# Step 7: Verify application
Write-Host "`n✅ Step 7: Verifying application..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000 -Method GET -TimeoutSec 5
    Write-Host "✅ Application is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Application may still be starting. Check with: podman logs mindlab-health-v5" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + "=" * 80
Write-Host "🎉 PostgreSQL Setup Complete!" -ForegroundColor Green -BackgroundColor Black
Write-Host "=" * 80

Write-Host "`n📋 Connection Details:" -ForegroundColor Cyan
Write-Host "  🌐 Application: http://localhost:8000"
Write-Host "  🗄️  Database: PostgreSQL on localhost:5432"
Write-Host "  👤 Admin User: admin / Admin123!@#"
Write-Host "  🔑 DB User: mindlab_admin / MindLab2024!Secure"

Write-Host "`n🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "  View app logs:       podman logs -f mindlab-health-v5"
Write-Host "  View DB logs:        podman logs -f mindlab-postgres"
Write-Host "  Connect to DB:       podman exec -it mindlab-postgres psql -U mindlab_admin -d mindlab_health"
Write-Host "  Stop all:            podman stop mindlab-health-v5 mindlab-postgres"
Write-Host "  Restart app:         podman restart mindlab-health-v5"

Write-Host "`n💾 Database Backup:" -ForegroundColor Cyan
Write-Host '  podman exec mindlab-postgres pg_dump -U mindlab_admin mindlab_health > backup.sql'

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8000 in your browser"
Write-Host "  2. Login with admin / Admin123!@#"
Write-Host "  3. Test all modules (Users, Meals, Nutrients, Ingredient Nutrition)"
Write-Host "  4. Your data is now persistent in PostgreSQL!"

Write-Host "`n✨ Ready to use! ✨`n" -ForegroundColor Green
