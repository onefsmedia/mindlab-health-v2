#!/usr/bin/env python3

from sqlalchemy import create_engine
from models import Base

# Create database connection - use correct credentials from 07_main.py
DATABASE_URL = 'postgresql://mindlab_admin:MindLab2024!Secure@host.containers.internal:5433/mindlab_health'
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(bind=engine)
print('Security tables created successfully!')