# Architecture

```
pingera_mcp/
  __main__.py     pingera-mcp command: settings from env + options, runs stdio or uvicorn
  asgi.py         `app` for production ASGI servers (always HTTP)
  config.py       Settings (environment variables)
  server.py       builds the MCPServer: tools, resources, prompts, routes, middleware; the HTTP app
  context.py      per-request scope (credentials, read-only flag, toolsets) in a ContextVar
  api.py          shared Pingera SDK client; calls with the current request's credentials
  registry.py     tool registry; tools generated from SDK request models
  reference.py    reference text for check parameters and alerting
  toolsets/       one module per toolset
```

## Request flow

1. **HTTP only:** `RequireCredentials` (an ASGI wrapper) answers `401` when an MCP request carries no Pingera
   credentials, unless the server runs with `MCP_HTTP_AUTH=env`.
2. The SDK's streamable HTTP transport runs **stateless**: every POST is a complete MCP exchange and nothing is kept
   between requests, so workers and replicas are interchangeable.
3. `ScopeMiddleware` (an MCP server middleware) builds a `RequestScope` from the request headers (credentials,
   `X-Pingera-Mode`, `X-Pingera-Toolsets`, `X-Pingera-Tools`), or from the environment for stdio, and sets it in a ContextVar for the
   duration of the request. On `tools/list` it removes the tools the scope doesn't allow.
4. Tools are synchronous functions; the SDK runs them in a worker thread, which inherits the ContextVar. The registry
   wrapper refuses tools outside the scope (read-only, toolset), converts the result to compact JSON and turns
   `PingeraToolError` and validation errors into MCP tool errors.
5. `api(SomeApi).operation(...)` calls the SDK's `*_without_preload_content` variant on one shared `ApiClient` with
   `_request_auth` set to the scope's credentials. Credentials are never stored on shared objects, so concurrent
   requests from different tenants cannot see each other's. Responses are returned as the API's raw JSON, so tools
   expose new API fields without SDK changes; request bodies are still validated by the SDK models.

In read-only server mode, tools that change data are not registered at all; the `X-Pingera-Mode` header can only
restrict further.

## Adding tools

Hand-written tool (the signature and docstring become the MCP schema):

```python
@tool("checks")                      # toolset; access="read" by default
def list_check_regions(check_type: CheckType | None = None) -> Any:
    """List the regions checks can run from."""
    return api(ChecksApi).v1_checks_get_regions_get(check_type=check_type)
```

Use `access="run"` for actions that don't change configuration (allowed in read-only mode) and `access="write"` (plus
`destructive=True` for deletes) for everything that changes data.

Create/update tools from an SDK model:

```python
model_tool(
    "checks", "update_check",
    model=MonitorCheck1, partial=True,                      # partial: every field optional, only given ones sent
    path=[("check_id", "ID of the check to update.")],
    call=lambda body, check_id: api(ChecksApi).v1_checks_check_id_patch(check_id=check_id, monitor_check1=body),
    description="Change a check. ...",
)
```

The registry drops the model's read-only fields (from the generated `to_dict`), lists enum values (from the generated
validators) and strips read-only fields from nested models. Use `exclude` for fields the API ignores, `descriptions`
to improve field docs and `advanced` to fold rarely used fields into one object argument.

New toolsets go in `toolsets/__init__.py` (`TOOLSETS`, and `DEFAULT_TOOLSETS` if enabled by default).
`tests/test_registry.py` checks that every tool is documented and classified consistently.
