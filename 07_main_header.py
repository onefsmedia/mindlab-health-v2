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

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mindlab:mindlab123@localhost:5432/mindlab_health")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mindlab_health")
POSTGRES_USER = os.getenv("POSTGRES_USER", "mindlab")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mindlab123")

# Construct DATABASE_URL if individual components are provided
if not DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Secret key for JWT tokens
SECRET_KEY = os.getenv("SECRET_KEY", "mindlab-health-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")