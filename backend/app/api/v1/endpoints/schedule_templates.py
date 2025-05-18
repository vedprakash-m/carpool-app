from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from app.core.auth import get_current_user, check_admin_role
from app.db.cosmos import get_container
from app.models.core import WeeklyScheduleTemplateSlot

router = APIRouter()

@router.post("/", response_model=WeeklyScheduleTemplateSlot)
async def create_schedule_template(
    template: WeeklyScheduleTemplateSlot,
    current_user: dict = Depends(check_admin_role)
):
    """
    Create a new weekly schedule template slot (Admin only).
    """
    schedule_container = get_container("schedule_templates")
    
    template_data = template.model_dump()
    template_data.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })
    
    schedule_container.create_item(body=template_data)
    return WeeklyScheduleTemplateSlot(**template_data)

@router.get("/", response_model=List[WeeklyScheduleTemplateSlot])
async def list_schedule_templates(
    current_user: dict = Depends(get_current_user)
):
    """
    List all weekly schedule template slots.
    """
    schedule_container = get_container("schedule_templates")
    
    # Get all schedule templates
    query = "SELECT * FROM c"
    templates = list(schedule_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    return [WeeklyScheduleTemplateSlot(**template) for template in templates]

@router.get("/{template_id}", response_model=WeeklyScheduleTemplateSlot)
async def get_schedule_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific weekly schedule template slot.
    """
    schedule_container = get_container("schedule_templates")
    
    try:
        template = schedule_container.read_item(
            item=template_id,
            partition_key=template_id
        )
        return WeeklyScheduleTemplateSlot(**template)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule template not found"
        )

@router.put("/{template_id}", response_model=WeeklyScheduleTemplateSlot)
async def update_schedule_template(
    template_id: str,
    template_update: WeeklyScheduleTemplateSlot,
    current_user: dict = Depends(check_admin_role)
):
    """
    Update a weekly schedule template slot (Admin only).
    """
    schedule_container = get_container("schedule_templates")
    
    try:
        existing_template = schedule_container.read_item(
            item=template_id,
            partition_key=template_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule template not found"
        )
    
    update_data = template_update.model_dump(exclude={"id", "created_at"})
    update_data["id"] = template_id
    update_data["created_at"] = existing_template["created_at"]
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_template = schedule_container.replace_item(
        item=template_id,
        body=update_data
    )
    
    return WeeklyScheduleTemplateSlot(**updated_template)

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule_template(
    template_id: str,
    current_user: dict = Depends(check_admin_role)
):
    """
    Delete a weekly schedule template slot (Admin only).
    """
    schedule_container = get_container("schedule_templates")
    
    try:
        schedule_container.delete_item(
            item=template_id,
            partition_key=template_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule template not found"
        ) 