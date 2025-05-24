"""
Direct test script for the Schedule Generator
"""
import os
import sys
import unittest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

# Set required environment variables
os.environ["COSMOS_ENDPOINT"] = "https://mock-cosmos.azure.com:443/"
os.environ["COSMOS_KEY"] = "mock-key=="
os.environ["COSMOS_DATABASE"] = "carpool_db_test" 
os.environ["JWT_SECRET_KEY"] = "mock-jwt-key"

# Import after setting environment variables
from app.services.schedule_generator import ScheduleGenerator
from app.models.core import PreferenceLevel, AssignmentMethod

class ScheduleGeneratorTest(unittest.TestCase):
    
    @patch('app.services.schedule_generator.get_container')
    def test_get_template_slots(self, mock_get_container):
        # Setup
        mock_container = MagicMock()
        mock_container.query_items.return_value = [
            {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"},
            {"id": "slot2", "day_of_week": 0, "time_slot": "AFTERNOON"}
        ]
        mock_get_container.return_value = mock_container
        
        # Execute
        week_start = date(2025, 5, 26)
        generator = ScheduleGenerator(week_start)
        slots = generator._get_template_slots()
        
        # Assert
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0]["id"], "slot1")
        print("✓ get_template_slots works correctly")
    
    @patch('app.services.schedule_generator.get_container')
    def test_get_active_drivers(self, mock_get_container):
        # Setup
        mock_container = MagicMock()
        mock_container.query_items.return_value = [
            {"id": "driver1", "name": "Driver One", "is_active_driver": True},
            {"id": "driver2", "name": "Driver Two", "is_active_driver": True}
        ]
        mock_get_container.return_value = mock_container
        
        # Execute
        week_start = date(2025, 5, 26)
        generator = ScheduleGenerator(week_start)
        drivers = generator._get_active_drivers()
        
        # Assert
        self.assertEqual(len(drivers), 2)
        self.assertEqual(drivers[0]["id"], "driver1")
        print("✓ get_active_drivers works correctly")
    
    @patch('app.services.schedule_generator.get_container')
    def test_assign_driver_to_slot(self, mock_get_container):
        # Setup
        mock_container = MagicMock()
        mock_get_container.return_value = mock_container
        
        # Test data
        week_start = date(2025, 5, 26)
        slot = {"id": "slot1", "day_of_week": 0, "time_slot": "MORNING"}
        drivers = [
            {"id": "driver1", "name": "Driver One"},
            {"id": "driver2", "name": "Driver Two"}
        ]
        all_preferences = {
            "driver1": {"slot1": PreferenceLevel.PREFERRED},
            "driver2": {"slot1": PreferenceLevel.LESS_PREFERRED}
        }
        driver_metrics = {
            "driver1": {"count": 3, "weighted_count": 2.5, "last_assignment_date": date(2025, 5, 19)},
            "driver2": {"count": 1, "weighted_count": 0.5, "last_assignment_date": date(2025, 5, 12)}
        }
        
        # Execute
        with patch('uuid.uuid4', return_value='12345678-1234-5678-1234-567812345678'):
            generator = ScheduleGenerator(week_start)
            assignment = generator._assign_driver_to_slot(
                slot, drivers, all_preferences, driver_metrics, week_start
            )
        
        # Assert
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment["driver_parent_id"], "driver2")  # Lower count should win
        self.assertEqual(assignment["template_slot_id"], "slot1")
        print("✓ assign_driver_to_slot works correctly with fairness algorithm")

if __name__ == "__main__":
    print("\n==== Schedule Generator Implementation Tests ====\n")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n==== All Tests Completed ====\n")
