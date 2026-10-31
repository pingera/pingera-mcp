# Pingera MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server for [Pingera](https://pingera.ru?utm_source=mcp_readme):
let AI assistants investigate and manage uptime, API, SSL, DNS, port-scan and Playwright checks, alerts, heartbeat
monitors and status pages.

It runs two ways:

- **Self-hosted** - on your machine over **stdio** (Claude Desktop, Cursor, VS Code, ...) or as your own HTTP server,
  with your Pingera API key.
- **Multi-tenant** - the hosted server at `https://mcp.app.pingera.ru/mcp` (or your own deployment): one HTTP server
  for many users, where every request carries the user's own Pingera credentials.

Built on the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 2.x and the
[Pingera Python SDK](https://pypi.org/project/pingera-sdk/).

## Quick start

You need a Pingera API key: create one at [app.pingera.ru/settings/tokens](https://app.pingera.ru/settings/tokens).

### Hosted server (nothing to install)

Connect your MCP client to `https://mcp.app.pingera.ru/mcp` (streamable HTTP) and send your key in the
`Authorization` header. Claude Code:

```bash
claude mcp add --transport http pingera https://mcp.app.pingera.ru/mcp --header "Authorization: Bearer YOUR_PINGERA_API_KEY"
```

Cursor (`.cursor/mcp.json`; VS Code's `.vscode/mcp.json` is the same under `"servers"` with `"type": "http"`):

```json
{
  "mcpServers": {
    "pingera": {
      "url": "https://mcp.app.pingera.ru/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_PINGERA_API_KEY",
        "X-Pingera-Toolsets": "default,heartbeats"
      }
    }
  }
}
```

The optional `X-Pingera-Toolsets`, `X-Pingera-Tools` and `X-Pingera-Mode: read_only` headers choose which tools this
client gets (see [Tools](#tools) and [Per-request options](#per-request-options)).

### Local server over stdio

Requires [uv](https://docs.astral.sh/uv/). Claude Desktop (`claude_desktop_config.json`), Cursor (`.cursor/mcp.json`)
and similar clients:

```json
{
  "mcpServers": {
    "pingera": {
      "command": "uvx",
      "args": ["--from", "pingera-mcp-server", "pingera-mcp"],
      "env": {
        "PINGERA_API_KEY": "YOUR_PINGERA_API_KEY",
        "PINGERA_MODE": "read_write"
      }
    }
  }
}
```

Leave out `PINGERA_MODE` to start read-only. From a checkout: `uv sync && uv run pingera-mcp`.

Then ask things like *"Which checks failed in the last 24 hours and why?"*, *"Create an API check for
https://api.example.com/health from Moscow and Frankfurt and alert me in Telegram after 3 failures"* or *"Post an
incident on our status page: payments are degraded"*.

## Tools

Tools are grouped into **toolsets**. The default toolsets cover monitoring, alerting and status pages (78 tools in
read-write mode, 48 read-only; 121 with all toolsets). Fewer tools means a smaller prompt and better tool choice, so
enable only what you use:

| Where | Choose toolsets | Choose exact tools |
| --- | --- | --- |
| Hosted or any HTTP server, per client | `X-Pingera-Toolsets: default,heartbeats` header | `X-Pingera-Tools: list_checks,get_check` header (alias `X-MCP-Tools`) |
| Your own server (stdio or HTTP default) | `PINGERA_TOOLSETS` or `--toolsets` | `PINGERA_TOOLS` or `--tools` |

Toolset names are listed below; `default` and `all` work everywhere. A header overrides the server's default for that
client; exact tools override toolsets. Selection is per connection (headers or server settings), not per tool call:
clients load the tool list once, before the model uses any tool.

| Toolset | What | Tools |
| --- | --- | --- |
| `core` (default) | Connection check and reference documentation (always enabled) | `check_connection`, `get_reference` |
| `account` (default) | Organization details and usage | `get_organization`, `get_usage` |
| `pages` (default) | Status pages | `list_status_pages`, `get_status_page`, `find_status_page_by_domain`, `list_page_templates`<br>changes: `create_status_page`, `update_status_page`, `delete_status_page` |
| `components` (default) | Status page components, component groups and component uptime | `list_components`, `get_component`, `list_component_groups`, `get_component_group`, `list_component_statuses`, `get_component_uptime`, `get_page_uptime`<br>changes: `create_component`, `update_component`, `delete_component`, `create_component_group`, `update_component_group`, `delete_component_group` |
| `incidents` (default) | Status page incidents, incident updates, scheduled maintenance and postmortems | `list_incidents`, `list_unresolved_incidents`, `list_maintenances`, `get_incident`, `list_incident_updates`, `get_incident_options`, `get_incident_postmortem`<br>changes: `create_incident`, `update_incident`, `delete_incident`, `add_incident_update`, `edit_incident_update`, `delete_incident_update`, `log_past_incident`, `save_incident_postmortem`, `publish_incident_postmortem` |
| `checks` (default) | Monitoring checks: configuration, regions and on-demand runs | `list_checks`, `get_check`, `list_check_regions`, `get_check_job`, `list_check_jobs`<br>runs: `run_check`, `run_custom_check`<br>changes: `create_check`, `update_check`, `delete_check`, `move_check_to_group` |
| `results` (default) | Check results, uptime, response times, status history and multi-region executions | `list_check_results`, `get_check_result`, `search_results`, `get_check_uptime`, `get_check_status_periods`, `get_response_times`, `get_status_counts`, `list_execution_groups`, `get_execution_group` |
| `alerts` (default) | Alerts, alert rules and alert channels | `list_alerts`, `get_alert`, `list_alert_notifications`, `get_alert_stats`, `list_alert_rules`, `get_alert_rule`, `list_alert_channels`, `get_alert_channel`<br>runs: `test_alert_channel`, `test_alert_channel_settings`<br>changes: `acknowledge_alert`, `resolve_alert`, `create_alert_rule`, `update_alert_rule`, `delete_alert_rule`, `create_alert_channel`, `update_alert_channel`, `delete_alert_channel` |
| `heartbeats` | Heartbeat (cron job) monitors and their pings | `list_heartbeats`, `get_heartbeat`, `list_heartbeat_pings`, `count_heartbeat_pings`, `list_heartbeat_channels`<br>runs: `send_heartbeat_ping`<br>changes: `create_heartbeat`, `update_heartbeat`, `delete_heartbeat`, `set_heartbeat_channels`, `remove_heartbeat_channel` |
| `check_groups` | Check groups | `list_check_groups`, `get_check_group`, `list_group_checks`<br>changes: `create_check_group`, `update_check_group`, `delete_check_group` |
| `secrets` | Organization secrets and the secrets injected into checks | `list_secrets`, `get_secret`, `list_check_secrets`<br>changes: `create_secret`, `update_secret`, `delete_secret`, `add_check_secret`, `remove_check_secret` |
| `page_access` | Status page passwords and custom sender email domains | `list_page_passwords`, `get_page_email_domain`<br>runs: `verify_page_email_domain`<br>changes: `create_page_password`, `update_page_password`, `delete_page_password`, `generate_page_email_domain_records` |
| `private_locations` | Private locations and runner tokens for self-hosted check runners | `list_private_locations`, `get_private_location`<br>changes: `create_private_location`, `update_private_location`, `delete_private_location`, `create_runner_token`, `revoke_runner_token` |
| `reports` | PDF uptime reports | `list_reports`, `get_report`<br>runs: `request_report` |
| `audit` | Organization audit log | `list_audit_events` |

**Access levels.** Read tools only read. *Runs* execute something without changing configuration (run a check now,
send a test notification, request a report); they are available in read-only mode. *Changes* create, update or delete
data and are hidden in read-only mode. Tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`) tell
clients which tools need confirmation.

**Arguments.** Create and update tools are generated from the Pingera SDK models, so their schemas carry the API's
field descriptions, limits and allowed values. Update tools change only the fields you pass. Time arguments accept ISO
8601 or relative values like `30m`, `24h`, `7d`.

**Also available:** resources `pingera://reference/check_types` and `pingera://reference/alerts` (also through the
`get_reference` tool) and prompts `investigate_check`, `create_synthetic_check` and `communicate_incident`.

## Configuration

Environment variables (a `.env` file is read too; see [.env.example](.env.example)). Command line options
(`pingera-mcp --help`) override them.

| Variable | Default | Meaning |
| --- | --- | --- |
| `PINGERA_API_KEY` / `PINGERA_JWT_TOKEN` | - | Credentials for stdio and for HTTP with `MCP_HTTP_AUTH=env` (the JWT wins if both are set) |
| `PINGERA_BASE_URL` | `https://api.pingera.ru` | Pingera API (a trailing `/v1` is accepted) |
| `PINGERA_MODE` (alias `MCP_MODE`) | `read_only` | `read_only` or `read_write` |
| `PINGERA_TOOLSETS` | `default` | Comma-separated toolsets, `default` or `all` |
| `PINGERA_TOOLS` | - | Comma-separated tool names to expose instead of toolsets, e.g. `list_checks,get_check,list_check_results` |
| `PINGERA_TIMEOUT`, `PINGERA_MAX_RETRIES` | `30`, `3` | API request timeout (seconds) and retries |
| `MCP_TRANSPORT` | `stdio` | `stdio` or `http` (streamable HTTP) |
| `MCP_HOST`, `MCP_PORT`, `MCP_PATH` | `127.0.0.1`, `8000`, `/mcp` | HTTP listener and endpoint |
| `MCP_HTTP_AUTH` | `request` | HTTP credentials: `request` (each request sends its own) or `env` (the server's key) |
| `MCP_JSON_RESPONSE` | `true` | Answer HTTP requests with JSON instead of SSE streams |
| `MCP_ALLOWED_HOSTS`, `MCP_ALLOWED_ORIGINS` | - | Only accept these Host / Origin values (DNS rebinding protection; `host:*` allows any port). Without them, only a loopback server with `MCP_HTTP_AUTH=env` checks them (localhost only) |
| `LOG_LEVEL` | `INFO` | Logging level (`PINGERA_DEBUG=true` sets `DEBUG`) |

## HTTP server

```bash
pingera-mcp --transport http --mode read_write             # development, http://127.0.0.1:8000/mcp
uvicorn pingera_mcp.asgi:app --host 0.0.0.0 --workers 4    # production (configured by environment)
docker compose up                                          # the Docker image, see DOCKER.md
```

The endpoint is `/mcp`; `/health` is the health check and `/` describes the server. The server is **stateless**: it
keeps no MCP sessions, so any worker or replica can answer any request and it scales horizontally without sticky
sessions.

### Credentials

With the default `MCP_HTTP_AUTH=request` (multi-tenant), every request must carry Pingera credentials, otherwise the
server answers `401`:

| Header | Meaning |
| --- | --- |
| `Authorization: Bearer <API key>` | API key (works with clients that only support bearer tokens) |
| `Authorization: Bearer <JWT>` | Pingera JWT access token (recognized by its format) |
| `Authorization: <API key>` or `X-API-KEY: <API key>` | API key, the way the Pingera API itself accepts it |

Credentials are used only for that request's API calls; they are never stored or shared between requests.

With `MCP_HTTP_AUTH=env` the server uses its own `PINGERA_API_KEY` for every client. Use it only for a private,
single-account deployment.

### Per-request options

| Header | Effect |
| --- | --- |
| `X-Pingera-Mode: read_only` | Hide and block tools that change data for this client (cannot lift a read-only server) |
| `X-Pingera-Toolsets: checks,results,alerts` | Use these toolsets instead of the server default (`all` and `default` work too) |
| `X-Pingera-Tools: list_checks,get_check` (alias `X-MCP-Tools`) | Expose exactly these tools |

## Development

```bash
uv sync --extra dev
uv run pytest --ignore=tests/e2e     # unit and integration tests (fake Pingera API, no network)
PINGERA_E2E_URL=http://localhost:8000/mcp PINGERA_E2E_API_KEY=... uv run pytest tests/e2e
```

The end-to-end tests run against a real server and API and create and delete objects in that organization, so use a
test organization. [docs/architecture.md](docs/architecture.md) explains how the server is put together and how to
add tools. [scripts/smoke_client.py](scripts/smoke_client.py) calls a tool on a running server, and
[examples/langgraph_agent.py](examples/langgraph_agent.py) connects a LangGraph agent to it.

## License

MIT - see [LICENSE](LICENSE).
