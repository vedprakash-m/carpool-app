from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import date
import logging

from app.core.auth import check_admin_role
from app.models.core import RideAssignment
from app.services.schedule_generator import ScheduleGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-schedule", response_model=List[RideAssignment])
async def generate_schedule(
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(check_admin_role)
):
    """
    Generate a carpool schedule for the specified week (Admin only).
    Uses the ScheduleGenerator service to create a balanced schedule based on
    driver preferences and historical assignments.
    """
    try:
        # Initialize schedule generator with the requested week start date
        schedule_generator = ScheduleGenerator(week_start_date)
        
        # Generate the schedule
        assignments = schedule_generator.generate_schedule(clear_existing=True)
        
        if not assignments:
            logger.warning(f"No assignments generated for week starting {week_start_date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No assignments could be generated. Please check driver availability and schedule templates."
            )
        
        logger.info(f"Successfully generated {len(assignments)} assignments for week of {week_start_date}")
        return assignments
        
    except Exception as e:
        logger.error(f"Error generating schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate schedule: {str(e)}"
        )

@router.get("/schedule", response_model=List[RideAssignment])
async def get_schedule(
    week_start_date: date = Query(..., description="Start date of the week (Monday) in ISO format"),
    current_user: dict = Depends(check_admin_role)
):
    """
    Get the existing schedule for the specified week (Admin only).
    """
    try:
        # Create a schedule generator instance to use its methods
        schedule_generator = ScheduleGenerator(week_start_date)
        
        # Use a helper method to get existing assignments for the week
        # This would need to be added to the ScheduleGenerator class
        assignments = schedule_generator.get_existing_assignments()
        
        logger.info(f"Retrieved {len(assignments)} assignments for week of {week_start_date}")
        return assignments
        
    except Exception as e:
        logger.error(f"Error getting schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schedule: {str(e)}"
        )