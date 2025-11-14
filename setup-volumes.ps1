# MindLab Health - Podman Setup with Persistent Volumes
Write-Host "MindLab Health - Setting up with persistent volumes using Podman..." -ForegroundColor Green

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
try {
    podman stop mindlab-health-v59 mindlab-postgres mindlab-app 2>$null | Out-Null
    podman rm mindlab-health-v59 mindlab-postgres mindlab-app 2>$null | Out-Null
} catch {
    Write-Host "No existing containers to stop" -ForegroundColor Gray
}

# Create volume directories
Write-Host "Creating volume directories..." -ForegroundColor Yellow
$projectPath = $PWD
$postgresPath = Join-Path $projectPath "volumes\postgres_data"
$logsPath = Join-Path $projectPath "volumes\app_logs"

New-Item -ItemType Directory -Path $postgresPath -Force | Out-Null
New-Item -ItemType Directory -Path $logsPath -Force | Out-Null

Write-Host "PostgreSQL data: $postgresPath" -ForegroundColor Cyan
Write-Host "Application logs: $logsPath" -ForegroundColor Cyan

# Create network
Write-Host "Creating network..." -ForegroundColor Yellow
try {
    podman network rm mindlab-network 2>$null | Out-Null
} catch {}
podman network create mindlab-network

# Start PostgreSQL with persistent volume
Write-Host "Starting PostgreSQL database..." -ForegroundColor Yellow
podman run -d `
    --name mindlab-postgres `
    --network mindlab-network `
    -e POSTGRES_DB=mindlab_health `
    -e POSTGRES_USER=mindlab_admin `
    -e "POSTGRES_PASSWORD=MindLab2024!Secure" `
    -e PGDATA=/var/lib/postgresql/data/pgdata `
    -v "${postgresPath}:/var/lib/postgresql/data" `
    -p 5432:5432 `
    --restart unless-stopped `
    postgres:16

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Build the application image
Write-Host "Building application image..." -ForegroundColor Yellow
podman build -t mindlab-health-volumes:latest .

# Start the application with volume mounts
Write-Host "Starting MindLab Health application..." -ForegroundColor Yellow
podman run -d `
    --name mindlab-app `
    --network mindlab-network `
    -e "DATABASE_URL=postgresql://mindlab_admin:MindLab2024!Secure@mindlab-postgres:5432/mindlab_health" `
    -e PYTHONPATH=/app `
    -v "${logsPath}:/app/logs" `
    -p 8000:8000 `
    --restart unless-stopped `
    mindlab-health-volumes:latest

# Wait for application to be ready
Write-Host "Waiting for application to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Yellow
podman ps --filter name=mindlab

Write-Host ""
Write-Host "Setup complete! Services available at:" -ForegroundColor Green
Write-Host "MindLab Health App: http://localhost:8000" -ForegroundColor White
Write-Host "PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "Database files: $postgresPath" -ForegroundColor White
Write-Host "Application logs: $logsPath" -ForegroundColor White
Write-Host ""
Write-Host "Management commands:" -ForegroundColor Cyan
Write-Host "View app logs: podman logs -f mindlab-app" -ForegroundColor White
Write-Host "View DB logs: podman logs -f mindlab-postgres" -ForegroundColor White
Write-Host "Stop all: podman stop mindlab-app mindlab-postgres" -ForegroundColor White
Write-Host "Remove all: podman rm mindlab-app mindlab-postgres" -ForegroundColor White
Write-Host ""
Write-Host "DATABASE IS NOW PERSISTENT! Data will survive container restarts." -ForegroundColor Green