"""End-to-end tests against a running Pingera MCP server (HTTP transport) and Pingera API.

Skipped unless configured:
    PINGERA_E2E_URL      MCP endpoint, e.g. http://localhost:8000/mcp
    PINGERA_E2E_API_KEY  API key of a test organization (objects are created and deleted there)
    PINGERA_E2E_JWT      optional JWT access token of the same user
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

import httpx2
import pytest
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

URL = os.environ.get("PINGERA_E2E_URL")
API_KEY = os.environ.get("PINGERA_E2E_API_KEY")
JWT = os.environ.get("PINGERA_E2E_JWT")

pytestmark = pytest.mark.skipif(not (URL and API_KEY), reason="PINGERA_E2E_URL and PINGERA_E2E_API_KEY not set")

SUFFIX = uuid.uuid4().hex[:6]


@asynccontextmanager
async def connect(headers: dict[str, str] | None = None, mode: str = "auto"):
    headers = {"Authorization": f"Bearer {API_KEY}"} if headers is None else headers
    async with httpx2.AsyncClient(headers=headers, timeout=60) as http:
        async with Client(streamable_http_client(URL, http_client=http), mode=mode) as client:
            yield client


async def call(client: Client, tool: str, **arguments: Any) -> Any:
    result = await client.call_tool(tool, arguments)
    text = "".join(getattr(block, "text", "") for block in result.content)
    if result.is_error:
        raise AssertionError(f"{tool} failed: {text}")
    try:
        return json.loads(text)
    except ValueError:
        return text


async def call_error(client: Client, tool: str, **arguments: Any) -> str:
    result = await client.call_tool(tool, arguments)
    text = "".join(getattr(block, "text", "") for block in result.content)
    assert result.is_error, f"{tool} unexpectedly succeeded: {text[:300]}"
    return text


async def call_unless_plan_limited(client: Client, tool: str, **arguments: Any) -> Any:
    """Call a tool for a feature the test organization's plan may not include (HTTP 402)."""
    result = await client.call_tool(tool, arguments)
    text = "".join(getattr(block, "text", "") for block in result.content)
    if result.is_error and "HTTP 402" not in text:
        raise AssertionError(f"{tool} failed: {text}")
    return text


async def tool_names(client: Client) -> set[str]:
    return {tool.name for tool in (await client.list_tools()).tools}


# --- transport and authentication -------------------------------------------------------------


async def test_health_and_info():
    base = URL.rsplit("/", 1)[0]
    async with httpx2.AsyncClient(timeout=10) as http:
        health = await http.get(f"{base}/health")
        assert health.status_code == 200 and health.json()["status"] == "ok"
        info = (await http.get(f"{base}/")).json()
        assert info["auth"] == "per-request credentials"


async def test_missing_credentials_is_401():
    async with httpx2.AsyncClient(timeout=10) as http:
        response = await http.post(
            URL,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers={"Accept": "application/json, text/event-stream"},
        )
    assert response.status_code == 401
    assert response.headers["www-authenticate"].startswith("Bearer")


@pytest.mark.parametrize("mode", ["auto", "legacy"])
async def test_bearer_api_key(mode):
    async with connect(mode=mode) as client:
        result = await call(client, "check_connection")
        assert result["connected"] is True


async def test_x_api_key_and_raw_authorization():
    for headers in ({"X-API-KEY": API_KEY}, {"Authorization": API_KEY}):
        async with connect(headers) as client:
            assert (await call(client, "check_connection"))["connected"] is True


@pytest.mark.skipif(not JWT, reason="PINGERA_E2E_JWT not set")
async def test_bearer_jwt():
    async with connect({"Authorization": f"Bearer {JWT}"}) as client:
        assert (await call(client, "check_connection"))["connected"] is True


async def test_invalid_credentials_reported_as_tool_error():
    async with connect({"Authorization": "Bearer not-a-real-key"}) as client:
        message = await call_error(client, "check_connection")
        assert "401" in message


async def test_concurrent_requests_keep_credentials_apart():
    """Interleave valid and invalid credentials; each call must see only its own."""

    async def one(valid: bool) -> bool:
        headers = {"Authorization": f"Bearer {API_KEY if valid else 'invalid-' + uuid.uuid4().hex}"}
        async with connect(headers) as client:
            result = await client.call_tool("list_checks", {"page_size": 1})
            return not result.is_error

    outcomes = await asyncio.gather(*(one(i % 2 == 0) for i in range(24)))
    assert outcomes == [i % 2 == 0 for i in range(24)]


# --- toolsets and read-only -------------------------------------------------------------------


async def test_toolset_header_selects_tools():
    async with connect() as client:
        default = await tool_names(client)
    assert {"list_checks", "create_check", "check_connection"} <= default
    assert "list_heartbeats" not in default

    headers = {"Authorization": f"Bearer {API_KEY}", "X-Pingera-Toolsets": "heartbeats"}
    async with connect(headers) as client:
        names = await tool_names(client)
        assert "list_heartbeats" in names and "check_connection" in names
        assert "list_checks" not in names
        message = await call_error(client, "list_checks")
        assert "not enabled" in message


async def test_read_only_header_hides_and_blocks_writes():
    headers = {"Authorization": f"Bearer {API_KEY}", "X-Pingera-Mode": "read_only"}
    async with connect(headers) as client:
        names = await tool_names(client)
        assert "list_checks" in names and "run_check" in names
        assert not names & {"create_check", "delete_check", "update_check"}
        message = await call_error(client, "create_check", name="x", type="web", url="https://example.com", interval=300)
        assert "read-only" in message


# --- object lifecycles ------------------------------------------------------------------------


async def test_check_lifecycle():
    async with connect({"Authorization": f"Bearer {API_KEY}", "X-Pingera-Toolsets": "all"}) as client:
        regions = await call(client, "list_check_regions", check_type="web")
        assert regions["regions"]

        check = await call(
            client,
            "create_check",
            name=f"mcp-e2e-{SUFFIX}",
            type="web",
            url="https://example.com",
            interval=3600,
            active=False,
            parameters={"search_text": "Example"},
        )
        check_id = check["id"]
        try:
            assert (await call(client, "get_check", check_id=check_id))["name"] == f"mcp-e2e-{SUFFIX}"

            updated = await call(client, "update_check", check_id=check_id, name=f"mcp-e2e-{SUFFIX}-renamed", interval=1800)
            assert updated["interval"] == 1800

            listed = await call(client, "list_checks", name=f"mcp-e2e-{SUFFIX}")
            assert [item["id"] for item in listed["checks"]] == [check_id]

            await call(client, "list_check_results", check_id=check_id, start="7d", failed_only=True)
            await call(client, "get_check_uptime", check_id=check_id, start="24h")
            await call(client, "get_check_status_periods", check_id=check_id)
            await call(client, "search_results", check_id=check_id, start="1h")
            await call(client, "get_status_counts", start="24h")

            group = await call(client, "create_check_group", name=f"mcp-e2e-{SUFFIX}", color="#4F46E5")
            try:
                await call(client, "move_check_to_group", check_id=check_id, group_id=group["id"])
                in_group = await call(client, "list_group_checks", group_id=group["id"])
                assert check_id in json.dumps(in_group)
                await call(client, "move_check_to_group", check_id=check_id)
            finally:
                await call(client, "delete_check_group", group_id=group["id"])

            secret = await call(client, "create_secret", secret_name=f"MCP_E2E_{SUFFIX}", secret_value="s3cr3t")
            try:
                await call(client, "add_check_secret", check_id=check_id, secret_id=secret["id"], env_variable="E2E_TOKEN")
                assert "E2E_TOKEN" in json.dumps(await call(client, "list_check_secrets", check_id=check_id))
                await call(client, "remove_check_secret", check_id=check_id, secret_id=secret["id"])
            finally:
                await call(client, "delete_secret", secret_id=secret["id"])

            job = await call(client, "run_check", check_id=check_id)
            job_id = job.get("job_id") or job.get("id")
            assert job_id
            await call(client, "get_check_job", job_id=job_id)
            await call(client, "list_check_jobs")
        finally:
            await call(client, "delete_check", check_id=check_id)

        message = await call_error(client, "get_check", check_id=check_id)
        assert "404" in message


async def test_alerting_lifecycle():
    async with connect({"Authorization": f"Bearer {API_KEY}", "X-Pingera-Toolsets": "all"}) as client:
        check = await call(
            client, "create_check", name=f"mcp-e2e-alerts-{SUFFIX}", type="web", url="https://example.com", interval=3600, active=False
        )
        channel = await call(
            client,
            "create_alert_channel",
            name=f"mcp-e2e-{SUFFIX}",
            type="webhook",
            configuration={"url": "https://example.com/hook", "method": "POST"},
        )
        try:
            rule = await call(
                client,
                "create_alert_rule",
                name=f"mcp-e2e-{SUFFIX}",
                check_id=check["id"],
                condition="consecutive_failures",
                condition_parameters={"count": 2},
                channel_ids=[channel["id"]],
                severity="high",
            )
            updated = await call(client, "update_alert_rule", rule_id=rule["id"], enabled=False)
            assert updated["enabled"] is False
            assert updated["severity"] == "high"
            assert rule["id"] in json.dumps(await call(client, "list_alert_rules"))
            await call(client, "list_alerts", status="active")
            await call(client, "get_alert_stats")
            await call(client, "delete_alert_rule", rule_id=rule["id"])

            heartbeat = await call(client, "create_heartbeat", name=f"mcp-e2e-{SUFFIX}", period_seconds=3600)
            try:
                assert heartbeat.get("ping_url")
                await call(client, "set_heartbeat_channels", heartbeat_id=heartbeat["id"], channel_ids=[channel["id"]])
                assert channel["id"] in json.dumps(await call(client, "list_heartbeat_channels", heartbeat_id=heartbeat["id"]))
                await call(client, "remove_heartbeat_channel", heartbeat_id=heartbeat["id"], channel_id=channel["id"])
                await call(client, "send_heartbeat_ping", heartbeat_id=heartbeat["id"])
                await call(client, "list_heartbeat_pings", heartbeat_id=heartbeat["id"], start="1h")
                await call(client, "count_heartbeat_pings", heartbeat_id=heartbeat["id"])
                await call(client, "update_heartbeat", heartbeat_id=heartbeat["id"], grace_seconds=600)
            finally:
                await call(client, "delete_heartbeat", heartbeat_id=heartbeat["id"])
        finally:
            await call(client, "delete_alert_channel", channel_id=channel["id"])
            await call(client, "delete_check", check_id=check["id"])


async def test_status_page_lifecycle():
    async with connect({"Authorization": f"Bearer {API_KEY}", "X-Pingera-Toolsets": "all"}) as client:
        pages = await call(client, "list_status_pages")
        if not pages["pages"]:
            pytest.skip("the test organization has no status page")
        page_id = pages["pages"][0]["id"]
        await call(client, "get_status_page", page_id=page_id)
        await call(client, "update_status_page", page_id=page_id, headline=f"MCP e2e {SUFFIX}")

        component = await call(client, "create_component", page_id=page_id, name=f"mcp-e2e-{SUFFIX}")
        try:
            updated = await call(
                client, "update_component", page_id=page_id, component_id=component["id"], status="degraded_performance"
            )
            assert updated["status"] == "degraded_performance"
            await call(client, "get_component_uptime", page_id=page_id, component_id=component["id"])
            await call(client, "get_page_uptime", page_id=page_id)

            options = await call(client, "get_incident_options")
            assert options["impacts"]
            incident = await call(
                client,
                "create_incident",
                page_id=page_id,
                name=f"mcp-e2e-{SUFFIX}",
                status="investigating",
                impact="minor",
                body="Testing the MCP server",
                components={component["id"]: "partial_outage"},
                deliver_notifications=False,
            )
            try:
                await call(
                    client,
                    "add_incident_update",
                    page_id=page_id,
                    incident_id=incident["id"],
                    status="resolved",
                    body="Done",
                    deliver_notifications=False,
                )
                updates = await call(client, "list_incident_updates", page_id=page_id, incident_id=incident["id"])
                assert len(updates) >= 2
                await call(client, "list_incidents", page_id=page_id)
                await call(client, "list_unresolved_incidents", page_id=page_id)
            finally:
                await call(client, "delete_incident", page_id=page_id, incident_id=incident["id"])
        finally:
            await call(client, "delete_component", page_id=page_id, component_id=component["id"])


async def test_account_reports_audit():
    async with connect({"Authorization": f"Bearer {API_KEY}", "X-Pingera-Toolsets": "all"}) as client:
        organizations = (await call(client, "check_connection"))["organizations"]
        await call(client, "get_organization", org_id=organizations[0]["id"])
        await call(client, "get_usage")
        await call_unless_plan_limited(client, "list_reports")
        await call_unless_plan_limited(client, "list_audit_events", start="7d")
        await call_unless_plan_limited(client, "list_private_locations")
        reference = await call(client, "get_reference", topic="check_types")
        assert "pw_script" in reference
