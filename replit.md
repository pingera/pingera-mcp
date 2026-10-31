# Overview

The Pingera MCP Server is a Model Context Protocol server for the Pingera monitoring service, built on the MCP Python SDK 2.x (`MCPServer`) and pingera-sdk. It runs over stdio (self-hosted, credentials from the environment) or streamable HTTP (multi-tenant: every request carries the user's Pingera credentials). See README.md for usage and configuration.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

See docs/architecture.md. In short: `pingera_mcp/server.py` builds the server, `context.py` keeps per-request credentials in a ContextVar, `api.py` calls the Pingera SDK with those credentials, `registry.py` registers tools (create/update tools are generated from SDK models) and `toolsets/` holds one module per toolset.

# Running

- stdio: `PINGERA_API_KEY=... python -m pingera_mcp`
- HTTP: `python -m pingera_mcp --transport http` (endpoint `/mcp`, health `/health`)
- Tests: `pytest --ignore=tests/e2e`
