"""
Initialize default system settings for MindLab Health platform
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path to import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SystemSettings

# Database configuration (same as main app)
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL or DATABASE_URL.strip() == "":
    DATABASE_URL = "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5433/mindlab_health"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_default_settings():
    """Initialize default system settings"""
    db = SessionLocal()
    
    try:
        # Check if settings already exist
        existing_count = db.query(SystemSettings).count()
        if existing_count > 0:
            print(f"Settings already exist ({existing_count} settings found). Skipping initialization.")
            return
        
        # Default settings to create
        default_settings = [
            # General Settings
            {
                "setting_key": "app.name",
                "setting_value": "MindLab Health",
                "setting_type": "string",
                "category": "general",
                "description": "Application name displayed to users",
                "is_public": True,
                "is_editable": True
            },
            {
                "setting_key": "app.version",
                "setting_value": "1.0.0",
                "setting_type": "string",
                "category": "general",
                "description": "Current application version",
                "is_public": True,
                "is_editable": False
            },
            {
                "setting_key": "app.timezone",
                "setting_value": "UTC",
                "setting_type": "string",
                "category": "general",
                "description": "Default timezone for the application",
                "is_public": False,
                "is_editable": True
            },
            
            # Email Settings
            {
                "setting_key": "email.smtp.host",
                "setting_value": "smtp.gmail.com",
                "setting_type": "string",
                "category": "email",
                "description": "SMTP server hostname for sending emails",
                "is_public": False,
                "is_editable": True
            },
            {
                "setting_key": "email.smtp.port",
                "setting_value": "587",
                "setting_type": "integer",
                "category": "email",
                "description": "SMTP server port",
                "is_public": False,
                "is_editable": True
            },
            {
                "setting_key": "email.from_address",
                "setting_value": "noreply@mindlabhealth.com",
                "setting_type": "string",
                "category": "email",
                "description": "Default sender email address",
                "is_public": False,
                "is_editable": True
            },
            {
                "setting_key": "email.notifications.enabled",
                "setting_value": "true",
                "setting_type": "boolean",
                "category": "email",
                "description": "Enable/disable email notifications",
                "is_public": False,
                "is_editable": True
            },
            
            # Appointment Settings
            {
                "setting_key": "appointments.booking_window_days",
                "setting_value": "30",
                "setting_type": "integer",
                "category": "appointments",
                "description": "How many days in advance appointments can be booked",
                "is_public": True,
                "is_editable": True
            },
            {
                "setting_key": "appointments.cancellation_hours",
                "setting_value": "24",
                "setting_type": "integer",
                "category": "appointments",
                "description": "Minimum hours before appointment to allow cancellation",
                "is_public": True,
                "is_editable": True
            },
            {
                "setting_key": "appointments.default_duration_minutes",
                "setting_value": "60",
                "setting_type": "integer",
                "category": "appointments",
                "description": "Default appointment duration in minutes",
                "is_public": False,
                "is_editable": True
            },
            
            # Security Settings
            {
                "setting_key": "security.session_timeout_minutes",
                "setting_value": "120",
                "setting_type": "integer",
                "category": "security",
                "description": "User session timeout in minutes",
                "is_public": False,
                "is_editable": True
            },
            {
                "setting_key": "security.password_min_length",
                "setting_value": "8",
                "setting_type": "integer",
                "category": "security",
                "description": "Minimum password length requirement",
                "is_public": True,
                "is_editable": True
            },
            {
                "setting_key": "security.max_login_attempts",
                "setting_value": "5",
                "setting_type": "integer",
                "category": "security",
                "description": "Maximum failed login attempts before account lockout",
                "is_public": False,
                "is_editable": True
            },
            
            # API Settings
            {
                "setting_key": "api.rate_limit_per_minute",
                "setting_value": "100",
                "setting_type": "integer",
                "category": "api",
                "description": "API rate limit requests per minute per user",
                "is_public": False,
                "is_editable": True
            },
            {
                "setting_key": "api.enable_swagger_ui",
                "setting_value": "true",
                "setting_type": "boolean",
                "category": "api",
                "description": "Enable Swagger UI documentation interface",
                "is_public": False,
                "is_editable": True
            },
            
            # Payment Settings
            {
                "setting_key": "payments.enabled",
                "setting_value": "false",
                "setting_type": "boolean",
                "category": "payments",
                "description": "Enable payment processing functionality",
                "is_public": True,
                "is_editable": True
            },
            {
                "setting_key": "payments.currency",
                "setting_value": "USD",
                "setting_type": "string",
                "category": "payments",
                "description": "Default currency for payments",
                "is_public": True,
                "is_editable": True
            }
        ]
        
        # Create settings
        created_count = 0
        for setting_data in default_settings:
            setting = SystemSettings(**setting_data)
            db.add(setting)
            created_count += 1
        
        db.commit()
        print(f"✅ Successfully created {created_count} default settings")
        
        # Display created settings
        print("\nCreated Settings:")
        print("-" * 80)
        for setting in db.query(SystemSettings).order_by(SystemSettings.category, SystemSettings.setting_key).all():
            print(f"{setting.category:15} | {setting.setting_key:30} | {setting.setting_value}")
        
    except Exception as e:
        print(f"❌ Error initializing settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing MindLab Health default settings...")
    init_default_settings()
    print("Done!")