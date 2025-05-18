from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import datetime, date
import uuid

from app.core.auth import get_current_user
from app.db.cosmos import get_container
from app.models.core import DriverWeeklyPreference, PreferenceLevel, UserRole

router = APIRouter()

@router.post("/weekly-preferences", response_model=List[DriverWeeklyPreference])
async def submit_weekly_preferences(
    preferences: List[DriverWeeklyPreference],
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit weekly driving preferences for a parent.
    """
    # Check if user is a parent
    if current_user.get("role") != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents can submit preferences"
        )
    
    # Get the users container to check if user is an active driver
    users_container = get_container("users")
    try:
        user = users_container.read_item(
            item=current_user["user_id"],
            partition_key=current_user["user_id"]
        )
        
        if not user.get("is_active_driver", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an active driver"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    preferences_container = get_container("driver_preferences")
    
    # Delete existing preferences for this user and week
    query = """
    SELECT * FROM c 
    WHERE c.driver_parent_id = @driver_id 
    AND c.week_start_date = @week_start_date
    """
    params = [
        {"name": "@driver_id", "value": current_user["user_id"]},
        {"name": "@week_start_date", "value": week_start_date.isoformat()}
    ]
    
    existing_preferences = list(preferences_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    for pref in existing_preferences:
        preferences_container.delete_item(
            item=pref["id"],
            partition_key=pref["id"]
        )
    
    # Count preference levels to enforce limits
    preferred_count = sum(1 for p in preferences if p.preference_level == PreferenceLevel.PREFERRED)
    less_preferred_count = sum(1 for p in preferences if p.preference_level == PreferenceLevel.LESS_PREFERRED)
    unavailable_count = sum(1 for p in preferences if p.preference_level == PreferenceLevel.UNAVAILABLE)
    
    # Check preference level limits
    if preferred_count > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 PREFERRED slots allowed"
        )
    
    if less_preferred_count > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 2 LESS_PREFERRED slots allowed"
        )
    
    if unavailable_count > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 2 UNAVAILABLE slots allowed"
        )
    
    # Create new preferences
    saved_preferences = []
    for pref in preferences:
        pref_data = pref.model_dump()
        pref_data.update({
            "id": str(uuid.uuid4()),
            "driver_parent_id": current_user["user_id"],
            "week_start_date": week_start_date.isoformat(),
            "submission_timestamp": datetime.utcnow().isoformat()
        })
        
        saved_pref = preferences_container.create_item(body=pref_data)
        saved_preferences.append(DriverWeeklyPreference(**saved_pref))
    
    return saved_preferences

@router.get("/weekly-preferences", response_model=List[DriverWeeklyPreference])
async def get_weekly_preferences(
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get weekly driving preferences for the current user (parent).
    """
    # Check if user is a parent
    if current_user.get("role") != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents can access preferences"
        )
    
    preferences_container = get_container("driver_preferences")
    
    # Get preferences for this user and week
    query = """
    SELECT * FROM c 
    WHERE c.driver_parent_id = @driver_id 
    AND c.week_start_date = @week_start_date
    """
    params = [
        {"name": "@driver_id", "value": current_user["user_id"]},
        {"name": "@week_start_date", "value": week_start_date.isoformat()}
    ]
    
    preferences = list(preferences_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    return [DriverWeeklyPreference(**pref) for pref in preferences] 