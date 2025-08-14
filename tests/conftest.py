
"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
from unittest.mock import Mock, patch

from config import Config, OperationMode
from pingera_mcp import PingeraClient


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
def mock_page_list(mock_page):
    """Create a mock page list for testing."""
    return {
        "pages": [mock_page],
        "total": 1,
        "page": 1,
        "per_page": 10
    }


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
    
    # Mock the components endpoint
    client.components = Mock()
    client.components.get_component_groups.return_value = []
    client.components.get_component.return_value = None
    client.components.create_component.return_value = None
    client.components.update_component.return_value = None
    client.components.patch_component.return_value = None
    client.components.delete_component.return_value = True
    
    # Mock the pages endpoint
    client.pages = Mock()
    client.pages.list.return_value = None
    client.pages.get.return_value = None
    
    return client
