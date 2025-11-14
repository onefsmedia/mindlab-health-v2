"""
Verify System Status API and Database Connection
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check (no auth required)"""
    print("🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login():
    """Login and get authentication token"""
    print("\n🔐 Testing Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/token",
            data={
                "username": "admin2",
                "password": "admin123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful for user: {data.get('username', 'admin2')}")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_system_status(token):
    """Test system status endpoint with authentication"""
    print("\n📊 Testing System Status Endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/system/status", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ System Status Retrieved:")
            print(f"   Database Type: {data['database']['type']}")
            print(f"   Database Status: {data['database']['status']}")
            print(f"   Total Users: {data['statistics']['total_users']}")
            print(f"   Total Ingredients: {data['statistics']['total_ingredients']}")
            print(f"   Total Nutrients: {data['statistics']['total_nutrients']}")
            print(f"   Total Meals: {data['statistics']['total_meals']}")
            print(f"   Total Appointments: {data['statistics']['total_appointments']}")
            
            # Verify PostgreSQL
            if data['database']['type'] == 'PostgreSQL':
                print("\n🎉 SUCCESS: Application is running on PostgreSQL!")
                return True
            else:
                print(f"\n⚠️  WARNING: Expected PostgreSQL, got {data['database']['type']}")
                return False
        else:
            print(f"❌ System status failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ingredients(token):
    """Test ingredient nutrition endpoint"""
    print("\n🥗 Testing Ingredient Nutrition Endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/ingredient-nutrition", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ingredients Retrieved: {len(data)} total")
            if len(data) > 0:
                sample = data[0]
                print(f"   Sample: {sample['ingredient_name']}")
                print(f"   Category: {sample.get('main_category', 'N/A')}")
                print(f"   Energy: {sample.get('energy_kcal', 0)} kcal")
                print(f"   Vitamin B12: {sample.get('vitamin_b12_mcg', 0)} mcg")
                print(f"   Omega-3: {sample.get('omega3_g', 0)} g")
            return True
        else:
            print(f"❌ Ingredients endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("MindLab Health System Verification")
    print("=" * 60)
    
    # Test 1: Health Check
    health_ok = test_health_check()
    
    # Test 2: Login
    token = test_login()
    
    if token:
        # Test 3: System Status
        status_ok = test_system_status(token)
        
        # Test 4: Ingredients
        ingredients_ok = test_ingredients(token)
        
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Health Check:     {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Authentication:   {'✅ PASS' if token else '❌ FAIL'}")
        print(f"System Status:    {'✅ PASS' if status_ok else '❌ FAIL'}")
        print(f"Ingredients API:  {'✅ PASS' if ingredients_ok else '❌ FAIL'}")
        print("=" * 60)
        
        if all([health_ok, token, status_ok, ingredients_ok]):
            print("\n🎉 ALL TESTS PASSED! System is ready.")
        else:
            print("\n⚠️  Some tests failed. Check logs above.")
    else:
        print("\n❌ Cannot proceed without authentication.")

if __name__ == "__main__":
    main()
