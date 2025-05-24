from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from app.core.auth import check_admin_role, get_password_hash
from app.db.cosmos import get_container
from app.models.core import User, UserCreate

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user_admin(
    user_data: UserCreate,
    current_user: dict = Depends(check_admin_role)
):
    """
    Create a new user as an admin (Admin only)
    This endpoint allows admins to create new users and set their initial password.
    """
    users_container = get_container("users")
    
    # Check if user with this email already exists
    query = "SELECT * FROM c WHERE c.email = @email"
    params = [{"name": "@email", "value": user_data.email}]
    
    existing_users = list(users_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create the new user
    user_dict = user_data.model_dump()
    
    # Replace the plain password with a hashed one
    hashed_password = get_password_hash(user_dict.pop("initial_password"))
    
    # Add system fields
    now = datetime.utcnow().isoformat()
    new_user = {
        **user_dict,
        "id": str(uuid.uuid4()),
        "hashed_password": hashed_password,
        "created_at": now,
        "updated_at": now,
        "is_active_driver": user_dict.get("is_active_driver", False) 
    }
    
    # Save to database
    created_user = users_container.create_item(body=new_user)
    
    # Return the user (without hashed_password)
    return User(**created_user)
