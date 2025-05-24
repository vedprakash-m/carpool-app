"""
Configuration file for pytest
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to allow imports from the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock settings fixture
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock the settings to avoid needing actual environment variables for testing"""
    with patch('app.core.config.get_settings') as mock_get_settings:
        # Create a mock settings object with all required properties
        mock_settings = MagicMock()
        mock_settings.COSMOS_ENDPOINT = "https://mock-cosmos.azure.com:443/"
        mock_settings.COSMOS_KEY = "mock-key=="
        mock_settings.COSMOS_DATABASE = "carpool_db_test"
        mock_settings.JWT_SECRET_KEY = "mock-jwt-key"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
        
        mock_get_settings.return_value = mock_settings
        yield mock_get_settings

# Mock Cosmos DB container fixture
@pytest.fixture
def mock_cosmos_container():
    """Mock Cosmos DB container for testing"""
    with patch('app.db.cosmos.get_container') as mock_get_container:
        # Create a mock container
        mock_container = MagicMock()
        
        # Set up default return values for common methods
        mock_container.query_items.return_value = []
        mock_container.create_item.return_value = {}
        mock_container.upsert_item.return_value = {}
        mock_container.read_item.return_value = {}
        mock_container.delete_item.return_value = {}
        
        # Make the function return the mock container
        mock_get_container.return_value = mock_container
        
        yield mock_container
