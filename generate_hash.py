"""
Generate bcrypt hash for admin123 password
"""
import bcrypt

password = "admin123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(f"Password: {password}")
print(f"Hash: {hashed.decode('utf-8')}")
