"""Thin layer over the Pingera SDK used by the tools.

One SDK `ApiClient` (and its connection pool) is shared by all requests. Credentials are never
stored on it: every call passes the current request's credentials through the SDK's per-call
`_request_auth` override. Responses are returned as the raw JSON the API sent, so tools expose
every field even when the SDK models lag behind the API.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, TypeVar

import urllib3
from pingera import ApiClient, Configuration
from pydantic import ValidationError

from . import __version__
from .config import Settings
from .context import Credentials, current_scope

logger = logging.getLogger(__name__)

ApiT = TypeVar("ApiT")


class PingeraToolError(Exception):
    """An error that is reported back to the model as the tool result."""


class PingeraApiError(PingeraToolError):
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(message)


_HINTS = {
    401: "Pingera rejected the credentials. Check the API key or JWT token sent to the MCP server.",
    402: "The Pingera organization has run out of credits or its plan doesn't allow this.",
    403: "These credentials are not allowed to do this.",
    404: "Not found. Check the ID; list tools return valid IDs.",
    429: "Rate limited by the Pingera API. Wait a bit before retrying.",
}


def _error_message(status: int, body: bytes | None) -> str:
    detail: Any = None
    if body:
        try:
            parsed = json.loads(body)
        except ValueError:
            detail = body.decode("utf-8", "replace")[:500]
        else:
            if isinstance(parsed, dict):
                detail = parsed.get("message") or parsed.get("error") or parsed.get("errors") or parsed
            else:
                detail = parsed
    if isinstance(detail, (dict, list)):
        detail = json.dumps(detail, ensure_ascii=False)
    message = f"Pingera API error (HTTP {status})"
    if detail:
        message += f": {str(detail).rstrip('. ')}"
    if status in _HINTS:
        message += f". {_HINTS[status]}"
    return message


def format_validation_error(error: ValidationError) -> str:
    problems = []
    for item in error.errors():
        location = ".".join(str(part) for part in item.get("loc", ()) if part != "__root__")
        problems.append(f"{location}: {item.get('msg')}" if location else str(item.get("msg")))
    return "Invalid arguments: " + "; ".join(problems)


class PingeraClient:
    """The shared SDK client for one MCP server process."""

    def __init__(self, settings: Settings):
        configuration = Configuration(host=settings.base_url)
        # Retries cover connection errors and, for idempotent methods only, transient statuses.
        configuration.retries = urllib3.Retry(
            total=settings.max_retries,
            backoff_factor=0.5,
            status_forcelist=(502, 503, 504),
            raise_on_status=False,
        )
        self.api_client = ApiClient(configuration)
        self.api_client.user_agent = f"pingera-mcp/{__version__} {self.api_client.user_agent}"
        self.timeout = settings.timeout

    def api(self, api_cls: type[ApiT], credentials: Credentials) -> _ApiProxy:
        return _ApiProxy(api_cls(self.api_client), credentials, self.timeout)


class _ApiProxy:
    """Calls SDK operations with the request's credentials and returns parsed JSON."""

    def __init__(self, api: Any, credentials: Credentials, timeout: float):
        self._api = api
        self._credentials = credentials
        self._timeout = timeout

    def __getattr__(self, operation: str):
        method = getattr(self._api, f"{operation}_without_preload_content")

        def call(**kwargs: Any) -> Any:
            kwargs = {key: value for key, value in kwargs.items() if value is not None}
            try:
                response = method(
                    **kwargs,
                    _request_auth=self._credentials.request_auth(),
                    _request_timeout=self._timeout,
                )
            except ValidationError as error:
                raise PingeraToolError(format_validation_error(error)) from error
            except urllib3.exceptions.HTTPError as error:
                raise PingeraToolError(f"Could not reach the Pingera API: {error}") from error
            body = response.data
            if response.status >= 400:
                raise PingeraApiError(response.status, _error_message(response.status, body))
            if not body:
                return {"success": True}
            try:
                return json.loads(body)
            except ValueError:
                return body.decode("utf-8", "replace")

        return call


_client: PingeraClient | None = None


def configure(settings: Settings) -> PingeraClient:
    global _client
    _client = PingeraClient(settings)
    return _client


def api(api_cls: type[ApiT]) -> Any:
    """An SDK API for the current request, e.g. ``api(ChecksApi).v1_checks_get(page=1)``."""
    if _client is None:
        raise RuntimeError("Pingera client is not configured")
    scope = current_scope()
    if scope is None or scope.credentials is None:
        raise PingeraToolError(
            "No Pingera credentials for this request. Send 'Authorization: Bearer <API key or JWT>' "
            "or 'X-API-KEY: <API key>' to the MCP server."
        )
    return _client.api(api_cls, scope.credentials)


_RELATIVE = re.compile(r"^\s*(\d+)\s*(s|m|h|d|w)\s*(?:ago)?\s*$", re.IGNORECASE)
_UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}


def parse_time(value: str | None) -> datetime | None:
    """Parse an ISO 8601 timestamp, 'now', or a relative time such as '30m', '24h', '7d' (meaning ago)."""
    if value is None or not str(value).strip():
        return None
    text = str(value).strip()
    if text.lower() == "now":
        return datetime.now(timezone.utc)
    match = _RELATIVE.match(text)
    if match:
        amount, unit = int(match.group(1)), match.group(2).lower()
        return datetime.now(timezone.utc) - timedelta(**{_UNITS[unit]: amount})
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise PingeraToolError(
            f"Invalid time {value!r}: use ISO 8601 (e.g. 2026-01-31T12:00:00Z) or a relative time like 30m, 24h, 7d"
        ) from None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
