# MindLab Health Local Python Setup (Clean)
# Run the application locally with Python (no containers)

Write-Host "=== MINDLAB HEALTH - LOCAL PYTHON SETUP ===" -ForegroundColor Cyan
Write-Host "Setting up MindLab Health to run with Python server only" -ForegroundColor Yellow
Write-Host ""

# Check current location
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Gray

# 1. Create virtual environment
Write-Host "`n1. Creating Python virtual environment..." -ForegroundColor Green
if (Test-Path "venv") {
    Write-Host "   Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   Virtual environment created" -ForegroundColor Green
}

# 2. Install dependencies in virtual environment
Write-Host "`n2. Installing dependencies..." -ForegroundColor Green
& "venv\Scripts\python.exe" -m pip install --upgrade pip
& "venv\Scripts\pip.exe" install -r requirements.txt
Write-Host "   Dependencies installed" -ForegroundColor Green

# 3. Create local SQLite configuration
Write-Host "`n3. Configuring for local SQLite database..." -ForegroundColor Green

# Create a local configuration file
$localConfig = @"
import os
LOCAL_DATABASE_URL = "sqlite:///./mindlab_health_local.db"
os.environ["DATABASE_URL"] = LOCAL_DATABASE_URL
print(f"Using local database: {LOCAL_DATABASE_URL}")
"@

$localConfig | Out-File -FilePath "local_config.py" -Encoding UTF8
Write-Host "   Local configuration created" -ForegroundColor Green

# 4. Create startup script
Write-Host "`n4. Creating startup script..." -ForegroundColor Green

$startupScript = @'
import local_config
import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import Base
from sqlalchemy import create_engine
import uvicorn

def init_database():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database tables ensured")

if __name__ == "__main__":
    print("Starting MindLab Health locally...")
    print("Application will be available at: http://localhost:8080")
    print("Database: SQLite (local file)")
    print("Hot reload: Enabled")
    print("")
    
    init_database()
    
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import the actual app module
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", "07_main.py")
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    
    uvicorn.run(
        main_module.app,
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
'@

$startupScript | Out-File -FilePath "start_local.py" -Encoding UTF8
Write-Host "   Startup script created (start_local.py)" -ForegroundColor Green

Write-Host "`n=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start MindLab Health:" -ForegroundColor Cyan
Write-Host "   1. Activate virtual environment: venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   2. Start the server: python start_local.py" -ForegroundColor White
Write-Host "   3. Open browser: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Files created:" -ForegroundColor Yellow
Write-Host "   - venv/              (Python virtual environment)" -ForegroundColor Gray
Write-Host "   - local_config.py    (SQLite configuration)" -ForegroundColor Gray  
Write-Host "   - start_local.py     (Application startup script)" -ForegroundColor Gray
Write-Host ""
Write-Host "This setup:" -ForegroundColor Green
Write-Host "   - Uses pure Python (no podman/containers)" -ForegroundColor White
Write-Host "   - SQLite database (no external DB required)" -ForegroundColor White
Write-Host "   - Port 8080 (won't conflict with anything else)" -ForegroundColor White