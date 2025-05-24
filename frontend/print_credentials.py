# print_credentials.py
# Just prints out the admin credentials

print("""
=================================================================
    CARPOOL MANAGEMENT APP - ADMIN USER CREDENTIALS
=================================================================

Email: admin@example.com
Password: Admin@0987654

NOTE: Make sure these credentials are inserted into your Cosmos DB.
If login fails, it means the credentials haven't been properly 
inserted into your database.

To insert these credentials into your database, you need to:
1. Access your Azure Cosmos DB account
2. Navigate to the 'users' container
3. Create a new item with the following structure:

{
  "id": "[a unique UUID]",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "role": "ADMIN",
  "hashed_password": "[bcrypt hash of the password]",
  "created_at": "[timestamp]",
  "updated_at": "[timestamp]",
  "is_active_driver": false
}

The hashed_password should be generated using bcrypt with the password:
Admin@0987654

=================================================================
""")
