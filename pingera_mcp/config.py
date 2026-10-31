"""Server configuration, read from environment variables (and an optional .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://api.pingera.ru"


class Mode(str, Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"

    @classmethod
    def parse(cls, value: str | None, default: Mode) -> Mode:
        if not value or not value.strip():
            return default
        normalized = value.strip().lower().replace("-", "_")
        try:
            return cls(normalized)
        except ValueError:
            raise ValueError(f"Invalid mode {value!r}: use 'read_only' or 'read_write'") from None


class Transport(str, Enum):
    STDIO = "stdio"
    HTTP = "http"

    @classmethod
    def parse(cls, value: str | None) -> Transport:
        normalized = (value or "stdio").strip().lower()
        if normalized in ("http", "streamable-http", "streamable_http"):
            return cls.HTTP
        if normalized == "stdio":
            return cls.STDIO
        raise ValueError(f"Invalid transport {value!r}: use 'stdio' or 'http'")


class HttpAuth(str, Enum):
    """Where an HTTP server takes Pingera credentials from."""

    REQUEST = "request"  # every request carries its own credentials (multi-tenant)
    ENV = "env"  # the server's PINGERA_API_KEY / PINGERA_JWT_TOKEN serve every client (self-hosted)

    @classmethod
    def parse(cls, value: str | None) -> HttpAuth:
        normalized = (value or "request").strip().lower()
        try:
            return cls(normalized)
        except ValueError:
            raise ValueError(f"Invalid MCP_HTTP_AUTH {value!r}: use 'request' or 'env'") from None


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _list(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def normalize_base_url(url: str) -> str:
    # The SDK adds /v1 to every path, so a trailing /v1 is accepted and stripped.
    url = url.strip().rstrip("/")
    if url.endswith("/v1"):
        url = url[: -len("/v1")]
    return url or DEFAULT_BASE_URL


@dataclass
class Settings:
    # Pingera API
    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    jwt_token: str | None = None
    timeout: float = 30.0
    max_retries: int = 3

    # What the server exposes
    mode: Mode = Mode.READ_ONLY
    toolsets: list[str] = field(default_factory=lambda: ["default"])
    tools: list[str] | None = None
    """Exact tool names to expose; overrides `toolsets` when set."""

    # Transport
    transport: Transport = Transport.STDIO
    host: str = "127.0.0.1"
    port: int = 8000
    path: str = "/mcp"
    http_auth: HttpAuth = HttpAuth.REQUEST
    json_response: bool = True
    allowed_hosts: list[str] = field(default_factory=list)
    allowed_origins: list[str] = field(default_factory=list)

    log_level: str = "INFO"

    @property
    def has_env_credentials(self) -> bool:
        return bool(self.api_key or self.jwt_token)

    @property
    def uses_env_credentials(self) -> bool:
        """True when tools run with the server's own credentials instead of per-request ones."""
        return self.transport is Transport.STDIO or self.http_auth is HttpAuth.ENV

    def validate(self) -> None:
        if self.uses_env_credentials and not self.has_env_credentials:
            where = "the stdio transport" if self.transport is Transport.STDIO else "MCP_HTTP_AUTH=env"
            raise ValueError(f"PINGERA_API_KEY or PINGERA_JWT_TOKEN is required with {where}")
        if not self.path.startswith("/"):
            raise ValueError(f"MCP_PATH must start with '/', got {self.path!r}")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        if environ is None:
            load_dotenv()
            environ = os.environ
        env = environ
        return cls(
            base_url=normalize_base_url(env.get("PINGERA_BASE_URL") or DEFAULT_BASE_URL),
            api_key=env.get("PINGERA_API_KEY") or None,
            jwt_token=env.get("PINGERA_JWT_TOKEN") or None,
            timeout=float(env.get("PINGERA_TIMEOUT") or 30),
            max_retries=int(env.get("PINGERA_MAX_RETRIES") or 3),
            mode=Mode.parse(env.get("PINGERA_MODE") or env.get("MCP_MODE"), Mode.READ_ONLY),
            toolsets=_list(env.get("PINGERA_TOOLSETS")) or ["default"],
            tools=_list(env.get("PINGERA_TOOLS")) or None,
            transport=Transport.parse(env.get("MCP_TRANSPORT")),
            host=env.get("MCP_HOST") or "127.0.0.1",
            port=int(env.get("MCP_PORT") or 8000),
            path=env.get("MCP_PATH") or "/mcp",
            http_auth=HttpAuth.parse(env.get("MCP_HTTP_AUTH")),
            json_response=_bool(env.get("MCP_JSON_RESPONSE"), True),
            allowed_hosts=_list(env.get("MCP_ALLOWED_HOSTS")),
            allowed_origins=_list(env.get("MCP_ALLOWED_ORIGINS")),
            log_level=(env.get("LOG_LEVEL") or ("DEBUG" if _bool(env.get("PINGERA_DEBUG")) else "INFO")).upper(),
        )
