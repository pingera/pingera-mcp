"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
from unittest.mock import Mock, patch

from config import Config, OperationMode
from pingera_mcp.sdk_client import PingeraSDKClient as PingeraClient


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Config()
    config.api_key = "test_api_key"
    config.base_url = "https://api.test.com/v1"
    config.mode = OperationMode.READ_ONLY
    config.timeout = 30
    config.max_retries = 3
    config.debug = False
    config.server_name = "Test MCP Server"
    return config


@pytest.fixture
def mock_page():
    """Create a mock page object for testing."""
    return {
        "id": "123",
        "name": "Test Page",
        "url": "https://example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "organization_id": "org123"
    }


@pytest.fixture
def mock_page_list():
    """Mock page list response."""
    from unittest.mock import Mock

    # Create a mock page object directly
    page = Mock()
    page.id = 1
    page.name = "Test Page"
    page.subdomain = "test"
    page.url = "https://example.com"
    page.language = "en"
    page.created_at = "2024-01-01T00:00:00Z"
    page.dict.return_value = {
        "id": 1,
        "name": "Test Page",
        "subdomain": "test",
        "url": "https://example.com",
        "language": "en",
        "created_at": "2024-01-01T00:00:00Z"
    }

    # Create a mock response object that matches the SDK structure
    mock_response = Mock()
    mock_response.pages = [page]
    mock_response.total = 1
    mock_response.page = 1
    mock_response.per_page = 10
    return mock_response


@pytest.fixture
def mock_component():
    """Create a mock component object for testing."""
    return {
        "id": "comp123",
        "name": "Test Component",
        "description": "Test component description",
        "status": "operational",
        "page_id": "page123",
        "group": False,
        "showcase": True,
        "position": 1
    }


@pytest.fixture
def mock_pingera_client():
    """Create a mock Pingera client for testing."""
    client = Mock(spec=PingeraClient)
    client.test_connection.return_value = True
    client.get_api_info.return_value = {
        "connected": True,
        "version": "v1",
        "status": "ok"
    }

    # Mock the component methods directly on client
    client.get_component_groups.return_value = []
    client.get_component.return_value = None
    client.create_component.return_value = None
    client.update_component.return_value = None
    client.patch_component.return_value = None
    client.delete_component.return_value = True

    # Mock the page methods directly on client
    client.get_pages.return_value = None
    client.get_page.return_value = None
    client.create_page.return_value = None
    client.update_page.return_value = None
    client.patch_page.return_value = None
    client.delete_page.return_value = True

    return client