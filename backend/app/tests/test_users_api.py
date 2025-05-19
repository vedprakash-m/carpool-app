"""
Tests for the users API endpoints
"""
import pytest
import uuid
import json
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Import the router
from app.api.v1.endpoints.users import router, create_user
from app.models.core import UserCreate, UserRole

class TestUsersEndpoints:
    
    @pytest.fixture
    def mock_container(self):
        """Creates a mock container for CosmosDB"""
        with patch('app.api.v1.endpoints.users.get_container') as mock_get_container:
            container = MagicMock()
            mock_get_container.return_value = container
            yield container
    
    @pytest.fixture
    def mock_auth(self):
        """Mocks authentication functions"""
        with patch('app.api.v1.endpoints.users.check_admin_role') as mock_check_admin:
            # Simulate an admin user
            admin_user = {
                "id": str(uuid.uuid4()),
                "email": "admin@example.com",
                "role": "ADMIN"
            }
            mock_check_admin.return_value = admin_user
            yield admin_user
            
        with patch('app.api.v1.endpoints.users.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password_123"
            yield
            
        with patch('app.api.v1.endpoints.users.validate_password_strength') as mock_validate:
            mock_validate.return_value = (True, "")
            yield
    
    async def test_create_user_success(self, mock_container, mock_auth):
        """Test creating a user successfully"""
        # Setup
        mock_container.query_items.return_value = []  # No existing users with same email
        mock_container.create_item.return_value = {
            "id": "123",
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "PARENT",
            "is_active_driver": True,
            "created_at": "2025-05-18T10:00:00",
            "updated_at": "2025-05-18T10:00:00"
        }
        
        # Test data
        new_user = UserCreate(
            email="newuser@example.com",
            full_name="New User",
            role=UserRole.PARENT,
            is_active_driver=True,
            initial_password="SecurePass1!"
        )
        
        # Call the function
        response = await create_user(new_user, mock_auth)
        
        # Assertions
        assert response["email"] == "newuser@example.com"
        assert response["full_name"] == "New User"
        assert response["role"] == "PARENT"
        assert mock_container.create_item.called
        
    async def test_create_user_email_exists(self, mock_container, mock_auth):
        """Test creating a user with an existing email should fail"""
        # Setup
        mock_container.query_items.return_value = [{
            "id": "456",
            "email": "existing@example.com",
        }]
        
        # Test data
        new_user = UserCreate(
            email="existing@example.com",
            full_name="Existing User",
            role=UserRole.PARENT,
            initial_password="SecurePass1!"
        )
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await create_user(new_user, mock_auth)
        
        # Assertions
        assert excinfo.value.status_code == 400
        assert "Email already registered" in str(excinfo.value.detail)

    @patch('app.api.v1.endpoints.users.validate_password_strength')
    async def test_create_user_weak_password(self, mock_validate, mock_container, mock_auth):
        """Test creating a user with a weak password should fail"""
        # Setup
        mock_container.query_items.return_value = []  # No existing users
        mock_validate.return_value = (False, "Password must contain at least one uppercase letter")
        
        # Test data
        new_user = UserCreate(
            email="newuser@example.com",
            full_name="New User",
            role=UserRole.PARENT,
            initial_password="weakpassword"  # Weak password
        )
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await create_user(new_user, mock_auth)
        
        # Assertions
        assert excinfo.value.status_code == 400
        assert "Password is too weak" in str(excinfo.value.detail)
