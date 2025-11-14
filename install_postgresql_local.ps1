# Quick PostgreSQL Local Setup
# This will try to install PostgreSQL using Windows package managers

Write-Host "🏥 MindLab Health - PostgreSQL Local Setup" -ForegroundColor Cyan
Write-Host "NO containers - Installing PostgreSQL locally" -ForegroundColor Yellow
Write-Host ""

# Method 1: Try winget (Windows Package Manager)
Write-Host "📦 Trying Windows Package Manager (winget)..." -ForegroundColor Green
try {
    $wingetVersion = winget --version
    Write-Host "   ✅ winget available: $wingetVersion" -ForegroundColor Green
    
    Write-Host "   Installing PostgreSQL via winget..." -ForegroundColor Yellow
    winget install PostgreSQL.PostgreSQL --silent --accept-package-agreements --accept-source-agreements
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ PostgreSQL installed successfully!" -ForegroundColor Green
        $pgInstalled = $true
    } else {
        Write-Host "   ⚠️  winget installation failed" -ForegroundColor Yellow
        $pgInstalled = $false
    }
} catch {
    Write-Host "   ❌ winget not available" -ForegroundColor Red
    $pgInstalled = $false
}

# Method 2: Try Chocolatey (if winget failed)
if (-not $pgInstalled) {
    Write-Host "`n📦 Trying Chocolatey..." -ForegroundColor Green
    try {
        $chocoVersion = choco --version
        Write-Host "   ✅ Chocolatey available: $chocoVersion" -ForegroundColor Green
        
        Write-Host "   Installing PostgreSQL via Chocolatey..." -ForegroundColor Yellow
        # Run as administrator if possible
        Start-Process -FilePath "choco" -ArgumentList "install postgresql --confirm -y" -Verb RunAs -Wait
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ PostgreSQL installed successfully!" -ForegroundColor Green
            $pgInstalled = $true
        } else {
            Write-Host "   ⚠️  Chocolatey installation failed" -ForegroundColor Yellow
            $pgInstalled = $false
        }
    } catch {
        Write-Host "   ❌ Chocolatey not available" -ForegroundColor Red
        $pgInstalled = $false
    }
}

# Method 3: Manual download
if (-not $pgInstalled) {
    Write-Host "`n📥 Manual Installation Required" -ForegroundColor Yellow
    Write-Host "=" * 50
    Write-Host "Automatic installation failed. Please install manually:"
    Write-Host ""
    Write-Host "1. 🌐 Open: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads" -ForegroundColor Cyan
    Write-Host "2. 📱 Download PostgreSQL 16.x for Windows" -ForegroundColor Cyan
    Write-Host "3. 🚀 Run the installer with these settings:" -ForegroundColor Cyan
    Write-Host "   - Port: 5432 (default)" -ForegroundColor White
    Write-Host "   - Password: Set a password for 'postgres' user" -ForegroundColor White
    Write-Host "   - Install all components" -ForegroundColor White
    Write-Host "4. ✅ After installation, restart this script" -ForegroundColor Cyan
    Write-Host ""
    
    $continue = Read-Host "Press Enter after installing PostgreSQL manually, or 'q' to quit"
    if ($continue -eq 'q') {
        exit
    }
}

# Test PostgreSQL installation
Write-Host "`n🔍 Testing PostgreSQL installation..." -ForegroundColor Green
try {
    $pgVersion = psql --version
    Write-Host "   ✅ PostgreSQL found: $pgVersion" -ForegroundColor Green
    $pgAvailable = $true
} catch {
    Write-Host "   ❌ PostgreSQL not found in PATH" -ForegroundColor Red
    Write-Host "   💡 You may need to restart your terminal or add PostgreSQL to PATH" -ForegroundColor Yellow
    $pgAvailable = $false
}

# Setup database if PostgreSQL is available
if ($pgAvailable) {
    Write-Host "`n📊 Setting up MindLab Health database..." -ForegroundColor Green
    
    # Get postgres password
    $postgresPassword = Read-Host "Enter the password you set for 'postgres' user during installation" -AsSecureString
    $postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))
    
    # Set environment variable for psql
    $env:PGPASSWORD = $postgresPasswordPlain
    
    try {
        # Create database
        Write-Host "   Creating database 'mindlab_health_local'..." -ForegroundColor Yellow
        psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE mindlab_health_local;" 2>$null
        
        # Create user
        Write-Host "   Creating user 'mindlab_admin'..." -ForegroundColor Yellow
        psql -U postgres -h localhost -p 5432 -c "CREATE USER mindlab_admin WITH PASSWORD 'MindLab2024!Secure';" 2>$null
        
        # Grant privileges
        Write-Host "   Granting privileges..." -ForegroundColor Yellow
        psql -U postgres -h localhost -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE mindlab_health_local TO mindlab_admin;" 2>$null
        
        # Test connection as mindlab_admin
        $env:PGPASSWORD = "MindLab2024!Secure"
        $testResult = psql -U mindlab_admin -h localhost -p 5432 -d mindlab_health_local -c "SELECT version();" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Database setup complete!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🎉 SUCCESS! PostgreSQL is ready for MindLab Health" -ForegroundColor Green
            Write-Host "=" * 50
            Write-Host "Database: mindlab_health_local" -ForegroundColor White
            Write-Host "User: mindlab_admin" -ForegroundColor White
            Write-Host "Host: localhost:5432" -ForegroundColor White
            Write-Host ""
            Write-Host "▶️  Ready to run: python start_local.py" -ForegroundColor Cyan
        } else {
            Write-Host "   ⚠️  Database setup had issues, but PostgreSQL is installed" -ForegroundColor Yellow
            Write-Host "   💡 You may need to run: python setup_standalone_postgres.py" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "   ⚠️  Error during database setup: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   💡 PostgreSQL is installed, run: python setup_standalone_postgres.py" -ForegroundColor Yellow
    }
    
    # Clear password from environment
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    
} else {
    Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Install PostgreSQL manually (see instructions above)"
    Write-Host "2. Restart your terminal"
    Write-Host "3. Run this script again"
}

Write-Host "Setup complete!" -ForegroundColor Green