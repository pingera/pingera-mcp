"""The streamable HTTP transport: per-request credentials, isolation, read-only and toolset headers."""

import asyncio
import threading
import time

import httpx2

from pingera_mcp.config import HttpAuth, Mode, Transport

from .conftest import call
from .test_context import make_jwt


async def test_health_and_info(http_server):
    server = http_server()
    async with httpx2.AsyncClient() as http:
        assert (await http.get(f"{server.base}/health")).json()["status"] == "ok"
        info = (await http.get(f"{server.base}/")).json()
    assert info["mcp_endpoint"] == "/mcp"
    assert info["auth"] == "per-request credentials"


async def test_requests_without_credentials_get_401(http_server):
    server = http_server()
    async with httpx2.AsyncClient() as http:
        response = await http.post(
            server.url,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"Accept": "application/json, text/event-stream"},
        )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Bearer realm="pingera"'


async def test_each_credential_form_is_forwarded(fake_api, http_server):
    fake_api.route("GET", "/v1/organizations", body=[{"id": "org"}])
    server = http_server()
    jwt = make_jwt()
    cases = [
        ({"Authorization": "Bearer key-1"}, "key-1"),
        ({"Authorization": "key-2"}, "key-2"),
        ({"X-API-KEY": "key-3"}, "key-3"),
        ({"Authorization": f"Bearer {jwt}"}, f"Bearer {jwt}"),
    ]
    for headers, forwarded in cases:
        async with server.client(headers) as client:
            is_error, _ = await call(client, "check_connection")
        assert not is_error
        assert fake_api.last("/v1/organizations").headers["authorization"] == forwarded


async def test_concurrent_tenants_never_share_credentials(fake_api, http_server):
    """Slow API responses force many tool calls to overlap; each must reach the API with its own key."""
    lock = threading.Lock()
    in_flight = {"now": 0, "max": 0}

    def slow(request):
        with lock:
            in_flight["now"] += 1
            in_flight["max"] = max(in_flight["max"], in_flight["now"])
        time.sleep(0.2)
        with lock:
            in_flight["now"] -= 1
        return 200, {"checks": [], "seen": request.headers.get("authorization")}

    fake_api.route("GET", "/v1/checks", handler=slow)
    server = http_server()

    async def tenant(index: int) -> tuple[str, str]:
        key = f"tenant-key-{index}"
        async with server.client({"Authorization": f"Bearer {key}"}) as client:
            is_error, text = await call(client, "list_checks")
            assert not is_error, text
            return key, text

    results = await asyncio.gather(*(tenant(i) for i in range(20)))
    assert in_flight["max"] > 1, "calls did not overlap"
    for key, text in results:
        assert f'"seen": "{key}"' in text


async def test_read_only_header(fake_api, http_server):
    server = http_server()
    headers = {"Authorization": "Bearer key", "X-Pingera-Mode": "read_only"}
    async with server.client(headers) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
        assert "list_checks" in names and "run_check" in names
        assert "create_check" not in names and "delete_check" not in names
        is_error, text = await call(client, "delete_check", check_id="c1")
    assert is_error and "read-only" in text
    assert not [r for r in fake_api.requests if r.method == "DELETE"]


async def test_toolsets_header(http_server):
    server = http_server()
    async with server.client({"Authorization": "Bearer key", "X-Pingera-Toolsets": "heartbeats,nope"}) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
        assert "list_heartbeats" in names and "check_connection" in names
        assert "list_checks" not in names
        is_error, text = await call(client, "list_checks")
    assert is_error and "not enabled" in text

    async with server.client({"Authorization": "Bearer key", "X-Pingera-Toolsets": "all"}) as client:
        assert "list_audit_events" in {tool.name for tool in (await client.list_tools()).tools}


async def test_tools_header(http_server):
    server = http_server()
    for header in ("X-Pingera-Tools", "X-MCP-Tools"):
        async with server.client({"Authorization": "Bearer key", header: "list_heartbeats, get_check, nope"}) as client:
            names = {tool.name for tool in (await client.list_tools()).tools}
            is_error, text = await call(client, "list_checks")
        assert names == {"list_heartbeats", "get_check"}
        assert is_error and "not among the tools" in text


async def test_server_read_only_mode_cannot_be_lifted_by_header(http_server):
    server = http_server(mode=Mode.READ_ONLY)
    async with server.client({"Authorization": "Bearer key", "X-Pingera-Mode": "read_write"}) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
        is_error, _ = await call(client, "delete_check", check_id="c1")
    assert "delete_check" not in names
    assert is_error


async def test_env_credentials_mode(fake_api, http_server):
    fake_api.route("GET", "/v1/organizations", body=[])
    server = http_server(http_auth=HttpAuth.ENV, api_key="server-key")
    async with server.client() as client:
        is_error, _ = await call(client, "check_connection")
    assert not is_error
    assert fake_api.last("/v1/organizations").headers["authorization"] == "server-key"
    async with httpx2.AsyncClient() as http:
        assert (await http.get(f"{server.base}/")).json()["auth"] == "server credentials"


async def test_public_host_header_is_accepted(http_server):
    """Behind a proxy (or bound to 0.0.0.0 with the default MCP_HOST) the Host header is the public name."""
    server = http_server()
    async with httpx2.AsyncClient() as http:
        response = await http.post(
            server.url,
            json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
            headers={"Host": "mcp.example.com", "Authorization": "Bearer key", "Accept": "application/json, text/event-stream"},
        )
    assert response.status_code != 421


def test_transport_security_policy(settings):
    from pingera_mcp.server import transport_security

    settings.transport = Transport.HTTP
    assert transport_security(settings).enable_dns_rebinding_protection is False

    settings.http_auth, settings.api_key = HttpAuth.ENV, "key"
    assert transport_security(settings).allowed_hosts == ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    settings.host = "0.0.0.0"
    assert transport_security(settings).enable_dns_rebinding_protection is False

    settings.allowed_hosts = ["mcp.example.com"]
    policy = transport_security(settings)
    assert policy.enable_dns_rebinding_protection and policy.allowed_hosts == ["mcp.example.com"]
