
"""
Tests for configuration management.
"""
import os
import pytest
from unittest.mock import patch

from pingera_mcp.config import Config, OperationMode


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            assert config.api_key == ""
            assert config.base_url == "https://api.pingera.ru/v1"
            assert config.mode == OperationMode.READ_ONLY
            assert config.timeout == 30
            assert config.max_retries == 3
            assert config.debug is False
            assert config.server_name == "Pingera MCP Server"
    
    def test_environment_override(self):
        """Test configuration from environment variables."""
        env_vars = {
            "PINGERA_API_KEY": "test_key",
            "PINGERA_BASE_URL": "https://custom.api.com/v1",
            "PINGERA_MODE": "read_write",
            "PINGERA_TIMEOUT": "60",
            "PINGERA_MAX_RETRIES": "5",
            "PINGERA_DEBUG": "true",
            "PINGERA_SERVER_NAME": "Custom Server"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config()
            
            assert config.api_key == "test_key"
            assert config.base_url == "https://custom.api.com/v1"
            assert config.mode == OperationMode.READ_WRITE
            assert config.timeout == 60
            assert config.max_retries == 5
            assert config.debug is True
            assert config.server_name == "Custom Server"
    
    def test_invalid_mode_defaults_to_read_only(self):
        """Test that invalid mode defaults to read-only."""
        with patch.dict(os.environ, {"PINGERA_MODE": "invalid_mode"}, clear=True):
            config = Config()
            assert config.mode == OperationMode.READ_ONLY
    
    def test_mode_helpers(self):
        """Test mode helper methods."""
        # Test read-only mode
        with patch.dict(os.environ, {"PINGERA_MODE": "read_only"}, clear=True):
            config = Config()
            assert config.is_read_only() is True
            assert config.is_read_write() is False
        
        # Test read-write mode
        with patch.dict(os.environ, {"PINGERA_MODE": "read_write"}, clear=True):
            config = Config()
            assert config.is_read_only() is False
            assert config.is_read_write() is True
