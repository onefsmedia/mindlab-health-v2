# PostgreSQL Manual Installation Guide for MindLab Health
Write-Host "MindLab Health - PostgreSQL Manual Installation Guide" -ForegroundColor Cyan
Write-Host "Setting up PostgreSQL locally (NO podman/containers)" -ForegroundColor Yellow
Write-Host ""

Write-Host "STEP-BY-STEP INSTALLATION:" -ForegroundColor Green
Write-Host "=========================="

Write-Host "`n1. Download PostgreSQL:" -ForegroundColor Cyan
Write-Host "   • Open your browser and go to:" -ForegroundColor White
Write-Host "     https://www.enterprisedb.com/downloads/postgres-postgresql-downloads" -ForegroundColor Yellow
Write-Host "   • Click 'Download' for PostgreSQL 16.x (Windows x86-64)" -ForegroundColor White
Write-Host "   • Save the installer file" -ForegroundColor White

Write-Host "`n2. Run the Installer:" -ForegroundColor Cyan
Write-Host "   • Double-click the downloaded .exe file" -ForegroundColor White
Write-Host "   • Click 'Next' through the welcome screens" -ForegroundColor White
Write-Host "   • IMPORTANT: Use these settings:" -ForegroundColor Red

Write-Host "`n   Installation Settings:" -ForegroundColor Yellow
Write-Host "   - Port: 5432 (keep default)" -ForegroundColor Green
Write-Host "   - Superuser password: SET A STRONG PASSWORD" -ForegroundColor Green
Write-Host "   - Install directory: Keep default" -ForegroundColor Green
Write-Host "   - Components: Install ALL (pgAdmin, Stack Builder, etc.)" -ForegroundColor Green

Write-Host "`n3. Password Setup:" -ForegroundColor Cyan
Write-Host "   • When asked for 'postgres' user password:" -ForegroundColor White
Write-Host "   • Choose a STRONG password (write it down!)" -ForegroundColor Red
Write-Host "   • You'll need this password for database setup" -ForegroundColor Yellow

Write-Host "`n4. Complete Installation:" -ForegroundColor Cyan
Write-Host "   • Let the installer finish completely" -ForegroundColor White
Write-Host "   • Don't launch Stack Builder (uncheck if asked)" -ForegroundColor White
Write-Host "   • Click 'Finish'" -ForegroundColor White

Write-Host "`n5. Test Installation:" -ForegroundColor Cyan
Write-Host "   • Open Command Prompt or PowerShell" -ForegroundColor White
Write-Host "   • Type: psql --version" -ForegroundColor Yellow
Write-Host "   • You should see PostgreSQL version information" -ForegroundColor White

Write-Host "`n=================================================="
Write-Host "AFTER INSTALLATION IS COMPLETE:" -ForegroundColor Green
Write-Host "=================================================="

Write-Host "`nRun the database setup script:" -ForegroundColor Yellow
Write-Host "   python setup_standalone_postgres.py" -ForegroundColor Cyan

Write-Host "`nStart MindLab Health:" -ForegroundColor Yellow
Write-Host "   python start_local.py" -ForegroundColor Cyan

Write-Host "`nAccess the application:" -ForegroundColor Yellow
Write-Host "   http://localhost:8081" -ForegroundColor Cyan

Write-Host "`n=================================================="
Write-Host ""
Write-Host "TROUBLESHOOTING TIPS:" -ForegroundColor Yellow
Write-Host "• If 'psql' command not found: Restart your terminal" -ForegroundColor White
Write-Host "• If port 5432 is busy: Choose different port during install" -ForegroundColor White
Write-Host "• If connection fails: Check Windows Firewall settings" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Press Enter after PostgreSQL installation is complete"

# After installation, test if PostgreSQL is available
Write-Host "`nTesting PostgreSQL installation..." -ForegroundColor Green

try {
    $pgVersion = psql --version
    Write-Host "SUCCESS! PostgreSQL found: $pgVersion" -ForegroundColor Green
    
    Write-Host "`nGreat! PostgreSQL is installed." -ForegroundColor Green
    Write-Host "Now running database setup script..." -ForegroundColor Yellow
    
    # Run the database setup
    python setup_standalone_postgres.py
    
} catch {
    Write-Host "PostgreSQL not found in PATH" -ForegroundColor Red
    Write-Host "Please restart your terminal and try again" -ForegroundColor Yellow
    Write-Host "Then run: python setup_standalone_postgres.py" -ForegroundColor Cyan
}

Write-Host "`nManual installation guide complete!" -ForegroundColor Green