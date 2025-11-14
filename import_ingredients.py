"""
Bulk import ingredient nutrition data from CSV file
"""
import sys
import os
import csv
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import IngredientNutrition, Base
import local_config

def import_ingredients_from_csv(csv_file_path):
    """Import ingredients from CSV file"""
    
    # Create database connection
    engine = create_engine(local_config.LOCAL_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Read CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            imported_count = 0
            updated_count = 0
            
            for row in csv_reader:
                ingredient_name = row['ingredient_name'].strip()
                
                # Check if ingredient already exists
                existing = session.query(IngredientNutrition).filter_by(
                    ingredient_name=ingredient_name
                ).first()
                
                if existing:
                    # Update existing ingredient
                    existing.serving_size = row['serving_size']
                    existing.energy_kcal = float(row['energy_kcal']) if row['energy_kcal'] else None
                    existing.protein_g = float(row['protein_g']) if row['protein_g'] else None
                    existing.carb_g = float(row['carb_g']) if row['carb_g'] else None
                    existing.fat_g = float(row['fat_g']) if row['fat_g'] else None
                    existing.fiber_g = float(row['fiber_g']) if row['fiber_g'] else None
                    existing.sugar_g = float(row['sugar_g']) if row['sugar_g'] else None
                    existing.sodium_mg = float(row['sodium_mg']) if row['sodium_mg'] else None
                    existing.cholesterol_mg = float(row['cholesterol_mg']) if row['cholesterol_mg'] else None
                    existing.calcium_mg = float(row['calcium_mg']) if row['calcium_mg'] else None
                    existing.iron_mg = float(row['iron_mg']) if row['iron_mg'] else None
                    existing.potassium_mg = float(row['potassium_mg']) if row['potassium_mg'] else None
                    existing.vitamin_a_mcg = float(row['vitamin_a_mcg']) if row['vitamin_a_mcg'] else None
                    existing.vitamin_c_mg = float(row['vitamin_c_mg']) if row['vitamin_c_mg'] else None
                    existing.vitamin_d_mcg = float(row['vitamin_d_mcg']) if row['vitamin_d_mcg'] else None
                    
                    updated_count += 1
                    print(f"  Updated: {ingredient_name}")
                else:
                    # Create new ingredient
                    new_ingredient = IngredientNutrition(
                        ingredient_name=ingredient_name,
                        serving_size=row['serving_size'],
                        energy_kcal=float(row['energy_kcal']) if row['energy_kcal'] else None,
                        protein_g=float(row['protein_g']) if row['protein_g'] else None,
                        carb_g=float(row['carb_g']) if row['carb_g'] else None,
                        fat_g=float(row['fat_g']) if row['fat_g'] else None,
                        fiber_g=float(row['fiber_g']) if row['fiber_g'] else None,
                        sugar_g=float(row['sugar_g']) if row['sugar_g'] else None,
                        sodium_mg=float(row['sodium_mg']) if row['sodium_mg'] else None,
                        cholesterol_mg=float(row['cholesterol_mg']) if row['cholesterol_mg'] else None,
                        calcium_mg=float(row['calcium_mg']) if row['calcium_mg'] else None,
                        iron_mg=float(row['iron_mg']) if row['iron_mg'] else None,
                        potassium_mg=float(row['potassium_mg']) if row['potassium_mg'] else None,
                        vitamin_a_mcg=float(row['vitamin_a_mcg']) if row['vitamin_a_mcg'] else None,
                        vitamin_c_mg=float(row['vitamin_c_mg']) if row['vitamin_c_mg'] else None,
                        vitamin_d_mcg=float(row['vitamin_d_mcg']) if row['vitamin_d_mcg'] else None
                    )
                    
                    session.add(new_ingredient)
                    imported_count += 1
                    print(f"  Added: {ingredient_name}")
            
            # Commit all changes
            session.commit()
            
            print(f"\n✅ Import completed successfully!")
            print(f"   New ingredients: {imported_count}")
            print(f"   Updated ingredients: {updated_count}")
            print(f"   Total processed: {imported_count + updated_count}")
            
    except Exception as e:
        session.rollback()
        print(f"\n❌ Import failed: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    # Default CSV file path
    csv_file = r"C:\Users\onefs\Downloads\ingredient_nutrition_bulk_import_template.csv"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    print(f"Importing ingredients from: {csv_file}")
    print("="* 60)
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)
    
    import_ingredients_from_csv(csv_file)
