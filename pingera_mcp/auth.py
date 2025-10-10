
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
    
    Args:
        auth_header: The Authorization header value
        
    Returns:
        Tuple of (auth_type, credentials)
        auth_type is either "bearer" or "api_key"
    """
    parts = auth_header.strip().split(maxsplit=1)
    
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return ("bearer", parts[1])
    else:
        # Assume it's an API key (no Bearer prefix)
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
    # For now, always return default client since we haven't implemented
    # HTTP mode transport yet (that's Phase 3-4)
    # This function is ready for when we add SSE transport
    
    # Future implementation (Phase 3+):
    # if config.transport_mode == "sse":
    #     auth = extract_auth_from_request()
    #     if auth:
    #         api_key, jwt_token = auth
    #         return create_client_from_auth(api_key, jwt_token, config)
    
    return default_client
