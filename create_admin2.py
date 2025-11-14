"""
Create admin2 user with proper password hash
"""
import psycopg2
import bcrypt

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="mindlab_health",
    user="mindlab_admin",
    password="MindLab2024!Secure"
)

# Generate password hash
password = "admin123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

print(f"Password: {password}")
print(f"Hash: {hashed}")

# Delete existing admin2 if exists
cur = conn.cursor()
cur.execute("DELETE FROM users WHERE username = 'admin2';")
print(f"Deleted existing admin2 user")

# Insert new admin2 user
cur.execute(
    "INSERT INTO users (username, email, hashed_password, role, created_at) VALUES (%s, %s, %s, %s, NOW());",
    ('admin2', 'admin2@mindlabhealth.com', hashed, 'admin')
)

conn.commit()
print(f"✅ Created admin2 user successfully!")

# Verify
cur.execute("SELECT username, email, role FROM users WHERE username = 'admin2';")
result = cur.fetchone()
print(f"Verified: {result}")

cur.close()
conn.close()
