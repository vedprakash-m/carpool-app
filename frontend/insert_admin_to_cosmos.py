# insert_admin_to_cosmos.py
# Python script to insert an admin user into Cosmos DB

import os
import json
import sys
from azure.cosmos import CosmosClient, exceptions

# Admin user details
password = "Admin@0987654"  # The actual password to use

# Generate a fresh password hash using bcrypt
import bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

hashed_password = hash_password(password)

admin_user = {
    "id": "f1321b8a-c55c-4a6c-9e0d-df8e3a764b8b",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "hashed_password": hashed_password,  # Fresh hash
    "created_at": "2025-05-23T05:52:49.558443",
    "updated_at": "2025-05-23T05:52:49.558443",
    "is_active_driver": False
}

# Get Cosmos DB connection details
def get_cosmos_details():
    # Try to read from .env file first
    cosmos_endpoint = None
    cosmos_key = None
    cosmos_database = None
    
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
    if os.path.exists(env_file_path):
        print(f"Loading environment variables from {env_file_path}")
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.startswith('COSMOS_ENDPOINT='):
                    cosmos_endpoint = line.strip().split('=', 1)[1]
                elif line.startswith('COSMOS_KEY='):
                    cosmos_key = line.strip().split('=', 1)[1]
                elif line.startswith('COSMOS_DATABASE='):
                    cosmos_database = line.strip().split('=', 1)[1]
    
    # If not found in .env, try environment variables
    cosmos_endpoint = cosmos_endpoint or os.environ.get('COSMOS_ENDPOINT')
    cosmos_key = cosmos_key or os.environ.get('COSMOS_KEY')
    cosmos_database = cosmos_database or os.environ.get('COSMOS_DATABASE')
    
    # If still not found, prompt the user
    if not cosmos_endpoint:
        cosmos_endpoint = input("Enter Cosmos DB Endpoint URL: ")
    if not cosmos_key:
        cosmos_key = input("Enter Cosmos DB Key: ")
    if not cosmos_database:
        cosmos_database = input("Enter Cosmos DB Database Name: ")
    
    return cosmos_endpoint, cosmos_key, cosmos_database

def insert_admin_user():
    try:
        # Get Cosmos DB connection details
        cosmos_endpoint, cosmos_key, cosmos_database = get_cosmos_details()
        
        # Connect to Cosmos DB
        print(f"Connecting to Cosmos DB: {cosmos_database}")
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client(cosmos_database)
        container = database.get_container_client("users")
        
        # Check if user with this email already exists
        query = "SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": admin_user["email"]}]
        
        existing_users = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        
        if existing_users:
            print(f"A user with email {admin_user['email']} already exists!")
            return False
        
        # Insert the admin user
        print("Inserting admin user...")
        container.create_item(body=admin_user)
        print("Admin user inserted successfully!")
        
        # Display the login credentials
        print("\n============================================================")
        print("    Admin User Credentials")
        print("============================================================")
        print(f"Email: {admin_user['email']}")
        print(f"Password: Admin@0987654")  # Using the known password
        print(f"User ID: {admin_user['id']}")
        print("============================================================")
        print("\nYou can now log in to the application with these credentials.")
        return True
        
    except exceptions.CosmosResourceNotFoundError as e:
        print(f"Error: Database or container not found. {str(e)}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error: HTTP response error. {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("=================================================================")
    print("    Carpool Management Application - Admin User Creation Tool")
    print("=================================================================")
    print("")
    
    # Run without asking for confirmation
    print("Automatically inserting admin user into Cosmos DB...")
    insert_admin_user()
