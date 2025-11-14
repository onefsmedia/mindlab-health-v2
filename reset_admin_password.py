"""
Reset admin user password
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

# Generate password hash for admin123
password = "admin123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

print(f"Password: {password}")
print(f"New Hash: {hashed}")

# Update admin user password
cur = conn.cursor()
cur.execute(
    "UPDATE users SET hashed_password = %s WHERE username = 'admin';",
    (hashed,)
)

conn.commit()
print(f"✅ Updated admin password successfully!")

# Verify
cur.execute("SELECT username, email, role FROM users WHERE username = 'admin';")
result = cur.fetchone()
print(f"Verified: {result}")

cur.close()
conn.close()