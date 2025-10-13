"""
Pingera MCP client library for monitoring service integration.
"""

__version__ = "0.1.9"

from .sdk_client import PingeraSDKClient as PingeraClient

from .exceptions import (
    PingeraError,
    PingeraAPIError,
    PingeraAuthError,
    PingeraConnectionError,
    PingeraTimeoutError
)

__all__ = [
    "PingeraClient",
    "PingeraError",
    "PingeraAPIError",
    "PingeraAuthError",
    "PingeraConnectionError",
    "PingeraTimeoutError"
]