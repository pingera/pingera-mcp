"""
Tests for Pydantic models.
"""
import pytest
from datetime import datetime

from pingera.models import Page, PageList, APIResponse


class TestModels:
    """Test cases for Pydantic models."""

    def test_page_model_creation(self):
        """Test Page model creation with required fields."""
        page_data = {
            "id": "123",
            "name": "Test Page",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "organization_id": "org123"
        }

        page = Page(**page_data)

        assert page.id == "123"
        assert page.name == "Test Page"
        assert page.url == "https://example.com"
        assert page.organization_id == "org123"

    def test_page_model_with_optional_fields(self):
        """Test Page model with optional fields."""
        page_data = {
            "id": "123",
            "name": "Test Page",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "organization_id": "org123",
            "subdomain": "test",
            "language": "en",
            "allow_email_subscribers": True,
            "css_body_background_color": "#ffffff"
        }

        page = Page(**page_data)

        assert page.subdomain == "test"
        assert page.language == "en"
        assert page.allow_email_subscribers is True
        assert page.css_body_background_color == "#ffffff"

    def test_page_list_model(self):
        """Test PageList model."""
        page_data = {
            "id": "123",
            "name": "Test Page",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "organization_id": "org123"
        }

        page = Page(**page_data)
        page_list = PageList(
            pages=[page],
            total=1,
            page=1,
            per_page=10
        )

        assert len(page_list.pages) == 1
        assert page_list.total == 1
        assert page_list.page == 1
        assert page_list.per_page == 10

    def test_api_response_model(self):
        """Test APIResponse model."""
        response = APIResponse(
            success=True,
            message="Operation successful",
            data={"key": "value"}
        )

        assert response.success is True
        assert response.message == "Operation successful"
        assert response.data == {"key": "value"}
        assert response.errors == []

    def test_api_response_with_errors(self):
        """Test APIResponse model with errors."""
        response = APIResponse(
            success=False,
            errors=["Error 1", "Error 2"]
        )

        assert response.success is False
        assert len(response.errors) == 2
        assert "Error 1" in response.errors

    def test_page_model_required_field_validation(self):
        """Test that required fields are properly validated."""
        # Test missing required 'name' field
        with pytest.raises(ValueError):
            Page(
                id="123",
                url="https://example.com",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                organization_id="org123"
                # missing 'name' field
            )

    def test_page_model_field_length_validation(self):
        """Test field length constraints."""
        # Test name field length constraints
        with pytest.raises(ValueError):
            Page(name="")  # Too short (min_length=1)

        with pytest.raises(ValueError):
            Page(name="x" * 101)  # Too long (max_length=100)