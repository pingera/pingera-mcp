"""
Pingera API client library for monitoring service integration.
"""

try:
    from .sdk_client import PingeraSDKClient as PingeraClient
except ImportError:
    # Fallback to custom client if SDK is not available
    from .client import PingeraClient

from .exceptions import (
    PingeraError,
    PingeraAPIError,
    PingeraAuthError,
    PingeraConnectionError,
    PingeraTimeoutError
)
from .models import *

__all__ = [
    "PingeraClient",
    "PingeraError",
    "PingeraAPIError",
    "PingeraAuthError",
    "PingeraConnectionError",
    "PingeraTimeoutError"
]