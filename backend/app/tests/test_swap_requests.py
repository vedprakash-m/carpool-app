"""
Tests for swap request functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Import the router and functions
from app.api.v1.endpoints.swap_requests import create_swap_request
from app.models.core import UserRole

class TestSwapRequests:
    
    @pytest.fixture
    def mock_containers(self):
        """Creates mock containers for CosmosDB"""
        # This is a bit more complex as we need to mock multiple container calls
        with patch('app.api.v1.endpoints.swap_requests.get_container') as mock_get_container:
            # Create mock containers for different collections
            ride_assignments_container = MagicMock()
            users_container = MagicMock()
            swap_requests_container = MagicMock()
            
            # Define the behavior for each container type
            def get_mock_container(container_name):
                if container_name == "ride_assignments":
                    return ride_assignments_container
                elif container_name == "users":
                    return users_container
                elif container_name == "swap_requests":
                    return swap_requests_container
                return MagicMock()
            
            mock_get_container.side_effect = get_mock_container
            
            yield {
                "ride_assignments": ride_assignments_container,
                "users": users_container,
                "swap_requests": swap_requests_container
            }
    
    @pytest.fixture
    def mock_email_service(self):
        """Mocks the email service"""
        with patch('app.api.v1.endpoints.swap_requests.email_service') as mock_service:
            yield mock_service
    
    @pytest.fixture
    def parent_user(self):
        """Creates a mock parent user"""
        return {
            "id": "parent123",
            "user_id": "parent123",
            "email": "parent@example.com",
            "full_name": "Parent User",
            "role": UserRole.PARENT,
            "is_active_driver": True
        }
    
    @pytest.fixture
    def other_parent_user(self):
        """Creates another mock parent user (the requested driver)"""
        return {
            "id": "parent456",
            "user_id": "parent456",
            "email": "otherparent@example.com",
            "full_name": "Other Parent",
            "role": UserRole.PARENT,
            "is_active_driver": True
        }
    
    @pytest.fixture
    def ride_assignment(self):
        """Creates a mock ride assignment"""
        return {
            "id": "ride123",
            "driver_parent_id": "parent123",
            "date": "2025-05-25",
            "time_slot": "MORNING",
            "students": ["student1", "student2"],
            "status": "ASSIGNED"
        }
    
    async def test_create_swap_request_success(self, mock_containers, mock_email_service, parent_user, other_parent_user, ride_assignment):
        """Test successful creation of a swap request"""
        # Setup containers
        mock_containers["ride_assignments"].read_item.return_value = ride_assignment
        mock_containers["users"].read_item.return_value = other_parent_user
        mock_containers["swap_requests"].query_items.return_value = []  # No existing requests
        mock_containers["swap_requests"].create_item.return_value = {
            "id": "swap123",
            "requester_id": "parent123",
            "requested_driver_id": "parent456",
            "ride_assignment_id": "ride123",
            "status": "PENDING",
            "created_at": "2025-05-18T12:00:00Z"
        }
        
        # Call function
        result = await create_swap_request(
            ride_assignment_id="ride123",
            requested_driver_id="parent456",
            current_user=parent_user
        )
        
        # Assertions
        assert result["id"] == "swap123"
        assert result["requester_id"] == "parent123"
        assert result["requested_driver_id"] == "parent456"
        assert result["status"] == "PENDING"
        assert mock_email_service.send_swap_request_notification.called
    
    async def test_create_swap_request_non_parent(self, mock_containers, parent_user):
        """Test that only parents can create swap requests"""
        # Modify the user to be a student
        student_user = parent_user.copy()
        student_user["role"] = UserRole.STUDENT
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await create_swap_request(
                ride_assignment_id="ride123",
                requested_driver_id="parent456",
                current_user=student_user
            )
        
        # Assertions
        assert excinfo.value.status_code == 403
        assert "Only parents can create swap requests" in str(excinfo.value.detail)
    
    async def test_create_swap_request_ride_not_found(self, mock_containers, parent_user):
        """Test handling of non-existent ride assignment"""
        # Setup
        mock_containers["ride_assignments"].read_item.side_effect = Exception("Item not found")
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await create_swap_request(
                ride_assignment_id="nonexistent",
                requested_driver_id="parent456",
                current_user=parent_user
            )
        
        # Assertions
        assert excinfo.value.status_code == 404
        assert "Ride assignment not found" in str(excinfo.value.detail)
    
    async def test_create_swap_request_not_assigned_driver(self, mock_containers, parent_user, ride_assignment):
        """Test that user can only request swaps for their own assignments"""
        # Modify ride_assignment to have a different driver
        ride_assignment["driver_parent_id"] = "someone_else"
        mock_containers["ride_assignments"].read_item.return_value = ride_assignment
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await create_swap_request(
                ride_assignment_id="ride123",
                requested_driver_id="parent456",
                current_user=parent_user
            )
        
        # Assertions
        assert excinfo.value.status_code == 403
        assert "You can only request swaps for rides assigned to you" in str(excinfo.value.detail)
