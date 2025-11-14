"""
MindLab Health - SQLAlchemy Models
==================================
Database models for users, appointments, messages, and role-based permissions
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UserRole(enum.Enum):
    """User role enumeration"""
    patient = "patient"
    therapist = "therapist"
    admin = "admin"
    health_coach = "health_coach"
    partner = "partner"
    physician = "physician"

class Permission(Base):
    """Permission model for role-based access control"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")

class RolePermission(Base):
    """Role-Permission junction table for RBAC"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate role-permission pairs
    __table_args__ = (UniqueConstraint('role', 'permission_id', name='unique_role_permission'),)
    
    # Relationships
    permission = relationship("Permission", back_populates="role_permissions")

class AppointmentStatus(enum.Enum):
    """Appointment status enumeration"""
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="patient")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments_as_patient = relationship(
        "Appointment",
        foreign_keys="Appointment.user_id",
        back_populates="patient"
    )
    appointments_as_therapist = relationship(
        "Appointment",
        foreign_keys="Appointment.therapist_id",
        back_populates="therapist"
    )
    sent_messages = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender"
    )
    received_messages = relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        back_populates="recipient"
    )
    
    def has_permission(self, permission_name, db_session):
        """Check if user has a specific permission"""
        # Admin has all permissions
        if str(self.role) == "admin":
            return True
            
        # Query for role-based permissions
        result = db_session.query(Permission.id).join(RolePermission).filter(
            RolePermission.role == str(self.role),
            Permission.name == permission_name
        ).first()
        
        return result is not None
    
    def get_permissions(self, db_session):
        """Get all permissions for this user's role"""
        # Admin gets all permissions
        if str(self.role) == "admin":
            permissions = db_session.query(Permission.name).all()
            return [perm[0] for perm in permissions]
            
        # Get role-specific permissions
        permissions = db_session.query(Permission.name).join(RolePermission).filter(
            RolePermission.role == str(self.role)
        ).all()
        
        return [perm[0] for perm in permissions]
    
    def can_access_module(self, module_name, db_session):
        """Check if user can access a specific module"""
        # Admin can access everything
        if str(self.role) == "admin":
            return True
            
        # Check if user has any permission for this module
        result = db_session.query(Permission.id).join(RolePermission).filter(
            RolePermission.role == str(self.role),
            Permission.module == module_name
        ).first()
        
        return result is not None

class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60, nullable=False)  # Default 1 hour
    status = Column(String(20), nullable=False, default="scheduled")
    notes = Column(Text)
    
    # Google Calendar Integration
    google_calendar_event_id = Column(String(255), nullable=True, index=True)
    sync_with_calendar = Column(Boolean, default=True, nullable=False)
    last_calendar_sync = Column(DateTime, nullable=True)
    
    # Appointment Details
    appointment_type = Column(String(50), default="consultation")  # consultation, therapy, follow-up, etc.
    location = Column(String(255), nullable=True)  # office, online, phone
    reminder_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="appointments_as_patient"
    )
    therapist = relationship(
        "User",
        foreign_keys=[therapist_id],
        back_populates="appointments_as_therapist"
    )

class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )
    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="received_messages"
    )

class Meal(Base):
    """Meal model for meal tracking"""
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    ingredients = Column(Text)  # Comma-separated list of ingredients
    method_preparation = Column(Text)  # Method of preparation
    meal_type = Column(String(50))  # breakfast, lunch, dinner, snack, special
    meal_time = Column(String(10))  # HH:MM format or time range like "8 AM- 11 AM"
    period_type = Column(String(20))  # Week 1, Week 2, Week 3, Week 4, etc.
    meal_date = Column(DateTime, default=datetime.utcnow, index=True)
    day_number = Column(Integer)  # Day 1-7 for weekly plans
    meal_notes = Column(Text)  # Special notes for this meal
    week_notes = Column(Text)  # Weekly guidelines/notes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="meals")

class MealType(Base):
    """Meal type configuration"""
    __tablename__ = "meal_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    default_time = Column(String(10))  # HH:MM format
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Nutrient(Base):
    """Nutrient tracking model"""
    __tablename__ = "nutrients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nutrient_name = Column(String(100), nullable=False)  # Vitamin D, Calcium, etc.
    amount = Column(Float, nullable=False)  # Changed from Integer to Float to support decimal values
    unit = Column(String(20), default="mg")
    date_tracked = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="nutrients")

class IngredientNutrition(Base):
    """Comprehensive Ingredient nutritional values and health information model"""
    __tablename__ = "ingredient_nutrition"
    
    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(String(50), index=True)  # e.g., "Fru001"
    unique_id = Column(String(50), index=True)  # e.g., "Fru001"
    ingredient_name = Column(String(200), nullable=False, index=True)
    
    # Classification
    main_category = Column(String(100))  # Fruits, Vegetables, Grains, etc.
    sub_category = Column(String(100))  # Tropical Fruits, Leafy Greens, etc.
    state = Column(String(50))  # Raw, Cooked, Dried, etc.
    
    # Health & Benefits
    health_benefits = Column(Text)
    phytochemicals = Column(Text)  # Phytochemicals / Antioxidants / Healing
    source_notes = Column(Text)
    reference_primary = Column(String(500))
    
    # Basic Macronutrients (per 100g unless specified)
    serving_size = Column(String(50), default="100g")
    energy_kcal = Column(Float, default=0)  # Calories
    protein_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    carb_g = Column(Float, default=0)  # Carbohydrates
    fiber_g = Column(Float, default=0)
    sugar_g = Column(Float, default=0)  # If available
    
    # Minerals
    calcium_mg = Column(Float, default=0)
    iron_mg = Column(Float, default=0)
    zinc_mg = Column(Float, default=0)
    magnesium_mg = Column(Float, default=0)
    potassium_mg = Column(Float, default=0)
    sodium_mg = Column(Float, default=0)  # If available
    cholesterol_mg = Column(Float, default=0)  # If available
    
    # Vitamins
    vitamin_a_mcg = Column(Float, default=0)  # mcg
    vitamin_c_mg = Column(Float, default=0)
    vitamin_d_mcg = Column(Float, default=0)  # If available
    vitamin_e_mg = Column(Float, default=0)
    vitamin_k_mcg = Column(Float, default=0)
    
    # B Vitamins
    vitamin_b1_mg = Column(Float, default=0)  # Thiamine
    vitamin_b2_mg = Column(Float, default=0)  # Riboflavin
    vitamin_b3_mg = Column(Float, default=0)  # Niacin
    vitamin_b5_mg = Column(Float, default=0)  # Pantothenic Acid
    vitamin_b6_mg = Column(Float, default=0)  # Pyridoxine
    vitamin_b9_mcg = Column(Float, default=0)  # Folate
    vitamin_b12_mcg = Column(Float, default=0)  # Cobalamin
    
    # Essential Fatty Acids
    omega3_g = Column(Float, default=0)
    omega6_g = Column(Float, default=0)  # If available
    
    # Metadata
    index_number = Column(Integer)  # Original CSV index
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemSettings(Base):
    """System Settings configuration model"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), default="string")  # string, integer, boolean, json
    category = Column(String(100), default="general")  # general, email, appointments, payments, api, security
    description = Column(Text)
    is_public = Column(Boolean, default=False)  # Whether non-admin users can view this setting
    is_editable = Column(Boolean, default=True)  # Whether this setting can be edited
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

class UserActivity(Base):
    """User activity tracking for analytics"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # login, logout, appointment_book, meal_log, etc.
    activity_data = Column(Text)  # JSON string with additional activity details
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    session_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="activities")

class SystemMetrics(Base):
    """System-wide metrics for analytics dashboard"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)  # daily_logins, appointments_booked, etc.
    metric_value = Column(Float, nullable=False)
    metric_date = Column(DateTime, default=datetime.utcnow, index=True)
    metric_type = Column(String(50), default="count")  # count, percentage, average, sum
    category = Column(String(50), default="general")  # users, appointments, messages, meals, system
    additional_data = Column(Text)  # JSON string for extra metric details
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsReport(Base):
    """Stored analytics reports for performance optimization"""
    __tablename__ = "analytics_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(100), nullable=False, index=True)
    report_type = Column(String(50), nullable=False)  # dashboard, export, scheduled
    report_data = Column(Text, nullable=False)  # JSON string with report results
    generated_for = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_range_start = Column(DateTime)
    date_range_end = Column(DateTime)
    parameters = Column(Text)  # JSON string with report parameters
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)  # For cached reports
    is_cached = Column(Boolean, default=True)
    
    # Relationship
    generated_by = relationship("User", backref="analytics_reports")


class SecurityEvent(Base):
    """Security Event model for audit trail and security monitoring"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # login_success, login_failed, admin_action, data_access, etc.
    event_category = Column(String(30), nullable=False, default="general")  # authentication, authorization, data_access, admin, system
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be null for system events
    ip_address = Column(String(45), nullable=True)  # Support IPv4 and IPv6
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(200), nullable=True)  # API endpoint accessed
    method = Column(String(10), nullable=True)  # HTTP method
    status_code = Column(Integer, nullable=True)  # HTTP response status
    details = Column(Text, nullable=True)  # Additional event details in JSON format
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="security_events")
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type={self.event_type}, user_id={self.user_id})>"


class LoginAttempt(Base):
    """Login Attempt model for tracking authentication attempts"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, nullable=False, default=False)
    failure_reason = Column(String(100), nullable=True)  # invalid_credentials, account_locked, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Set only on successful login
    session_token = Column(String(500), nullable=True)  # JWT token hash for session tracking
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="login_attempts")
    
    def __repr__(self):
        return f"<LoginAttempt(id={self.id}, username={self.username}, success={self.success})>"


class AuditLog(Base):
    """Audit Log model for tracking admin actions and system changes"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # user_created, user_deleted, settings_modified, etc.
    resource_type = Column(String(50), nullable=False)  # user, appointment, message, settings, etc.
    resource_id = Column(String(100), nullable=True)  # ID of the affected resource
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_role = Column(String(20), nullable=False)  # Role at time of action
    ip_address = Column(String(45), nullable=True)
    old_values = Column(Text, nullable=True)  # JSON string of old values
    new_values = Column(Text, nullable=True)  # JSON string of new values
    details = Column(Text, nullable=True)  # Additional context
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class SecurityAlert(Base):
    """Security Alert model for tracking security incidents and threats"""
    __tablename__ = "security_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # brute_force, suspicious_activity, unauthorized_access
    severity = Column(String(20), nullable=False, default="medium")  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String(200), nullable=True)
    event_count = Column(Integer, default=1)  # Number of similar events
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="security_alerts_user")
    resolver = relationship("User", foreign_keys=[resolved_by], backref="security_alerts_resolved")
    
    def __repr__(self):
        return f"<SecurityAlert(id={self.id}, type={self.alert_type}, severity={self.severity})>"


# ========================================
# PATIENT MANAGEMENT MODELS
# ========================================

class PatientProvider(Base):
    """Patient-Provider relationship model"""
    __tablename__ = "patient_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_type = Column(String(50), nullable=False)  # physician, therapist, health_coach
    relationship_status = Column(String(20), default="active")  # active, inactive, transferred
    assigned_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate patient-provider pairs
    __table_args__ = (UniqueConstraint('patient_id', 'provider_id', name='unique_patient_provider'),)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="assigned_providers")
    provider = relationship("User", foreign_keys=[provider_id], backref="assigned_patients")

class HealthRecord(Base):
    """Patient health records model"""
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(String(50), nullable=False)  # consultation, diagnosis, treatment, progress_note
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Vital signs and metrics
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    heart_rate_bpm = Column(Integer, nullable=True)
    temperature_c = Column(Float, nullable=True)
    
    # Medical information
    symptoms = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    
    # Flags and status
    is_confidential = Column(Boolean, default=False)
    is_emergency = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # active, resolved, follow_up_needed
    
    record_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="health_records_patient")
    provider = relationship("User", foreign_keys=[provider_id], backref="health_records_provider")

class PatientNutritionPlan(Base):
    """Patient-specific nutrition plans"""
    __tablename__ = "patient_nutrition_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Nutritional goals
    daily_calories_target = Column(Integer, nullable=True)
    protein_target_g = Column(Float, nullable=True)
    carbs_target_g = Column(Float, nullable=True)
    fat_target_g = Column(Float, nullable=True)
    fiber_target_g = Column(Float, nullable=True)
    
    # Dietary restrictions and preferences
    dietary_restrictions = Column(Text)  # JSON array of restrictions
    food_allergies = Column(Text)  # JSON array of allergies
    food_preferences = Column(Text)  # JSON array of preferences
    
    # Plan details
    instructions = Column(Text)
    meal_frequency = Column(String(50))  # 3 meals, 5 small meals, etc.
    hydration_target_ml = Column(Integer, nullable=True)
    
    # Status and dates
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="nutrition_plans_patient")
    provider = relationship("User", foreign_keys=[provider_id], backref="nutrition_plans_provider")

class PatientMealPlan(Base):
    """Patient-specific meal plans"""
    __tablename__ = "patient_meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nutrition_plan_id = Column(Integer, ForeignKey("patient_nutrition_plans.id"), nullable=True)
    
    # Meal details
    meal_name = Column(String(200), nullable=False)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    meal_time = Column(String(10))  # HH:MM format
    
    # Nutritional information
    ingredients = Column(Text, nullable=False)  # JSON array of ingredients
    preparation_instructions = Column(Text)
    portion_size = Column(String(100))
    
    # Calculated nutrition (per serving)
    calories = Column(Integer, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    
    # Schedule
    planned_date = Column(DateTime, nullable=False, index=True)
    is_completed = Column(Boolean, default=False)
    completion_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="meal_plans_patient")
    provider = relationship("User", foreign_keys=[provider_id], backref="meal_plans_provider")
    nutrition_plan = relationship("PatientNutritionPlan", backref="meal_plans")

# ========================================
# EARNINGS AND COMMISSION MODELS
# ========================================

class EarningsRecord(Base):
    """Provider earnings tracking"""
    __tablename__ = "earnings_records"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Earnings details
    service_type = Column(String(100), nullable=False)  # consultation, therapy_session, nutrition_consultation
    service_description = Column(Text)
    
    # Financial information
    base_amount = Column(Float, nullable=False)  # Base service fee
    commission_rate = Column(Float, default=0.0)  # Commission percentage (0.0 to 1.0)
    commission_amount = Column(Float, default=0.0)  # Calculated commission
    net_earnings = Column(Float, nullable=False)  # Amount after commission
    
    # Payment details
    payment_status = Column(String(20), default="pending")  # pending, processed, paid, disputed
    payment_method = Column(String(50))  # bank_transfer, paypal, check
    payment_date = Column(DateTime, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # Dates
    service_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("User", foreign_keys=[provider_id], backref="earnings_records")
    patient = relationship("User", foreign_keys=[patient_id], backref="earnings_records_patient")
    appointment = relationship("Appointment", backref="earnings_record")

class CommissionStructure(Base):
    """Commission structure configuration"""
    __tablename__ = "commission_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_role = Column(String(50), nullable=False)  # physician, therapist, health_coach
    service_type = Column(String(100), nullable=False)
    
    # Commission rates
    commission_rate = Column(Float, nullable=False)  # Percentage (0.0 to 1.0)
    minimum_amount = Column(Float, default=0.0)  # Minimum service amount for commission
    maximum_commission = Column(Float, nullable=True)  # Maximum commission cap
    
    # Tier-based commission (optional)
    tier_1_threshold = Column(Float, nullable=True)  # Monthly earning threshold for tier 1
    tier_1_rate = Column(Float, nullable=True)
    tier_2_threshold = Column(Float, nullable=True)
    tier_2_rate = Column(Float, nullable=True)
    tier_3_threshold = Column(Float, nullable=True)
    tier_3_rate = Column(Float, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentRecord(Base):
    """Payment records for providers"""
    __tablename__ = "payment_records"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    payment_period_start = Column(DateTime, nullable=False)
    payment_period_end = Column(DateTime, nullable=False)
    total_earnings = Column(Float, nullable=False)
    total_commission = Column(Float, nullable=False)
    net_payment = Column(Float, nullable=False)
    
    # Payment information
    payment_method = Column(String(50), nullable=False)  # bank_transfer, paypal, check
    payment_reference = Column(String(100), nullable=True)
    payment_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    payment_date = Column(DateTime, nullable=True)
    
    # Associated earnings
    earnings_count = Column(Integer, default=0)  # Number of earnings records included
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("User", backref="payment_records")


# ============================================================================
# SUBSCRIPTION PLANS & FEATURES
# ============================================================================

class SubscriptionFeature(Base):
    """Features/Services that can be included in subscription plans"""
    __tablename__ = "subscription_features"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(100), unique=True, nullable=False, index=True)
    feature_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'appointments_booking', 'meal_planning'
    description = Column(Text)
    category = Column(String(50), index=True)  # e.g., 'health_tracking', 'appointments', 'nutrition'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan_features = relationship("SubscriptionPlanFeature", back_populates="feature", cascade="all, delete-orphan")


class SubscriptionPlan(Base):
    """Subscription tiers/plans"""
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(100), unique=True, nullable=False, index=True)
    plan_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'basic', 'premium', 'enterprise'
    description = Column(Text)
    price_monthly = Column(Float, nullable=False, default=0.0)
    price_yearly = Column(Float, nullable=True)  # Optional yearly pricing
    currency = Column(String(3), default='USD')
    
    # Plan configuration
    max_appointments_per_month = Column(Integer, nullable=True)  # NULL = unlimited
    max_health_records = Column(Integer, nullable=True)
    priority_support = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)  # Highlight as popular/recommended
    display_order = Column(Integer, default=0)  # For sorting plans in UI
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan_features = relationship("SubscriptionPlanFeature", back_populates="plan", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="plan")


class SubscriptionPlanFeature(Base):
    """Junction table linking plans to features"""
    __tablename__ = "subscription_plan_features"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("subscription_features.id"), nullable=False)
    
    # Feature-specific limits (optional, overrides plan defaults)
    feature_limit = Column(Integer, nullable=True)  # e.g., max uses per month for this feature
    feature_metadata = Column(Text, nullable=True)  # JSON string for additional config
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('plan_id', 'feature_id', name='unique_plan_feature'),)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="plan_features")
    feature = relationship("SubscriptionFeature", back_populates="plan_features")


class UserSubscription(Base):
    """User subscription records"""
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription period
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)  # NULL = active subscription
    billing_cycle = Column(String(20), default='monthly')  # monthly, yearly
    
    # Payment info
    amount_paid = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    
    # Status
    status = Column(String(20), default='active')  # active, cancelled, expired, suspended
    auto_renew = Column(Boolean, default=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")


