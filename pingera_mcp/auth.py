
"""
Authentication extraction utilities for dual-mode MCP operation.
"""
import logging
from typing import Optional, Tuple
from fastmcp.server.dependencies import get_http_request

from .sdk_client import PingeraSDKClient
from .config import Config

logger = logging.getLogger(__name__)


def extract_auth_from_request() -> Optional[Tuple[Optional[str], Optional[str]]]:
    """
    Extract authentication credentials from HTTP request headers.
    
    Returns:
        Tuple of (api_key, jwt_token) or None if not in HTTP mode
        At most one will be set, the other will be None
    """
    try:
        request = get_http_request()
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("No Authorization header found in HTTP request")
            return None
            
        # Parse the auth header
        auth_type, credentials = get_auth_type(auth_header)
        
        if auth_type == "bearer":
            logger.debug("Extracted Bearer token from request")
            return (None, credentials)
        elif auth_type == "api_key":
            logger.debug("Extracted API key from request")
            return (credentials, None)
        else:
            logger.warning(f"Unknown auth type: {auth_type}")
            return None
            
    except Exception as e:
        # Not in HTTP context, return None
        logger.debug(f"Not in HTTP context or error extracting auth: {e}")
        return None


def get_auth_type(auth_header: str) -> Tuple[str, str]:
    """
    Determine authentication type from Authorization header.
    
    Supports two formats:
    1. "Bearer JWT_TOKEN" - JWT token authentication
    2. "API_KEY" - Raw API key authentication (no prefix)
    
    Args:
        auth_header: The Authorization header value
        
    Returns:
        Tuple of (auth_type, credentials)
        auth_type is either "bearer" or "api_key"
    """
    parts = auth_header.strip().split(maxsplit=1)
    
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        # Format: "Bearer JWT_TOKEN"
        return ("bearer", parts[1])
    else:
        # Format: "API_KEY" (raw API key, no prefix)
        return ("api_key", auth_header.strip())


def create_client_from_auth(
    api_key: Optional[str] = None,
    jwt_token: Optional[str] = None,
    config: Optional[Config] = None
) -> PingeraSDKClient:
    """
    Create a PingeraClient instance from extracted authentication credentials.
    
    Args:
        api_key: API key for authentication
        jwt_token: JWT token for Bearer authentication  
        config: Configuration object for base_url, timeout, etc.
        
    Returns:
        Configured PingeraSDKClient instance
    """
    if config is None:
        from .config import Config
        config = Config()
    
    logger.info(f"Creating client with {'JWT token' if jwt_token else 'API key'}")
    
    return PingeraSDKClient(
        api_key=api_key,
        jwt_token=jwt_token,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries
    )


def get_request_client(
    config: Config,
    default_client: PingeraSDKClient
) -> PingeraSDKClient:
    """
    Get the appropriate client for the current request context.
    
    In HTTP/SSE mode: Creates a new client from request auth headers
    In stdio mode: Returns the default global client
    
    Args:
        config: Server configuration
        default_client: The default/global client instance
        
    Returns:
        Client instance to use for this request
    """
    # In SSE/HTTP mode, try to get auth from request headers
    if config.transport_mode == "sse":
        auth = extract_auth_from_request()
        if auth:
            api_key, jwt_token = auth
            logger.info(f"Creating client from request auth header ({'JWT' if jwt_token else 'API Key'})")
            return create_client_from_auth(api_key, jwt_token, config)
        elif config.require_auth_header:
            logger.warning("No Authorization header found but REQUIRE_AUTH_HEADER=true")
            # Could raise an exception here, but for now fall back to default
        else:
            logger.debug("No auth header found, using default client credentials")
    
    # For stdio mode or when no auth header in SSE mode, use default client
    return default_client
