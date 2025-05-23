"""
Unit tests for the ScheduleGenerator service
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta, datetime
import uuid

from app.services.schedule_generator import ScheduleGenerator
from app.models.core import PreferenceLevel, AssignmentMethod

@pytest.mark.unit
class TestScheduleGenerator:
    
    @pytest.fixture
    def mock_cosmos_containers(self):
        """Setup mocks for all CosmosDB containers used by ScheduleGenerator"""
        with patch('app.services.schedule_generator.get_container') as mock_get_container:
            templates_container = MagicMock()
            prefs_container = MagicMock()
            assignments_container = MagicMock()
            users_container = MagicMock()
            
            # Setup template slots mock data
            templates_container.query_items.return_value = [
                {
                    "id": "slot1",
                    "day_of_week": 0,  # Monday
                    "time_slot": "MORNING",
                    "display_name": "Monday Morning"
                },
                {
                    "id": "slot2",
                    "day_of_week": 0,  # Monday
                    "time_slot": "AFTERNOON",
                    "display_name": "Monday Afternoon"
                },
                {
                    "id": "slot3",
                    "day_of_week": 1,  # Tuesday
                    "time_slot": "MORNING",
                    "display_name": "Tuesday Morning"
                }
            ]
            
            # Setup drivers mock data
            users_container.query_items.return_value = [
                {
                    "id": "driver1",
                    "name": "Driver One",
                    "is_active_driver": True
                },
                {
                    "id": "driver2",
                    "name": "Driver Two",
                    "is_active_driver": True
                },
                {
                    "id": "driver3",
                    "name": "Driver Three",
                    "is_active_driver": True
                }
            ]
            
            # Configure the mock container behavior
            def get_mock_container(container_name):
                if container_name == "weekly_schedule_template_slots":
                    return templates_container
                elif container_name == "driver_weekly_preferences":
                    return prefs_container
                elif container_name == "ride_assignments":
                    return assignments_container
                elif container_name == "users":
                    return users_container
                return MagicMock()
            
            mock_get_container.side_effect = get_mock_container
            
            # Return the mock containers for tests to configure further
            yield {
                "templates_container": templates_container,
                "prefs_container": prefs_container,
                "assignments_container": assignments_container,
                "users_container": users_container,
                "get_container": mock_get_container
            }
    
    def test_get_template_slots(self, mock_cosmos_containers):
        """Test retrieving template slots"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Call the method
        slots = generator._get_template_slots()
        
        # Verify results
        assert len(slots) == 3
        assert slots[0]["id"] == "slot1"
        assert slots[1]["time_slot"] == "AFTERNOON"
        
        # Verify container was called correctly
        mock_cosmos_containers["templates_container"].query_items.assert_called_once()
    
    def test_get_active_drivers(self, mock_cosmos_containers):
        """Test retrieving active drivers"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Call the method
        drivers = generator._get_active_drivers()
        
        # Verify results
        assert len(drivers) == 3
        assert drivers[0]["id"] == "driver1"
        assert drivers[2]["name"] == "Driver Three"
        
        # Verify container was called correctly
        mock_cosmos_containers["users_container"].query_items.assert_called_once()
    
    def test_get_driver_preferences(self, mock_cosmos_containers):
        """Test retrieving driver preferences"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Setup mock preferences data
        mock_cosmos_containers["prefs_container"].query_items.return_value = [
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            },
            {
                "id": "pref2",
                "driver_parent_id": "driver1",
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.LESS_PREFERRED,
                "week_start_date": week_start.isoformat()
            }
        ]
        
        # Call the method
        prefs = generator._get_driver_preferences("driver1")
        
        # Verify results
        assert len(prefs) == 2
        assert prefs["slot1"] == PreferenceLevel.PREFERRED
        assert prefs["slot2"] == PreferenceLevel.LESS_PREFERRED
        
        # Verify container was called correctly
        mock_cosmos_containers["prefs_container"].query_items.assert_called_once()
    
    def test_get_driver_preferences_error(self, mock_cosmos_containers):
        """Test error handling in driver preferences"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Setup mock to raise exception
        mock_cosmos_containers["prefs_container"].query_items.side_effect = Exception("Database error")
        
        # Call should return empty dict on error
        prefs = generator._get_driver_preferences("driver1")
        assert prefs == {}
    
    def test_get_historical_assignments(self, mock_cosmos_containers):
        """Test retrieving and processing historical assignments"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Setup historical assignments mock
        two_weeks_ago = (week_start - timedelta(days=14)).isoformat()
        one_week_ago = (week_start - timedelta(days=7)).isoformat()
        
        mock_cosmos_containers["assignments_container"].query_items.return_value = [
            {
                "id": "assign1",
                "driver_parent_id": "driver1",
                "assigned_date": two_weeks_ago
            },
            {
                "id": "assign2",
                "driver_parent_id": "driver1",
                "assigned_date": one_week_ago
            },
            {
                "id": "assign3",
                "driver_parent_id": "driver2",
                "assigned_date": two_weeks_ago
            }
        ]
        
        # Call the method
        historical_data = generator._get_historical_assignments()
        
        # Verify results
        assert len(historical_data) == 2
        assert historical_data["driver1"]["count"] == 2
        assert historical_data["driver2"]["count"] == 1
        
        # Driver1 has more recent assignments so weighted count should be higher
        assert historical_data["driver1"]["weighted_count"] > historical_data["driver2"]["weighted_count"]
        
        # Verify container was called correctly
        mock_cosmos_containers["assignments_container"].query_items.assert_called_once()
    
    @patch('uuid.uuid4')
    def test_assign_driver_to_slot(self, mock_uuid, mock_cosmos_containers):
        """Test driver assignment algorithm"""
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
        
        week_start = date(2025, 5, 26)  # A Monday
        assignment_date = week_start  # Monday
        generator = ScheduleGenerator(week_start)
        
        # Test data
        slot = {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"}
        drivers = [
            {"id": "driver1", "name": "Driver One"},
            {"id": "driver2", "name": "Driver Two"},
            {"id": "driver3", "name": "Driver Three"}
        ]
        
        # All drivers have preferences for this slot
        all_preferences = {
            "driver1": {"slot1": PreferenceLevel.PREFERRED},
            "driver2": {"slot1": PreferenceLevel.LESS_PREFERRED},
            "driver3": {"slot1": PreferenceLevel.UNAVAILABLE}
        }
        
        # Historical metrics
        driver_metrics = {
            "driver1": {"count": 3, "weighted_count": 2.5, "last_assignment_date": date(2025, 5, 19)},
            "driver2": {"count": 1, "weighted_count": 0.5, "last_assignment_date": date(2025, 5, 12)},
            "driver3": {"count": 2, "weighted_count": 1.0, "last_assignment_date": None}
        }
        
        # Call the method
        assignment = generator._assign_driver_to_slot(
            slot, drivers, all_preferences, driver_metrics, assignment_date
        )
        
        # Verify results
        assert assignment is not None
        assert assignment["driver_parent_id"] == "driver2"  # Driver 2 has fewest assignments
        assert assignment["template_slot_id"] == "slot1"
        assert assignment["assignment_method"] == AssignmentMethod.PREFERENCE_BASED
        assert assignment["id"] == "12345678-1234-5678-1234-567812345678"
        
        # Test with driver3 not being unavailable
        all_preferences["driver3"]["slot1"] = PreferenceLevel.PREFERRED
        driver_metrics["driver3"]["count"] = 0  # Make driver3 the best choice
        
        # Call the method again
        assignment = generator._assign_driver_to_slot(
            slot, drivers, all_preferences, driver_metrics, assignment_date
        )
        
        # Verify different results
        assert assignment["driver_parent_id"] == "driver3"  # Driver 3 now has no assignments
    
    @patch('uuid.uuid4')
    def test_generate_schedule(self, mock_uuid, mock_cosmos_containers):
        """Test the complete schedule generation process"""
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
        
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Setup preferences mock
        mock_cosmos_containers["prefs_container"].query_items.side_effect = lambda **kwargs: [
            # driver1 prefers Monday morning
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            }
        ] if kwargs.get("parameters", [{}])[0].get("value") == "driver1" else [
            # driver2 prefers Monday afternoon
            {
                "id": "pref2",
                "driver_parent_id": "driver2",
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            }
        ] if kwargs.get("parameters", [{}])[0].get("value") == "driver2" else [
            # driver3 prefers Tuesday morning
            {
                "id": "pref3",
                "driver_parent_id": "driver3",
                "template_slot_id": "slot3",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            }
        ]
        
        # Setup historical assignments mock (empty for this test)
        mock_cosmos_containers["assignments_container"].query_items.return_value = []
        
        # Call the method
        assignments = generator.generate_schedule()
        
        # Verify results
        assert len(assignments) == 3  # All 3 slots should be assigned
        
        # Check that preferences were respected
        driver1_assignments = [a for a in assignments if a["driver_parent_id"] == "driver1"]
        driver2_assignments = [a for a in assignments if a["driver_parent_id"] == "driver2"]
        driver3_assignments = [a for a in assignments if a["driver_parent_id"] == "driver3"]
        
        assert any(a["template_slot_id"] == "slot1" for a in driver1_assignments)
        assert any(a["template_slot_id"] == "slot2" for a in driver2_assignments)
        assert any(a["template_slot_id"] == "slot3" for a in driver3_assignments)
        
        # Verify container was called to create each assignment
        assert mock_cosmos_containers["assignments_container"].create_item.call_count == 3
        mock_cosmos_containers["templates_container"].query_items.assert_called_once()
    
    def test_get_driver_preferences(self, mock_cosmos_containers):
        """Test retrieving driver preferences"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Setup preferences mock data
        mock_cosmos_containers["prefs_container"].query_items.return_value = [
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            },
            {
                "id": "pref2",
                "driver_parent_id": "driver1",
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.LESS_PREFERRED,
                "week_start_date": week_start.isoformat()
            }
        ]
        
        # Call the method
        prefs = generator._get_driver_preferences("driver1")
        
        # Verify results
        assert len(prefs) == 2
        assert prefs["slot1"] == PreferenceLevel.PREFERRED
        assert prefs["slot2"] == PreferenceLevel.LESS_PREFERRED
        
        # Verify container was called correctly 
        mock_cosmos_containers["prefs_container"].query_items.assert_called_once()
    
    def test_get_existing_assignments(self, mock_cosmos_containers):
        """Test retrieving existing assignments"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Setup mock data for existing assignments
        mock_cosmos_containers["assignments_container"].query_items.return_value = [
            {
                "id": "assign1",
                "template_slot_id": "slot1",
                "driver_parent_id": "driver1",
                "assigned_date": week_start.isoformat(),
                "status": "SCHEDULED"
            },
            {
                "id": "assign2",
                "template_slot_id": "slot2",
                "driver_parent_id": "driver2",
                "assigned_date": week_start.isoformat(),
                "status": "SCHEDULED"
            }
        ]
        
        # Call the method
        assignments = generator.get_existing_assignments()
        
        # Verify results
        assert len(assignments) == 2
        assert assignments[0]["driver_parent_id"] == "driver1"
        assert assignments[1]["driver_parent_id"] == "driver2"
        
        # Verify container was called correctly
        mock_cosmos_containers["assignments_container"].query_items.assert_called_once()
    
    def test_assign_driver_to_slot(self, mock_cosmos_containers):
        """Test the driver assignment algorithm"""
        week_start = date(2025, 5, 26)  # A Monday
        assignment_date = week_start  # Monday
        generator = ScheduleGenerator(week_start)
        
        # Test data
        slot = {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"}
        drivers = [
            {"id": "driver1", "name": "Driver One"},
            {"id": "driver2", "name": "Driver Two"},
            {"id": "driver3", "name": "Driver Three"}
        ]
          # All drivers have preferences for this slot
        all_preferences = {
            "driver1": {"slot1": PreferenceLevel.PREFERRED},
            "driver2": {"slot1": PreferenceLevel.LESS_PREFERRED},
            "driver3": {"slot1": PreferenceLevel.UNAVAILABLE}
        }
        
        # Historical metrics - driver2 has lower counts and should be selected
        driver_metrics = {
            "driver1": {"count": 3, "weighted_count": 2.5, "last_assignment_date": date(2025, 5, 19)},
            "driver2": {"count": 1, "weighted_count": 0.5, "last_assignment_date": date(2025, 5, 12)},
            "driver3": {"count": 2, "weighted_count": 1.0, "last_assignment_date": None}
        }
        
        # Call the method
        with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')):
            assignment = generator._assign_driver_to_slot(
                slot, drivers, all_preferences, driver_metrics, assignment_date
            )
        
        # Verify results
        assert assignment is not None
        # With our improved fairness algorithm, driver1 is selected because PREFERRED status
        # outweighs the historical assignment count
        assert assignment["driver_parent_id"] == "driver1"  
        assert assignment["template_slot_id"] == "slot1"
        assert assignment["assignment_method"] == AssignmentMethod.PREFERENCE_BASED
        
        # Test with different preference levels
        all_preferences["driver3"]["slot1"] = PreferenceLevel.PREFERRED
        driver_metrics["driver3"]["count"] = 0  # Make driver3 the best choice
        
        with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')):
            assignment = generator._assign_driver_to_slot(
                slot, drivers, all_preferences, driver_metrics, assignment_date
            )
        
        # Verify driver3 is now selected as it has PREFERRED and lowest count
        assert assignment["driver_parent_id"] == "driver3"
    
    def test_generate_schedule(self, mock_cosmos_containers):
        """Test the full schedule generation process"""
        week_start = date(2025, 5, 26)  # A Monday
        generator = ScheduleGenerator(week_start)
        
        # Configure preference mock data
        mock_cosmos_containers["prefs_container"].query_items.return_value = [
            # driver1 prefers Monday morning
            {
                "id": "pref1",
                "driver_parent_id": "driver1",
                "template_slot_id": "slot1",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            },
            # driver2 prefers Monday afternoon
            {
                "id": "pref2",
                "driver_parent_id": "driver2",
                "template_slot_id": "slot2",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            },
            # driver3 prefers Tuesday morning
            {
                "id": "pref3",
                "driver_parent_id": "driver3",
                "template_slot_id": "slot3",
                "preference_level": PreferenceLevel.PREFERRED,
                "week_start_date": week_start.isoformat()
            }
        ]
        
        # Configure historical assignments (empty for simplicity)
        mock_cosmos_containers["assignments_container"].query_items.return_value = []
        
        # Call the method with UUID patched for consistent test results
        with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')):
            assignments = generator.generate_schedule()
        
        # Verify results
        assert len(assignments) == 3  # All slots should be assigned
        
        # Check assignments match preferences
        driver_assignments = {}
        for assignment in assignments:
            driver_id = assignment["driver_parent_id"]
            if driver_id not in driver_assignments:
                driver_assignments[driver_id] = []
            driver_assignments[driver_id].append(assignment["template_slot_id"])
        
        assert "slot1" in driver_assignments.get("driver1", [])
        assert "slot2" in driver_assignments.get("driver2", [])
        assert "slot3" in driver_assignments.get("driver3", [])
