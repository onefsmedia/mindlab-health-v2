import local_config
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from models import Base
    from sqlalchemy import create_engine
except ImportError:
    # If models.py doesn't exist, we'll import from 07_main.py later
    Base = None
    from sqlalchemy import create_engine

import uvicorn

def init_database():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        if Base:
            Base.metadata.create_all(bind=engine)
            print("Database tables ensured")
        else:
            print("Skipping table creation - will be handled by main app")

if __name__ == "__main__":
    print("Starting MindLab Health locally...")
    print("Application will be available at: http://localhost:8000")
    print("Database: PostgreSQL (connecting to existing container)")
    print("Hot reload: Enabled")
    print("")
    
    init_database()
    
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import the actual app module
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", "07_main.py")
    if spec and spec.loader:
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        uvicorn.run(
            main_module.app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    else:
        print("Error: Could not load 07_main.py")
