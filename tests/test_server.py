"""Server behavior through an in-process MCP client (no HTTP: the server's own credentials are used)."""

import json

import pytest
from mcp import Client

from pingera_mcp import toolsets
from pingera_mcp.config import Mode
from pingera_mcp.registry import TOOLS
from pingera_mcp.server import create_server

from .conftest import call


async def tool_names(server) -> set[str]:
    async with Client(server) as client:
        return {tool.name for tool in (await client.list_tools()).tools}


async def test_default_toolsets(settings):
    settings.api_key = "env-key"
    names = await tool_names(create_server(settings))
    expected = {name for name, spec in TOOLS.items() if spec.toolset in toolsets.resolve(["default"])}
    assert names == expected
    assert {"check_connection", "get_reference", "list_checks", "create_incident"} <= names
    assert "list_heartbeats" not in names


async def test_read_only_mode_registers_no_write_tools(settings):
    settings.api_key = "env-key"
    settings.mode = Mode.READ_ONLY
    settings.toolsets = ["all"]
    names = await tool_names(create_server(settings))
    assert names == {name for name, spec in TOOLS.items() if spec.access != "write"}
    assert "run_check" in names and "delete_check" not in names


async def test_explicit_tool_list(settings):
    settings.api_key = "env-key"
    settings.tools = ["list_checks", "get_check", "delete_check"]
    assert await tool_names(create_server(settings)) == {"list_checks", "get_check", "delete_check"}

    settings.tools = ["list_checks", "no_such_tool"]
    with pytest.raises(ValueError, match="no_such_tool"):
        create_server(settings)


async def test_tool_metadata(settings):
    settings.api_key = "env-key"
    settings.toolsets = ["all"]
    async with Client(create_server(settings)) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
    delete = tools["delete_check"]
    assert delete.annotations.destructive_hint is True
    assert delete.annotations.read_only_hint is False
    assert tools["list_checks"].annotations.read_only_hint is True
    assert tools["run_check"].annotations.destructive_hint is False
    assert delete.meta == {"pingera/toolset": "checks", "pingera/access": "write"}
    assert tools["create_check"].input_schema["properties"]["type"]["enum"][0] == "web"


async def test_calls_use_server_credentials(fake_api, settings):
    settings.api_key = "env-key"
    fake_api.route("GET", "/v1/checks", body={"checks": [{"id": "c1", "name": "Site", "url": None}]})
    async with Client(create_server(settings)) as client:
        is_error, text = await call(client, "list_checks", name="Site", start="24h")
    assert not is_error
    assert json.loads(text) == {"checks": [{"id": "c1", "name": "Site"}]}
    request = fake_api.last("/v1/checks")
    assert request.headers["authorization"] == "env-key"
    assert "name=Site" in request.path and "start_date=" in request.path


async def test_create_sends_only_given_fields(fake_api, settings):
    settings.api_key = "env-key"
    fake_api.route("POST", "/v1/checks", status=201, body={"id": "new"})
    fake_api.route("PATCH", "/v1/checks/c1", body={"id": "c1"})
    async with Client(create_server(settings)) as client:
        is_error, _ = await call(
            client,
            "create_check",
            name="Site",
            type="web",
            url="https://example.com",
            interval=60,
            secrets=[{"secret_id": "s1", "env_variable": "TOKEN"}],
        )
        assert not is_error
        assert fake_api.last("/v1/checks").body == {
            "name": "Site",
            "type": "web",
            "url": "https://example.com",
            "interval": 60,
            "scheduling_type": "interval",  # an SDK model default
            "secrets": [{"secret_id": "s1", "env_variable": "TOKEN"}],
        }

        is_error, _ = await call(client, "update_check", check_id="c1", active=False)
        assert not is_error
        assert fake_api.last("/v1/checks/c1").body == {"active": False}


async def test_errors_are_tool_results(fake_api, settings):
    settings.api_key = "env-key"
    fake_api.route("GET", "/v1/checks/c1", status=401, body={"message": "Invalid token"})
    async with Client(create_server(settings)) as client:
        is_error, text = await call(client, "get_check", check_id="c1")
        assert is_error and "HTTP 401" in text and "Invalid token" in text

        is_error, text = await call(client, "create_check", name="x", type="nope")
        assert is_error and "type" in text


async def test_reference_resources_and_prompts(settings):
    settings.api_key = "env-key"
    async with Client(create_server(settings)) as client:
        resources = {str(resource.uri) for resource in (await client.list_resources()).resources}
        assert resources == {"pingera://reference/check_types", "pingera://reference/alerts"}
        content = await client.read_resource("pingera://reference/check_types")
        assert "pw_script" in content.contents[0].text
        prompts = {prompt.name for prompt in (await client.list_prompts()).prompts}
        assert prompts == {"investigate_check", "create_synthetic_check", "communicate_incident"}


def test_invalid_settings_rejected(settings):
    settings.api_key = None
    with pytest.raises(ValueError):
        create_server(settings)


async def test_stdio_transport(fake_api):
    """`python -m pingera_mcp` speaks MCP over stdio with the credentials from its environment."""
    import os
    import sys

    from mcp import StdioServerParameters

    fake_api.route("GET", "/v1/organizations", body=[{"id": "org", "name": "Acme"}])
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "pingera_mcp", "--toolsets", "checks"],
        env={**os.environ, "PINGERA_API_KEY": "stdio-key", "PINGERA_BASE_URL": fake_api.url, "MCP_TRANSPORT": "stdio"},
    )
    async with Client(params) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
        is_error, text = await call(client, "check_connection")
    assert "list_checks" in names and "list_alerts" not in names
    assert not is_error and "Acme" in text
    assert fake_api.last("/v1/organizations").headers["authorization"] == "stdio-key"
