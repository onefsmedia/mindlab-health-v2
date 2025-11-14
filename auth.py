"""
Authentication Module for MindLab Health
Implements bcrypt password hashing and JWT token authentication.
"""

import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
import os

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic models
class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Decoded JWT token data."""
    username: Optional[str] = None


# Password hashing functions using bcrypt directly
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password
        hashed_password: The bcrypt hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Convert password to bytes
        password_bytes = plain_password.encode('utf-8')
        
        # Truncate to 72 bytes (bcrypt limit)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Convert hash to bytes if it's a string
        if isinstance(hashed_password, str):
            hash_bytes = hashed_password.encode('utf-8')
        else:
            hash_bytes = hashed_password
        
        # Use bcrypt directly
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password
    
    Returns:
        The bcrypt hashed password
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Truncate to 72 bytes (bcrypt limit)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


# JWT token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The payload data to encode (usually {"sub": username})
        expires_delta: Optional custom expiration time
    
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token to decode
    
    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
        
        return TokenData(username=username)
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: The JWT token from the Authorization header
    
    Returns:
        User object if authenticated
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from sqlalchemy.orm import Session
    import sys
    import os
    import importlib
    # Import get_db from the main application module
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main_module = importlib.import_module("07_main")
    get_db = main_module.get_db
    from models import User
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    # Get database session
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.username == token_data.username).first()
        
        if user is None:
            raise credentials_exception
        
        return user
    finally:
        db.close()


# Validation functions
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: The password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 72:
        return False, "Password must not exceed 72 characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.
    
    Args:
        username: The username to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    
    if not username[0].isalpha():
        return False, "Username must start with a letter"
    
    if not all(c.isalnum() or c in '_-' for c in username):
        return False, "Username can only contain letters, numbers, underscore, and hyphen"
    
    return True, ""
