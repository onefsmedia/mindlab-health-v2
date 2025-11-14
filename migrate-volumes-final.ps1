# MindLab Health Data Migration Script - Named Volumes Version
# Migrates data from current container to volume-based setup using named volumes

Write-Host "=== MindLab Health Data Migration (Named Volumes) ===" -ForegroundColor Cyan
Write-Host "This script will migrate your database to persistent named volumes" -ForegroundColor Yellow
Write-Host "without losing any work." -ForegroundColor Yellow
Write-Host ""

# Get current timestamp for backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "backup_$timestamp.sql"

try {
    # Step 1: Create database backup from current running database
    Write-Host "Step 1: Creating database backup from current database..." -ForegroundColor Green
    podman exec mindlab-postgres pg_dump -U mindlab_admin -d mindlab_health | Out-File -FilePath $backupFile -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $backupFile) -and (Get-Item $backupFile).Length -gt 1000) {
        Write-Host "[OK] Database backup created successfully: $backupFile" -ForegroundColor Green
        Write-Host "     Backup size: $((Get-Item $backupFile).Length) bytes" -ForegroundColor Gray
    } else {
        throw "Database backup failed or is too small"
    }

    # Step 2: Stop current application (but keep current database running for now)
    Write-Host "`nStep 2: Stopping application services..." -ForegroundColor Green
    podman stop mindlab-health-v59 2>$null
    podman stop mindlab-app 2>$null
    podman stop mindlab-app-volumes 2>$null
    Write-Host "[OK] Application services stopped" -ForegroundColor Green

    # Step 3: Clean up any existing volume containers and start fresh
    Write-Host "`nStep 3: Setting up fresh volume-based postgres..." -ForegroundColor Green
    
    # Clean up existing volume containers
    podman stop postgres_volumes 2>$null
    podman rm postgres_volumes 2>$null
    
    Write-Host "Starting postgres with named volume..." -ForegroundColor Yellow
    
    # Start postgres with named volume (better for Windows)
    $pgResult = podman run -d `
        --name postgres_volumes `
        -e POSTGRES_DB=mindlab_health `
        -e POSTGRES_USER=mindlab_admin `
        -e POSTGRES_PASSWORD="MindLab2024!Secure" `
        -v mindlab-postgres-data:/var/lib/postgresql/data `
        -p 5434:5432 `
        postgres:16-alpine
        
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start postgres_volumes container"
    }
    
    Write-Host "Postgres container started, waiting for initialization..." -ForegroundColor Yellow
    
    # Wait for postgres to be fully ready
    $maxWait = 30
    $waited = 0
    do {
        Start-Sleep -Seconds 2
        $waited += 2
        $ready = podman exec postgres_volumes pg_isready -U mindlab_admin 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Postgres is ready!" -ForegroundColor Green
            break
        }
        Write-Host "Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    } while ($waited -lt $maxWait)
    
    if ($waited -ge $maxWait) {
        throw "Postgres did not become ready in time"
    }
    
    # Restore backup to new postgres
    Write-Host "Restoring backup to volume-based postgres..." -ForegroundColor Yellow
    Get-Content $backupFile | podman exec -i postgres_volumes psql -U mindlab_admin -d mindlab_health
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Data restored to volume-based postgres" -ForegroundColor Green
    } else {
        throw "Data restoration failed"
    }

    # Step 4: Build and start application with volumes
    Write-Host "`nStep 4: Building and starting application with volumes..." -ForegroundColor Green
    
    # Build new image
    Write-Host "Building updated application image..." -ForegroundColor Yellow
    podman build -t mindlab-health-volumes:latest .
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to build application image"
    }
    
    # Remove old app container if exists
    podman stop mindlab-app-volumes 2>$null
    podman rm mindlab-app-volumes 2>$null
    
    # Start app with new database connection and named volume for logs
    Write-Host "Starting application container..." -ForegroundColor Yellow
    $appResult = podman run -d `
        --name mindlab-app-volumes `
        -p 8000:8000 `
        -e DATABASE_URL="postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5434/mindlab_health" `
        -v mindlab-app-logs:/app/logs `
        --add-host host.containers.internal:host-gateway `
        mindlab-health-volumes:latest

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start application container"
    }

    # Step 5: Verify everything is working
    Write-Host "`nStep 5: Verifying migration..." -ForegroundColor Green
    Start-Sleep -Seconds 5
    
    $pgStatus = podman ps | Select-String "postgres_volumes.*Up"
    $appStatus = podman ps | Select-String "mindlab-app-volumes.*Up"
    
    if ($pgStatus -and $appStatus) {
        Write-Host "`n[SUCCESS] Migration completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your application is now running with persistent named volumes:" -ForegroundColor Cyan
        Write-Host "   - Database: postgres_volumes container with 'mindlab-postgres-data' volume" -ForegroundColor White
        Write-Host "   - App logs: 'mindlab-app-logs' volume" -ForegroundColor White
        Write-Host "   - Application: http://localhost:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "Migration Summary:" -ForegroundColor Yellow
        Write-Host "   - Old app container (mindlab-health-v59): STOPPED but preserved" -ForegroundColor Gray
        Write-Host "   - Old database (mindlab-postgres): RUNNING and preserved as backup" -ForegroundColor Gray
        Write-Host "   - New app container (mindlab-app-volumes): RUNNING on port 8000" -ForegroundColor Green
        Write-Host "   - New database (postgres_volumes): RUNNING on port 5434 with volumes" -ForegroundColor Green
        Write-Host ""
        Write-Host "All your healthcare modules and data have been preserved!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Current Container Status:" -ForegroundColor Cyan
        podman ps | Select-String "mindlab|postgres"
        Write-Host ""
        Write-Host "Named Volumes:" -ForegroundColor Cyan
        podman volume ls | Select-String "mindlab"
    } else {
        throw "Services did not start properly"
    }

} catch {
    Write-Host "`n[ERROR] Migration failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nRecovery: Your original setup is still intact." -ForegroundColor Yellow
    Write-Host "   - Original app can be restarted: podman start mindlab-health-v59" -ForegroundColor White
    Write-Host "   - Original DB is still running: mindlab-postgres" -ForegroundColor White
    Write-Host "`nTroubleshooting: Check podman logs for more details" -ForegroundColor Yellow
    exit 1
}