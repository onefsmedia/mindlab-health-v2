# MindLab Health Deployment Script
Write-Host "Starting MindLab Health deployment..." -ForegroundColor Green

# Check if Podman is installed
if (!(Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Podman is not installed!" -ForegroundColor Red
    exit 1
}

Write-Host "Podman version:" -ForegroundColor Cyan
podman --version

# Stop existing containers
Write-Host "\nStopping existing containers..." -ForegroundColor Yellow
podman compose -f 12_compose.yml down 2>$null

# Build the image
Write-Host "\nBuilding container image..." -ForegroundColor Cyan
podman build -f 11_Dockerfile -t mindlab-health:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "\nStarting services..." -ForegroundColor Cyan
podman compose -f 12_compose.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services!" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "\nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check health
Write-Host "\nChecking application health..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/health -TimeoutSec 5
    Write-Host "SUCCESS: Application is healthy!" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "WARNING: Health check failed. Services may still be starting..." -ForegroundColor Yellow
}

# Show running containers
Write-Host "\nRunning containers:" -ForegroundColor Cyan
podman ps

Write-Host "\nDeployment complete! Access the application at http://localhost:8000" -ForegroundColor Green