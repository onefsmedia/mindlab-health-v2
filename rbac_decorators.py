# Role-Based Access Control Decorators for FastAPI
# Add comprehensive permission checking to API endpoints

from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from models import User, Permission, RolePermission
from auth import get_current_user

def require_permission(permission_name: str):
    """Decorator to require specific permission for API endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user and db from kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            if not current_user.has_permission(permission_name, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """Decorator to require admin role for API endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check admin role
            if str(current_user.role) != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(allowed_roles: list):
    """Decorator to require specific roles for API endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check role
            if str(current_user.role) not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(current_user: User, db: Session):
    """Get all permissions for the current user"""
    return current_user.get_permissions(db)

def can_access_user_data(current_user: User, target_user_id: int, db: Session):
    """Check if user can access specific user data"""
    # Admin can access all user data
    if str(current_user.role) == "admin":
        return True
    
    # Users can access their own data
    if current_user.id == target_user_id:
        return True
    
    # Therapists and physicians can access assigned patients
    if str(current_user.role) in ["therapist", "physician", "health_coach"]:
        # Check if there's an appointment relationship
        from models import Appointment
        appointment = db.query(Appointment).filter(
            Appointment.therapist_id == current_user.id,
            Appointment.user_id == target_user_id
        ).first()
        return appointment is not None
    
    return False

def can_access_appointment(current_user: User, appointment_id: int, db: Session):
    """Check if user can access specific appointment"""
    from models import Appointment
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return False
    
    # Admin can access all appointments
    if str(current_user.role) == "admin":
        return True
    
    # Users can access their own appointments
    if appointment.user_id == current_user.id or appointment.therapist_id == current_user.id:
        return True
    
    return False