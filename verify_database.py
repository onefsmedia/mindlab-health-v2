#!/usr/bin/env python3
"""
Database Verification Script
Check PostgreSQL connection and data
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import User, Meal, Nutrient, IngredientNutrition

def verify_database():
    """Verify PostgreSQL database connection and data"""
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL", "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5432/mindlab_health")
    
    print("=" * 80)
    print("🔍 Database Verification")
    print("=" * 80)
    print(f"\n📡 Connecting to: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    try:
        # Create engine
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version[:50]}...")
        
        # Count records in each table
        print(f"\n📊 Record Counts:")
        
        tables = [
            (User, "Users"),
            (Meal, "Meals"),
            (Nutrient, "Nutrients"),
            (IngredientNutrition, "Ingredient Nutrition")
        ]
        
        for model, name in tables:
            try:
                count = session.query(model).count()
                print(f"   {name:25} {count:>5} records")
            except Exception as e:
                print(f"   {name:25} ❌ Error: {str(e)[:40]}")
        
        # Check admin user exists
        print(f"\n👤 Admin User Check:")
        admin = session.query(User).filter_by(username="admin").first()
        if admin:
            print(f"   ✅ Admin user exists (ID: {admin.id}, Email: {admin.email})")
        else:
            print(f"   ⚠️  Admin user not found (will be created on app startup)")
        
        # Show sample meals
        meals = session.query(Meal).limit(3).all()
        if meals:
            print(f"\n🍽️  Sample Meals:")
            for meal in meals:
                print(f"   - Week {meal.week_number}, Day {meal.day_number}: {meal.meal_type} - {meal.meal_name}")
        
        # Show sample ingredients
        ingredients = session.query(IngredientNutrition).limit(3).all()
        if ingredients:
            print(f"\n🥕 Sample Ingredients:")
            for ing in ingredients:
                print(f"   - {ing.ingredient_name}: {ing.calories} cal, {ing.protein}g protein")
        
        print(f"\n✅ Database verification complete!")
        
    except Exception as e:
        print(f"\n❌ Database connection failed!")
        print(f"   Error: {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check PostgreSQL is running: podman ps | Select-String postgres")
        print(f"   2. Check connection string is correct")
        print(f"   3. Verify credentials")
        return False
    finally:
        session.close()
        engine.dispose()
    
    print("=" * 80)
    return True

if __name__ == "__main__":
    verify_database()
