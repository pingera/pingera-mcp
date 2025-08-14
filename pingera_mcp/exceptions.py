"""
Custom exceptions for Pingera API client.
"""
from typing import Optional


class PingeraError(Exception):
    """Base exception for Pingera API client."""
    pass


class PingeraAPIError(PingeraError):
    """Raised when Pingera API returns an error response."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class PingeraAuthError(PingeraAPIError):
    """Raised when authentication fails."""
    pass


class PingeraConnectionError(PingeraError):
    """Raised when connection to Pingera API fails."""
    pass


class PingeraTimeoutError(PingeraError):
    """Raised when request to Pingera API times out."""
    pass
