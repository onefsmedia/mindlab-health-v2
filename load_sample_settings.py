"""
Add sample system settings for testing
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SystemSettings, Base
import local_config

def add_sample_settings():
    """Add sample system settings"""
    
    # Create database connection
    engine = create_engine(local_config.LOCAL_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    sample_settings = [
        # General Settings
        {
            'setting_key': 'app.name',
            'setting_value': 'MindLab Health System',
            'setting_type': 'string',
            'category': 'general',
            'description': 'Application display name',
            'is_public': True,
            'is_editable': True
        },
        {
            'setting_key': 'app.timezone',
            'setting_value': 'UTC',
            'setting_type': 'string',
            'category': 'general',
            'description': 'Default timezone for the application',
            'is_public': True,
            'is_editable': True
        },
        {
            'setting_key': 'app.max_upload_size_mb',
            'setting_value': '10',
            'setting_type': 'integer',
            'category': 'general',
            'description': 'Maximum file upload size in megabytes',
            'is_public': False,
            'is_editable': True
        },
        
        # Email Settings
        {
            'setting_key': 'email.smtp.host',
            'setting_value': 'smtp.gmail.com',
            'setting_type': 'string',
            'category': 'email',
            'description': 'SMTP server hostname',
            'is_public': False,
            'is_editable': True
        },
        {
            'setting_key': 'email.smtp.port',
            'setting_value': '587',
            'setting_type': 'integer',
            'category': 'email',
            'description': 'SMTP server port',
            'is_public': False,
            'is_editable': True
        },
        {
            'setting_key': 'email.from_address',
            'setting_value': 'noreply@mindlabhealth.com',
            'setting_type': 'string',
            'category': 'email',
            'description': 'Default sender email address',
            'is_public': False,
            'is_editable': True
        },
        {
            'setting_key': 'email.notifications_enabled',
            'setting_value': 'true',
            'setting_type': 'boolean',
            'category': 'email',
            'description': 'Enable/disable email notifications',
            'is_public': False,
            'is_editable': True
        },
        
        # Appointments Settings
        {
            'setting_key': 'appointments.booking_buffer_minutes',
            'setting_value': '30',
            'setting_type': 'integer',
            'category': 'appointments',
            'description': 'Minimum time buffer between appointments in minutes',
            'is_public': True,
            'is_editable': True
        },
        {
            'setting_key': 'appointments.max_advance_booking_days',
            'setting_value': '90',
            'setting_type': 'integer',
            'category': 'appointments',
            'description': 'Maximum days in advance for booking appointments',
            'is_public': True,
            'is_editable': True
        },
        {
            'setting_key': 'appointments.cancellation_hours',
            'setting_value': '24',
            'setting_type': 'integer',
            'category': 'appointments',
            'description': 'Minimum hours before appointment for cancellation',
            'is_public': True,
            'is_editable': True
        },
        
        # Payments Settings
        {
            'setting_key': 'payments.currency',
            'setting_value': 'USD',
            'setting_type': 'string',
            'category': 'payments',
            'description': 'Default currency for payments',
            'is_public': True,
            'is_editable': True
        },
        {
            'setting_key': 'payments.tax_rate',
            'setting_value': '0.07',
            'setting_type': 'string',
            'category': 'payments',
            'description': 'Tax rate (0.07 = 7%)',
            'is_public': False,
            'is_editable': True
        },
        
        # API Settings
        {
            'setting_key': 'api.rate_limit_per_minute',
            'setting_value': '60',
            'setting_type': 'integer',
            'category': 'api',
            'description': 'API requests allowed per minute',
            'is_public': False,
            'is_editable': True
        },
        
        # Security Settings
        {
            'setting_key': 'security.session_timeout_minutes',
            'setting_value': '30',
            'setting_type': 'integer',
            'category': 'security',
            'description': 'Session timeout in minutes',
            'is_public': False,
            'is_editable': True
        },
        {
            'setting_key': 'security.password_min_length',
            'setting_value': '8',
            'setting_type': 'integer',
            'category': 'security',
            'description': 'Minimum password length',
            'is_public': True,
            'is_editable': False
        },
        {
            'setting_key': 'security.require_2fa',
            'setting_value': 'false',
            'setting_type': 'boolean',
            'category': 'security',
            'description': 'Require two-factor authentication',
            'is_public': False,
            'is_editable': True
        }
    ]
    
    try:
        added_count = 0
        updated_count = 0
        
        for setting_data in sample_settings:
            # Check if setting already exists
            existing = session.query(SystemSettings).filter_by(
                setting_key=setting_data['setting_key']
            ).first()
            
            if existing:
                # Update existing setting
                for key, value in setting_data.items():
                    if key != 'setting_key':
                        setattr(existing, key, value)
                updated_count += 1
                print(f"  Updated: {setting_data['setting_key']}")
            else:
                # Create new setting
                new_setting = SystemSettings(**setting_data)
                session.add(new_setting)
                added_count += 1
                print(f"  Added: {setting_data['setting_key']}")
        
        # Commit all changes
        session.commit()
        
        print(f"\n✅ Sample settings loaded successfully!")
        print(f"   New settings: {added_count}")
        print(f"   Updated settings: {updated_count}")
        print(f"   Total processed: {added_count + updated_count}")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Failed to load sample settings: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Loading sample system settings...")
    print("="* 60)
    add_sample_settings()
