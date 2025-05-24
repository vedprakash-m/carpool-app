# create_admin.py
# Python script to generate admin user credentials

import bcrypt
import uuid
import json
from datetime import datetime
import sys

# Admin user details
email = "admin@example.com"
full_name = "Admin User"
password = "Admin@0987654"

# Generate a unique ID for the user
user_id = str(uuid.uuid4())
timestamp = datetime.utcnow().isoformat()

# Hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

hashed_password = hash_password(password)

# Create the user document in JSON format
user_doc = {
    "id": user_id,
    "email": email,
    "full_name": full_name,
    "role": "ADMIN",
    "hashed_password": hashed_password,
    "created_at": timestamp,
    "updated_at": timestamp,
    "is_active_driver": False
}

# Print the user document
print(json.dumps(user_doc, indent=2))

print("\n============================================================")
print("    Admin User Credentials")
print("============================================================")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"User ID: {user_id}")
print("============================================================")
print("\nYou can use these credentials to log in to the application.")
print("To insert this user into your Cosmos DB, you'll need to use the Azure Portal")
print("or the appropriate Azure CLI commands with your specific Cosmos DB details.")
