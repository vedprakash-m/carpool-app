from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict
from datetime import datetime, date, timedelta
import uuid

from app.core.auth import check_admin_role
from app.db.cosmos import get_container
from app.models.core import RideAssignment, AssignmentMethod, PreferenceLevel

router = APIRouter()

@router.post("/generate-schedule", response_model=List[RideAssignment])
async def generate_schedule(
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(check_admin_role)
):
    """
    Generate a carpool schedule for the specified week (Admin only).
    """
    # Get containers
    schedule_container = get_container("schedule_templates")
    preferences_container = get_container("driver_preferences")
    users_container = get_container("users")
    ride_assignments_container = get_container("ride_assignments")
    
    # Get all schedule template slots
    query = "SELECT * FROM c"
    template_slots = list(schedule_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    # Get all active drivers
    query = "SELECT * FROM c WHERE c.is_active_driver = true"
    drivers = list(users_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    if not drivers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active drivers found"
        )
    
    # Get all driver preferences for the week
    query = "SELECT * FROM c WHERE c.week_start_date = @week_start_date"
    params = [{"name": "@week_start_date", "value": week_start_date.isoformat()}]
    all_preferences = list(preferences_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    # Get historical ride assignments (last 4 weeks) for fairness
    historical_end = week_start_date
    historical_start = historical_end - timedelta(days=28)
    query = """
    SELECT * FROM c 
    WHERE c.assigned_date >= @start_date 
    AND c.assigned_date < @end_date
    """
    params = [
        {"name": "@start_date", "value": historical_start.isoformat()},
        {"name": "@end_date", "value": historical_end.isoformat()}
    ]
    historical_assignments = list(ride_assignments_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    # Count historical assignments per driver
    driver_assignment_counts = {}
    for driver in drivers:
        driver_id = driver["id"]
        count = sum(1 for a in historical_assignments if a["driver_parent_id"] == driver_id)
        driver_assignment_counts[driver_id] = count
    
    # Delete any existing assignments for this week
    week_end_date = week_start_date + timedelta(days=7)
    query = """
    SELECT * FROM c 
    WHERE c.assigned_date >= @start_date 
    AND c.assigned_date < @end_date
    """
    params = [
        {"name": "@start_date", "value": week_start_date.isoformat()},
        {"name": "@end_date", "value": week_end_date.isoformat()}
    ]
    existing_assignments = list(ride_assignments_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    for assignment in existing_assignments:
        ride_assignments_container.delete_item(
            item=assignment["id"],
            partition_key=assignment["id"]
        )
    
    # Create a nested dictionary of preferences by driver and slot
    # Default to AVAILABLE_NEUTRAL if no preference is specified
    driver_preferences = {}
    for driver in drivers:
        driver_id = driver["id"]
        driver_preferences[driver_id] = {}
        
    for pref in all_preferences:
        driver_id = pref["driver_parent_id"]
        slot_id = pref["template_slot_id"]
        if driver_id in driver_preferences:
            driver_preferences[driver_id][slot_id] = pref["preference_level"]
    
    # Generate assignments for each day of the week
    new_assignments = []
    for day_offset in range(7):  # 0 = Monday, 6 = Sunday
        day_date = week_start_date + timedelta(days=day_offset)
        
        # Get slots for this day of the week
        day_slots = [s for s in template_slots if s["day_of_week"] == day_offset]
        
        for slot in day_slots:
            slot_id = slot["id"]
            
            # Find the best driver for this slot
            assigned_driver = None
            assignment_method = None
            
            # Step 1: Filter out drivers who marked this slot as UNAVAILABLE
            available_drivers = [
                d_id for d_id in driver_preferences 
                if slot_id not in driver_preferences[d_id] or 
                driver_preferences[d_id].get(slot_id) != PreferenceLevel.UNAVAILABLE
            ]
            
            if not available_drivers:
                continue  # No available drivers for this slot
            
            # Step 2: Try to find drivers who marked this slot as PREFERRED
            preferred_drivers = [
                d_id for d_id in available_drivers
                if slot_id in driver_preferences[d_id] and 
                driver_preferences[d_id].get(slot_id) == PreferenceLevel.PREFERRED
            ]
            
            if preferred_drivers:
                # If multiple preferred drivers, pick the one with fewest historical assignments
                assigned_driver = min(
                    preferred_drivers, 
                    key=lambda d: driver_assignment_counts.get(d, 0)
                )
                assignment_method = AssignmentMethod.PREFERENCE_BASED
            else:
                # Step 3: Try to find drivers who marked this slot as LESS_PREFERRED
                less_preferred_drivers = [
                    d_id for d_id in available_drivers
                    if slot_id in driver_preferences[d_id] and 
                    driver_preferences[d_id].get(slot_id) == PreferenceLevel.LESS_PREFERRED
                ]
                
                if less_preferred_drivers:
                    assigned_driver = min(
                        less_preferred_drivers, 
                        key=lambda d: driver_assignment_counts.get(d, 0)
                    )
                    assignment_method = AssignmentMethod.PREFERENCE_BASED
                else:
                    # Step 4: Use AVAILABLE_NEUTRAL drivers
                    neutral_drivers = [
                        d_id for d_id in available_drivers
                        if slot_id not in driver_preferences[d_id] or 
                        driver_preferences[d_id].get(slot_id) == PreferenceLevel.AVAILABLE_NEUTRAL
                    ]
                    
                    if neutral_drivers:
                        assigned_driver = min(
                            neutral_drivers, 
                            key=lambda d: driver_assignment_counts.get(d, 0)
                        )
                        assignment_method = AssignmentMethod.HISTORICAL_BASED
            
            # Create assignment if a driver was found
            if assigned_driver:
                assignment_data = {
                    "id": str(uuid.uuid4()),
                    "template_slot_id": slot_id,
                    "driver_parent_id": assigned_driver,
                    "assigned_date": day_date.isoformat(),
                    "status": "SCHEDULED",
                    "assignment_method": assignment_method,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Save assignment
                new_assignment = ride_assignments_container.create_item(body=assignment_data)
                new_assignments.append(RideAssignment(**new_assignment))
                
                # Update the count for this driver (for fairness in subsequent assignments)
                driver_assignment_counts[assigned_driver] = driver_assignment_counts.get(assigned_driver, 0) + 1
    
    return new_assignments

@router.get("/schedule", response_model=List[RideAssignment])
async def get_schedule(
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(check_admin_role)
):
    """
    Get the generated schedule for the specified week (Admin only).
    """
    ride_assignments_container = get_container("ride_assignments")
    
    # Calculate the end date (exclusive)
    week_end_date = week_start_date + timedelta(days=7)
    
    # Get all assignments for the week
    query = """
    SELECT * FROM c 
    WHERE c.assigned_date >= @start_date 
    AND c.assigned_date < @end_date
    """
    params = [
        {"name": "@start_date", "value": week_start_date.isoformat()},
        {"name": "@end_date", "value": week_end_date.isoformat()}
    ]
    
    assignments = list(ride_assignments_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    return [RideAssignment(**assignment) for assignment in assignments] 