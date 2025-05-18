from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.auth import get_current_user
from app.db.cosmos import get_container
from app.models.core import SwapRequest, UserRole

router = APIRouter()

@router.post("/", response_model=SwapRequest)
async def create_swap_request(
    ride_assignment_id: str,
    requested_driver_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new swap request.
    """
    # Check if user is a parent
    if current_user.get("role") != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents can create swap requests"
        )
    
    # Get the ride assignment
    ride_assignments_container = get_container("ride_assignments")
    try:
        ride_assignment = ride_assignments_container.read_item(
            item=ride_assignment_id,
            partition_key=ride_assignment_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride assignment not found"
        )
    
    # Check if user is the assigned driver
    if ride_assignment["driver_parent_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request swaps for rides assigned to you"
        )
    
    # Check if the requested driver exists and is an active driver
    users_container = get_container("users")
    try:
        requested_user = users_container.read_item(
            item=requested_driver_id,
            partition_key=requested_driver_id
        )
        
        if not requested_user.get("is_active_driver", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested user is not an active driver"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested driver not found"
        )
    
    # Check if a swap request already exists for this ride
    swap_requests_container = get_container("swap_requests")
    query = "SELECT * FROM c WHERE c.ride_assignment_id = @ride_id AND c.status = 'PENDING'"
    params = [{"name": "@ride_id", "value": ride_assignment_id}]
    
    existing_requests = list(swap_requests_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    if existing_requests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending swap request already exists for this ride"
        )
    
    # Create the swap request
    swap_request_data = {
        "id": str(uuid.uuid4()),
        "requesting_driver_id": current_user["user_id"],
        "requested_driver_id": requested_driver_id,
        "ride_assignment_id": ride_assignment_id,
        "status": "PENDING",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    swap_requests_container.create_item(body=swap_request_data)
    return SwapRequest(**swap_request_data)

@router.get("/", response_model=List[SwapRequest])
async def list_swap_requests(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List swap requests for the current user.
    """
    swap_requests_container = get_container("swap_requests")
    
    # Build query based on parameters
    if status:
        query = """
        SELECT * FROM c 
        WHERE (c.requesting_driver_id = @user_id OR c.requested_driver_id = @user_id)
        AND c.status = @status
        """
        params = [
            {"name": "@user_id", "value": current_user["user_id"]},
            {"name": "@status", "value": status}
        ]
    else:
        query = """
        SELECT * FROM c 
        WHERE c.requesting_driver_id = @user_id OR c.requested_driver_id = @user_id
        """
        params = [{"name": "@user_id", "value": current_user["user_id"]}]
    
    swap_requests = list(swap_requests_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    
    return [SwapRequest(**request) for request in swap_requests]

@router.put("/{request_id}/accept", response_model=SwapRequest)
async def accept_swap_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Accept a swap request.
    """
    # Get the swap request
    swap_requests_container = get_container("swap_requests")
    try:
        swap_request = swap_requests_container.read_item(
            item=request_id,
            partition_key=request_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
    
    # Check if user is the requested driver
    if swap_request["requested_driver_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only accept swap requests sent to you"
        )
    
    # Check if the swap request is still pending
    if swap_request["status"] != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Swap request is no longer pending"
        )
    
    # Get the ride assignment
    ride_assignments_container = get_container("ride_assignments")
    try:
        ride_assignment = ride_assignments_container.read_item(
            item=swap_request["ride_assignment_id"],
            partition_key=swap_request["ride_assignment_id"]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride assignment not found"
        )
    
    # Update the ride assignment with the new driver
    ride_assignment["driver_parent_id"] = current_user["user_id"]
    ride_assignment["updated_at"] = datetime.utcnow().isoformat()
    ride_assignment["assignment_method"] = "MANUAL"  # Swap is considered manual assignment
    
    ride_assignments_container.replace_item(
        item=ride_assignment["id"],
        body=ride_assignment
    )
    
    # Update the swap request status
    swap_request["status"] = "ACCEPTED"
    swap_request["updated_at"] = datetime.utcnow().isoformat()
    
    updated_request = swap_requests_container.replace_item(
        item=swap_request["id"],
        body=swap_request
    )
    
    return SwapRequest(**updated_request)

@router.put("/{request_id}/reject", response_model=SwapRequest)
async def reject_swap_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Reject a swap request.
    """
    # Get the swap request
    swap_requests_container = get_container("swap_requests")
    try:
        swap_request = swap_requests_container.read_item(
            item=request_id,
            partition_key=request_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
    
    # Check if user is the requested driver
    if swap_request["requested_driver_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reject swap requests sent to you"
        )
    
    # Check if the swap request is still pending
    if swap_request["status"] != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Swap request is no longer pending"
        )
    
    # Update the swap request status
    swap_request["status"] = "REJECTED"
    swap_request["updated_at"] = datetime.utcnow().isoformat()
    
    updated_request = swap_requests_container.replace_item(
        item=swap_request["id"],
        body=swap_request
    )
    
    return SwapRequest(**updated_request) 