import psycopg2

# Connect to database
conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/mindlab_health')
cur = conn.cursor()

# Get all features
print("\n" + "="*80)
print("ALL SUBSCRIPTION FEATURES")
print("="*80)
cur.execute('SELECT id, feature_name, description, category FROM subscription_features ORDER BY id')
features = cur.fetchall()
for row in features:
    print(f"ID: {row[0]:2} | Name: {row[1]:30} | Category: {row[3]:15} | Desc: {row[2]}")

# Get plan-feature assignments
print("\n" + "="*80)
print("SUBSCRIPTION PLANS WITH THEIR FEATURES")
print("="*80)
cur.execute('''
    SELECT 
        sp.id,
        sp.plan_name,
        sp.price_monthly,
        sf.feature_name
    FROM subscription_plans sp
    LEFT JOIN subscription_plan_features spf ON sp.id = spf.plan_id
    LEFT JOIN subscription_features sf ON spf.feature_id = sf.id
    ORDER BY sp.id, sf.feature_name
''')
assignments = cur.fetchall()

current_plan = None
for row in assignments:
    plan_id, plan_name, price, feature_name = row
    if current_plan != plan_id:
        print(f"\n📦 Plan {plan_id}: {plan_name} (${price:.2f}/month)")
        current_plan = plan_id
    if feature_name:
        print(f"   ✓ {feature_name}")
    else:
        print(f"   (No features assigned)")

conn.close()
print("\n" + "="*80)
