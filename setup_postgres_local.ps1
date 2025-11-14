# Setup Local PostgreSQL for MindLab Health Python Development
# This script sets up PostgreSQL to work with the local Python server

Write-Host "=== POSTGRESQL LOCAL SETUP ===" -ForegroundColor Cyan
Write-Host "Setting up PostgreSQL for local Python development" -ForegroundColor Yellow
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "1. Checking PostgreSQL installation..." -ForegroundColor Green

$postgresService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($postgresService) {
    Write-Host "   PostgreSQL service found: $($postgresService.Name)" -ForegroundColor Green
    Write-Host "   Status: $($postgresService.Status)" -ForegroundColor Gray
} else {
    Write-Host "   PostgreSQL service not found" -ForegroundColor Yellow
    Write-Host "   Checking for PostgreSQL in common locations..." -ForegroundColor Gray
    
    $commonPaths = @(
        "C:\Program Files\PostgreSQL\*\bin\postgres.exe",
        "C:\Program Files (x86)\PostgreSQL\*\bin\postgres.exe",
        "C:\PostgreSQL\*\bin\postgres.exe"
    )
    
    $postgresFound = $false
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            Write-Host "   Found PostgreSQL at: $path" -ForegroundColor Green
            $postgresFound = $true
            break
        }
    }
    
    if (-not $postgresFound) {
        Write-Host "   PostgreSQL not found. Options:" -ForegroundColor Red
        Write-Host "   1. Install PostgreSQL from https://www.postgresql.org/download/windows/" -ForegroundColor White
        Write-Host "   2. Use PostgreSQL in Docker/Podman (but you want pure Python)" -ForegroundColor White
        Write-Host "   3. Switch back to SQLite for local development" -ForegroundColor White
        Write-Host ""
        $choice = Read-Host "Would you like to continue with SQLite instead? (y/n)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            Write-Host "   Configuring for SQLite..." -ForegroundColor Yellow
            
            # Update local config to use SQLite
            $sqliteConfig = @"
import os
# SQLite configuration for local development
LOCAL_DATABASE_URL = "sqlite:///./mindlab_health_local.db"
os.environ["DATABASE_URL"] = LOCAL_DATABASE_URL
print(f"Using local database: {LOCAL_DATABASE_URL}")
"@
            $sqliteConfig | Out-File -FilePath "local_config.py" -Encoding UTF8
            Write-Host "   Updated local_config.py to use SQLite" -ForegroundColor Green
            exit 0
        } else {
            Write-Host "   Please install PostgreSQL and run this script again" -ForegroundColor Red
            exit 1
        }
    }
}

# Check if we can connect to PostgreSQL
Write-Host "`n2. Testing PostgreSQL connection..." -ForegroundColor Green

$testConnection = $false
$ports = @(5432, 5433, 5434, 5435)

foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "   PostgreSQL found on port $port" -ForegroundColor Green
            $pgPort = $port
            $testConnection = $true
            break
        }
    } catch {
        # Continue to next port
    }
}

if (-not $testConnection) {
    Write-Host "   No PostgreSQL instance responding on common ports" -ForegroundColor Yellow
    Write-Host "   You may need to start PostgreSQL service" -ForegroundColor White
    Write-Host ""
    Write-Host "   Common commands to start PostgreSQL:" -ForegroundColor Gray
    Write-Host "   - net start postgresql-x64-[version]" -ForegroundColor White
    Write-Host "   - sc start postgresql-x64-[version]" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Would you like to continue with SQLite instead? (y/n)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        Write-Host "   Configuring for SQLite..." -ForegroundColor Yellow
        
        # Update local config to use SQLite
        $sqliteConfig = @"
import os
# SQLite configuration for local development  
LOCAL_DATABASE_URL = "sqlite:///./mindlab_health_local.db"
os.environ["DATABASE_URL"] = LOCAL_DATABASE_URL
print(f"Using local database: {LOCAL_DATABASE_URL}")
"@
        $sqliteConfig | Out-File -FilePath "local_config.py" -Encoding UTF8
        Write-Host "   Updated local_config.py to use SQLite" -ForegroundColor Green
        exit 0
    } else {
        exit 1
    }
} else {
    Write-Host "   Using PostgreSQL on port $pgPort" -ForegroundColor Green
}

# Create database and user
Write-Host "`n3. Setting up database..." -ForegroundColor Green

$dbName = "mindlab_health_local"
$dbUser = "mindlab_local"
$dbPassword = "mindlab123"

# Update local config for PostgreSQL
$postgresConfig = @"
import os
# PostgreSQL configuration for local development
LOCAL_DATABASE_URL = "postgresql://${dbUser}:${dbPassword}@localhost:${pgPort}/${dbName}"
os.environ["DATABASE_URL"] = LOCAL_DATABASE_URL
print(f"Using local database: {LOCAL_DATABASE_URL}")
"@

$postgresConfig | Out-File -FilePath "local_config.py" -Encoding UTF8
Write-Host "   Updated local_config.py for PostgreSQL" -ForegroundColor Green

# Create SQL commands to set up database
$setupSQL = @"
-- Create database and user for MindLab Health local development
CREATE DATABASE ${dbName};
CREATE USER ${dbUser} WITH PASSWORD '${dbPassword}';
GRANT ALL PRIVILEGES ON DATABASE ${dbName} TO ${dbUser};
ALTER USER ${dbUser} CREATEDB;
"@

$setupSQL | Out-File -FilePath "setup_db.sql" -Encoding UTF8

Write-Host "`n4. Database setup files created:" -ForegroundColor Green
Write-Host "   - local_config.py (updated for PostgreSQL)" -ForegroundColor Gray
Write-Host "   - setup_db.sql (database creation script)" -ForegroundColor Gray

Write-Host "`n5. Next steps:" -ForegroundColor Yellow
Write-Host "   1. Connect to PostgreSQL as superuser:" -ForegroundColor White
Write-Host "      psql -U postgres -h localhost -p $pgPort" -ForegroundColor Gray
Write-Host "   2. Run the setup script:" -ForegroundColor White  
Write-Host "      \i setup_db.sql" -ForegroundColor Gray
Write-Host "   3. Start your Python application:" -ForegroundColor White
Write-Host "      python start_local.py" -ForegroundColor Gray

Write-Host "`n=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host "Local PostgreSQL configuration ready for Python development" -ForegroundColor Cyan