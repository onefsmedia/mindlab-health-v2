# Create Test Users for Role-Based Dashboard Testing
# This script creates test users for each role to demonstrate the RBAC system

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from auth import get_password_hash
import logging

# Database configuration
DATABASE_URL = "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5433/mindlab_health"

def create_test_users():
    """Create test users for each role"""
    engine = create_engine(DATABASE_URL)
    
    test_users = [
        {'username': 'physician1', 'email': 'physician@test.com', 'password': 'test123', 'role': 'physician'},
        {'username': 'therapist1', 'email': 'therapist@test.com', 'password': 'test123', 'role': 'therapist'},
        {'username': 'coach1', 'email': 'coach@test.com', 'password': 'test123', 'role': 'health_coach'},
        {'username': 'patient1', 'email': 'patient@test.com', 'password': 'test123', 'role': 'patient'},
        {'username': 'partner1', 'email': 'partner@test.com', 'password': 'test123', 'role': 'partner'},
    ]
    
    try:
        with engine.connect() as conn:
            for user_data in test_users:
                # Check if user already exists
                result = conn.execute(text("""
                    SELECT id FROM users WHERE username = :username OR email = :email
                """), {"username": user_data['username'], "email": user_data['email']})
                
                if result.fetchone():
                    print(f"⚠️  User {user_data['username']} already exists, skipping...")
                    continue
                
                # Hash the password
                hashed_password = get_password_hash(user_data['password'])
                
                # Insert the user
                conn.execute(text("""
                    INSERT INTO users (username, email, hashed_password, role)
                    VALUES (:username, :email, :hashed_password, :role)
                """), {
                    "username": user_data['username'],
                    "email": user_data['email'],
                    "hashed_password": hashed_password,
                    "role": user_data['role']
                })
                
                print(f"✅ Created user: {user_data['username']} ({user_data['role']})")
            
            conn.commit()
            
            print("\n🎯 Test Users Created Successfully!")
            print("\nYou can now test different role dashboards with these credentials:")
            print("=" * 60)
            for user_data in test_users:
                print(f"Role: {user_data['role'].upper():<12} | Username: {user_data['username']:<12} | Password: {user_data['password']}")
            print("=" * 60)
            print("🔐 Admin user: username=admin, password=admin123")
            
    except Exception as e:
        print(f"❌ Failed to create test users: {e}")
        raise

if __name__ == "__main__":
    create_test_users()