"""
Mock implementation of the Cosmos DB module for testing
"""
from unittest.mock import MagicMock

# Mock containers
mock_containers = {
    "weekly_schedule_template_slots": MagicMock(),
    "driver_weekly_preferences": MagicMock(),
    "ride_assignments": MagicMock(),
    "users": MagicMock()
}

# Set up default behavior for the containers
mock_containers["weekly_schedule_template_slots"].query_items.return_value = [
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

mock_containers["users"].query_items.return_value = [
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

mock_containers["ride_assignments"].query_items.return_value = []
mock_containers["driver_weekly_preferences"].query_items.return_value = []

def get_container(container_name: str):
    """Get a mock container by name"""
    if container_name in mock_containers:
        return mock_containers[container_name]
    
    # If container doesn't exist, create a new mock
    mock = MagicMock()
    mock_containers[container_name] = mock
    return mock

# Other functions that might be called but don't need real implementation for testing
def get_cosmos_client():
    return MagicMock()

def get_database():
    return MagicMock()

def init_cosmos_db():
    """Mock initialization"""
    pass
