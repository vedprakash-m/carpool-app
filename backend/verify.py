"""
Verification script for the schedule generator's main functionality
"""

print("Starting verification...")

# Import the schedule generator and models
from app.services.schedule_generator import ScheduleGenerator
from app.models.core import PreferenceLevel, AssignmentMethod
from datetime import date, timedelta
import uuid

# Create a mock UUID function
def mock_uuid4():
    return "test-uuid"

# Override the uuid.uuid4 function
uuid.uuid4 = mock_uuid4

# Import mock cosmos module
from app.tests.mock_cosmos import get_container

# Create a schedule generator
week_start = date(2025, 5, 26)  # A Monday
generator = ScheduleGenerator(week_start)

# Test getting template slots
print("\nTesting _get_template_slots:")
slots = generator._get_template_slots()
print(f"Got {len(slots)} template slots")

# Test getting active drivers
print("\nTesting _get_active_drivers:")
drivers = generator._get_active_drivers()
print(f"Got {len(drivers)} active drivers")

# Test the assignment algorithm
print("\nTesting _assign_driver_to_slot:")
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
    "driver1": {"count": 3, "weighted_count": 2.5, "last_assignment_date": week_start - timedelta(days=7)},
    "driver2": {"count": 1, "weighted_count": 0.5, "last_assignment_date": week_start - timedelta(days=14)}
}

assignment = generator._assign_driver_to_slot(
    slot, drivers, all_preferences, driver_metrics, week_start
)

if assignment:
    print(f"Successfully assigned driver {assignment['driver_parent_id']} to slot {assignment['template_slot_id']}")
    print(f"Assignment method: {assignment['assignment_method']}")
else:
    print("Failed to create assignment")

print("\nVerification completed")
