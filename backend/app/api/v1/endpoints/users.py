from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from app.core.auth import get_current_user, check_admin_role, get_password_hash, verify_password
from app.db.cosmos import get_container
from app.models.core import User, UserCreate, UserUpdate, UserPasswordChange

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: dict = Depends(check_admin_role)
):
    """
    Create new user (Admin only).
    """
    users_container = get_container("users")
    
    # Check if user with email already exists
    query = f"SELECT * FROM c WHERE c.email = @email"
    params = [{"name": "@email", "value": user_in.email}]
    existing_users = list(users_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_data = user_in.model_dump(exclude={"initial_password"})
    user_data.update({
        "id": str(uuid.uuid4()),
        "hashed_password": get_password_hash(user_in.initial_password),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })
    
    users_container.create_item(body=user_data)
    return User(**user_data)

@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: UserPasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change own password (any authenticated user).
    """
    users_container = get_container("users")
    
    # Get current user from database
    try:
        user = users_container.read_item(
            item=current_user["user_id"],
            partition_key=current_user["user_id"]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_change.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Update password
    user["hashed_password"] = get_password_hash(password_change.new_password)
    user["updated_at"] = datetime.utcnow().isoformat()
    
    users_container.replace_item(
        item=user["id"],
        body=user
    )
    
    return {"message": "Password updated successfully"}

@router.get("/me", response_model=User)
async def read_user_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user.
    """
    users_container = get_container("users")
    try:
        user = users_container.read_item(
            item=current_user["user_id"],
            partition_key=current_user["user_id"]
        )
        return User(**user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update own user information.
    """
    users_container = get_container("users")
    try:
        user = users_container.read_item(
            item=current_user["user_id"],
            partition_key=current_user["user_id"]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        user[field] = value
    
    user["updated_at"] = datetime.utcnow().isoformat()
    
    updated_user = users_container.replace_item(
        item=user["id"],
        body=user
    )
    
    return User(**updated_user) 