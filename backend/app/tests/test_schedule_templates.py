"""
Tests for schedule templates functionality
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Import the router and functions
from app.api.v1.endpoints.schedule_templates import create_template, get_template, list_templates, update_template, delete_template

class TestScheduleTemplates:
    
    @pytest.fixture
    def mock_container(self):
        """Creates a mock container for CosmosDB"""
        with patch('app.api.v1.endpoints.schedule_templates.get_container') as mock_get_container:
            container = MagicMock()
            mock_get_container.return_value = container
            yield container
    
    @pytest.fixture
    def mock_admin(self):
        """Mocks authentication functions for an admin user"""
        with patch('app.api.v1.endpoints.schedule_templates.check_admin_role') as mock_check_admin:
            # Simulate an admin user
            admin_user = {
                "id": str(uuid.uuid4()),
                "email": "admin@example.com",
                "role": "ADMIN"
            }
            mock_check_admin.return_value = admin_user
            yield admin_user
    
    @pytest.fixture
    def template_data(self):
        """Sample template data"""
        return {
            "name": "Fall 2025 Schedule",
            "description": "Template for Fall 2025 semester",
            "preferences": {
                "max_students_per_car": 4,
                "preferred_drivers": ["parent1", "parent2"],
                "excluded_drivers": [],
                "student_groups": [
                    {
                        "name": "Group A",
                        "students": ["student1", "student2"]
                    },
                    {
                        "name": "Group B",
                        "students": ["student3", "student4"]
                    }
                ]
            }
        }
    
    async def test_create_template_success(self, mock_container, mock_admin, template_data):
        """Test successfully creating a schedule template"""
        # Setup
        mock_container.create_item.return_value = {
            "id": "template1",
            **template_data,
            "created_by": mock_admin["id"],
            "created_at": "2025-05-18T12:00:00Z",
            "updated_at": "2025-05-18T12:00:00Z"
        }
        
        # Call function
        result = await create_template(template_data, mock_admin)
        
        # Assertions
        assert result["name"] == "Fall 2025 Schedule"
        assert result["description"] == "Template for Fall 2025 semester"
        assert result["preferences"]["max_students_per_car"] == 4
        assert len(result["preferences"]["student_groups"]) == 2
        assert result["created_by"] == mock_admin["id"]
        assert mock_container.create_item.called
    
    async def test_get_template_success(self, mock_container, mock_admin):
        """Test successfully retrieving a template"""
        # Setup
        mock_template = {
            "id": "template1",
            "name": "Fall 2025 Schedule",
            "description": "Template for Fall 2025 semester",
            "preferences": {
                "max_students_per_car": 4
            },
            "created_by": mock_admin["id"],
            "created_at": "2025-05-18T12:00:00Z"
        }
        mock_container.read_item.return_value = mock_template
        
        # Call function
        result = await get_template("template1", mock_admin)
        
        # Assertions
        assert result["id"] == "template1"
        assert result["name"] == "Fall 2025 Schedule"
        assert mock_container.read_item.called
        assert mock_container.read_item.call_args[1]["id"] == "template1"
    
    async def test_get_template_not_found(self, mock_container, mock_admin):
        """Test retrieving a non-existent template"""
        # Setup
        mock_container.read_item.side_effect = Exception("Resource not found")
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as excinfo:
            await get_template("nonexistent", mock_admin)
        
        # Assertions
        assert excinfo.value.status_code == 404
        assert "Template not found" in str(excinfo.value.detail)
    
    async def test_list_templates(self, mock_container, mock_admin):
        """Test listing all templates"""
        # Setup
        mock_templates = [
            {
                "id": "template1",
                "name": "Fall 2025 Schedule",
                "description": "Template for Fall 2025 semester"
            },
            {
                "id": "template2",
                "name": "Spring 2026 Schedule",
                "description": "Template for Spring 2026 semester"
            }
        ]
        mock_container.query_items.return_value = mock_templates
        
        # Call function
        result = await list_templates(mock_admin)
        
        # Assertions
        assert len(result) == 2
        assert result[0]["id"] == "template1"
        assert result[1]["id"] == "template2"
        assert mock_container.query_items.called
    
    async def test_update_template_success(self, mock_container, mock_admin):
        """Test successfully updating a template"""
        # Setup
        template_id = "template1"
        update_data = {
            "name": "Updated Fall 2025 Schedule",
            "preferences": {
                "max_students_per_car": 5
            }
        }
        
        # Mock existing template
        mock_container.read_item.return_value = {
            "id": template_id,
            "name": "Fall 2025 Schedule",
            "description": "Template for Fall 2025 semester",
            "preferences": {
                "max_students_per_car": 4
            },
            "created_by": mock_admin["id"],
            "created_at": "2025-05-18T12:00:00Z"
        }
        
        # Mock update result
        mock_container.replace_item.return_value = {
            "id": template_id,
            "name": "Updated Fall 2025 Schedule",
            "description": "Template for Fall 2025 semester",
            "preferences": {
                "max_students_per_car": 5
            },
            "created_by": mock_admin["id"],
            "created_at": "2025-05-18T12:00:00Z",
            "updated_at": "2025-05-18T14:00:00Z"
        }
        
        # Call function
        result = await update_template(template_id, update_data, mock_admin)
        
        # Assertions
        assert result["name"] == "Updated Fall 2025 Schedule"
        assert result["preferences"]["max_students_per_car"] == 5
        assert mock_container.read_item.called
        assert mock_container.replace_item.called
    
    async def test_delete_template_success(self, mock_container, mock_admin):
        """Test successfully deleting a template"""
        # Setup
        template_id = "template1"
        
        # Mock successful deletion
        mock_container.delete_item.return_value = {}
        
        # Call function
        result = await delete_template(template_id, mock_admin)
        
        # Assertions
        assert result["success"] is True
        assert mock_container.delete_item.called
        assert mock_container.delete_item.call_args[1]["id"] == template_id
