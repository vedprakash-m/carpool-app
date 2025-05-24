"""
Tests for the schedule generation functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, date, timedelta

# Import the router and functions
from app.api.v1.endpoints.schedule_generation import generate_schedule
from app.services.schedule_generator import ScheduleGenerator

class TestScheduleGeneration:
    
    @pytest.fixture
    def mock_schedule_generator_instance(self):
        """Mock the schedule generator class"""
        with patch('app.api.v1.endpoints.schedule_generation.ScheduleGenerator') as mock_generator_class:
            # Create a mock instance that will be returned when ScheduleGenerator is instantiated
            mock_instance = MagicMock()
            mock_generator_class.return_value = mock_instance
            
            # Setup the generate_schedule method to return test data
            mock_instance.generate_schedule.return_value = [
                {
                    "id": "ride1",
                    "template_slot_id": "slot1",
                    "driver_parent_id": "parent1",
                    "assigned_date": "2025-06-01",
                    "status": "SCHEDULED",
                    "assignment_method": "PREFERENCE_BASED",
                    "created_at": "2025-06-01T10:00:00",
                    "updated_at": "2025-06-01T10:00:00"
                },
                {
                    "id": "ride2",
                    "template_slot_id": "slot2",
                    "driver_parent_id": "parent2",
                    "assigned_date": "2025-06-01",
                    "status": "SCHEDULED",
                    "assignment_method": "HISTORICAL_BASED",
                    "created_at": "2025-06-01T10:00:00",
                    "updated_at": "2025-06-01T10:00:00"
                }
            ]
            
            yield mock_generator_class, mock_instance
    
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
    
    async def test_generate_schedule_success(self, mock_schedule_generator_instance, mock_admin):
        """Test successful schedule generation"""
        # Unpack the mocks
        mock_generator_class, mock_instance = mock_schedule_generator_instance
        
        # Call the function
        week_start = date(2025, 6, 1)  # A Monday
        
        result = await generate_schedule(
            week_start_date=week_start,
            current_user=mock_admin
        )
        
        # Assertions
        assert len(result) == 2
        assert result[0]["driver_parent_id"] == "parent1"
        assert result[1]["driver_parent_id"] == "parent2"
        assert result[0]["template_slot_id"] == "slot1"
        assert result[1]["template_slot_id"] == "slot2"
        
        # Verify that the ScheduleGenerator was instantiated and generate_schedule was called
        mock_generator_class.assert_called_once_with(week_start)
        mock_instance.generate_schedule.assert_called_once_with(clear_existing=True)
        
    async def test_generate_schedule_no_assignments(self, mock_schedule_generator_instance, mock_admin):
        """Test schedule generation with no assignments generated"""
        # Unpack the mocks
        mock_generator_class, mock_instance = mock_schedule_generator_instance
        
        # Setup the mock to return empty assignments
        mock_instance.generate_schedule.return_value = []
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await generate_schedule(
                week_start_date=date(2025, 6, 1),
                current_user=mock_admin
            )
        
        # Assertions
        assert excinfo.value.status_code == 400
        assert "No assignments could be generated" in str(excinfo.value.detail)
        
    async def test_generate_schedule_error(self, mock_schedule_generator_instance, mock_admin):
        """Test schedule generation with an error"""
        # Unpack the mocks
        mock_generator_class, mock_instance = mock_schedule_generator_instance
        
        # Setup the mock to raise an exception
        mock_instance.generate_schedule.side_effect = Exception("Database error")
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await generate_schedule(
                week_start_date=date(2025, 6, 1),
                current_user=mock_admin
            )
        
        # Assertions
        assert excinfo.value.status_code == 500
        assert "Failed to generate schedule" in str(excinfo.value.detail)

    async def test_generate_schedule_with_wrong_user_role(self):
        """Test schedule generation with non-admin user"""
        # Create a patch for check_admin_role that raises an exception
        with patch('app.api.v1.endpoints.schedule_generation.check_admin_role') as mock_check_admin:
            # Simulate authentication failure
            mock_check_admin.side_effect = HTTPException(
                status_code=403,
                detail="Not authorized to perform this action"
            )
            
            # Call the function and expect the same exception
            with pytest.raises(HTTPException) as excinfo:
                await generate_schedule(
                    week_start_date=date(2025, 6, 1),
                    current_user=None  # This value doesn't matter as the Depends() will raise exception
                )
            
            # Assertions
            assert excinfo.value.status_code == 403
            assert "Not authorized" in str(excinfo.value.detail)
