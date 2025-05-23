"""
Integration test for schedule generation functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from app.api.v1.endpoints.schedule_generation import generate_schedule, get_schedule
from app.models.core import RideAssignment

@pytest.mark.integration
class TestScheduleGenerationIntegration:
    
    @pytest.fixture
    def mock_schedule_generator(self):
        """Mock the ScheduleGenerator class and its methods"""
        with patch('app.api.v1.endpoints.schedule_generation.ScheduleGenerator') as mock_generator_class:
            # Create a mock for the instance that will be returned
            mock_instance = MagicMock()
            mock_generator_class.return_value = mock_instance
            
            # Set up the mock to return test data
            mock_instance.generate_schedule.return_value = [
                {
                    "id": "assign1",
                    "template_slot_id": "slot1",
                    "driver_parent_id": "driver1",
                    "assigned_date": "2025-05-26",
                    "status": "SCHEDULED",
                    "assignment_method": "PREFERENCE_BASED",
                    "created_at": "2025-05-26T10:00:00",
                    "updated_at": "2025-05-26T10:00:00"
                },
                {
                    "id": "assign2",
                    "template_slot_id": "slot2",
                    "driver_parent_id": "driver2",
                    "assigned_date": "2025-05-26",
                    "status": "SCHEDULED",
                    "assignment_method": "HISTORICAL_BASED",
                    "created_at": "2025-05-26T10:00:00",
                    "updated_at": "2025-05-26T10:00:00"
                }
            ]
            
            mock_instance.get_existing_assignments.return_value = [
                {
                    "id": "assign1",
                    "template_slot_id": "slot1",
                    "driver_parent_id": "driver1",
                    "assigned_date": "2025-05-26",
                    "status": "SCHEDULED",
                    "assignment_method": "PREFERENCE_BASED",
                    "created_at": "2025-05-26T10:00:00",
                    "updated_at": "2025-05-26T10:00:00"
                }
            ]
            
            yield mock_generator_class, mock_instance
    
    @pytest.fixture
    def mock_auth(self):
        """Mock the authentication dependency"""
        with patch('app.api.v1.endpoints.schedule_generation.check_admin_role') as mock_auth:
            # Return a mock admin user
            mock_auth.return_value = {
                "id": "admin1",
                "email": "admin@example.com",
                "role": "ADMIN"
            }
            yield mock_auth
    
    @pytest.mark.asyncio
    async def test_generate_schedule_endpoint(self, mock_schedule_generator, mock_auth):
        """Test the generate_schedule endpoint"""
        mock_class, mock_instance = mock_schedule_generator
        
        # Call the endpoint
        week_start = date(2025, 5, 26)  # A Monday
        result = await generate_schedule(
            week_start_date=week_start,
            current_user=mock_auth.return_value
        )
        
        # Verify response
        assert len(result) == 2
        assert result[0]["driver_parent_id"] == "driver1"
        assert result[1]["driver_parent_id"] == "driver2"
        
        # Verify that ScheduleGenerator was properly instantiated and called
        mock_class.assert_called_once_with(week_start)
        mock_instance.generate_schedule.assert_called_once_with(clear_existing=True)
    
    @pytest.mark.asyncio
    async def test_get_schedule_endpoint(self, mock_schedule_generator, mock_auth):
        """Test the get_schedule endpoint"""
        mock_class, mock_instance = mock_schedule_generator
        
        # Call the endpoint
        week_start = date(2025, 5, 26)  # A Monday
        result = await get_schedule(
            week_start_date=week_start,
            current_user=mock_auth.return_value
        )
        
        # Verify response
        assert len(result) == 1
        assert result[0]["driver_parent_id"] == "driver1"
        assert result[0]["template_slot_id"] == "slot1"
        
        # Verify that ScheduleGenerator was properly instantiated and called
        mock_class.assert_called_once_with(week_start)
        mock_instance.get_existing_assignments.assert_called_once()
