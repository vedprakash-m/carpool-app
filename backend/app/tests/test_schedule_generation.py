"""
Tests for the schedule generation functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, timedelta

# Import the router and functions
from app.api.v1.endpoints.schedule_generation import generate_schedule
from app.services.schedule_generator import generate_ride_assignments

class TestScheduleGeneration:
    
    @pytest.fixture
    def mock_containers(self):
        """Creates mock containers for CosmosDB"""
        with patch('app.api.v1.endpoints.schedule_generation.get_container') as mock_get_container:
            # Create mock containers for different collections
            templates_container = MagicMock()
            users_container = MagicMock()
            ride_assignments_container = MagicMock()
            
            # Define the behavior for each container type
            def get_mock_container(container_name):
                if container_name == "schedule_templates":
                    return templates_container
                elif container_name == "users":
                    return users_container
                elif container_name == "ride_assignments":
                    return ride_assignments_container
                return MagicMock()
            
            mock_get_container.side_effect = get_mock_container
            
            yield {
                "schedule_templates": templates_container,
                "users": users_container,
                "ride_assignments": ride_assignments_container
            }
    
    @pytest.fixture
    def mock_schedule_generator(self):
        """Mock the schedule generator service"""
        with patch('app.api.v1.endpoints.schedule_generation.generate_ride_assignments') as mock_generator:
            mock_generator.return_value = [
                {
                    "id": "ride1",
                    "driver_parent_id": "parent1",
                    "date": "2025-06-01",
                    "time_slot": "MORNING",
                    "students": ["student1", "student2"],
                    "status": "ASSIGNED"
                },
                {
                    "id": "ride2",
                    "driver_parent_id": "parent2",
                    "date": "2025-06-01",
                    "time_slot": "AFTERNOON",
                    "students": ["student3", "student4"],
                    "status": "ASSIGNED"
                }
            ]
            yield mock_generator
    
    @pytest.fixture
    def mock_admin(self):
        """Mocks authentication functions for an admin user"""
        with patch('app.api.v1.endpoints.schedule_generation.check_admin_role') as mock_check_admin:
            # Simulate an admin user
            admin_user = {
                "id": "admin1",
                "email": "admin@example.com",
                "role": "ADMIN"
            }
            mock_check_admin.return_value = admin_user
            yield admin_user
    
    async def test_generate_schedule_success(self, mock_containers, mock_schedule_generator, mock_admin):
        """Test successful schedule generation"""
        # Setup mock template data
        mock_template = {
            "id": "template1",
            "name": "Summer Schedule",
            "preferences": {
                "max_students_per_car": 4
            }
        }
        mock_containers["schedule_templates"].read_item.return_value = mock_template
        
        # Setup mock users (drivers)
        mock_drivers = [
            {"id": "parent1", "full_name": "Parent One", "is_active_driver": True},
            {"id": "parent2", "full_name": "Parent Two", "is_active_driver": True}
        ]
        mock_containers["users"].query_items.return_value = mock_drivers
        
        # Setup mock students
        mock_students = [
            {"id": "student1", "full_name": "Student One"},
            {"id": "student2", "full_name": "Student Two"},
            {"id": "student3", "full_name": "Student Three"},
            {"id": "student4", "full_name": "Student Four"}
        ]
        
        # Call the function
        start_date = "2025-06-01"
        end_date = "2025-06-07"
        
        result = await generate_schedule(
            template_id="template1", 
            start_date=start_date, 
            end_date=end_date, 
            current_user=mock_admin
        )
        
        # Assertions
        assert len(result) == 2
        assert result[0]["driver_parent_id"] == "parent1"
        assert result[1]["driver_parent_id"] == "parent2"
        assert len(result[0]["students"]) == 2
        assert len(result[1]["students"]) == 2
        
        # Verify that the schedule generator was called with correct params
        mock_schedule_generator.assert_called_once()
        call_args = mock_schedule_generator.call_args[0]
        assert call_args[0] == mock_template  # template
        assert isinstance(call_args[1], list)  # drivers
        assert isinstance(call_args[2], list)  # students
        
    async def test_generate_schedule_no_template(self, mock_containers, mock_admin):
        """Test schedule generation with non-existent template"""
        # Setup mock container to simulate template not found
        mock_containers["schedule_templates"].read_item.side_effect = Exception("Item not found")
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await generate_schedule(
                template_id="nonexistent", 
                start_date="2025-06-01", 
                end_date="2025-06-07", 
                current_user=mock_admin
            )
        
        # Assertions
        assert excinfo.value.status_code == 404
        assert "Template not found" in str(excinfo.value.detail)
        
    async def test_generate_schedule_no_drivers(self, mock_containers, mock_admin):
        """Test schedule generation with no available drivers"""
        # Setup mock template data
        mock_template = {
            "id": "template1",
            "name": "Summer Schedule",
            "preferences": {
                "max_students_per_car": 4
            }
        }
        mock_containers["schedule_templates"].read_item.return_value = mock_template
        
        # Setup empty drivers list
        mock_containers["users"].query_items.return_value = []
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await generate_schedule(
                template_id="template1", 
                start_date="2025-06-01", 
                end_date="2025-06-07", 
                current_user=mock_admin
            )
        
        # Assertions
        assert excinfo.value.status_code == 400
        assert "No active drivers" in str(excinfo.value.detail)
