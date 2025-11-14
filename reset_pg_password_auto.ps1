# Automated PostgreSQL Password Reset
# Sets password to: postgres

Write-Host "Resetting PostgreSQL password..." -ForegroundColor Cyan

$pgDataDir = "C:\Program Files\PostgreSQL\16\data"
$pgHbaFile = "$pgDataDir\pg_hba.conf"

try {
    # Step 1: Backup pg_hba.conf
    Write-Host "1. Backing up pg_hba.conf..." -ForegroundColor Yellow
    Copy-Item $pgHbaFile "$pgHbaFile.backup_$(Get-Date -Format 'yyyyMMddHHmmss')" -Force
    
    # Step 2: Modify pg_hba.conf to trust authentication
    Write-Host "2. Modifying pg_hba.conf for trust authentication..." -ForegroundColor Yellow
    $content = Get-Content $pgHbaFile -Raw
    $originalContent = $content
    $content = $content -replace 'scram-sha-256', 'trust'
    $content = $content -replace 'md5', 'trust'
    Set-Content $pgHbaFile $content -Force
    
    # Step 3: Restart PostgreSQL
    Write-Host "3. Restarting PostgreSQL service..." -ForegroundColor Yellow
    Restart-Service postgresql-x64-16 -Force
    Start-Sleep -Seconds 8
    
    # Step 4: Reset password
    Write-Host "4. Setting new password to 'postgres'..." -ForegroundColor Yellow
    $env:PGPASSWORD = ''
    $result = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Password changed successfully!" -ForegroundColor Green
    } else {
        Write-Host "   Warning: $result" -ForegroundColor Yellow
    }
    
    # Step 5: Restore original pg_hba.conf
    Write-Host "5. Restoring pg_hba.conf..." -ForegroundColor Yellow
    Set-Content $pgHbaFile $originalContent -Force
    
    # Step 6: Restart PostgreSQL again
    Write-Host "6. Restarting PostgreSQL with secure authentication..." -ForegroundColor Yellow
    Restart-Service postgresql-x64-16 -Force
    Start-Sleep -Seconds 8
    
    # Step 7: Test connection
    Write-Host "7. Testing new password..." -ForegroundColor Yellow
    $env:PGPASSWORD = 'postgres'
    $testResult = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "SELECT 'Password reset successful!' as status;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nSUCCESS!" -ForegroundColor Green
        Write-Host "==========" -ForegroundColor Green
        Write-Host "PostgreSQL password has been reset to: postgres" -ForegroundColor Cyan
        Write-Host "`nCredentials:" -ForegroundColor Yellow
        Write-Host "  Username: postgres" -ForegroundColor White
        Write-Host "  Password: postgres" -ForegroundColor White
        Write-Host "  Host: localhost" -ForegroundColor White
        Write-Host "  Port: 5432" -ForegroundColor White
        Write-Host "`nTest result:" -ForegroundColor Yellow
        Write-Host $testResult
    } else {
        Write-Host "`nPassword may have been reset, but connection test failed." -ForegroundColor Yellow
        Write-Host "Error: $testResult" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Attempting to restore pg_hba.conf..." -ForegroundColor Yellow
    
    # Try to restore original file
    if ($originalContent) {
        Set-Content $pgHbaFile $originalContent -Force
        Restart-Service postgresql-x64-16 -Force
    }
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")