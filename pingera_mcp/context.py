"""Per-request state: Pingera credentials, read-only restriction and selected toolsets.

The values live in a ContextVar that the MCP middleware sets for every request, so concurrent
requests from different tenants never share credentials.
"""

from __future__ import annotations

import base64
import binascii
import json
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Literal, Mapping

READ_ONLY_HEADER = "x-pingera-mode"
TOOLSETS_HEADER = "x-pingera-toolsets"
TOOLS_HEADERS = ("x-pingera-tools", "x-mcp-tools")


@dataclass(frozen=True)
class Credentials:
    kind: Literal["api_key", "jwt"]
    value: str

    def __repr__(self) -> str:
        return f"Credentials(kind={self.kind!r}, value=<redacted>)"

    def request_auth(self) -> dict[str, Any]:
        """The SDK `_request_auth` override that sends these credentials with one API call."""
        if self.kind == "jwt":
            return {"in": "header", "key": "Authorization", "type": "bearer", "value": f"Bearer {self.value}"}
        return {"in": "header", "key": "Authorization", "type": "api_key", "value": self.value}


def looks_like_jwt(token: str) -> bool:
    parts = token.split(".")
    if len(parts) != 3 or not all(parts[:2]):
        return False
    try:
        header = json.loads(base64.urlsafe_b64decode(parts[0] + "=" * (-len(parts[0]) % 4)))
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return False
    return isinstance(header, dict) and "alg" in header


def credentials_from_headers(headers: Mapping[str, str]) -> Credentials | None:
    """Read Pingera credentials from HTTP request headers.

    Accepted forms (the first match wins):
    - ``Authorization: Bearer <jwt>``: a Pingera JWT access token
    - ``Authorization: Bearer <api key>``: an API key, for MCP clients that only send bearer tokens
    - ``Authorization: <api key>``: an API key, as the Pingera API itself accepts it
    - ``X-API-KEY: <api key>``
    """
    authorization = (headers.get("authorization") or "").strip()
    if authorization:
        parts = authorization.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()
            if token:
                return Credentials("jwt" if looks_like_jwt(token) else "api_key", token)
        elif len(parts) == 1 and parts[0].lower() != "bearer":
            return Credentials("api_key", parts[0])
    api_key = (headers.get("x-api-key") or "").strip()
    if api_key:
        return Credentials("api_key", api_key)
    return None


def env_credentials(api_key: str | None, jwt_token: str | None) -> Credentials | None:
    if jwt_token:
        return Credentials("jwt", jwt_token)
    if api_key:
        return Credentials("api_key", api_key)
    return None


def read_only_requested(headers: Mapping[str, str]) -> bool:
    value = (headers.get(READ_ONLY_HEADER) or "").strip().lower().replace("-", "_")
    return value in ("read_only", "readonly", "ro")


def _header_list(headers: Mapping[str, str], *names: str) -> list[str] | None:
    for name in names:
        value = headers.get(name)
        if value is not None:
            return [item.strip() for item in value.split(",") if item.strip()]
    return None


def toolsets_requested(headers: Mapping[str, str]) -> list[str] | None:
    return _header_list(headers, TOOLSETS_HEADER)


def tools_requested(headers: Mapping[str, str]) -> list[str] | None:
    return _header_list(headers, *TOOLS_HEADERS)


@dataclass(frozen=True)
class RequestScope:
    credentials: Credentials | None
    read_only: bool
    toolsets: frozenset[str]
    """Names of the toolsets visible to this request."""
    tools: frozenset[str] | None = None
    """Exact tool names visible to this request; when set, `toolsets` is ignored."""

    def allows(self, spec) -> bool:
        if self.read_only and not spec.allowed_in_read_only:
            return False
        if self.tools is not None:
            return spec.name in self.tools
        return spec.toolset in self.toolsets


_scope: ContextVar[RequestScope | None] = ContextVar("pingera_request_scope", default=None)


def current_scope() -> RequestScope | None:
    return _scope.get()


def set_scope(scope: RequestScope | None):
    return _scope.set(scope)


def reset_scope(token) -> None:
    _scope.reset(token)
