import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from app.services.schedule_generator import ScheduleGenerator
from app.models.core import PreferenceLevel, AssignmentMethod

@pytest.mark.asyncio
async def test_scheduler_balanced_preferences():
    """Test with balanced preferences"""
    # Setup mock data
    with patch('app.services.schedule_generator.get_container') as mock_get_container:
        # Setup mock containers
        mock_templates = MagicMock()
        mock_prefs = MagicMock()
        mock_assignments = MagicMock()
        mock_users = MagicMock()
        
        # Configure container behavior
        def get_mock_container(container_name):
            if container_name == "weekly_schedule_template_slots":
                return mock_templates
            elif container_name == "driver_weekly_preferences":
                return mock_prefs
            elif container_name == "ride_assignments":
                return mock_assignments
            elif container_name == "users":
                return mock_users
            return MagicMock()
        
        mock_get_container.side_effect = get_mock_container
        
        # Setup test data
        week_start = date(2025, 6, 2)
        
        # Configure mock template slots
        template_slots = [
            {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"},
            {"id": "slot2", "day_of_week": 0, "time_slot": "AFTERNOON"}
        ]
        mock_templates.query_items.return_value = template_slots
        
        # Configure mock drivers
        drivers = [
            {"id": "driver1", "name": "Driver 1", "is_active_driver": True},
            {"id": "driver2", "name": "Driver 2", "is_active_driver": True}
        ]
        mock_users.query_items.return_value = drivers
        
        # Configure preferences
        prefs = [
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref2",
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.PREFERRED
            }
        ]
        mock_prefs.query_items.return_value = prefs
        
        # Empty historical assignments
        mock_assignments.query_items.return_value = []
        
        # Run the test
        scheduler = ScheduleGenerator(week_start)
        assignments = scheduler.generate_schedule(clear_existing=True)
        
        # Verify results
        assert len(assignments) == len(template_slots)
        
        # Each driver should get their preferred slot
        slot1_assignment = next(a for a in assignments if a["template_slot_id"] == "slot1")
        slot2_assignment = next(a for a in assignments if a["template_slot_id"] == "slot2")
        
        assert slot1_assignment["driver_parent_id"] == "driver1"
        assert slot2_assignment["driver_parent_id"] == "driver2"

@pytest.mark.asyncio
async def test_scheduler_conflicting_preferences():
    """Test with conflicting preferences"""
    # Setup mock data
    with patch('app.services.schedule_generator.get_container') as mock_get_container:
        # Setup mock containers
        mock_templates = MagicMock()
        mock_prefs = MagicMock()
        mock_assignments = MagicMock()
        mock_users = MagicMock()
        
        # Configure container behavior
        def get_mock_container(container_name):
            if container_name == "weekly_schedule_template_slots":
                return mock_templates
            elif container_name == "driver_weekly_preferences":
                return mock_prefs
            elif container_name == "ride_assignments":
                return mock_assignments
            elif container_name == "users":
                return mock_users
            return MagicMock()
        
        mock_get_container.side_effect = get_mock_container
        
        # Setup test data
        week_start = date(2025, 6, 2)
        
        # Configure mock template slots
        template_slots = [
            {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"},
            {"id": "slot2", "day_of_week": 0, "time_slot": "AFTERNOON"}
        ]
        mock_templates.query_items.return_value = template_slots
        
        # Configure mock drivers
        drivers = [
            {"id": "driver1", "name": "Driver 1", "is_active_driver": True},
            {"id": "driver2", "name": "Driver 2", "is_active_driver": True},
            {"id": "driver3", "name": "Driver 3", "is_active_driver": True}
        ]
        mock_users.query_items.return_value = drivers
        
        # Configure preferences - all drivers want slot1
        prefs = [
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref2",
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref3",
                "driver_parent_id": "driver3",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            }
        ]
        mock_prefs.query_items.return_value = prefs
        
        # Empty historical assignments
        mock_assignments.query_items.return_value = []
        
        # Run the test
        scheduler = ScheduleGenerator(week_start)
        assignments = scheduler.generate_schedule(clear_existing=True)
        
        # Verify results
        assert len(assignments) == len(template_slots)
        
        # Only one driver should get slot1
        slot1_assignments = [a for a in assignments if a["template_slot_id"] == "slot1"]
        assert len(slot1_assignments) == 1, "Only one driver should get the conflicted slot"

@pytest.mark.asyncio
async def test_scheduler_historical_balancing():
    """Test with historical balancing"""
    # Setup mock data
    with patch('app.services.schedule_generator.get_container') as mock_get_container:
        # Setup mock containers
        mock_templates = MagicMock()
        mock_prefs = MagicMock()
        mock_assignments = MagicMock()
        mock_users = MagicMock()
        
        # Configure container behavior
        def get_mock_container(container_name):
            if container_name == "weekly_schedule_template_slots":
                return mock_templates
            elif container_name == "driver_weekly_preferences":
                return mock_prefs
            elif container_name == "ride_assignments":
                return mock_assignments
            elif container_name == "users":
                return mock_users
            return MagicMock()
        
        mock_get_container.side_effect = get_mock_container
        
        # Setup test data
        week_start = date(2025, 6, 2)
        
        # Configure mock template slots
        template_slots = [
            {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"},
            {"id": "slot2", "day_of_week": 0, "time_slot": "AFTERNOON"}
        ]
        mock_templates.query_items.return_value = template_slots
        
        # Configure mock drivers
        drivers = [
            {"id": "driver1", "name": "Driver 1", "is_active_driver": True},
            {"id": "driver2", "name": "Driver 2", "is_active_driver": True}
        ]
        mock_users.query_items.return_value = drivers
        
        # Configure preferences - both want slot1
        prefs = [
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            },
            {
                "id": "pref2",
                "driver_parent_id": "driver2",
                "week_start_date": week_start.isoformat(),
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED
            }
        ]
        mock_prefs.query_items.return_value = prefs
        
        # Historical assignments - driver1 has driven more
        historical = [
            {
                "id": "past1",
                "driver_parent_id": "driver1",
                "assigned_date": (week_start - timedelta(days=7)).isoformat(),
                "template_slot_id": "slot1"
            },
            {
                "id": "past2",
                "driver_parent_id": "driver1",
                "assigned_date": (week_start - timedelta(days=14)).isoformat(),
                "template_slot_id": "slot1"
            }
        ]
        mock_assignments.query_items.return_value = historical
        
        # Run the test
        scheduler = ScheduleGenerator(week_start)
        assignments = scheduler.generate_schedule(clear_existing=True)
        
        # Verify results
        assert len(assignments) == len(template_slots)
        
        # Driver2 should get slot1 due to having fewer historical assignments
        slot1_assignment = next(a for a in assignments if a["template_slot_id"] == "slot1")
        assert slot1_assignment["driver_parent_id"] == "driver2", "Driver with fewer historical rides should get the slot"
        assert slot1_assignment["assignment_method"] == AssignmentMethod.HISTORICAL_BASED