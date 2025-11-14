# MindLab Health - System Protection & Isolation Strategy
# Ensures current working system remains untouched during new development

Write-Host "=== MINDLAB HEALTH PROTECTION PROTOCOL ===" -ForegroundColor Cyan
Write-Host "Protecting your current working system before any new development" -ForegroundColor Yellow
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\system_state_$timestamp"

try {
    # Create backup directory
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Write-Host "Created backup directory: $backupDir" -ForegroundColor Green
    
    # 1. FULL DATABASE BACKUP
    Write-Host "`n1. Creating complete database backup..." -ForegroundColor Yellow
    $dbBackup = "$backupDir\complete_database_backup.sql"
    podman exec postgres_volumes pg_dump -U mindlab_admin -d mindlab_health | Out-File -FilePath $dbBackup -Encoding UTF8
    
    if (Test-Path $dbBackup -and (Get-Item $dbBackup).Length -gt 1000) {
        Write-Host "   ✓ Database backup: $((Get-Item $dbBackup).Length) bytes" -ForegroundColor Green
    } else {
        throw "Database backup failed"
    }
    
    # 2. APPLICATION CODE BACKUP
    Write-Host "`n2. Backing up application code..." -ForegroundColor Yellow
    $excludePatterns = @("volumes", "backups", "*.log", "__pycache__", "*.pyc", ".git")
    $appBackup = "$backupDir\application_code"
    
    # Copy all application files except excluded patterns
    robocopy "." "$appBackup" /E /XD volumes backups __pycache__ .git /XF *.log *.pyc /NFL /NDL /NP | Out-Null
    Write-Host "   ✓ Application code backed up to: $appBackup" -ForegroundColor Green
    
    # 3. CONTAINER STATE BACKUP
    Write-Host "`n3. Recording container configurations..." -ForegroundColor Yellow
    $containerInfo = @"
=== WORKING CONTAINER CONFIGURATION ===
Date: $(Get-Date)
Application Container: mindlab-app-volumes
Database Container: postgres_volumes
Application Port: 8000
Database Port: 5434
Volumes: mindlab-postgres-data, mindlab-app-logs

Container Details:
$(podman ps | Select-String "mindlab-app-volumes|postgres_volumes")

Volume Details:
$(podman volume ls | Select-String "mindlab")

Application Status: $(try { Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 3 | Out-Null; "WORKING" } catch { "ERROR" })
Database Status: $(if ((podman exec postgres_volumes pg_isready -U mindlab_admin 2>$null) -and $LASTEXITCODE -eq 0) { "WORKING" } else { "ERROR" })
"@
    
    $containerInfo | Out-File -FilePath "$backupDir\container_state.txt" -Encoding UTF8
    Write-Host "   ✓ Container state recorded" -ForegroundColor Green
    
    # 4. ENVIRONMENT VARIABLES
    Write-Host "`n4. Saving environment configuration..." -ForegroundColor Yellow
    $envConfig = @"
# MindLab Health Environment Configuration
DATABASE_URL=postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5434/mindlab_health
APP_PORT=8000
DB_PORT=5434

# Volume Configuration
POSTGRES_VOLUME=mindlab-postgres-data
APP_LOGS_VOLUME=mindlab-app-logs

# Container Names
APP_CONTAINER=mindlab-app-volumes
DB_CONTAINER=postgres_volumes
"@
    
    $envConfig | Out-File -FilePath "$backupDir\environment.env" -Encoding UTF8
    Write-Host "   ✓ Environment configuration saved" -ForegroundColor Green
    
    # 5. RESTORE SCRIPT
    Write-Host "`n5. Creating restore script..." -ForegroundColor Yellow
    $restoreScript = @"
# MindLab Health System Restore Script
# Restores the complete working system from backup

Write-Host "=== MINDLAB HEALTH SYSTEM RESTORE ===" -ForegroundColor Cyan
Write-Host "Restoring system from backup: $backupDir" -ForegroundColor Yellow
Write-Host ""

try {
    # Stop any conflicting containers
    podman stop mindlab-app-volumes postgres_volumes 2>`$null
    podman rm mindlab-app-volumes postgres_volumes 2>`$null
    
    # Recreate volumes if needed
    podman volume create mindlab-postgres-data 2>`$null
    podman volume create mindlab-app-logs 2>`$null
    
    # Restore database
    Write-Host "Restoring database..." -ForegroundColor Yellow
    podman run -d --name postgres_volumes -e POSTGRES_DB=mindlab_health -e POSTGRES_USER=mindlab_admin -e POSTGRES_PASSWORD="MindLab2024!Secure" -v mindlab-postgres-data:/var/lib/postgresql/data -p 5434:5432 postgres:16-alpine
    Start-Sleep -Seconds 15
    Get-Content "$backupDir\complete_database_backup.sql" | podman exec -i postgres_volumes psql -U mindlab_admin -d mindlab_health
    
    # Restore application
    Write-Host "Restoring application..." -ForegroundColor Yellow
    Copy-Item -Path "$backupDir\application_code\*" -Destination "." -Recurse -Force
    podman build -t mindlab-health-volumes:latest .
    podman run -d --name mindlab-app-volumes -p 8000:8000 -e DATABASE_URL="postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5434/mindlab_health" -v mindlab-app-logs:/app/logs --add-host host.containers.internal:host-gateway mindlab-health-volumes:latest
    
    Write-Host "`nSystem restored successfully!" -ForegroundColor Green
    Write-Host "Application: http://localhost:8000" -ForegroundColor Cyan
    
} catch {
    Write-Host "Restore failed: `$(`$_.Exception.Message)" -ForegroundColor Red
}
"@
    
    $restoreScript | Out-File -FilePath "$backupDir\restore_system.ps1" -Encoding UTF8
    Write-Host "   ✓ Restore script created: $backupDir\restore_system.ps1" -ForegroundColor Green
    
    # 6. SUMMARY
    Write-Host "`n=== PROTECTION COMPLETE ===" -ForegroundColor Green
    Write-Host "Your current working system is fully protected:" -ForegroundColor White
    Write-Host "   📁 Backup Location: $backupDir" -ForegroundColor Cyan
    Write-Host "   💾 Database Backup: $((Get-Item $dbBackup).Length) bytes" -ForegroundColor White
    Write-Host "   📦 Application Code: Fully backed up" -ForegroundColor White
    Write-Host "   🔧 Restore Script: Available" -ForegroundColor White
    Write-Host ""
    Write-Host "🛡️  ISOLATION STRATEGY:" -ForegroundColor Yellow
    Write-Host "   • Current system runs on ports 8000 (app) and 5434 (db)" -ForegroundColor White
    Write-Host "   • New development will use DIFFERENT ports (8001+, 5435+)" -ForegroundColor White
    Write-Host "   • New containers will have DIFFERENT names (*-dev, *-test)" -ForegroundColor White
    Write-Host "   • New volumes will be SEPARATE (*-dev, *-test)" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ SAFE TO PROCEED with any new development!" -ForegroundColor Green
    Write-Host "   Your current system will remain completely untouched." -ForegroundColor White

} catch {
    Write-Host "`n❌ Protection setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Current system is still safe, but backup incomplete." -ForegroundColor Yellow
    exit 1
}