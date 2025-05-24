from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import datetime, date, timedelta
import uuid

from app.core.auth import get_current_user
from app.db.cosmos import get_container
from app.models.core import UserRole

router = APIRouter()

@router.get("/rides")
async def get_student_rides(
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all rides for a student for a specific week.
    """
    # Check if user is a student
    if current_user.get("role") != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their rides"
        )
    
    student_id = current_user["user_id"]
    
    # Get the student's parent(s)
    users_container = get_container("users")
    query = """
    SELECT * FROM c
    WHERE c.id = @student_id
    """
    params = [{"name": "@student_id", "value": student_id}]
    
    student_items = list(users_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    if not student_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student = student_items[0]
    
    # Calculate the week's end date (Sunday)
    week_end_date = week_start_date + timedelta(days=6)
    
    # Get all ride assignments for the week
    rides_container = get_container("ride_assignments")
    
    # Query for rides in the date range
    query = """
    SELECT r.id, r.template_slot_id, r.driver_parent_id, r.assigned_date, r.status,
           t.day_of_week, t.start_time, t.end_time, t.route_type,
           u.full_name as driver_name, u.phone_number as driver_phone
    FROM ride_assignments r
    JOIN weekly_schedule_template_slots t ON r.template_slot_id = t.id
    JOIN users u ON r.driver_parent_id = u.id
    WHERE r.assigned_date >= @week_start_date
    AND r.assigned_date <= @week_end_date
    AND r.status = 'ACTIVE'
    """
    
    params = [
        {"name": "@week_start_date", "value": week_start_date.isoformat()},
        {"name": "@week_end_date", "value": week_end_date.isoformat()}
    ]
    
    # Execute the query
    rides = list(rides_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    # Format the response
    result = []
    for ride in rides:
        result.append({
            "id": ride["id"],
            "day_of_week": ride["day_of_week"],
            "assigned_date": ride["assigned_date"],
            "start_time": ride["start_time"],
            "end_time": ride["end_time"],
            "route_type": ride["route_type"],
            "driver_name": ride["driver_name"],
            "driver_phone": ride["driver_phone"],
            "status": ride["status"]
        })
    
    return result
