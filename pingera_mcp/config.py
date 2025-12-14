"""
Configuration management for Pingera MCP Server.
"""
import os
from enum import Enum
from typing import Optional, List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OperationMode(str, Enum):
    """Operation modes for the MCP server."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"


class Config:
    """Configuration class for Pingera MCP Server."""
    
    def __init__(self, cli_args=None) -> None:
        """Initialize configuration from environment variables and CLI args."""
        # API Configuration
        self.api_key: str = os.getenv("PINGERA_API_KEY", "")
        self.jwt_token: str = os.getenv("PINGERA_JWT_TOKEN", "")
        self.base_url: str = os.getenv("PINGERA_BASE_URL", "https://api.pingera.ru/v1")
        
        # Server Configuration
        mode_str = os.getenv("PINGERA_MODE", "read_only").lower()
        try:
            self.mode: OperationMode = OperationMode(mode_str)
        except ValueError:
            self.mode = OperationMode.READ_ONLY
        
        # Transport Configuration (for future dual-mode support)
        self.transport_mode: str = os.getenv("TRANSPORT_MODE", "stdio").lower()
        self.http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
        self.http_port: int = int(os.getenv("HTTP_PORT", "5000"))
        self.require_auth_header: bool = os.getenv("REQUIRE_AUTH_HEADER", "false").lower() == "true"
        
        # Request Configuration
        self.timeout: int = int(os.getenv("PINGERA_TIMEOUT", "30"))
        self.max_retries: int = int(os.getenv("PINGERA_MAX_RETRIES", "3"))
        
        # Logging Configuration
        self.debug: bool = os.getenv("PINGERA_DEBUG", "false").lower() == "true"
        
        # Server Name
        self.server_name: str = os.getenv("PINGERA_SERVER_NAME", "Pingera MCP Server")
        
        # Tool filtering
        self.requested_tools: Optional[List[str]] = self._parse_tools(cli_args)
    
    def _parse_tools(self, cli_args) -> Optional[List[str]]:
        """Parse --tools flag from CLI args."""
        if cli_args and hasattr(cli_args, 'tools') and cli_args.tools:
            tools_str = cli_args.tools.strip()
            if tools_str:
                tools = [t.strip() for t in tools_str.split(',') if t.strip()]
                return tools if tools else None
        return None
    
    def is_read_only(self) -> bool:
        """Check if server is in read-only mode."""
        return self.mode == OperationMode.READ_ONLY
    
    def is_read_write(self) -> bool:
        """Check if server is in read-write mode."""
        return self.mode == OperationMode.READ_WRITE
