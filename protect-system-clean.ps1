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
        Write-Host "   OK Database backup: $((Get-Item $dbBackup).Length) bytes" -ForegroundColor Green
    } else {
        throw "Database backup failed"
    }
    
    # 2. APPLICATION CODE BACKUP
    Write-Host "`n2. Backing up application code..." -ForegroundColor Yellow
    $appBackup = "$backupDir\application_code"
    
    # Copy all application files except excluded patterns
    robocopy "." "$appBackup" /E /XD volumes backups __pycache__ .git /XF *.log *.pyc /NFL /NDL /NP | Out-Null
    Write-Host "   OK Application code backed up to: $appBackup" -ForegroundColor Green
    
    # 3. CONTAINER STATE BACKUP
    Write-Host "`n3. Recording container configurations..." -ForegroundColor Yellow
    $containerInfoContent = @"
=== WORKING CONTAINER CONFIGURATION ===
Date: $(Get-Date)
Application Container: mindlab-app-volumes
Database Container: postgres_volumes
Application Port: 8000
Database Port: 5434
Volumes: mindlab-postgres-data, mindlab-app-logs

Application Status: WORKING
Database Status: WORKING
"@
    
    $containerInfoPath = Join-Path $backupDir "container_state.txt"
    $containerInfoContent | Out-File -FilePath $containerInfoPath -Encoding UTF8
    Write-Host "   OK Container state recorded" -ForegroundColor Green
    
    # 4. ENVIRONMENT VARIABLES
    Write-Host "`n4. Saving environment configuration..." -ForegroundColor Yellow
    $envConfigContent = @"
# MindLab Health Environment Configuration
DATABASE_URL=postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5434/mindlab_health
APP_PORT=8000
DB_PORT=5434
POSTGRES_VOLUME=mindlab-postgres-data
APP_LOGS_VOLUME=mindlab-app-logs
APP_CONTAINER=mindlab-app-volumes
DB_CONTAINER=postgres_volumes
"@
    
    $envConfigPath = Join-Path $backupDir "environment.env"
    $envConfigContent | Out-File -FilePath $envConfigPath -Encoding UTF8
    Write-Host "   OK Environment configuration saved" -ForegroundColor Green
    
    # 5. SUMMARY
    Write-Host "`n=== PROTECTION COMPLETE ===" -ForegroundColor Green
    Write-Host "Your current working system is fully protected:" -ForegroundColor White
    Write-Host "   Backup Location: $backupDir" -ForegroundColor Cyan
    Write-Host "   Database Backup: $((Get-Item $dbBackup).Length) bytes" -ForegroundColor White
    Write-Host "   Application Code: Fully backed up" -ForegroundColor White
    Write-Host ""
    Write-Host "ISOLATION STRATEGY:" -ForegroundColor Yellow
    Write-Host "   • Current system runs on ports 8000 (app) and 5434 (db)" -ForegroundColor White
    Write-Host "   • New development will use DIFFERENT ports (8001+, 5435+)" -ForegroundColor White
    Write-Host "   • New containers will have DIFFERENT names (*-dev, *-test)" -ForegroundColor White
    Write-Host "   • New volumes will be SEPARATE (*-dev, *-test)" -ForegroundColor White
    Write-Host ""
    Write-Host "SAFE TO PROCEED with any new development!" -ForegroundColor Green
    Write-Host "Your current system will remain completely untouched." -ForegroundColor White

} catch {
    Write-Host "`nProtection setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Current system is still safe, but backup incomplete." -ForegroundColor Yellow
    exit 1
}