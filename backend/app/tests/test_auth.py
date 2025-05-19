"""
Tests for authentication endpoints and functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import timedelta

# Import the router and functions
from app.api.v1.endpoints.auth import login_access_token
from app.core.auth import create_access_token, verify_password

class TestAuthEndpoints:
    
    @pytest.fixture
    def mock_container(self):
        """Creates a mock container for CosmosDB"""
        with patch('app.api.v1.endpoints.auth.get_container') as mock_get_container:
            container = MagicMock()
            mock_get_container.return_value = container
            yield container
    
    @pytest.fixture
    def mock_auth_functions(self):
        """Mocks auth-related functions"""
        with patch('app.api.v1.endpoints.auth.verify_password') as mock_verify:
            yield mock_verify
    
    @pytest.fixture
    def mock_token_creation(self):
        """Mocks token creation"""
        with patch('app.api.v1.endpoints.auth.create_access_token') as mock_create:
            mock_create.return_value = "mocked_access_token"
            yield mock_create
    
    @pytest.fixture
    def mock_form_data(self):
        """Creates mock OAuth2 form data"""
        mock_form = MagicMock()
        mock_form.username = "test@example.com"
        mock_form.password = "password123"
        return mock_form
    
    async def test_login_success(self, mock_container, mock_auth_functions, mock_token_creation, mock_form_data):
        """Test successful login flow"""
        # Setup
        mock_container.query_items.return_value = [{
            "id": "123",
            "email": "test@example.com",
            "role": "PARENT",
            "hashed_password": "hashed_password_123"
        }]
        mock_auth_functions.return_value = True  # Password verification succeeds
        
        # Call the function
        response = await login_access_token(mock_form_data)
        
        # Assertions
        assert response["access_token"] == "mocked_access_token"
        assert response["token_type"] == "bearer"
        assert response["email"] == "test@example.com"
        assert response["role"] == "PARENT"
        mock_auth_functions.assert_called_once_with("password123", "hashed_password_123")
    
    async def test_login_user_not_found(self, mock_container, mock_form_data):
        """Test login with non-existent user"""
        # Setup
        mock_container.query_items.return_value = []  # User not found
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await login_access_token(mock_form_data)
        
        # Assertions
        assert excinfo.value.status_code == 401
        assert "Incorrect email or password" in str(excinfo.value.detail)
    
    async def test_login_incorrect_password(self, mock_container, mock_auth_functions, mock_form_data):
        """Test login with incorrect password"""
        # Setup
        mock_container.query_items.return_value = [{
            "id": "123",
            "email": "test@example.com",
            "role": "PARENT",
            "hashed_password": "hashed_password_123"
        }]
        mock_auth_functions.return_value = False  # Password verification fails
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await login_access_token(mock_form_data)
        
        # Assertions
        assert excinfo.value.status_code == 401
        assert "Incorrect email or password" in str(excinfo.value.detail)

class TestAuthCoreFunctions:
    
    def test_verify_password(self):
        """Test password verification"""
        with patch('app.core.auth.pwd_context.verify') as mock_verify:
            mock_verify.return_value = True
            result = verify_password("plain_password", "hashed_password")
            assert result is True
            mock_verify.assert_called_once_with("plain_password", "hashed_password")
    
    def test_create_access_token(self):
        """Test access token creation"""
        with patch('app.core.auth.jwt.encode') as mock_encode:
            mock_encode.return_value = "encoded_jwt"
            with patch('app.core.auth.settings.SECRET_KEY', "test_secret"):
                with patch('app.core.auth.settings.ALGORITHM', "HS256"):
                    # Test with expires_delta
                    token = create_access_token(
                        data={"sub": "user123"},
                        expires_delta=timedelta(minutes=30)
                    )
                    assert token == "encoded_jwt"
                    assert mock_encode.called
                    
                    # Test without expires_delta (should use default)
                    mock_encode.reset_mock()
                    token = create_access_token(data={"sub": "user123"})
                    assert token == "encoded_jwt"
                    assert mock_encode.called
