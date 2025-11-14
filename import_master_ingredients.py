#!/usr/bin/env python3
"""
Import Master Ingredients Database from CSV into PostgreSQL
"""
import csv
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import IngredientNutrition

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mindlab_admin:MindLab2024!Secure@localhost:5433/mindlab_health")

# Create database connection
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_numeric_value(value):
    """Convert CSV value to float, handling empty strings and errors"""
    if not value or value.strip() == "" or value.strip().lower() == "na":
        return 0.0
    try:
        # Remove any whitespace
        cleaned = value.strip()
        return float(cleaned)
    except ValueError:
        print(f"Warning: Could not convert '{value}' to float, using 0.0")
        return 0.0

def import_csv(csv_path):
    """Import ingredients from CSV file"""
    db = SessionLocal()
    
    try:
        # Try different encodings
        encodings_to_try = ['utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        csvfile = None
        
        for encoding in encodings_to_try:
            try:
                csvfile = open(csv_path, 'r', encoding=encoding)
                # Test read first line
                csvfile.readline()
                csvfile.seek(0)
                print(f"✓ Successfully opened CSV with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                if csvfile:
                    csvfile.close()
                continue
        
        if not csvfile:
            raise Exception("Could not open CSV file with any encoding")
        
        with csvfile:
            # Use DictReader to map column names to values
            reader = csv.DictReader(csvfile)
            
            imported_count = 0
            skipped_count = 0
            
            for index, row in enumerate(reader, start=1):
                # Check if ingredient already exists
                ingredient_name = row.get('Ingredient_Name', '').strip()
                if not ingredient_name:
                    print(f"Row {index}: Skipping - no ingredient name")
                    skipped_count += 1
                    continue
                
                existing = db.query(IngredientNutrition).filter(
                    IngredientNutrition.ingredient_name == ingredient_name
                ).first()
                
                if existing:
                    print(f"Row {index}: Skipping '{ingredient_name}' - already exists")
                    skipped_count += 1
                    continue
                
                # Create new ingredient record
                ingredient = IngredientNutrition(
                    # Identifiers
                    ingredient_id=row.get('Ingredient_ID', '').strip(),
                    unique_id=row.get('Unique_ID', '').strip(),
                    ingredient_name=ingredient_name,
                    index_number=index,
                    
                    # Classification
                    main_category=row.get('Main_Category', '').strip(),
                    sub_category=row.get('Sub_Category', '').strip(),
                    state=row.get('State', '').strip(),
                    
                    # Health information
                    health_benefits=row.get('Health_Benefits', '').strip(),
                    phytochemicals=row.get('Phytochemicals / Antioxidants / Healing', '').strip(),
                    source_notes=row.get('Source/Notes', '').strip(),
                    reference_primary=row.get('Reference_Primary', '').strip(),
                    
                    # Basic macronutrients (per 100g)
                    serving_size="100g",
                    energy_kcal=clean_numeric_value(row.get('Energy_kcal', '0')),
                    protein_g=clean_numeric_value(row.get('Protein_g', '0')),
                    fat_g=clean_numeric_value(row.get('Fat_g', '0')),
                    carb_g=clean_numeric_value(row.get('Carb_g', '0')),
                    fiber_g=clean_numeric_value(row.get('Fiber_g', '0')),
                    sugar_g=0.0,  # Not in CSV
                    
                    # Minerals
                    calcium_mg=clean_numeric_value(row.get('Calcium_mg', '0')),
                    iron_mg=clean_numeric_value(row.get('Iron_mg', '0')),
                    zinc_mg=clean_numeric_value(row.get('Zinc_mg', '0')),
                    magnesium_mg=clean_numeric_value(row.get('Magnesium_mg', '0')),
                    potassium_mg=clean_numeric_value(row.get('Potassium_mg', '0')),
                    sodium_mg=0.0,  # Not in CSV
                    cholesterol_mg=0.0,  # Not in CSV
                    
                    # Vitamins
                    vitamin_a_mcg=clean_numeric_value(row.get('VitaminA_µg', '0')),
                    vitamin_c_mg=clean_numeric_value(row.get('VitaminC_mg', '0')),
                    vitamin_d_mcg=0.0,  # Not in CSV
                    vitamin_e_mg=clean_numeric_value(row.get('VitaminE_mg', '0')),
                    vitamin_k_mcg=clean_numeric_value(row.get('VitaminK_µg', '0')),
                    
                    # B Vitamins
                    vitamin_b1_mg=clean_numeric_value(row.get('VitaminB1_mg', '0')),
                    vitamin_b2_mg=clean_numeric_value(row.get('VitaminB2_mg', '0')),
                    vitamin_b3_mg=clean_numeric_value(row.get('VitaminB3_mg', '0')),
                    vitamin_b5_mg=clean_numeric_value(row.get('Pantothenic_B5_mg', '0')),
                    vitamin_b6_mg=clean_numeric_value(row.get('VitaminB6_mg', '0')),
                    vitamin_b9_mcg=clean_numeric_value(row.get('Folate_B9_µg', '0')),
                    vitamin_b12_mcg=clean_numeric_value(row.get('VitaminB12_µg', '0')),
                    
                    # Essential fatty acids
                    omega3_g=clean_numeric_value(row.get('Omega3_g', '0')),
                    omega6_g=0.0,  # Not in CSV
                    
                    # Timestamps
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(ingredient)
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"Imported {imported_count} ingredients...")
                    db.commit()
            
            # Final commit
            db.commit()
            
            print(f"\n✅ Import complete!")
            print(f"   - Successfully imported: {imported_count} ingredients")
            print(f"   - Skipped (duplicates/invalid): {skipped_count}")
            print(f"   - Total rows processed: {imported_count + skipped_count}")
            
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    csv_file = "Master_Ingredients_Database.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found")
        sys.exit(1)
    
    print(f"Starting import from {csv_file}...")
    import_csv(csv_file)
