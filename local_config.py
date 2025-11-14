import os

# PostgreSQL configuration for standalone local installation
# NO containers - pure local PostgreSQL setup

# Local PostgreSQL settings
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mindlab_health_local"
DB_USER = "mindlab_admin" 
DB_PASSWORD = "MindLab2024!Secure"

# PostgreSQL connection string for local installation
LOCAL_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Using local PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")
os.environ["DATABASE_URL"] = LOCAL_DATABASE_URL
