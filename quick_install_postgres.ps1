# MindLab Health - PostgreSQL Local Setup
Write-Host "Installing PostgreSQL locally (NO containers)" -ForegroundColor Cyan

# Try winget first
Write-Host "Trying winget..." -ForegroundColor Yellow
try {
    winget install PostgreSQL.PostgreSQL
    Write-Host "PostgreSQL installation initiated via winget" -ForegroundColor Green
} catch {
    Write-Host "winget failed, trying manual approach..." -ForegroundColor Yellow
    
    Write-Host "Manual Installation Required:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads"
    Write-Host "2. Download PostgreSQL 16 for Windows"
    Write-Host "3. Install with default settings (port 5432)"
    Write-Host "4. Set password for 'postgres' user"
    Write-Host "5. After installation, run: python setup_standalone_postgres.py"
}

Write-Host "Installation process started..." -ForegroundColor Green