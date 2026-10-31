# Changelog

All notable changes to this project are documented in this file. The project follows
[Semantic Versioning](https://semver.org/).

## 0.2.0

A rewrite on the MCP Python SDK 2.x (`MCPServer`) and pingera-sdk 1.2.0. Tool names, arguments and configuration
changed; see **Migrating from 0.1.x** below.

### Security

- Multi-tenant HTTP: each request now uses only its own credentials. 0.1.x stored the caller's client on shared tool
  objects, so concurrent requests from different users could run with each other's credentials.
- Multi-tenant HTTP answers `401` to requests without credentials instead of falling back to a placeholder client.

### Added

- Toolsets (`PINGERA_TOOLSETS`, per request `X-Pingera-Toolsets`) with 121 tools in 15 toolsets, and exact tool
  lists (`PINGERA_TOOLS` / `--tools`, per request `X-Pingera-Tools` or `X-MCP-Tools`). New: alert rules and
  channels (create, update, delete, test), alert acknowledge/resolve and notification log, check uptime, status
  periods, response times and status counts, cross-check result search, multi-region execution groups, check groups,
  secrets and check secrets, heartbeat pings and channels, component and page uptime, component groups, incident
  updates, past incidents, maintenance windows and postmortems, status page passwords and sender email domains,
  private locations and runner tokens, PDF reports, audit log and usage.
- Create/update tools generated from the SDK models: field descriptions, limits and enum values in the schemas; update
  tools send only the fields passed.
- Per-request `X-Pingera-Mode: read_only`, tool annotations (read-only, destructive, idempotent), relative time
  arguments (`24h`, `7d`), reference resources and the `get_reference` tool, and three prompts.
- Credentials as `Authorization: Bearer <API key>` (in addition to bearer JWTs, raw API keys and `X-API-KEY`).
- `pingera-mcp` command with `--transport`, `--mode`, `--toolsets`, `--host`, `--port` and `--http-auth`.
- `MCP_HTTP_AUTH=env` for single-account HTTP servers, DNS rebinding protection settings, and stateless HTTP so any
  worker or replica can serve any request.

### Changed

- Tool results are the API's JSON without null fields, and errors are returned as MCP tool errors with the API status
  and message.
- Releases are published by a tag-triggered GitHub workflow (PyPI Trusted Publishing and a GitHub release); the
  manual `build/build.sh` script is gone.
- The Docker image is built from source, runs `WORKERS` uvicorn workers and works with a read-only root filesystem.
- Python 3.10+; dependencies trimmed to `mcp`, `pingera-sdk`, `pydantic`, `python-dotenv`, `starlette`, `urllib3`
  and `uvicorn`.

### Fixed

- `MCP_MODE` (used by the Kubernetes manifest) was ignored, so the hosted server always ran read-only. It is now an
  alias of `PINGERA_MODE`.
- Pingera API calls no longer block the server's event loop.

### Migrating from 0.1.x

| 0.1.x | 0.2.0 |
| --- | --- |
| `TRANSPORT_MODE=sse` | `MCP_TRANSPORT=http` |
| `HTTP_HOST`, `HTTP_PORT` | `MCP_HOST`, `MCP_PORT` |
| `REQUIRE_AUTH_HEADER=true` | default (`MCP_HTTP_AUTH=request`); `MCP_HTTP_AUTH=env` uses the server's key instead |
| `PINGERA_SERVER_NAME`, `UVICORN_WORKERS` | removed; the Docker image uses `WORKERS` |
| `PINGERA_BASE_URL=https://api.pingera.ru/v1` | still accepted; `https://api.pingera.ru` is the default |
| `python -m pingera_mcp` | still works; `pingera-mcp` is the installed command |

Tools were renamed for consistency:

| 0.1.x | 0.2.0 |
| --- | --- |
| `list_pages`, `get_page_details`, `create_page`, `delete_page` | `list_status_pages`, `get_status_page`, `create_status_page`, `delete_status_page` |
| `update_page` (PUT), `patch_page` | `update_status_page` (changes only the fields passed; same for every `update_*` tool) |
| `test_pingera_connection` | `check_connection` |
| `get_component_details`, `patch_component` | `get_component`, `update_component` |
| `get_check_details`, `get_check_results` | `get_check`, `list_check_results` |
| `get_check_statistics`, `get_unified_statistics` | `get_check_uptime`, `get_response_times`, `get_status_counts` |
| `get_unified_results` | `search_results` |
| `pause_check`, `resume_check` | `update_check(active=false/true)` |
| `execute_existing_check`, `execute_custom_check` | `run_check`, `run_custom_check` |
| `get_on_demand_job_status`, `get_check_job_details`, `list_on_demand_checks` | `get_check_job`, `list_check_jobs` |
| `get_secret_details`, `get_check_secrets` | `get_secret`, `list_check_secrets` |
| `add_secret_to_check`, `remove_secret_from_check`, `update_check_secrets` | `add_check_secret`, `remove_check_secret`, `update_check(secrets=...)` |
| `get_check_group_details`, `get_checks_in_group` | `get_check_group`, `list_group_checks` |
| `get_alert_details`, `get_alert_statistics` | `get_alert`, `get_alert_stats` |
| `create_alert`, `update_alert`, `delete_alert` | `create_alert_rule`, `update_alert_rule`, `delete_alert_rule` |
| `get_heartbeat_details`, `get_heartbeat_logs` | `get_heartbeat`, `list_heartbeat_pings` |
| `get_incident_details`, `get_incident_updates`, `patch_incident` | `get_incident`, `list_incident_updates`, `update_incident` |
| `update_incident_update`, `get_incident_update_details` | `edit_incident_update`, `list_incident_updates` |
| `create_dns_check`, `create_icmp_check`, `create_synthetic_check`, `create_multistep_check` | `create_check(type=..., parameters={...})`; `get_reference('check_types')` documents the parameters of every type |
| `execute_dns_check`, `execute_icmp_check`, `execute_synthetic_check`, `execute_multistep_check` | `run_custom_check(type=..., parameters={...})` |
| `assign_check_to_group` | `move_check_to_group` |
| `--tools` / `X-MCP-Tools` | unchanged; `PINGERA_TOOLS` and `X-Pingera-Tools` also work |
| `generate_synthetic_check_script`, `generate_api_check_script` | `get_reference('check_types')` and the `create_synthetic_check` prompt: the model writes the script and tests it with `run_custom_check` |

## 0.1.0 - 2024-08-07

- Initial release.
