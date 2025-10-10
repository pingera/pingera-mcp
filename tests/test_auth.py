"""
Tests for authentication utilities.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from pingera_mcp.auth import (
    extract_auth_from_request,
    get_auth_type,
    create_client_from_auth,
    get_request_client
)
from pingera_mcp.config import Config
from pingera_mcp.sdk_client import PingeraSDKClient


def test_get_auth_type_bearer():
    """Test Bearer token parsing."""
    auth_type, credentials = get_auth_type("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    assert auth_type == "bearer"
    assert credentials == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


def test_get_auth_type_api_key():
    """Test API key parsing."""
    auth_type, credentials = get_auth_type("sk_test_12345")
    assert auth_type == "api_key"
    assert credentials == "sk_test_12345"


def test_get_auth_type_case_insensitive():
    """Test case-insensitive Bearer parsing."""
    auth_type, credentials = get_auth_type("bearer token123")
    assert auth_type == "bearer"
    assert credentials == "token123"


def test_create_client_from_auth_with_api_key():
    """Test client creation with API key."""
    config = Config()
    client = create_client_from_auth(api_key="test_key", config=config)

    assert isinstance(client, PingeraSDKClient)
    assert client.api_key == "test_key"
    assert client.jwt_token is None


def test_create_client_from_auth_with_jwt():
    """Test client creation with JWT token."""
    config = Config()
    client = create_client_from_auth(jwt_token="test_token", config=config)

    assert isinstance(client, PingeraSDKClient)
    assert client.jwt_token == "test_token"
    assert client.api_key is None


def test_get_request_client_returns_default():
    """Test that get_request_client returns default client in stdio mode."""
    config = Config()
    config.transport_mode = "stdio"
    default_client = Mock(spec=PingeraSDKClient)

    result = get_request_client(config, default_client)

    assert result is default_client


def test_extract_auth_from_request_not_in_http_context():
    """Test auth extraction when not in HTTP context."""
    result = extract_auth_from_request()
    assert result is None

# New tests for dual-mode authentication

def test_create_client_from_auth_dual_mode_http_api_key():
    """Test client creation in dual-mode (HTTP) with API key."""
    config = Config()
    config.transport_mode = "http"
    client = create_client_from_auth(api_key="http_api_key", config=config)

    assert isinstance(client, PingeraSDKClient)
    assert client.api_key == "http_api_key"
    assert client.jwt_token is None

def test_create_client_from_auth_dual_mode_http_jwt():
    """Test client creation in dual-mode (HTTP) with JWT token."""
    config = Config()
    config.transport_mode = "http"
    client = create_client_from_auth(jwt_token="http_jwt_token", config=config)

    assert isinstance(client, PingeraSDKClient)
    assert client.jwt_token == "http_jwt_token"
    assert client.api_key is None

def test_extract_auth_from_request_http_mode_bearer():
    """Test auth extraction in HTTP mode with Bearer token."""
    mock_request = Mock()
    mock_request.headers.get.return_value = "Bearer xyz123"
    with patch('pingera_mcp.auth.flask.request', mock_request):
        auth_type, credentials = extract_auth_from_request()
        assert auth_type == "bearer"
        assert credentials == "xyz123"

def test_extract_auth_from_request_http_mode_api_key():
    """Test auth extraction in HTTP mode with API key."""
    mock_request = Mock()
    mock_request.headers.get.side_effect = lambda key, default=None: {
        "X-API-Key": "api_key_from_header"
    }.get(key, default)
    with patch('pingera_mcp.auth.flask.request', mock_request):
        auth_type, credentials = extract_auth_from_request()
        assert auth_type == "api_key"
        assert credentials == "api_key_from_header"

def test_get_request_client_dual_mode_http():
    """Test that get_request_client returns the correct client in HTTP mode."""
    config = Config()
    config.transport_mode = "http"
    default_client = Mock(spec=PingeraSDKClient)
    http_client = Mock(spec=PingeraSDKClient)

    # Mock extract_auth_from_request to return some credentials
    with patch('pingera_mcp.auth.extract_auth_from_request', return_value=("bearer", "dummy_token")):
        with patch('pingera_mcp.auth.create_client_from_auth', return_value=http_client):
            result = get_request_client(config, default_client)

    assert result is http_client
    default_client.assert_not_called()