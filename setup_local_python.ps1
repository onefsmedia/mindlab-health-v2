# MindLab Health - Local Python Development Setup
# Runs the application locally using Python server instead of containers

Write-Host "=== MINDLAB HEALTH LOCAL PYTHON SETUP ===" -ForegroundColor Cyan
Write-Host "Setting up local development environment..." -ForegroundColor Yellow
Write-Host ""

try {
    # Check if we're in the right directory
    if (-not (Test-Path "07_main.py")) {
        throw "Not in MindLab Health directory. Please run from C:\Multi Agent\mindlab_health_v2"
    }

    # Step 1: Check Python installation
    Write-Host "1. Checking Python installation..." -ForegroundColor Green
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "   Found: $pythonVersion" -ForegroundColor White
    } catch {
        throw "Python not found. Please install Python 3.9+ first."
    }

    # Step 2: Create virtual environment if it doesn't exist
    Write-Host "`n2. Setting up Python virtual environment..." -ForegroundColor Green
    if (-not (Test-Path "venv")) {
        Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
    }
    Write-Host "   Virtual environment ready" -ForegroundColor White

    # Step 3: Activate virtual environment and install dependencies
    Write-Host "`n3. Installing dependencies..." -ForegroundColor Green
    Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
    
    # Activate virtual environment
    if (Test-Path "venv\Scripts\activate.ps1") {
        & "venv\Scripts\activate.ps1"
    } elseif (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    } else {
        # Try direct path execution
        $env:VIRTUAL_ENV = (Resolve-Path "venv").Path
        $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"
    }

    Write-Host "   Installing packages..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    Write-Host "   Dependencies installed successfully" -ForegroundColor White

    # Step 4: Check database connection
    Write-Host "`n4. Checking database connection..." -ForegroundColor Green
    
    # Check if containerized postgres is running
    $postgresRunning = $false
    try {
        podman ps | Select-String "postgres" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $postgresRunning = $true
            Write-Host "   Found running PostgreSQL container" -ForegroundColor White
        }
    } catch {
        # Podman not available or no containers
    }

    if (-not $postgresRunning) {
        Write-Host "   No PostgreSQL container found. Options:" -ForegroundColor Yellow
        Write-Host "   A. Start existing container: podman start postgres_volumes" -ForegroundColor White
        Write-Host "   B. Install PostgreSQL locally" -ForegroundColor White
        Write-Host "   C. Use SQLite for development (will create local.db)" -ForegroundColor White
        Write-Host ""
        $choice = Read-Host "   Choose option (A/B/C) or press Enter for SQLite"
        
        switch ($choice.ToUpper()) {
            "A" {
                Write-Host "   Attempting to start container..." -ForegroundColor Yellow
                podman start postgres_volumes
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "   PostgreSQL container started" -ForegroundColor Green
                } else {
                    Write-Host "   Failed to start container, falling back to SQLite" -ForegroundColor Yellow
                    $env:DATABASE_URL = "sqlite:///./local_mindlab.db"
                }
            }
            "B" {
                Write-Host "   Please install PostgreSQL locally and update DATABASE_URL" -ForegroundColor Yellow
                Write-Host "   For now, using SQLite..." -ForegroundColor White
                $env:DATABASE_URL = "sqlite:///./local_mindlab.db"
            }
            default {
                Write-Host "   Using SQLite database for local development" -ForegroundColor White
                $env:DATABASE_URL = "sqlite:///./local_mindlab.db"
            }
        }
    } else {
        Write-Host "   Using existing PostgreSQL container" -ForegroundColor White
        $env:DATABASE_URL = "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5434/mindlab_health"
    }

    # Step 5: Initialize database if needed
    Write-Host "`n5. Initializing database..." -ForegroundColor Green
    if (Test-Path "setup_database.py") {
        Write-Host "   Running database initialization..." -ForegroundColor Yellow
        python setup_database.py
    } else {
        Write-Host "   Database initialization script not found, tables will be created automatically" -ForegroundColor Yellow
    }

    # Step 6: Create startup script
    Write-Host "`n6. Creating local startup script..." -ForegroundColor Green
    $startupScript = @"
# MindLab Health Local Startup Script
Write-Host "Starting MindLab Health locally..." -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path "venv\Scripts\activate.ps1") {
    & "venv\Scripts\activate.ps1"
} else {
    `$env:VIRTUAL_ENV = (Resolve-Path "venv").Path
    `$env:PATH = "`$env:VIRTUAL_ENV\Scripts;`$env:PATH"
}

# Set database URL if not already set
if (-not `$env:DATABASE_URL) {
    if (Test-Path "local_mindlab.db") {
        `$env:DATABASE_URL = "sqlite:///./local_mindlab.db"
        Write-Host "Using SQLite database: local_mindlab.db" -ForegroundColor Yellow
    } else {
        `$env:DATABASE_URL = "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5434/mindlab_health"
        Write-Host "Using PostgreSQL database" -ForegroundColor Yellow
    }
}

Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start the FastAPI server
python -m uvicorn 07_main:app --host 0.0.0.0 --port 8000 --reload
"@

    $startupScript | Out-File -FilePath "start_local.ps1" -Encoding UTF8
    Write-Host "   Startup script created: start_local.ps1" -ForegroundColor White

    # Step 7: Ready to run
    Write-Host "`n=== LOCAL SETUP COMPLETE ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your MindLab Health application is ready to run locally!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To start the application:" -ForegroundColor Yellow
    Write-Host "   .\start_local.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually:" -ForegroundColor Yellow
    Write-Host "   1. Activate virtual environment: .\venv\Scripts\activate.ps1" -ForegroundColor White
    Write-Host "   2. Start server: python -m uvicorn 07_main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
    Write-Host ""
    Write-Host "Application will be available at:" -ForegroundColor Green
    Write-Host "   http://localhost:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Features available:" -ForegroundColor Yellow
    Write-Host "   - All healthcare modules (Patient Management, Health Records, etc.)" -ForegroundColor White
    Write-Host "   - RBAC system with role-based dashboards" -ForegroundColor White
    Write-Host "   - Modern glassmorphism UI" -ForegroundColor White
    Write-Host "   - Hot reload for development" -ForegroundColor White

} catch {
    Write-Host "`nSetup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Ensure you're in the MindLab Health directory" -ForegroundColor White
    Write-Host "2. Check Python installation: python --version" -ForegroundColor White
    Write-Host "3. Check network connectivity for package installation" -ForegroundColor White
    exit 1
}