"""
Configuration management for Pingera MCP Server.
"""
import os
from enum import Enum
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OperationMode(str, Enum):
    """Operation modes for the MCP server."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"


class Config:
    """Configuration class for Pingera MCP Server."""
    
    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        # API Configuration
        self.api_key: str = os.getenv("PINGERA_API_KEY", "")
        self.base_url: str = os.getenv("PINGERA_BASE_URL", "https://api.pingera.ru/v1")
        
        # Server Configuration
        mode_str = os.getenv("PINGERA_MODE", "read_only").lower()
        try:
            self.mode: OperationMode = OperationMode(mode_str)
        except ValueError:
            self.mode = OperationMode.READ_ONLY
        
        # Request Configuration
        self.timeout: int = int(os.getenv("PINGERA_TIMEOUT", "30"))
        self.max_retries: int = int(os.getenv("PINGERA_MAX_RETRIES", "3"))
        
        # Logging Configuration
        self.debug: bool = os.getenv("PINGERA_DEBUG", "false").lower() == "true"
        
        # Server Name
        self.server_name: str = os.getenv("PINGERA_SERVER_NAME", "Pingera MCP Server")
    
    def is_read_only(self) -> bool:
        """Check if server is in read-only mode."""
        return self.mode == OperationMode.READ_ONLY
    
    def is_read_write(self) -> bool:
        """Check if server is in read-write mode."""
        return self.mode == OperationMode.READ_WRITE
