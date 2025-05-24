from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from enum import Enum

from app.core.auth import get_current_user
from app.db.cosmos import get_container
from app.models.core import UserRole

router = APIRouter()

class TimeframeEnum(str, Enum):
    WEEK = "week"
    MONTH = "month" 
    QUARTER = "quarter"
    YEAR = "year"

@router.get("/carpool")
async def get_carpool_statistics(
    timeframe: TimeframeEnum = Query(TimeframeEnum.MONTH, description="Timeframe for statistics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get carpool statistics for the specified timeframe.
    Only accessible to admins.
    """
    # Check if user is an admin
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view statistics"
        )
    
    # Calculate the start date based on the timeframe
    today = date.today()
    if timeframe == TimeframeEnum.WEEK:
        start_date = today - timedelta(days=7)
    elif timeframe == TimeframeEnum.MONTH:
        start_date = today - timedelta(days=30)
    elif timeframe == TimeframeEnum.QUARTER:
        start_date = today - timedelta(days=90)
    else:  # YEAR
        start_date = today - timedelta(days=365)
    
    # Get all ride assignments in the date range
    rides_container = get_container("ride_assignments")
    
    query = """
    SELECT r.id, r.driver_parent_id, r.assigned_date, r.status,
           t.day_of_week, t.route_type
    FROM ride_assignments r
    JOIN weekly_schedule_template_slots t ON r.template_slot_id = t.id
    WHERE r.assigned_date >= @start_date
    AND r.assigned_date <= @end_date
    """
    
    params = [
        {"name": "@start_date", "value": start_date.isoformat()},
        {"name": "@end_date", "value": today.isoformat()}
    ]
    
    # Execute the query
    ride_assignments = list(rides_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    # Get all active drivers
    users_container = get_container("users")
    query = """
    SELECT * FROM c
    WHERE c.is_active_driver = true
    """
    drivers = list(users_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    # Map driver IDs to names
    driver_names = {driver["id"]: driver["full_name"] for driver in drivers}
    
    # Process the data for statistics
    total_rides = len(ride_assignments)
    rides_by_driver = {}
    rides_by_route_type = {"TO_SCHOOL": 0, "FROM_SCHOOL": 0}
    rides_by_day_of_week = [0] * 7  # 0 to 6 for Sunday to Saturday
    
    for ride in ride_assignments:
        # Count by driver
        driver_id = ride["driver_parent_id"]
        driver_name = driver_names.get(driver_id, "Unknown")
        rides_by_driver[driver_id] = rides_by_driver.get(driver_id, {
            "name": driver_name,
            "rides": 0
        })
        rides_by_driver[driver_id]["rides"] += 1
        
        # Count by route type
        route_type = ride.get("route_type", "")
        if route_type in rides_by_route_type:
            rides_by_route_type[route_type] += 1
        
        # Count by day of week
        day_of_week = ride.get("day_of_week", 0)
        if 0 <= day_of_week < 7:
            rides_by_day_of_week[day_of_week] += 1
    
    # Convert rides_by_driver from dict to list
    by_driver_list = list(rides_by_driver.values())
    # Sort by number of rides, descending
    by_driver_list.sort(key=lambda x: x["rides"], reverse=True)
    
    return {
        "totalRides": total_rides,
        "byDriver": by_driver_list,
        "byRouteType": rides_by_route_type,
        "byDayOfWeek": rides_by_day_of_week
    }
