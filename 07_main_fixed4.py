"""
MindLab Health - Main FastAPI Application
==========================================
Complete mental health therapist matching platform API
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr

# Import models from our models module (models.py in same directory)
from models import (
    Base, User, Appointment, Message, UserRole, AppointmentStatus, Meal, Nutrient, MealType, 
    IngredientNutrition, SystemSettings, UserActivity, SystemMetrics, AnalyticsReport, 
    SecurityEvent, LoginAttempt, AuditLog, SecurityAlert, Permission, RolePermission,
    PatientProvider, HealthRecord, PatientNutritionPlan, PatientMealPlan, 
    EarningsRecord, CommissionStructure, PaymentRecord
)
from google_calendar_service import calendar_service

# Import auth functions from our auth module (auth.py in same directory)
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    validate_password_strength,
    validate_username
)

# Import RBAC decorators and functions
from rbac_decorators import (
    require_permission,
    require_admin,
    require_role,
    get_user_permissions,
    can_access_user_data,
    can_access_appointment
)

# Database configuration
# Production setup using PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL or DATABASE_URL.strip() == "":
    # PostgreSQL database (containerized on port 5433)
    DATABASE_URL = "postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5433/mindlab_health"
    # For local PostgreSQL on Windows: use "localhost" instead of "host.containers.internal"

engine = create_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool for PostgreSQL
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI(
    title="MindLab Health API",
    description="Mental health therapist matching platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

# Mount static files for frontend
# Middleware to handle HEAD requests
@app.middleware("http")
async def head_to_get_middleware(request, call_next):
    """
    Convert HEAD requests to GET requests and return empty body.
    This allows all GET routes to respond to HEAD requests properly.
    """
    if request.method == "HEAD":
        # Create a new request with GET method
        request._method = "GET"
        response = await call_next(request)
        # For HEAD requests, FastAPI should return headers only
        # The body is automatically stripped by Starlette
        return response
    return await call_next(request)


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mindlab_health.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Startup event to create default admin user
@app.on_event("startup")
async def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # Create default admin user
            hashed_password = get_password_hash("Admin123!@#")
            admin_user = User(
                username="admin",
                email="admin@mindlabhealth.com",
                hashed_password=hashed_password,
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Default admin user created successfully")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating default admin user: {e}")
        db.rollback()
    finally:
        db.close()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Database dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "patient"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    therapist_id: int
    appointment_datetime: datetime
    duration_minutes: Optional[int] = 60
    appointment_type: Optional[str] = "consultation"
    location: Optional[str] = None
    notes: Optional[str] = None
    sync_with_calendar: Optional[bool] = True

class AppointmentUpdate(BaseModel):
    therapist_id: Optional[int] = None
    appointment_datetime: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    appointment_type: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    sync_with_calendar: Optional[bool] = None

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    therapist_id: int
    appointment_datetime: datetime
    duration_minutes: int
    status: str
    appointment_type: str
    location: Optional[str]
    notes: Optional[str]
    google_calendar_event_id: Optional[str]
    sync_with_calendar: bool
    last_calendar_sync: Optional[datetime]
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    recipient_id: int
    subject: str
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    subject: str
    content: str
    read: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SystemSettingsCreate(BaseModel):
    setting_key: str
    setting_value: str
    setting_type: str = "string"
    category: str = "general"
    description: Optional[str] = None
    is_public: bool = False
    is_editable: bool = True

class SystemSettingsUpdate(BaseModel):
    setting_value: Optional[str] = None
    setting_type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_editable: Optional[bool] = None

class SystemSettingsResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    setting_type: str
    category: str
    description: Optional[str]
    is_public: bool
    is_editable: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Analytics Pydantic Models
class UserActivityCreate(BaseModel):
    activity_type: str
    activity_data: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_type: str
    activity_data: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SystemMetricsResponse(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    metric_date: datetime
    metric_type: str
    category: str
    additional_data: Optional[str]
    
    class Config:
        from_attributes = True

class AnalyticsReportCreate(BaseModel):
    report_name: str
    report_type: str
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    parameters: Optional[str] = None

class AnalyticsReportResponse(BaseModel):
    id: int
    report_name: str
    report_type: str
    report_data: str
    generated_for: int
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    parameters: Optional[str]
    generated_at: datetime
    expires_at: Optional[datetime]
    is_cached: bool
    
    class Config:
        from_attributes = True

class AnalyticsDashboardData(BaseModel):
    """Comprehensive dashboard data"""
    user_stats: dict
    appointment_stats: dict
    message_stats: dict
    meal_stats: dict
    system_stats: dict
    recent_activities: List[UserActivityResponse]
    generated_at: datetime

# Security Schemas
class SecurityEventCreate(BaseModel):
    event_type: str
    event_category: str = "general"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    details: Optional[str] = None
    risk_level: str = "low"

class SecurityEventResponse(BaseModel):
    id: int
    event_type: str
    event_category: str
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    status_code: Optional[int]
    details: Optional[str]
    risk_level: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class LoginAttemptResponse(BaseModel):
    id: int
    username: str
    ip_address: str
    user_agent: Optional[str]
    success: bool
    failure_reason: Optional[str]
    user_id: Optional[int]
    attempted_at: datetime
    
    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    action: str
    resource_type: str
    resource_id: Optional[str]
    user_id: int
    user_role: str
    ip_address: Optional[str]
    old_values: Optional[str]
    new_values: Optional[str]
    details: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SecurityAlertCreate(BaseModel):
    alert_type: str
    severity: str = "medium"
    title: str
    description: str
    ip_address: Optional[str] = None
    endpoint: Optional[str] = None

class SecurityAlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    description: str
    ip_address: Optional[str]
    user_id: Optional[int]
    endpoint: Optional[str]
    event_count: int
    first_seen: datetime
    last_seen: datetime
    resolved: bool
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SecurityDashboardData(BaseModel):
    """Security dashboard overview data"""
    total_events: int
    failed_logins: int
    active_alerts: int
    high_risk_events: int
    recent_events: List[SecurityEventResponse]
    recent_login_attempts: List[LoginAttemptResponse]
    recent_alerts: List[SecurityAlertResponse]
    login_success_rate: float
    generated_at: datetime

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend index.html"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Frontend not found</h1><p>Please check that frontend files are in the correct location.</p>"


# HTML file routes (for dashboard, login, register, etc.)
@app.get("/dashboard.html", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the dashboard HTML page"""
    try:
        with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard page not found")

@app.get("/login.html", response_class=HTMLResponse)
async def serve_login():
    """Serve the login HTML page"""
    try:
        with open("frontend/login.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Login page not found")

@app.get("/register.html", response_class=HTMLResponse)
async def serve_register():
    """Serve the register HTML page"""
    try:
        with open("frontend/register.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Register page not found")


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Welcome to MindLab Health API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def simple_health_check():
    """Simple health check for Docker"""
    return {"status": "ok"}

@app.get("/api/system/status")
async def get_system_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get comprehensive system status
    Returns real-time information about the system
    Requires authentication
    """
    try:
        # Check database type
        db_url = str(engine.url)
        if "sqlite" in db_url.lower():
            db_type = "SQLite"
            db_status = "Connected"
        elif "postgresql" in db_url.lower():
            db_type = "PostgreSQL"
            db_status = "Connected"
        elif "mysql" in db_url.lower():
            db_type = "MySQL"
            db_status = "Connected"
        else:
            db_type = "Unknown"
            db_status = "Connected"
        
        # Get counts
        total_users = db.query(User).count()
        total_appointments = db.query(Appointment).count()
        total_meals = db.query(Meal).count()
        total_nutrients = db.query(Nutrient).count()
        total_ingredients = db.query(IngredientNutrition).count()
        
        # Get user role breakdown
        user_roles = {}
        for role in UserRole:
            # Use role.value (string) instead of role (enum object)
            count = db.query(User).filter(User.role == role.value).count()
            user_roles[role.value] = count
        
        # Get appointment status breakdown
        appt_status = {}
        for status in AppointmentStatus:
            # Use status.value (string) instead of status (enum object)
            count = db.query(Appointment).filter(Appointment.status == status.value).count()
            appt_status[status.value] = count
        
        return {
            "api_server": {
                "status": "online",
                "uptime": "running"
            },
            "database": {
                "status": db_status.lower(),
                "type": db_type,
                "connection": "active"
            },
            "statistics": {
                "total_users": total_users,
                "total_appointments": total_appointments,
                "total_meals": total_meals,
                "total_nutrients": total_nutrients,
                "total_ingredients": total_ingredients
            },
            "user_breakdown": user_roles,
            "appointment_breakdown": appt_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            "api_server": {
                "status": "online",
                "uptime": "running"
            },
            "database": {
                "status": "error",
                "type": "unknown",
                "connection": "failed",
                "error": str(e)
            },
            "statistics": {
                "total_users": 0,
                "total_appointments": 0,
                "total_meals": 0,
                "total_nutrients": 0,
                "total_ingredients": 0
            },
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/users/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Registering new user: {user.username}")
    
    # Validate username
    if not validate_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username format"
        )
    
    # Validate password strength
    is_valid, message = validate_password_strength(user.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User registered successfully: {user.username}")
    return db_user

@app.post("/api/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint - OAuth2 password flow"""
    logger.info(f"Login attempt: {form_data.username}")
    
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    logger.info(f"User logged in successfully: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}



# OAuth2 compatible endpoint (alias for /api/token)
@app.post("/token", response_model=Token)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible login endpoint - alias for /api/token"""
    return await login(form_data, db)

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@app.get("/api/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users - Admin only"""
    # Check if user has permission to view users
    if not current_user.has_permission("users.view", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view users"
        )
    
    # Get all users
    users = db.query(User).all()
    return users

@app.patch("/api/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user role - Admin only"""
    if not current_user.has_permission("users.manage_roles", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to manage user roles"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate role
    new_role = role_data.get("role")
    valid_roles = ["patient", "therapist", "admin", "health_coach", "physician", "partner"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Update role
    user.role = new_role
    db.commit()
    
    logger.info(f"User {user.username} role updated to {new_role} by {current_user.username}")
    return {"message": "Role updated successfully", "user_id": user_id, "new_role": new_role}

# ================================
# ROLE-BASED ACCESS CONTROL ENDPOINTS
# ================================

@app.get("/api/users/me/permissions")
async def get_current_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's permissions"""
    permissions = current_user.get_permissions(db)
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": str(current_user.role),
        "permissions": permissions
    }

@app.get("/api/users/me/modules")
async def get_current_user_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get modules accessible to current user"""
    modules = [
        "users", "appointments", "messages", "analytics", "security", "settings", 
        "meals", "nutrition", "health", "admin", "patients", "health_records", 
        "earnings", "commission"
    ]
    accessible_modules = []
    
    for module in modules:
        if current_user.can_access_module(module, db):
            accessible_modules.append(module)
    
    return {
        "user_id": current_user.id,
        "role": str(current_user.role),
        "accessible_modules": accessible_modules
    }

@app.get("/api/rbac/permissions")
async def get_all_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available permissions - Admin only"""
    if str(current_user.role) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view all permissions"
        )
    
    permissions = db.query(Permission).all()
    return [
        {
            "id": perm.id,
            "name": perm.name,
            "description": perm.description,
            "module": perm.module,
            "action": perm.action
        }
        for perm in permissions
    ]

@app.get("/api/rbac/roles/{role}/permissions")
async def get_role_permissions(
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get permissions for a specific role - Admin only"""
    if str(current_user.role) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view role permissions"
        )
    
    valid_roles = ["patient", "therapist", "admin", "health_coach", "physician", "partner"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    permissions = db.query(Permission.name, Permission.description, Permission.module, Permission.action).join(
        RolePermission
    ).filter(RolePermission.role == role).all()
    
    return {
        "role": role,
        "permissions": [
            {
                "name": perm[0],
                "description": perm[1],
                "module": perm[2],
                "action": perm[3]
            }
            for perm in permissions
        ]
    }

@app.post("/api/rbac/check-permission")
async def check_user_permission(
    permission_check: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user has specific permission"""
    permission_name = permission_check.get("permission")
    if not permission_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission name is required"
        )
    
    has_permission = current_user.has_permission(permission_name, db)
    return {
        "user_id": current_user.id,
        "permission": permission_name,
        "has_permission": has_permission
    }

@app.patch("/api/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    status_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable or disable user - Admin only"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user status"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent disabling self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )
    
    # Update status
    new_status = status_data.get("is_active")
    if new_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="is_active field is required"
        )
    
    user.is_active = new_status
    db.commit()
    
    status_text = "enabled" if new_status else "disabled"
    logger.info(f"User {user.username} {status_text} by {current_user.username}")
    return {"message": f"User {status_text} successfully", "user_id": user_id, "is_active": new_status}

@app.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user - Admin only (PERMANENT)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    username = user.username
    
    # Delete user (cascade will handle related records)
    db.delete(user)
    db.commit()
    
    logger.warning(f"User {username} (ID: {user_id}) DELETED by {current_user.username}")
    return {"message": f"User '{username}' deleted successfully", "user_id": user_id}

@app.post("/api/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    logger.info(f"Creating appointment for user: {current_user.username}")
    
    # Verify therapist exists
    therapist = db.query(User).filter(
        User.id == appointment.therapist_id,
        User.role == "therapist"
    ).first()
    
    if not therapist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapist not found"
        )
    
    # Create appointment
    db_appointment = Appointment(
        user_id=current_user.id,
        therapist_id=appointment.therapist_id,
        appointment_datetime=appointment.appointment_datetime,
        duration_minutes=appointment.duration_minutes,
        appointment_type=appointment.appointment_type,
        location=appointment.location,
        status="scheduled",
        notes=appointment.notes,
        sync_with_calendar=appointment.sync_with_calendar
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Google Calendar Integration
    if appointment.sync_with_calendar and calendar_service.enabled:
        try:
            # Get patient and therapist info for calendar event
            patient = db.query(User).filter(User.id == current_user.id).first()
            therapist = db.query(User).filter(User.id == appointment.therapist_id).first()
            
            calendar_data = {
                'appointment_id': db_appointment.id,
                'appointment_datetime': appointment.appointment_datetime,
                'duration_minutes': appointment.duration_minutes,
                'appointment_type': appointment.appointment_type,
                'location': appointment.location,
                'notes': appointment.notes,
                'patient_name': patient.username if patient else 'Unknown',
                'patient_email': patient.email if patient else None,
                'therapist_name': therapist.username if therapist else 'Unknown',
                'therapist_email': therapist.email if therapist else None,
            }
            
            event_id = calendar_service.create_event(calendar_data)
            if event_id:
                db_appointment.google_calendar_event_id = event_id
                db_appointment.last_calendar_sync = datetime.utcnow()
                db.commit()
                db.refresh(db_appointment)
                logger.info(f"Google Calendar event created for appointment {db_appointment.id}: {event_id}")
            else:
                logger.warning(f"Failed to create Google Calendar event for appointment {db_appointment.id}")
                
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {e}")
    
    logger.info(f"Appointment created: {db_appointment.id}")
    return db_appointment

@app.get("/api/appointments/my", response_model=List[AppointmentResponse])
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's appointments"""
    if not current_user.has_permission("appointments.view_own", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view appointments"
        )
    
    appointments = db.query(Appointment).filter(
        (Appointment.user_id == current_user.id) | 
        (Appointment.therapist_id == current_user.id)
    ).all()
    
    return appointments

@app.get("/api/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific appointment"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization using RBAC
    if not can_access_appointment(current_user, appointment_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this appointment"
        )
    
    return appointment

# Additional Appointment Endpoints

@app.get("/api/appointments", response_model=List[AppointmentResponse])
async def get_all_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all appointments (Admin and Physicians)"""
    if not current_user.has_permission("appointments.view_all", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view all appointments"
        )
    
    appointments = db.query(Appointment).order_by(Appointment.appointment_datetime.desc()).all()
    return appointments

@app.put("/api/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization (patient, therapist, or admin)
    if (appointment.user_id != current_user.id and 
        appointment.therapist_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    # Update appointment fields (only if provided)
    if appointment_update.therapist_id is not None:
        appointment.therapist_id = appointment_update.therapist_id
    if appointment_update.appointment_datetime is not None:
        appointment.appointment_datetime = appointment_update.appointment_datetime
    if appointment_update.duration_minutes is not None:
        appointment.duration_minutes = appointment_update.duration_minutes
    if appointment_update.appointment_type is not None:
        appointment.appointment_type = appointment_update.appointment_type
    if appointment_update.location is not None:
        appointment.location = appointment_update.location
    if appointment_update.notes is not None:
        appointment.notes = appointment_update.notes
    if appointment_update.sync_with_calendar is not None:
        appointment.sync_with_calendar = appointment_update.sync_with_calendar
    
    db.commit()
    db.refresh(appointment)
    
    return appointment

@app.patch("/api/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if (appointment.user_id != current_user.id and 
        appointment.therapist_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    # Validate status
    new_status = status_update.get("status")
    valid_statuses = [status.value for status in AppointmentStatus]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    appointment.status = new_status
    db.commit()
    db.refresh(appointment)
    
    return {"message": "Status updated successfully", "status": new_status}

@app.delete("/api/appointments/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete/Cancel an appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if (appointment.user_id != current_user.id and 
        appointment.therapist_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this appointment"
        )
    
    # Instead of deleting, mark as cancelled
    appointment.status = "cancelled"
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}

@app.get("/api/therapists", response_model=List[dict])
async def get_therapists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available therapists"""
    therapists = db.query(User).filter(User.role == "therapist").all()
    
    return [
        {
            "id": therapist.id,
            "username": therapist.username,
            "email": therapist.email
        }
        for therapist in therapists
    ]

@app.post("/api/messages", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message"""
    logger.info(f"Sending message from {current_user.username}")
    
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    # Create message
    db_message = Message(
        sender_id=current_user.id,
        recipient_id=message.recipient_id,
        subject=message.subject,
        content=message.content
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    logger.info(f"Message sent: {db_message.id}")
    return db_message

@app.get("/api/messages/inbox", response_model=List[MessageResponse])
async def get_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inbox messages"""
    messages = db.query(Message).filter(
        Message.recipient_id == current_user.id
    ).order_by(Message.timestamp.desc()).all()
    
    return messages

@app.get("/api/messages/sent", response_model=List[MessageResponse])
async def get_sent_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sent messages"""
    messages = db.query(Message).filter(
        Message.sender_id == current_user.id
    ).order_by(Message.timestamp.desc()).all()
    
    return messages

@app.get("/api/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user is sender or recipient
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this message"
        )
    
    return message

@app.patch("/api/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Only recipient can mark message as read
    if message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only message recipient can mark as read"
        )
    
    message.read = True
    db.commit()
    db.refresh(message)
    
    logger.info(f"Message {message_id} marked as read by user {current_user.id}")
    return {"message": "Message marked as read", "message_id": message_id}

@app.delete("/api/messages/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user is sender or recipient
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this message"
        )
    
    db.delete(message)
    db.commit()
    
    logger.info(f"Message {message_id} deleted by user {current_user.id}")
    return {"message": "Message deleted successfully", "message_id": message_id}

@app.get("/api/messages/all", response_model=List[MessageResponse])
async def get_all_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for admin users"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    messages = db.query(Message).order_by(Message.timestamp.desc()).all()
    return messages

# ============================================================================
# MEALS ENDPOINTS
# ============================================================================

class MealCreate(BaseModel):
    """Meal creation schema"""
    name: str
    description: Optional[str] = None
    ingredients: Optional[str] = None  # Comma-separated list of ingredients
    method_preparation: Optional[str] = None  # Method of preparation
    meal_type: Optional[str] = None
    meal_time: Optional[str] = None  # HH:MM format
    period_type: Optional[str] = "daily"  # daily, weekly, monthly
    meal_date: Optional[datetime] = None

class MealResponse(BaseModel):
    """Meal response schema"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    ingredients: Optional[str]  # Comma-separated list of ingredients
    method_preparation: Optional[str]  # Method of preparation
    meal_type: Optional[str]
    meal_time: Optional[str]
    period_type: Optional[str]
    meal_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class MealTypeCreate(BaseModel):
    """Meal type creation schema"""
    name: str
    default_time: Optional[str] = None
    description: Optional[str] = None

class MealTypeResponse(BaseModel):
    """Meal type response schema"""
    id: int
    name: str
    default_time: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.post("/api/meal-types", response_model=MealTypeResponse)
async def create_meal_type(
    meal_type: MealTypeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new meal type (admin only)"""
    from models import MealType
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if meal type already exists
    existing = db.query(MealType).filter(MealType.name == meal_type.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meal type already exists"
        )
    
    db_meal_type = MealType(
        name=meal_type.name,
        default_time=meal_type.default_time,
        description=meal_type.description
    )
    
    db.add(db_meal_type)
    db.commit()
    db.refresh(db_meal_type)
    
    logger.info(f"Meal type created: {db_meal_type.name} by {current_user.username}")
    return db_meal_type

@app.get("/api/meal-types", response_model=List[MealTypeResponse])
async def get_meal_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active meal types"""
    from models import MealType
    
    meal_types = db.query(MealType).filter(MealType.is_active == True).order_by(MealType.name).all()
    return meal_types

@app.delete("/api/meal-types/{meal_type_id}")
async def delete_meal_type(
    meal_type_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meal type (admin only)"""
    from models import MealType
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    meal_type = db.query(MealType).filter(MealType.id == meal_type_id).first()
    if not meal_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal type not found"
        )
    
    name = meal_type.name
    db.delete(meal_type)
    db.commit()
    
    logger.info(f"Meal type '{name}' deleted by {current_user.username}")
    return {"message": f"Meal type '{name}' deleted successfully"}

@app.post("/api/meals", response_model=MealResponse)
async def create_meal(
    meal: MealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new meal entry"""
    from models import Meal
    
    db_meal = Meal(
        user_id=current_user.id,
        name=meal.name,
        description=meal.description,
        ingredients=meal.ingredients,
        method_preparation=meal.method_preparation,
        meal_type=meal.meal_type,
        meal_time=meal.meal_time,
        period_type=meal.period_type or "daily",
        meal_date=meal.meal_date or datetime.utcnow()
    )
    
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    
    logger.info(f"Meal created: {db_meal.id} by user {current_user.username}")
    return db_meal

@app.get("/api/meals", response_model=List[MealResponse])
async def get_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all meals for current user"""
    from models import Meal
    
    meals = db.query(Meal).filter(
        Meal.user_id == current_user.id
    ).order_by(Meal.meal_date.desc()).all()
    
    return meals

@app.get("/api/meals/all", response_model=List[MealResponse])
async def get_all_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all meals (admin only)"""
    from models import Meal
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    meals = db.query(Meal).order_by(Meal.meal_date.desc()).all()
    return meals

@app.put("/api/meals/{meal_id}", response_model=MealResponse)
async def update_meal(
    meal_id: int,
    meal: MealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing meal"""
    from models import Meal
    
    # Get the meal
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check ownership or admin
    if db_meal.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this meal"
        )
    
    # Update fields
    db_meal.name = meal.name
    db_meal.description = meal.description
    db_meal.ingredients = meal.ingredients
    db_meal.method_preparation = meal.method_preparation
    db_meal.meal_type = meal.meal_type
    db_meal.meal_time = meal.meal_time
    db_meal.period_type = meal.period_type or "daily"
    db_meal.meal_date = meal.meal_date or db_meal.meal_date
    
    db.commit()
    db.refresh(db_meal)
    
    logger.info(f"Meal {meal_id} updated by user {current_user.username}")
    return db_meal

@app.delete("/api/meals/{meal_id}")
async def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meal"""
    from models import Meal
    
    # Get the meal
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check ownership or admin
    if db_meal.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meal"
        )
    
    meal_name = db_meal.name
    db.delete(db_meal)
    db.commit()
    
    logger.info(f"Meal {meal_id} ('{meal_name}') deleted by user {current_user.username}")
    return {"message": f"Meal '{meal_name}' deleted successfully"}

# ============================================================================
# NUTRIENTS ENDPOINTS
# ============================================================================

class NutrientCreate(BaseModel):
    """Nutrient creation schema"""
    nutrient_name: str
    amount: float  # Changed from int to float to support decimal values
    unit: str = "mg"
    date_tracked: Optional[datetime] = None
    notes: Optional[str] = None

class NutrientResponse(BaseModel):
    """Nutrient response schema"""
    id: int
    user_id: int
    nutrient_name: str
    amount: float  # Changed from int to float to match NutrientCreate
    unit: str
    date_tracked: datetime
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class IngredientNutritionCreate(BaseModel):
    """Comprehensive Ingredient nutrition creation schema"""
    # Primary identifiers
    ingredient_id: Optional[str] = None
    unique_id: Optional[str] = None
    ingredient_name: str
    
    # Classification
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    state: Optional[str] = None
    
    # Health & Benefits
    health_benefits: Optional[str] = None
    phytochemicals: Optional[str] = None
    source_notes: Optional[str] = None
    reference_primary: Optional[str] = None
    
    # Basic Macronutrients (per 100g unless specified)
    serving_size: Optional[str] = "100g"
    energy_kcal: Optional[float] = 0
    protein_g: Optional[float] = 0
    fat_g: Optional[float] = 0
    carb_g: Optional[float] = 0
    fiber_g: Optional[float] = 0
    sugar_g: Optional[float] = 0
    
    # Minerals
    calcium_mg: Optional[float] = 0
    iron_mg: Optional[float] = 0
    zinc_mg: Optional[float] = 0
    magnesium_mg: Optional[float] = 0
    potassium_mg: Optional[float] = 0
    sodium_mg: Optional[float] = 0
    cholesterol_mg: Optional[float] = 0
    
    # Vitamins
    vitamin_a_mcg: Optional[float] = 0
    vitamin_c_mg: Optional[float] = 0
    vitamin_d_mcg: Optional[float] = 0
    vitamin_e_mg: Optional[float] = 0
    vitamin_k_mcg: Optional[float] = 0
    
    # B Vitamins
    vitamin_b1_mg: Optional[float] = 0
    vitamin_b2_mg: Optional[float] = 0
    vitamin_b3_mg: Optional[float] = 0
    vitamin_b5_mg: Optional[float] = 0
    vitamin_b6_mg: Optional[float] = 0
    vitamin_b9_mcg: Optional[float] = 0
    vitamin_b12_mcg: Optional[float] = 0
    
    # Essential Fatty Acids
    omega3_g: Optional[float] = 0
    omega6_g: Optional[float] = 0
    
    # Metadata
    index_number: Optional[int] = None
    notes: Optional[str] = None

class IngredientNutritionResponse(BaseModel):
    """Comprehensive Ingredient nutrition response schema - matches expanded database model"""
    # Primary identifiers
    id: int
    ingredient_id: Optional[str] = None
    unique_id: Optional[str] = None
    ingredient_name: str
    
    # Classification
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    state: Optional[str] = None
    
    # Health & Benefits
    health_benefits: Optional[str] = None
    phytochemicals: Optional[str] = None
    source_notes: Optional[str] = None
    reference_primary: Optional[str] = None
    
    # Basic Macronutrients (per 100g unless specified)
    serving_size: Optional[str] = "100g"
    energy_kcal: Optional[float] = 0
    protein_g: Optional[float] = 0
    fat_g: Optional[float] = 0
    carb_g: Optional[float] = 0
    fiber_g: Optional[float] = 0
    sugar_g: Optional[float] = 0
    
    # Minerals
    calcium_mg: Optional[float] = 0
    iron_mg: Optional[float] = 0
    zinc_mg: Optional[float] = 0
    magnesium_mg: Optional[float] = 0
    potassium_mg: Optional[float] = 0
    sodium_mg: Optional[float] = 0
    cholesterol_mg: Optional[float] = 0
    
    # Vitamins
    vitamin_a_mcg: Optional[float] = 0
    vitamin_c_mg: Optional[float] = 0
    vitamin_d_mcg: Optional[float] = 0
    vitamin_e_mg: Optional[float] = 0
    vitamin_k_mcg: Optional[float] = 0
    
    # B Vitamins
    vitamin_b1_mg: Optional[float] = 0
    vitamin_b2_mg: Optional[float] = 0
    vitamin_b3_mg: Optional[float] = 0
    vitamin_b5_mg: Optional[float] = 0
    vitamin_b6_mg: Optional[float] = 0
    vitamin_b9_mcg: Optional[float] = 0
    vitamin_b12_mcg: Optional[float] = 0
    
    # Essential Fatty Acids
    omega3_g: Optional[float] = 0
    omega6_g: Optional[float] = 0
    
    # Metadata
    index_number: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Ingredient Nutrition Endpoints
@app.post("/api/ingredient-nutrition", response_model=IngredientNutritionResponse)
async def create_ingredient_nutrition(
    ingredient: IngredientNutritionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update ingredient nutritional values"""
    from models import IngredientNutrition
    
    # Check if ingredient already exists
    existing = db.query(IngredientNutrition).filter(
        IngredientNutrition.ingredient_name == ingredient.ingredient_name
    ).first()
    
    if existing:
        # Update existing
        for key, value in ingredient.dict().items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        logger.info(f"Ingredient nutrition updated: {existing.ingredient_name}")
        return existing
    
    # Create new
    db_ingredient = IngredientNutrition(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    
    logger.info(f"Ingredient nutrition created: {db_ingredient.ingredient_name}")
    return db_ingredient

@app.get("/api/ingredient-nutrition", response_model=List[IngredientNutritionResponse])
async def get_all_ingredient_nutrition(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all ingredient nutritional values"""
    from models import IngredientNutrition
    
    ingredients = db.query(IngredientNutrition).order_by(
        IngredientNutrition.ingredient_name
    ).all()
    
    return ingredients

@app.get("/api/ingredient-nutrition/{ingredient_name}", response_model=IngredientNutritionResponse)
async def get_ingredient_nutrition(
    ingredient_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get nutritional values for a specific ingredient"""
    from models import IngredientNutrition
    
    ingredient = db.query(IngredientNutrition).filter(
        IngredientNutrition.ingredient_name == ingredient_name
    ).first()
    
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )
    
    return ingredient

@app.put("/api/ingredient-nutrition/{ingredient_id}", response_model=IngredientNutritionResponse)
async def update_ingredient_nutrition(
    ingredient_id: int,
    ingredient: IngredientNutritionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ingredient nutritional values"""
    from models import IngredientNutrition
    
    db_ingredient = db.query(IngredientNutrition).filter(
        IngredientNutrition.id == ingredient_id
    ).first()
    
    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )
    
    # Update fields
    for key, value in ingredient.dict().items():
        setattr(db_ingredient, key, value)
    
    db_ingredient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_ingredient)
    
    logger.info(f"Ingredient nutrition updated: {db_ingredient.ingredient_name}")
    return db_ingredient

@app.delete("/api/ingredient-nutrition/{ingredient_id}")
async def delete_ingredient_nutrition(
    ingredient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete ingredient nutritional values"""
    from models import IngredientNutrition
    
    db_ingredient = db.query(IngredientNutrition).filter(
        IngredientNutrition.id == ingredient_id
    ).first()
    
    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )
    
    ingredient_name = db_ingredient.ingredient_name
    db.delete(db_ingredient)
    db.commit()
    
    logger.info(f"Ingredient nutrition deleted: {ingredient_name}")
    return {"message": f"Ingredient {ingredient_name} deleted successfully"}

@app.post("/api/nutrients", response_model=NutrientResponse)
async def create_nutrient(
    nutrient: NutrientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new nutrient tracking entry"""
    from models import Nutrient
    
    db_nutrient = Nutrient(
        user_id=current_user.id,
        nutrient_name=nutrient.nutrient_name,
        amount=nutrient.amount,
        unit=nutrient.unit,
        date_tracked=nutrient.date_tracked or datetime.utcnow(),
        notes=nutrient.notes
    )
    
    db.add(db_nutrient)
    db.commit()
    db.refresh(db_nutrient)
    
    logger.info(f"Nutrient tracked: {db_nutrient.id} by user {current_user.username}")
    return db_nutrient

@app.get("/api/nutrients", response_model=List[NutrientResponse])
async def get_nutrients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all nutrients for current user"""
    from models import Nutrient
    
    nutrients = db.query(Nutrient).filter(
        Nutrient.user_id == current_user.id
    ).order_by(Nutrient.date_tracked.desc()).all()
    
    return nutrients

@app.get("/api/nutrients/all", response_model=List[NutrientResponse])
async def get_all_nutrients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all nutrients (admin only)"""
    from models import Nutrient
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    nutrients = db.query(Nutrient).order_by(Nutrient.date_tracked.desc()).all()
    return nutrients

# ============================================================================
# SYSTEM SETTINGS ENDPOINTS
# ============================================================================

@app.post("/api/settings", response_model=SystemSettingsResponse)
async def create_setting(
    setting: SystemSettingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new system setting (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if setting already exists
    existing_setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == setting.setting_key
    ).first()
    
    if existing_setting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting with key '{setting.setting_key}' already exists"
        )
    
    db_setting = SystemSettings(
        setting_key=setting.setting_key,
        setting_value=setting.setting_value,
        setting_type=setting.setting_type,
        category=setting.category,
        description=setting.description,
        is_public=setting.is_public,
        is_editable=setting.is_editable,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    
    logger.info(f"Setting created: {db_setting.setting_key} by user {current_user.username}")
    return db_setting

@app.get("/api/settings", response_model=List[SystemSettingsResponse])
async def get_settings(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all system settings"""
    query = db.query(SystemSettings)
    
    # Non-admin users can only see public settings
    if current_user.role != "admin":
        query = query.filter(SystemSettings.is_public == True)
    
    # Filter by category if provided
    if category:
        query = query.filter(SystemSettings.category == category)
    
    settings = query.order_by(SystemSettings.category, SystemSettings.setting_key).all()
    return settings

@app.get("/api/settings/{setting_key}", response_model=SystemSettingsResponse)
async def get_setting(
    setting_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific system setting"""
    setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    # Non-admin users can only see public settings
    if current_user.role != "admin" and not setting.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return setting

@app.put("/api/settings/{setting_key}", response_model=SystemSettingsResponse)
async def update_setting(
    setting_key: str,
    setting_update: SystemSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a system setting (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db_setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == setting_key
    ).first()
    
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    if not db_setting.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This setting is not editable"
        )
    
    # Update fields
    for key, value in setting_update.dict(exclude_unset=True).items():
        setattr(db_setting, key, value)
    
    db_setting.updated_by = current_user.id
    db_setting.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_setting)
    
    logger.info(f"Setting updated: {db_setting.setting_key} by user {current_user.username}")
    return db_setting

@app.delete("/api/settings/{setting_key}")
async def delete_setting(
    setting_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a system setting (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db_setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == setting_key
    ).first()
    
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    if not db_setting.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This setting cannot be deleted"
        )
    
    db.delete(db_setting)
    db.commit()
    
    logger.info(f"Setting deleted: {setting_key} by user {current_user.username}")
    return {"message": f"Setting '{setting_key}' deleted successfully"}

@app.get("/api/settings/categories")
async def get_setting_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all setting categories"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    categories = db.query(SystemSettings.category).distinct().all()
    return [{"category": cat[0]} for cat in categories]

# ==========================================
# Analytics API Endpoints
# ==========================================

@app.get("/api/analytics/dashboard", response_model=AnalyticsDashboardData)
async def get_analytics_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard data"""
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta
    
    if current_user.role not in ["admin", "therapist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or therapist access required"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # User Statistics
    total_users = db.query(User).count()
    new_users = db.query(User).filter(User.created_at >= start_date).count()
    user_roles = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    
    user_stats = {
        "total_users": total_users,
        "new_users": new_users,
        "role_distribution": {role: count for role, count in user_roles}
    }
    
    # Appointment Statistics
    total_appointments = db.query(Appointment).count()
    recent_appointments = db.query(Appointment).filter(Appointment.appointment_datetime >= start_date).count()
    appointment_statuses = db.query(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status).all()
    
    appointment_stats = {
        "total_appointments": total_appointments,
        "recent_appointments": recent_appointments,
        "status_distribution": {status: count for status, count in appointment_statuses}
    }
    
    # Message Statistics
    total_messages = db.query(Message).count()
    recent_messages = db.query(Message).filter(Message.timestamp >= start_date).count()
    
    message_stats = {
        "total_messages": total_messages,
        "recent_messages": recent_messages
    }
    
    # Meal Statistics
    total_meals = db.query(Meal).count()
    recent_meals = db.query(Meal).filter(Meal.created_at >= start_date).count()
    meal_types = db.query(Meal.meal_type, func.count(Meal.id)).group_by(Meal.meal_type).all()
    
    meal_stats = {
        "total_meals": total_meals,
        "recent_meals": recent_meals,
        "type_distribution": {meal_type: count for meal_type, count in meal_types if meal_type}
    }
    
    # System Statistics
    total_ingredients = db.query(IngredientNutrition).count()
    total_settings = db.query(SystemSettings).count()
    
    system_stats = {
        "total_ingredients": total_ingredients,
        "total_settings": total_settings,
        "database_tables": ["users", "appointments", "messages", "meals", "nutrients", "ingredients", "settings"]
    }
    
    # Recent Activities (if activity tracking is enabled)
    recent_activities = []
    try:
        activities = db.query(UserActivity).filter(
            UserActivity.timestamp >= start_date
        ).order_by(desc(UserActivity.timestamp)).limit(20).all()
        recent_activities = [UserActivityResponse.from_orm(activity) for activity in activities]
    except:
        # Activity tracking might not be enabled yet
        pass
    
    return AnalyticsDashboardData(
        user_stats=user_stats,
        appointment_stats=appointment_stats,
        message_stats=message_stats,
        meal_stats=meal_stats,
        system_stats=system_stats,
        recent_activities=recent_activities,
        generated_at=datetime.utcnow()
    )

@app.get("/api/analytics/users", response_model=dict)
async def get_user_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user analytics"""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # User growth over time (by day)
    user_growth = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(
        func.date(User.created_at)
    ).order_by('date').all()
    
    # User roles distribution
    role_distribution = db.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    # Active users (users with recent appointments or messages)
    active_users = db.query(User.id).join(Appointment, User.id == Appointment.user_id).filter(
        Appointment.appointment_datetime >= start_date
    ).union(
        db.query(User.id).join(Message, User.id == Message.sender_id).filter(
            Message.timestamp >= start_date
        )
    ).distinct().count()
    
    return {
        "user_growth": [{"date": str(date), "count": count} for date, count in user_growth],
        "role_distribution": [{"role": role, "count": count} for role, count in role_distribution],
        "total_users": db.query(User).count(),
        "active_users": active_users,
        "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()}
    }

@app.get("/api/analytics/appointments", response_model=dict)
async def get_appointment_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed appointment analytics"""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    if current_user.role not in ["admin", "therapist"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or therapist access required"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Appointments over time
    appointment_trends = db.query(
        func.date(Appointment.appointment_datetime).label('date'),
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.appointment_datetime >= start_date
    ).group_by(
        func.date(Appointment.appointment_datetime)
    ).order_by('date').all()
    
    # Status distribution
    status_distribution = db.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).group_by(Appointment.status).all()
    
    # Top therapists by appointment count
    top_therapists = db.query(
        User.username,
        func.count(Appointment.id).label('appointment_count')
    ).join(
        Appointment, User.id == Appointment.therapist_id
    ).filter(
        Appointment.appointment_datetime >= start_date
    ).group_by(
        User.id, User.username
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(10).all()
    
    return {
        "appointment_trends": [{"date": str(date), "count": count} for date, count in appointment_trends],
        "status_distribution": [{"status": status, "count": count} for status, count in status_distribution],
        "top_therapists": [{"therapist": therapist, "count": count} for therapist, count in top_therapists],
        "total_appointments": db.query(Appointment).count(),
        "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()}
    }

@app.post("/api/analytics/activity", response_model=UserActivityResponse)
async def log_user_activity(
    activity: UserActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log user activity for analytics tracking"""
    
    new_activity = UserActivity(
        user_id=current_user.id,
        activity_type=activity.activity_type,
        activity_data=activity.activity_data,
        ip_address=activity.ip_address,
        user_agent=activity.user_agent,
        session_id=activity.session_id
    )
    
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    
    logger.info(f"Activity logged: {activity.activity_type} by user {current_user.username}")
    return UserActivityResponse.from_orm(new_activity)

@app.get("/api/analytics/activities", response_model=List[UserActivityResponse])
async def get_user_activities(
    days: int = 7,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent user activities"""
    from sqlalchemy import desc
    from datetime import datetime, timedelta
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    activities = db.query(UserActivity).filter(
        UserActivity.timestamp >= start_date
    ).order_by(desc(UserActivity.timestamp)).limit(limit).all()
    
    return [UserActivityResponse.from_orm(activity) for activity in activities]

@app.get("/api/analytics/system-metrics", response_model=List[SystemMetricsResponse])
async def get_system_metrics(
    category: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system metrics for analytics"""
    from sqlalchemy import desc
    from datetime import datetime, timedelta
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(SystemMetrics).filter(
        SystemMetrics.metric_date >= start_date
    )
    
    if category:
        query = query.filter(SystemMetrics.category == category)
    
    metrics = query.order_by(desc(SystemMetrics.metric_date)).all()
    
    return [SystemMetricsResponse.from_orm(metric) for metric in metrics]

# ============================================================================
# SECURITY ENDPOINTS
# ============================================================================

@app.get("/api/security/dashboard", response_model=SecurityDashboardData)
async def get_security_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security dashboard overview data"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get security statistics
    total_events = db.query(SecurityEvent).filter(
        SecurityEvent.timestamp >= start_date
    ).count()
    
    failed_logins = db.query(LoginAttempt).filter(
        LoginAttempt.attempted_at >= start_date,
        LoginAttempt.success == False
    ).count()
    
    active_alerts = db.query(SecurityAlert).filter(
        SecurityAlert.resolved == False
    ).count()
    
    high_risk_events = db.query(SecurityEvent).filter(
        SecurityEvent.timestamp >= start_date,
        SecurityEvent.risk_level.in_(["high", "critical"])
    ).count()
    
    # Get recent events
    recent_events = db.query(SecurityEvent).filter(
        SecurityEvent.timestamp >= start_date
    ).order_by(desc(SecurityEvent.timestamp)).limit(10).all()
    
    # Get recent login attempts
    recent_login_attempts = db.query(LoginAttempt).filter(
        LoginAttempt.attempted_at >= start_date
    ).order_by(desc(LoginAttempt.attempted_at)).limit(10).all()
    
    # Get recent alerts
    recent_alerts = db.query(SecurityAlert).filter(
        SecurityAlert.created_at >= start_date
    ).order_by(desc(SecurityAlert.created_at)).limit(10).all()
    
    # Calculate login success rate
    total_login_attempts = db.query(LoginAttempt).filter(
        LoginAttempt.attempted_at >= start_date
    ).count()
    
    successful_logins = db.query(LoginAttempt).filter(
        LoginAttempt.attempted_at >= start_date,
        LoginAttempt.success == True
    ).count()
    
    login_success_rate = (successful_logins / total_login_attempts * 100) if total_login_attempts > 0 else 0
    
    return SecurityDashboardData(
        total_events=total_events,
        failed_logins=failed_logins,
        active_alerts=active_alerts,
        high_risk_events=high_risk_events,
        recent_events=[SecurityEventResponse.from_orm(event) for event in recent_events],
        recent_login_attempts=[LoginAttemptResponse.from_orm(attempt) for attempt in recent_login_attempts],
        recent_alerts=[SecurityAlertResponse.from_orm(alert) for alert in recent_alerts],
        login_success_rate=round(login_success_rate, 2),
        generated_at=datetime.utcnow()
    )

@app.get("/api/security/events", response_model=List[SecurityEventResponse])
async def get_security_events(
    event_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security events with filtering"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(SecurityEvent).filter(SecurityEvent.timestamp >= start_date)
    
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    
    if risk_level:
        query = query.filter(SecurityEvent.risk_level == risk_level)
    
    events = query.order_by(desc(SecurityEvent.timestamp)).limit(limit).all()
    
    return [SecurityEventResponse.from_orm(event) for event in events]

@app.post("/api/security/events", response_model=SecurityEventResponse)
async def create_security_event(
    event: SecurityEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new security event"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db_event = SecurityEvent(
        event_type=event.event_type,
        event_category=event.event_category,
        user_id=current_user.id,
        ip_address=event.ip_address,
        user_agent=event.user_agent,
        endpoint=event.endpoint,
        method=event.method,
        status_code=event.status_code,
        details=event.details,
        risk_level=event.risk_level
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return SecurityEventResponse.from_orm(db_event)

@app.get("/api/security/login-attempts", response_model=List[LoginAttemptResponse])
async def get_login_attempts(
    success: Optional[bool] = None,
    username: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get login attempts with filtering"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(LoginAttempt).filter(LoginAttempt.attempted_at >= start_date)
    
    if success is not None:
        query = query.filter(LoginAttempt.success == success)
    
    if username:
        query = query.filter(LoginAttempt.username.ilike(f"%{username}%"))
    
    attempts = query.order_by(desc(LoginAttempt.attempted_at)).limit(limit).all()
    
    return [LoginAttemptResponse.from_orm(attempt) for attempt in attempts]

@app.get("/api/security/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[int] = None,
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(AuditLog).filter(AuditLog.timestamp >= start_date)
    
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    logs = query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
    
    return [AuditLogResponse.from_orm(log) for log in logs]

@app.get("/api/security/alerts", response_model=List[SecurityAlertResponse])
async def get_security_alerts(
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security alerts with filtering"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(SecurityAlert).filter(SecurityAlert.created_at >= start_date)
    
    if resolved is not None:
        query = query.filter(SecurityAlert.resolved == resolved)
    
    if severity:
        query = query.filter(SecurityAlert.severity == severity)
    
    if alert_type:
        query = query.filter(SecurityAlert.alert_type == alert_type)
    
    alerts = query.order_by(desc(SecurityAlert.created_at)).limit(limit).all()
    
    return [SecurityAlertResponse.from_orm(alert) for alert in alerts]

@app.post("/api/security/alerts", response_model=SecurityAlertResponse)
async def create_security_alert(
    alert: SecurityAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new security alert"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db_alert = SecurityAlert(
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        description=alert.description,
        ip_address=alert.ip_address,
        endpoint=alert.endpoint
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return SecurityAlertResponse.from_orm(db_alert)

@app.patch("/api/security/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: int,
    resolution_notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a security alert"""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security alert not found"
        )
    
    alert.resolved = True
    alert.resolved_by = current_user.id
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = resolution_notes
    
    db.commit()
    db.refresh(alert)
    
    return {"message": "Security alert resolved successfully", "alert_id": alert_id}

# ========================================
# PATIENT MANAGEMENT API ENDPOINTS
# ========================================

@app.get("/api/patients")
async def get_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patients assigned to current provider or all patients for admin"""
    
    if current_user.role == "admin":
        # Admin can see all patients
        patients_query = db.query(User).filter(User.role == "patient")
    else:
        # Providers can only see their assigned patients
        if current_user.role not in ["physician", "therapist", "health_coach"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only providers can access patient data"
            )
        
        # Get patients assigned to this provider
        patients_query = db.query(User).join(PatientProvider).filter(
            PatientProvider.provider_id == current_user.id,
            PatientProvider.relationship_status == "active",
            User.role == "patient"
        )
    
    patients = patients_query.all()
    
    # Add assignment info for providers
    patient_data = []
    for patient in patients:
        patient_info = {
            "id": patient.id,
            "username": patient.username,
            "email": patient.email,
            "created_at": patient.created_at,
            "assignments": []
        }
        
        # Get provider assignments for this patient
        assignments = db.query(PatientProvider).filter(
            PatientProvider.patient_id == patient.id,
            PatientProvider.relationship_status == "active"
        ).all()
        
        for assignment in assignments:
            provider = db.query(User).filter(User.id == assignment.provider_id).first()
            if provider:
                patient_info["assignments"].append({
                    "provider_id": provider.id,
                    "provider_name": provider.username,
                    "provider_type": assignment.provider_type,
                    "assigned_date": assignment.assigned_date
                })
        
        patient_data.append(patient_info)
    
    return {"patients": patient_data}

@app.post("/api/patients/{patient_id}/assign")
async def assign_patient_to_provider(
    patient_id: int,
    assignment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign patient to a provider (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can assign patients to providers"
        )
    
    provider_id = assignment_data.get("provider_id")
    provider_type = assignment_data.get("provider_type")
    notes = assignment_data.get("notes", "")
    
    # Validate patient exists
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Validate provider exists and has correct role
    provider = db.query(User).filter(User.id == provider_id).first()
    if not provider or provider.role not in ["physician", "therapist", "health_coach"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found or invalid provider type"
        )
    
    # Check if assignment already exists
    existing = db.query(PatientProvider).filter(
        PatientProvider.patient_id == patient_id,
        PatientProvider.provider_id == provider_id
    ).first()
    
    if existing:
        if existing.relationship_status == "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient is already assigned to this provider"
            )
        else:
            # Reactivate existing relationship
            existing.relationship_status = "active"
            existing.assigned_date = datetime.utcnow()
            existing.notes = notes
    else:
        # Create new assignment
        assignment = PatientProvider(
            patient_id=patient_id,
            provider_id=provider_id,
            provider_type=provider_type,
            notes=notes
        )
        db.add(assignment)
    
    db.commit()
    return {"message": "Patient assigned successfully"}

# ========================================
# HEALTH RECORDS API ENDPOINTS
# ========================================

@app.get("/api/health-records")
async def get_health_records(
    patient_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get health records for patients"""
    
    if current_user.role == "patient":
        # Patients can only see their own records
        records = db.query(HealthRecord).filter(HealthRecord.patient_id == current_user.id).order_by(desc(HealthRecord.record_date)).all()
    elif current_user.role in ["physician", "therapist", "health_coach"]:
        # Providers can see records for their assigned patients
        if patient_id:
            # Check if provider has access to this patient
            assignment = db.query(PatientProvider).filter(
                PatientProvider.patient_id == patient_id,
                PatientProvider.provider_id == current_user.id,
                PatientProvider.relationship_status == "active"
            ).first()
            
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this patient's records"
                )
            
            records = db.query(HealthRecord).filter(HealthRecord.patient_id == patient_id).order_by(desc(HealthRecord.record_date)).all()
        else:
            # Get records for all assigned patients
            assigned_patient_ids = db.query(PatientProvider.patient_id).filter(
                PatientProvider.provider_id == current_user.id,
                PatientProvider.relationship_status == "active"
            ).subquery()
            
            records = db.query(HealthRecord).filter(
                HealthRecord.patient_id.in_(assigned_patient_ids)
            ).order_by(desc(HealthRecord.record_date)).all()
    elif current_user.role == "admin":
        # Admin can see all records
        if patient_id:
            records = db.query(HealthRecord).filter(HealthRecord.patient_id == patient_id).order_by(desc(HealthRecord.record_date)).all()
        else:
            records = db.query(HealthRecord).order_by(desc(HealthRecord.record_date)).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access health records"
        )
    
    # Add patient and provider information
    records_data = []
    for record in records:
        patient = db.query(User).filter(User.id == record.patient_id).first()
        provider = db.query(User).filter(User.id == record.provider_id).first()
        
        record_data = {
            "id": record.id,
            "patient_id": record.patient_id,
            "patient_name": patient.username if patient else "Unknown",
            "provider_id": record.provider_id,
            "provider_name": provider.username if provider else "Unknown",
            "record_type": record.record_type,
            "title": record.title,
            "description": record.description,
            "height_cm": record.height_cm,
            "weight_kg": record.weight_kg,
            "blood_pressure_systolic": record.blood_pressure_systolic,
            "blood_pressure_diastolic": record.blood_pressure_diastolic,
            "heart_rate_bpm": record.heart_rate_bpm,
            "temperature_c": record.temperature_c,
            "symptoms": record.symptoms,
            "diagnosis": record.diagnosis,
            "treatment_plan": record.treatment_plan,
            "medications": record.medications,
            "follow_up_date": record.follow_up_date,
            "is_confidential": record.is_confidential,
            "is_emergency": record.is_emergency,
            "status": record.status,
            "record_date": record.record_date,
            "created_at": record.created_at
        }
        records_data.append(record_data)
    
    return {"health_records": records_data}

@app.post("/api/health-records")
async def create_health_record(
    record_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new health record (providers only)"""
    
    if current_user.role not in ["physician", "therapist", "health_coach", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can create health records"
        )
    
    patient_id = record_data.get("patient_id")
    
    # Validate patient exists
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if provider has access to this patient (unless admin)
    if current_user.role != "admin":
        assignment = db.query(PatientProvider).filter(
            PatientProvider.patient_id == patient_id,
            PatientProvider.provider_id == current_user.id,
            PatientProvider.relationship_status == "active"
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to create records for this patient"
            )
    
    # Create health record
    health_record = HealthRecord(
        patient_id=patient_id,
        provider_id=current_user.id,
        record_type=record_data.get("record_type", "consultation"),
        title=record_data.get("title", ""),
        description=record_data.get("description", ""),
        height_cm=record_data.get("height_cm"),
        weight_kg=record_data.get("weight_kg"),
        blood_pressure_systolic=record_data.get("blood_pressure_systolic"),
        blood_pressure_diastolic=record_data.get("blood_pressure_diastolic"),
        heart_rate_bpm=record_data.get("heart_rate_bpm"),
        temperature_c=record_data.get("temperature_c"),
        symptoms=record_data.get("symptoms"),
        diagnosis=record_data.get("diagnosis"),
        treatment_plan=record_data.get("treatment_plan"),
        medications=record_data.get("medications"),
        follow_up_date=record_data.get("follow_up_date"),
        is_confidential=record_data.get("is_confidential", False),
        is_emergency=record_data.get("is_emergency", False)
    )
    
    db.add(health_record)
    db.commit()
    db.refresh(health_record)
    
    return {"message": "Health record created successfully", "record_id": health_record.id}

# ========================================
# EARNINGS AND COMMISSION API ENDPOINTS
# ========================================

@app.get("/api/earnings")
async def get_earnings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get earnings records for current provider"""
    
    if current_user.role not in ["physician", "therapist", "health_coach", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can access earnings data"
        )
    
    if current_user.role == "admin":
        # Admin can see all earnings
        earnings = db.query(EarningsRecord).order_by(desc(EarningsRecord.service_date)).all()
    else:
        # Providers can only see their own earnings
        earnings = db.query(EarningsRecord).filter(
            EarningsRecord.provider_id == current_user.id
        ).order_by(desc(EarningsRecord.service_date)).all()
    
    # Add patient information
    earnings_data = []
    for earning in earnings:
        patient = db.query(User).filter(User.id == earning.patient_id).first() if earning.patient_id else None
        provider = db.query(User).filter(User.id == earning.provider_id).first()
        
        earning_data = {
            "id": earning.id,
            "provider_id": earning.provider_id,
            "provider_name": provider.username if provider else "Unknown",
            "patient_id": earning.patient_id,
            "patient_name": patient.username if patient else "N/A",
            "service_type": earning.service_type,
            "service_description": earning.service_description,
            "base_amount": earning.base_amount,
            "commission_rate": earning.commission_rate,
            "commission_amount": earning.commission_amount,
            "net_earnings": earning.net_earnings,
            "payment_status": earning.payment_status,
            "payment_method": earning.payment_method,
            "payment_date": earning.payment_date,
            "service_date": earning.service_date,
            "created_at": earning.created_at
        }
        earnings_data.append(earning_data)
    
    return {"earnings": earnings_data}

@app.post("/api/earnings")
async def create_earnings_record(
    earnings_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new earnings record"""
    
    if current_user.role not in ["physician", "therapist", "health_coach", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can create earnings records"
        )
    
    # Get commission structure for this provider role and service type
    commission_structure = db.query(CommissionStructure).filter(
        CommissionStructure.provider_role == current_user.role,
        CommissionStructure.service_type == earnings_data.get("service_type"),
        CommissionStructure.is_active == True
    ).first()
    
    base_amount = float(earnings_data.get("base_amount", 0))
    commission_rate = 0.0
    commission_amount = 0.0
    
    if commission_structure and base_amount >= commission_structure.minimum_amount:
        commission_rate = commission_structure.commission_rate
        commission_amount = base_amount * commission_rate
        
        # Apply maximum commission cap if set
        if commission_structure.maximum_commission and commission_amount > commission_structure.maximum_commission:
            commission_amount = commission_structure.maximum_commission
    
    net_earnings = base_amount - commission_amount
    
    # Create earnings record
    earnings_record = EarningsRecord(
        provider_id=current_user.id,
        patient_id=earnings_data.get("patient_id"),
        appointment_id=earnings_data.get("appointment_id"),
        service_type=earnings_data.get("service_type"),
        service_description=earnings_data.get("service_description", ""),
        base_amount=base_amount,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        net_earnings=net_earnings,
        service_date=datetime.fromisoformat(earnings_data.get("service_date", datetime.utcnow().isoformat()))
    )
    
    db.add(earnings_record)
    db.commit()
    db.refresh(earnings_record)
    
    return {"message": "Earnings record created successfully", "record_id": earnings_record.id}

@app.get("/api/commission-summary")
async def get_commission_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get commission summary for current provider"""
    
    if current_user.role not in ["physician", "therapist", "health_coach", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can access commission data"
        )
    
    if current_user.role == "admin":
        # Admin summary for all providers
        earnings = db.query(EarningsRecord).all()
    else:
        # Provider's own earnings
        earnings = db.query(EarningsRecord).filter(EarningsRecord.provider_id == current_user.id).all()
    
    # Calculate summary statistics
    total_earnings = sum(e.base_amount for e in earnings)
    total_commission = sum(e.commission_amount for e in earnings)
    net_earnings = sum(e.net_earnings for e in earnings)
    
    # Calculate by month (current year)
    current_year = datetime.now().year
    monthly_data = {}
    
    for earning in earnings:
        if earning.service_date.year == current_year:
            month_key = earning.service_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "gross_earnings": 0,
                    "commission": 0,
                    "net_earnings": 0,
                    "service_count": 0
                }
            
            monthly_data[month_key]["gross_earnings"] += earning.base_amount
            monthly_data[month_key]["commission"] += earning.commission_amount
            monthly_data[month_key]["net_earnings"] += earning.net_earnings
            monthly_data[month_key]["service_count"] += 1
    
    return {
        "summary": {
            "total_earnings": total_earnings,
            "total_commission": total_commission,
            "net_earnings": net_earnings,
            "total_services": len(earnings),
            "average_service_amount": total_earnings / len(earnings) if earnings else 0
        },
        "monthly_breakdown": monthly_data
    }

# =============================================
# ADMIN COMMISSION MANAGEMENT ENDPOINTS
# =============================================

@app.get("/api/admin/commission-structures")
async def get_all_commission_structures(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all commission structures (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    structures = db.query(CommissionStructure).all()
    return {"commission_structures": structures}

@app.post("/api/admin/commission-structures")
async def create_commission_structure(
    provider_type: str,
    service_type: str,
    commission_rate: float,
    flat_fee: Optional[float] = None,
    minimum_threshold: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new commission structure (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate commission rate
    if commission_rate < 0 or commission_rate > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Commission rate must be between 0 and 1"
        )
    
    new_structure = CommissionStructure(
        provider_type=provider_type,
        service_type=service_type,
        commission_rate=commission_rate,
        flat_fee=flat_fee,
        minimum_threshold=minimum_threshold
    )
    
    db.add(new_structure)
    db.commit()
    db.refresh(new_structure)
    
    return {"message": "Commission structure created successfully", "structure": new_structure}

@app.put("/api/admin/commission-structures/{structure_id}")
async def update_commission_structure(
    structure_id: int,
    commission_rate: Optional[float] = None,
    flat_fee: Optional[float] = None,
    minimum_threshold: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update commission structure (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    structure = db.query(CommissionStructure).filter(CommissionStructure.id == structure_id).first()
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission structure not found"
        )
    
    if commission_rate is not None:
        if commission_rate < 0 or commission_rate > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Commission rate must be between 0 and 1"
            )
        structure.commission_rate = commission_rate
    
    if flat_fee is not None:
        structure.flat_fee = flat_fee
    
    if minimum_threshold is not None:
        structure.minimum_threshold = minimum_threshold
    
    structure.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Commission structure updated successfully", "structure": structure}

@app.delete("/api/admin/commission-structures/{structure_id}")
async def delete_commission_structure(
    structure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete commission structure (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    structure = db.query(CommissionStructure).filter(CommissionStructure.id == structure_id).first()
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission structure not found"
        )
    
    db.delete(structure)
    db.commit()
    
    return {"message": "Commission structure deleted successfully"}

@app.get("/api/admin/earnings-overview")
async def get_earnings_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system-wide earnings overview (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get all earnings records
    earnings = db.query(EarningsRecord).all()
    
    # Calculate totals by provider type
    provider_totals = {}
    for earning in earnings:
        provider = db.query(User).filter(User.id == earning.provider_id).first()
        if provider:
            if provider.role not in provider_totals:
                provider_totals[provider.role] = {
                    "total_earnings": 0,
                    "total_commission": 0,
                    "service_count": 0
                }
            provider_totals[provider.role]["total_earnings"] += earning.base_amount
            provider_totals[provider.role]["total_commission"] += earning.commission_amount
            provider_totals[provider.role]["service_count"] += 1
    
    return {
        "total_system_earnings": sum(e.base_amount for e in earnings),
        "total_system_commission": sum(e.commission_amount for e in earnings),
        "provider_breakdown": provider_totals,
        "total_services": len(earnings)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
