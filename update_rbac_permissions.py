"""
Update RBAC permissions for new modules
=======================================
Adds permissions for:
- Patient management
- Health records
- Earnings & commission
"""

import psycopg2
from datetime import datetime

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="mindlab_health",
        user="mindlab_admin",
        password="MindLab2024!Secure"
    )

def update_permissions():
    """Update RBAC permissions for new modules"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("🔄 Updating RBAC permissions...")
        
        # 1. Add new permissions for patient management
        patient_permissions = [
            ('patients.view_assigned', 'View assigned patients', 'patients', 'view'),
            ('patients.view_all', 'View all patients', 'patients', 'view'),
            ('patients.assign', 'Assign patients to providers', 'patients', 'assign'),
            ('patients.manage', 'Manage patient assignments', 'patients', 'manage'),
        ]
        
        # 2. Add new permissions for health records
        health_record_permissions = [
            ('health_records.view_own', 'View own health records', 'health_records', 'view'),
            ('health_records.view_assigned', 'View assigned patient records', 'health_records', 'view'),
            ('health_records.view_all', 'View all health records', 'health_records', 'view'),
            ('health_records.create', 'Create health records', 'health_records', 'create'),
            ('health_records.edit_own', 'Edit own created records', 'health_records', 'edit'),
            ('health_records.edit_assigned', 'Edit records for assigned patients', 'health_records', 'edit'),
            ('health_records.delete', 'Delete health records', 'health_records', 'delete'),
        ]
        
        # 3. Add new permissions for earnings
        earnings_permissions = [
            ('earnings.view_own', 'View own earnings', 'earnings', 'view'),
            ('earnings.view_all', 'View all earnings', 'earnings', 'view'),
            ('earnings.create', 'Create earnings records', 'earnings', 'create'),
            ('earnings.manage', 'Manage earnings and payments', 'earnings', 'manage'),
            ('commission.view', 'View commission structure', 'commission', 'view'),
            ('commission.manage', 'Manage commission rates', 'commission', 'manage'),
        ]
        
        # 4. Enhanced nutrition permissions
        enhanced_nutrition_permissions = [
            ('nutrition.view_assigned', 'View nutrition for assigned patients', 'nutrition', 'view'),
            ('nutrition.create_plans', 'Create nutrition plans', 'nutrition', 'create'),
            ('nutrition.edit_plans', 'Edit nutrition plans', 'nutrition', 'edit'),
        ]
        
        # 5. Enhanced meal permissions
        enhanced_meal_permissions = [
            ('meals.view_assigned', 'View meals for assigned patients', 'meals', 'view'),
            ('meals.create_plans', 'Create meal plans', 'meals', 'create'),
            ('meals.edit_plans', 'Edit meal plans', 'meals', 'edit'),
        ]
        
        # Combine all permissions
        all_new_permissions = (patient_permissions + health_record_permissions + 
                              earnings_permissions + enhanced_nutrition_permissions + 
                              enhanced_meal_permissions)
        
        # Insert new permissions
        print("📋 Adding new permissions...")
        for name, description, module, action in all_new_permissions:
            cur.execute("""
                INSERT INTO permissions (name, description, module, action)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET 
                    description = EXCLUDED.description,
                    module = EXCLUDED.module,
                    action = EXCLUDED.action;
            """, (name, description, module, action))
        
        # 6. Update role permissions
        print("👥 Updating role permissions...")
        
        # Get permission IDs
        cur.execute("SELECT id, name FROM permissions;")
        permission_map = {name: pid for pid, name in cur.fetchall()}
        
        # Role-based permission assignments
        role_permissions = {
            'admin': [
                # All existing permissions plus new ones
                'patients.view_all', 'patients.assign', 'patients.manage',
                'health_records.view_all', 'health_records.create', 'health_records.edit_assigned', 'health_records.delete',
                'earnings.view_all', 'earnings.manage', 'commission.view', 'commission.manage',
                'nutrition.view_assigned', 'nutrition.create_plans', 'nutrition.edit_plans',
                'meals.view_assigned', 'meals.create_plans', 'meals.edit_plans'
            ],
            'physician': [
                'patients.view_assigned',
                'health_records.view_assigned', 'health_records.create', 'health_records.edit_assigned',
                'earnings.view_own', 'earnings.create',
                'nutrition.view_assigned', 'nutrition.create_plans', 'nutrition.edit_plans',
                'meals.view_assigned', 'meals.create_plans', 'meals.edit_plans'
            ],
            'therapist': [
                'patients.view_assigned',
                'health_records.view_assigned', 'health_records.create', 'health_records.edit_assigned',
                'earnings.view_own', 'earnings.create',
                'nutrition.view_assigned',
                'meals.view_assigned'
            ],
            'health_coach': [
                'patients.view_assigned',
                'health_records.view_assigned', 'health_records.create', 'health_records.edit_assigned',
                'earnings.view_own', 'earnings.create',
                'nutrition.view_assigned', 'nutrition.create_plans', 'nutrition.edit_plans',
                'meals.view_assigned', 'meals.create_plans', 'meals.edit_plans'
            ],
            'patient': [
                'health_records.view_own',
                'nutrition.view',
                'meals.view_own'
            ],
            'partner': [
                # Partners have limited access
            ]
        }
        
        # Assign permissions to roles
        for role, permissions in role_permissions.items():
            for permission_name in permissions:
                if permission_name in permission_map:
                    permission_id = permission_map[permission_name]
                    cur.execute("""
                        INSERT INTO role_permissions (role, permission_id)
                        VALUES (%s, %s)
                        ON CONFLICT (role, permission_id) DO NOTHING;
                    """, (role, permission_id))
        
        conn.commit()
        print("✅ RBAC permissions updated successfully!")
        
        # Print summary
        print("\n📊 Permission Update Summary:")
        cur.execute("SELECT COUNT(*) FROM permissions;")
        total_permissions = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM role_permissions;")
        total_role_permissions = cur.fetchone()[0]
        
        print(f"  • Total permissions: {total_permissions}")
        print(f"  • Total role assignments: {total_role_permissions}")
        
        # Show new module counts
        new_modules = ['patients', 'health_records', 'earnings', 'commission']
        for module in new_modules:
            cur.execute("SELECT COUNT(*) FROM permissions WHERE module = %s;", (module,))
            count = cur.fetchone()[0]
            print(f"  • {module} permissions: {count}")
        
    except Exception as e:
        print(f"❌ Permission update failed: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_permissions()