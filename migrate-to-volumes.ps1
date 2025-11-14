# MindLab Health Data Migration Script (PowerShell)
# Migrates data from current container to volume-based setup

Write-Host "=== MindLab Health Data Migration ===" -ForegroundColor Cyan
Write-Host "This script will migrate your database to persistent volumes" -ForegroundColor Yellow
Write-Host "without losing any work." -ForegroundColor Yellow
Write-Host ""

# Get current timestamp for backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "backup_$timestamp.sql"

try {
    # Step 1: Create database backup
    Write-Host "Step 1: Creating database backup..." -ForegroundColor Green
    $backupResult = podman exec mindlab-postgres pg_dump -U mindlab_admin -d mindlab_health
    $backupResult | Out-File -FilePath $backupFile -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database backup created successfully: $backupFile" -ForegroundColor Green
    } else {
        throw "Database backup failed"
    }

    # Step 2: Stop current application (but keep database)
    Write-Host "`nStep 2: Stopping application services..." -ForegroundColor Green
    podman stop mindlab-health-v59 2>$null
    podman stop mindlab-app 2>$null
    Write-Host "✓ Application services stopped" -ForegroundColor Green

    # Step 3: Setup volume-based postgres
    Write-Host "`nStep 3: Setting up volume-based postgres..." -ForegroundColor Green
    
    # Check if postgres_volumes exists
    $existingPgVolumes = podman ps -a | Select-String "postgres_volumes"
    
    if (-not $existingPgVolumes) {
        Write-Host "Creating new postgres container with volumes..." -ForegroundColor Yellow
        
        # Clean up any existing postgres_volumes
        podman stop postgres_volumes 2>$null
        podman rm postgres_volumes 2>$null
        
        # Start new postgres with volume
        $pgResult = podman run -d `
            --name postgres_volumes `
            -e POSTGRES_DB=mindlab_health `
            -e POSTGRES_USER=mindlab_admin `
            -e POSTGRES_PASSWORD="MindLab2024!Secure" `
            -v "${PWD}\volumes\postgres_data:/var/lib/postgresql/data" `
            -p 5434:5432 `
            postgres:16-alpine
            
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to start postgres_volumes container"
        }
        
        # Wait for postgres to be ready
        Write-Host "Waiting for postgres to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        # Test connection
        $testConnection = podman exec postgres_volumes pg_isready -U mindlab_admin
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Waiting a bit more for postgres..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
        }
        
        # Restore backup to new postgres
        Write-Host "Restoring backup to volume-based postgres..." -ForegroundColor Yellow
        Get-Content $backupFile | podman exec -i postgres_volumes psql -U mindlab_admin -d mindlab_health
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Data restored to volume-based postgres" -ForegroundColor Green
        } else {
            throw "Data restoration failed"
        }
    } else {
        Write-Host "✓ Volume-based postgres already exists" -ForegroundColor Green
        # Make sure it's running
        podman start postgres_volumes 2>$null
    }

    # Step 4: Update and start application
    Write-Host "`nStep 4: Starting application with volumes..." -ForegroundColor Green
    
    # Build new image
    Write-Host "Building updated application image..." -ForegroundColor Yellow
    podman build -t mindlab-health-volumes:latest .
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to build application image"
    }
    
    # Remove old app container if exists
    podman stop mindlab-app-volumes 2>$null
    podman rm mindlab-app-volumes 2>$null
    
    # Start app with new database connection
    $appResult = podman run -d `
        --name mindlab-app-volumes `
        -p 8000:8000 `
        -e DATABASE_URL="postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5434/mindlab_health" `
        -v "${PWD}\volumes\app_logs:/app/logs" `
        --add-host host.containers.internal:host-gateway `
        mindlab-health-volumes:latest

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start application container"
    }

    # Verify services are running
    Start-Sleep -Seconds 5
    $pgStatus = podman ps | Select-String "postgres_volumes"
    $appStatus = podman ps | Select-String "mindlab-app-volumes"
    
    if ($pgStatus -and $appStatus) {
        Write-Host "`n✓ Migration completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔗 Your application is now running with persistent volumes:" -ForegroundColor Cyan
        Write-Host "   - Database: postgres_volumes container with data in volumes/postgres_data" -ForegroundColor White
        Write-Host "   - App logs: volumes/app_logs" -ForegroundColor White
        Write-Host "   - Application: http://localhost:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "📦 Old containers (mindlab-postgres, mindlab-health-v59) are preserved" -ForegroundColor Yellow
        Write-Host "    You can remove them later once you confirm everything works" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🎯 All your healthcare modules and data have been preserved!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Container Status:" -ForegroundColor Cyan
        podman ps | Select-String "mindlab|postgres_volumes"
    } else {
        throw "Services did not start properly"
    }

} catch {
    Write-Host "`n❌ Migration failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔄 Your original setup is still intact." -ForegroundColor Yellow
    Write-Host "   - Original app: mindlab-health-v59" -ForegroundColor White
    Write-Host "   - Original DB: mindlab-postgres" -ForegroundColor White
    Write-Host "`n📞 Please check the error and try again." -ForegroundColor Yellow
    exit 1
}