# MindLab Health - Docker Compose Setup with Persistent Volumes (PowerShell)
# This script ensures the database and application are run with persistent storage

Write-Host "🔧 MindLab Health - Setting up with persistent volumes..." -ForegroundColor Green

# Stop any existing standalone containers
Write-Host "📦 Stopping existing containers..." -ForegroundColor Yellow
try {
    podman stop mindlab-health-v59 2>$null
    podman rm mindlab-health-v59 2>$null
} catch {
    # Container may not exist
}

# Create volume directories if they don't exist
Write-Host "📁 Creating volume directories..." -ForegroundColor Yellow
$volumesPath = Join-Path $PWD "volumes"
$postgresPath = Join-Path $volumesPath "postgres_data"
$logsPath = Join-Path $volumesPath "app_logs"

New-Item -ItemType Directory -Path $postgresPath -Force | Out-Null
New-Item -ItemType Directory -Path $logsPath -Force | Out-Null

# Build and start the stack using podman-compose (or docker-compose as fallback)
Write-Host "🚀 Starting Docker Compose stack..." -ForegroundColor Yellow

# Try podman-compose first, then docker-compose
try {
    podman-compose down 2>$null
} catch {
    try {
        docker-compose down 2>$null
    } catch {
        Write-Host "No existing compose stack to stop" -ForegroundColor Gray
    }
}

# Check if we should use podman-compose or docker-compose
$useCommand = "podman-compose"
try {
    & $useCommand --version 2>$null | Out-Null
} catch {
    $useCommand = "docker-compose"
    try {
        & $useCommand --version 2>$null | Out-Null
    } catch {
        Write-Error "Neither podman-compose nor docker-compose found!"
        exit 1
    }
}

Write-Host "Using $useCommand..." -ForegroundColor Cyan

& $useCommand build
& $useCommand up -d

Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Yellow
& $useCommand ps

Write-Host ""
Write-Host "✅ Setup complete! Services available at:" -ForegroundColor Green
Write-Host "   🌐 MindLab Health App: http://localhost:8000" -ForegroundColor White
Write-Host "   🗄️  PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "   📂 Database files: $postgresPath" -ForegroundColor White
Write-Host "   📝 Application logs: $logsPath" -ForegroundColor White
Write-Host ""
Write-Host "📋 To manage the stack:" -ForegroundColor Cyan
Write-Host "   • View logs: $useCommand logs -f" -ForegroundColor White
Write-Host "   • Stop services: $useCommand down" -ForegroundColor White
Write-Host "   • Start services: $useCommand up -d" -ForegroundColor White
Write-Host "   • Rebuild: $useCommand build; $useCommand up -d" -ForegroundColor White
Write-Host ""
Write-Host "💾 Your database is now persistent! Data will survive container restarts." -ForegroundColor Green