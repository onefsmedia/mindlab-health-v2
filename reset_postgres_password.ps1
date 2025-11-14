# Reset PostgreSQL Password for Local Installation
# Run this as Administrator

Write-Host "PostgreSQL Password Reset Tool" -ForegroundColor Cyan
Write-Host "================================" 
Write-Host ""

Write-Host "The local PostgreSQL password is unknown." -ForegroundColor Yellow
Write-Host "Here are your options:" -ForegroundColor Yellow
Write-Host ""

Write-Host "OPTION 1: Reset the postgres user password" -ForegroundColor Green
Write-Host "-------------------------------------------"
Write-Host "1. Stop PostgreSQL service:"
Write-Host "   Stop-Service postgresql-x64-16" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Edit pg_hba.conf to allow trust authentication temporarily:"
Write-Host "   File location: C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
Write-Host "   Change 'md5' or 'scram-sha-256' to 'trust' for local connections"
Write-Host ""
Write-Host "3. Restart PostgreSQL service:"
Write-Host "   Start-Service postgresql-x64-16" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Connect without password and reset:"
Write-Host "   & 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U postgres -d postgres" -ForegroundColor Cyan
Write-Host "   Then run: ALTER USER postgres PASSWORD 'postgres';" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Revert pg_hba.conf back to 'scram-sha-256'"
Write-Host "6. Restart service again"
Write-Host ""

Write-Host "OPTION 2: Use pgAdmin to reset password" -ForegroundColor Green
Write-Host "----------------------------------------"
Write-Host "1. Open pgAdmin (installed with PostgreSQL)"
Write-Host "2. Right-click on postgres server"
Write-Host "3. Properties > Definition > Password"
Write-Host "4. Set new password"
Write-Host ""

Write-Host "OPTION 3: Let me try to automatically reset it" -ForegroundColor Green
Write-Host "-----------------------------------------------"
Write-Host ""

$choice = Read-Host "Try automatic reset? (y/n)"

if ($choice -eq 'y') {
    Write-Host "`nAttempting automatic password reset..." -ForegroundColor Yellow
    
    # Backup current pg_hba.conf
    $pgDataDir = "C:\Program Files\PostgreSQL\16\data"
    $pgHbaFile = "$pgDataDir\pg_hba.conf"
    
    if (Test-Path $pgHbaFile) {
        Write-Host "Backing up pg_hba.conf..." -ForegroundColor Yellow
        Copy-Item $pgHbaFile "$pgHbaFile.backup"
        
        # Read and modify pg_hba.conf
        $content = Get-Content $pgHbaFile
        $newContent = $content -replace 'scram-sha-256', 'trust' -replace 'md5', 'trust'
        Set-Content $pgHbaFile $newContent
        
        Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow
        Restart-Service postgresql-x64-16
        
        Start-Sleep -Seconds 5
        
        Write-Host "Setting new password to 'postgres'..." -ForegroundColor Yellow
        $env:PGPASSWORD = ''
        & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres PASSWORD 'postgres';"
        
        # Restore original pg_hba.conf
        Write-Host "Restoring pg_hba.conf..." -ForegroundColor Yellow
        Copy-Item "$pgHbaFile.backup" $pgHbaFile -Force
        
        Write-Host "Restarting PostgreSQL service..." -ForegroundColor Yellow
        Restart-Service postgresql-x64-16
        
        Start-Sleep -Seconds 5
        
        Write-Host "`nPassword reset complete!" -ForegroundColor Green
        Write-Host "New password: postgres" -ForegroundColor Cyan
        
        # Test connection
        Write-Host "`nTesting connection..." -ForegroundColor Yellow
        $env:PGPASSWORD = 'postgres'
        & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nSUCCESS! Password is now: postgres" -ForegroundColor Green
        }
        
    } else {
        Write-Host "Could not find pg_hba.conf at expected location" -ForegroundColor Red
        Write-Host "Please use Option 1 or 2 manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nPlease follow Option 1 or 2 manually to reset the password." -ForegroundColor Yellow
}

Write-Host "`nRecommended Password: postgres" -ForegroundColor Cyan
Write-Host "After reset, your PostgreSQL credentials will be:" -ForegroundColor Yellow
Write-Host "  Username: postgres" -ForegroundColor White
Write-Host "  Password: postgres" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White