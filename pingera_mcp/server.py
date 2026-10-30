"""Builds the Pingera MCP server for the stdio and streamable HTTP transports."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Mapping

from mcp.server.context import CallNext, HandlerResult, ServerRequestContext
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp_types import ToolAnnotations
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from . import __version__, api, reference, toolsets
from .config import Mode, Settings, Transport
from .context import (
    RequestScope,
    credentials_from_headers,
    env_credentials,
    read_only_requested,
    reset_scope,
    set_scope,
    tools_requested,
    toolsets_requested,
)
from .registry import TOOLS, ToolSpec

logger = logging.getLogger(__name__)

INSTRUCTIONS = """\
Pingera is a monitoring platform: uptime/API/SSL/TCP/DNS/ICMP/port-scan checks, Playwright synthetic and \
multistep checks run from many regions, heartbeat (cron job) monitoring, alerting, and public status pages \
with components, incidents and scheduled maintenance.

- Discover IDs with list tools (list_checks, list_status_pages, list_components, list_alert_rules, ...).
- Time arguments accept ISO 8601 or relative values such as '30m', '24h', '7d'.
- To investigate a check: get_check, then list_check_results (failed_only=true), get_check_uptime and \
get_check_status_periods. run_check runs it now; poll get_check_job for the outcome.
- get_reference('check_types') documents check parameters and the Playwright runtime; \
get_reference('alerts') documents alert conditions and channel settings.
- Update tools change only the fields you pass.
"""


def resolve_tools(names: list[str]) -> frozenset[str]:
    unknown = sorted(set(names) - set(TOOLS))
    if unknown:
        raise ValueError(f"Unknown tools: {', '.join(unknown)}")
    return frozenset(names)


class ScopeMiddleware:
    """Sets the per-request scope (credentials, read-only flag, visible tools) and filters tools/list."""

    def __init__(self, settings: Settings, default_toolsets: frozenset[str], default_tools: frozenset[str] | None):
        self._settings = settings
        self._default_toolsets = default_toolsets
        self._default_tools = default_tools
        self._env_credentials = env_credentials(settings.api_key, settings.jwt_token)

    def scope_for(self, headers: Mapping[str, str] | None) -> RequestScope:
        headers = headers or {}
        credentials = credentials_from_headers(headers)
        if credentials is None and self._settings.uses_env_credentials:
            credentials = self._env_credentials
        toolset_names, tool_names = self._default_toolsets, self._default_tools
        requested_tools = tools_requested(headers)
        requested_toolsets = toolsets_requested(headers)
        if requested_tools is not None:
            known = [name for name in requested_tools if name in TOOLS]
            if len(known) < len(requested_tools):
                logger.warning("Ignoring unknown tools in request header: %s", ", ".join(sorted(set(requested_tools) - set(known))))
            tool_names = frozenset(known)
        elif requested_toolsets is not None:
            known = [name for name in requested_toolsets if name.lower() in ("default", "all") or name in toolsets.TOOLSETS]
            if len(known) < len(requested_toolsets):
                logger.warning("Ignoring unknown toolsets in request header: %s", ", ".join(sorted(set(requested_toolsets) - set(known))))
            toolset_names, tool_names = toolsets.resolve(known), None
        return RequestScope(
            credentials=credentials,
            read_only=self._settings.mode is Mode.READ_ONLY or read_only_requested(headers),
            toolsets=toolset_names,
            tools=tool_names,
        )

    async def __call__(self, ctx: ServerRequestContext[Any, Any], call_next: CallNext) -> HandlerResult:
        scope = self.scope_for(getattr(ctx.request, "headers", None))
        token = set_scope(scope)
        try:
            result = await call_next(ctx)
        finally:
            reset_scope(token)
        if ctx.method == "tools/list" and isinstance(result, dict) and isinstance(result.get("tools"), list):
            result = dict(result)
            result["tools"] = [
                item
                for item in result["tools"]
                if item.get("name") not in TOOLS or scope.allows(TOOLS[item["name"]])
            ]
        return result


def _annotations(spec: ToolSpec) -> ToolAnnotations:
    return ToolAnnotations(
        title=spec.title,
        read_only_hint=spec.access == "read",
        destructive_hint=spec.destructive if spec.access == "write" else False,
        idempotent_hint=spec.idempotent,
        open_world_hint=True,
    )


def create_server(settings: Settings) -> MCPServer:
    settings.validate()
    toolsets.load_all()
    default_toolsets = toolsets.resolve(settings.toolsets)
    default_tools = resolve_tools(settings.tools) if settings.tools else None
    if settings.transport is Transport.HTTP:
        # Clients may pick other tools per request (X-Pingera-Toolsets / X-Pingera-Tools), so all are registered.
        registered = set(TOOLS)
    elif default_tools is not None:
        registered = set(default_tools)
    else:
        registered = {name for name, spec in TOOLS.items() if spec.toolset in default_toolsets}
    api.configure(settings)

    server = MCPServer(
        name="pingera",
        title="Pingera",
        description="Pingera monitoring, alerting and status pages",
        instructions=INSTRUCTIONS,
        website_url="https://pingera.ru",
        version=__version__,
        log_level=settings.log_level if settings.log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL") else "INFO",
        middleware=[ScopeMiddleware(settings, default_toolsets, default_tools)],
    )

    for spec in TOOLS.values():
        if spec.name not in registered:
            continue
        if settings.mode is Mode.READ_ONLY and not spec.allowed_in_read_only:
            continue
        server.add_tool(
            spec.fn,
            name=spec.name,
            title=spec.title,
            annotations=_annotations(spec),
            meta={"pingera/toolset": spec.toolset, "pingera/access": spec.access},
            structured_output=False,
        )

    for topic, (description, text) in reference.TOPICS.items():
        server.resource(
            f"pingera://reference/{topic}",
            name=topic,
            title=f"Pingera reference: {topic.replace('_', ' ')}",
            description=description,
            mime_type="text/markdown",
        )(_constant(text))

    _register_prompts(server)
    _register_routes(server, settings, default_toolsets)
    logger.info(
        "Pingera MCP server %s: transport=%s mode=%s default toolsets=%s",
        __version__,
        settings.transport.value,
        settings.mode.value,
        ",".join(sorted(default_toolsets)),
    )
    return server


def _constant(text: str):
    def read() -> str:
        return text

    return read


def _register_prompts(server: MCPServer) -> None:
    @server.prompt(title="Investigate a failing check")
    def investigate_check(check_id: str) -> str:
        """Find out why a monitoring check is failing and what to do about it."""
        return (
            f"Investigate Pingera check {check_id}. Use get_check for its configuration, list_check_results with "
            "failed_only=true and start='24h' for recent failures (get_check_result for details of one), "
            "get_check_status_periods and get_check_uptime for the history, and list_alerts with the check_id for "
            "fired alerts. If the check runs in several regions, compare regions with get_response_times. Summarize "
            "when the problem started, which regions are affected, the error messages, the likely cause and next steps."
        )

    @server.prompt(title="Create a synthetic check")
    def create_synthetic_check(url: str, scenario: str) -> str:
        """Write a Playwright browser check for a user scenario, test it and save it as a monitor."""
        return (
            f"Create a Pingera synthetic (browser) check for {url}. Scenario: {scenario}\n\n"
            "Read get_reference('check_types') for the Playwright runtime. Write the script with "
            "`const { test, expect } = require('@playwright/test');` and assertions for the scenario, test it with "
            "run_custom_check (type 'synthetic', parameters.pw_script) and poll get_check_job until it finishes. "
            "Fix the script until the run passes, then save it with create_check and suggest an alert rule."
        )

    @server.prompt(title="Communicate an incident")
    def communicate_incident(page_id: str, summary: str) -> str:
        """Open an incident on a status page and keep customers informed."""
        return (
            f"Open an incident on Pingera status page {page_id}: {summary}\n\n"
            "Use list_components to pick the affected components and their status, get_incident_options for valid "
            "statuses and impacts, then create_incident with a clear customer-facing title and first update. "
            "Show me the draft before creating it."
        )


def _register_routes(server: MCPServer, settings: Settings, default_toolsets: frozenset[str]) -> None:
    @server.custom_route("/health", methods=["GET"], include_in_schema=False)
    async def health(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok", "version": __version__})

    @server.custom_route("/", methods=["GET"], include_in_schema=False)
    async def info(request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "service": "Pingera MCP Server",
                "version": __version__,
                "mcp_endpoint": settings.path,
                "mode": settings.mode.value,
                "auth": "server credentials" if settings.uses_env_credentials else "per-request credentials",
                "default_toolsets": sorted(default_toolsets),
                "default_tools": sorted(settings.tools) if settings.tools else None,
                "toolsets": toolsets.TOOLSETS,
                "time": datetime.now(timezone.utc).isoformat(),
            }
        )


class RequireCredentials:
    """ASGI guard that answers 401 to MCP requests without Pingera credentials."""

    def __init__(self, app: ASGIApp, path: str):
        self.app = app
        self.path = path.rstrip("/") or "/"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] != "OPTIONS" and (scope["path"].rstrip("/") or "/") == self.path:
            if credentials_from_headers(Headers(scope=scope)) is None:
                response = JSONResponse(
                    {
                        "error": "unauthorized",
                        "error_description": "Send your Pingera API key or JWT token: "
                        "'Authorization: Bearer <token>' or 'X-API-KEY: <API key>'.",
                    },
                    status_code=401,
                    headers={"WWW-Authenticate": 'Bearer realm="pingera"'},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")


def transport_security(settings: Settings) -> TransportSecuritySettings:
    """DNS rebinding protection (Host/Origin allow-lists) for the HTTP transport.

    Explicit MCP_ALLOWED_HOSTS / MCP_ALLOWED_ORIGINS always apply. Without them, protection is only
    needed when a loopback server acts with its own credentials: a malicious web page could otherwise
    reach it through the user's browser. With per-request credentials such a page has nothing to use,
    and behind proxies or on 0.0.0.0 the Host header can't be predicted, so the check is off.
    """
    if settings.allowed_hosts or settings.allowed_origins:
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=settings.allowed_hosts,
            allowed_origins=settings.allowed_origins,
        )
    if settings.uses_env_credentials and settings.host in LOOPBACK_HOSTS:
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*"],
            allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
        )
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)


def create_http_app(settings: Settings) -> ASGIApp:
    """The streamable HTTP ASGI app. Stateless, so any worker or replica can serve any request."""
    server = create_server(settings)
    app: ASGIApp = server.streamable_http_app(
        streamable_http_path=settings.path,
        stateless_http=True,
        json_response=settings.json_response,
        transport_security=transport_security(settings),
    )
    if not settings.uses_env_credentials:
        app = RequireCredentials(app, settings.path)
    return app
