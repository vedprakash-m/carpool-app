# simple_admin_creator.py
# A simplified script to create an admin user in Cosmos DB

import os
import bcrypt
import uuid
from datetime import datetime
from azure.cosmos import CosmosClient

print("================================================================")
print("    Admin User Creation for Carpool Management App")
print("================================================================")

# Admin user details
email = "admin@example.com"
full_name = "Admin User"
password = "Admin@0987654"

# Generate UUID and timestamps
user_id = str(uuid.uuid4())
timestamp = datetime.utcnow().isoformat()

# Hash the password using bcrypt
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
print(f"Generated password hash: {hashed_password}")

# Create user document
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

# Ask for Cosmos DB details
print("\nPlease provide your Azure Cosmos DB information:")
cosmos_endpoint = input("Cosmos DB Endpoint URL: ")
cosmos_key = input("Cosmos DB Key: ")
cosmos_database = input("Cosmos DB Database Name: ")

try:
    # Connect to Cosmos DB
    print("\nConnecting to Cosmos DB...")
    client = CosmosClient(cosmos_endpoint, cosmos_key)
    database = client.get_database_client(cosmos_database)
    container = database.get_container_client("users")
    
    # Insert user
    print("Inserting admin user...")
    container.create_item(body=user_doc)
    
    print("\n================================================================")
    print("SUCCESS! Admin user created successfully!")
    print("================================================================")
    print("You can now log in with:")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"User ID: {user_id}")
    
except Exception as e:
    print(f"\nERROR: Failed to create admin user: {str(e)}")
    
print("\n================================================================")
