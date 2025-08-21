# Pingera MCP Server

A Model Context Protocol (MCP) server for the [Pingera monitoring service](https://pingera.ru?utm_source=mcp_readme), providing seamless integration between AI models and monitoring data.

## Features

- **Modular Architecture**: Separate Pingera API client library with clean abstractions
- **Flexible Operation Modes**: Run in read-only or read-write mode
- **MCP Tools**: Execute monitoring operations through tools (list_pages, get_page_details, test_connection)
- **Robust Error Handling**: Comprehensive error handling with custom exception hierarchy
- **Real-time Data**: Direct integration with Pingera API v1 for live monitoring data
- **Type Safety**: Pydantic models for data validation and serialization
- **Configurable**: Environment-based configuration management

## Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- Pingera API key

### Installation and Setup

```bash
# Install dependencies
uv sync

# Set up your API key (required)
# Add PINGERA_API_KEY to your environment 

# Run the server
python main.py
```

The server will start in read-only mode by default and connect to the Pingera API.

## Claude Desktop Integration

To use this MCP server with Claude Desktop, you need to configure it in your Claude Desktop settings.

### Installation

First, install the package globally using UV:

```bash
uv tool install pingera-mcp-server
```

### Configuration

Open the Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following configuration:

```json
{
  "mcpServers": {
    "pingera": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "pingera-mcp-server",
        "--python",
        "3.10",
        "python",
        "-m",
        "pingera_mcp"
      ],
      "env": {
        "PINGERA_API_KEY": "your_api_key_here",
        "PINGERA_MODE": "read_only",
        "PINGERA_BASE_URL": "https://api.pingera.ru/v1",
        "PINGERA_TIMEOUT": "30",
        "PINGERA_MAX_RETRIES": "3",
        "PINGERA_DEBUG": "false",
        "PINGERA_SERVER_NAME": "Pingera MCP Server"
      }
    }
  }
}
```

### Required Environment Variables

- **`PINGERA_API_KEY`** - Your Pingera API key (required)

### Optional Environment Variables

- **`PINGERA_MODE`** - Operation mode: `read_only` (default) or `read_write`
- **`PINGERA_BASE_URL`** - API endpoint (default: `https://api.pingera.ru/v1`)
- **`PINGERA_TIMEOUT`** - Request timeout in seconds (default: `30`)
- **`PINGERA_MAX_RETRIES`** - Maximum retry attempts (default: `3`)
- **`PINGERA_DEBUG`** - Enable debug logging (default: `false`)
- **`PINGERA_SERVER_NAME`** - Server display name (default: `Pingera MCP Server`)

### Restart Claude Desktop

After updating the configuration file, restart Claude Desktop to load the new MCP server. You should now be able to access your Pingera monitoring data directly through Claude's interface.

### Verify Installation

Once configured, you can ask Claude to:
- "List my monitored status pages"
- "Show details for a specific page"
- "Test the Pingera API connection"
- "Get the current monitoring status"

## Configuration

Configure the server using environment variables:

```bash
# Required
PINGERA_API_KEY=your_api_key_here

# Optional
PINGERA_MODE=read_only                    # read_only or read_write
PINGERA_BASE_URL=https://api.pingera.ru/v1
PINGERA_TIMEOUT=30
PINGERA_MAX_RETRIES=3
PINGERA_DEBUG=false
PINGERA_SERVER_NAME=Pingera MCP Server
```

## MCP Tools

Available tools for AI agents:

### Pages Management
- **`list_pages`** - Get paginated list of monitored pages
  - Parameters: `page`, `per_page`, `status`
- **`get_page_details`** - Get detailed information about a specific page
  - Parameters: `page_id`

### Component Management
- **`list_component_groups`** - List all component groups for monitoring organization
- **`get_component_details`** - Get detailed information about a specific component
  - Parameters: `component_id`

### Monitoring Checks
- **`list_checks`** - List all monitoring checks (HTTP, TCP, ping, etc.)
  - Parameters: `page`, `page_size`, `status`, `check_type`
- **`get_check_details`** - Get detailed information about a specific check
  - Parameters: `check_id`

### Alert Rules
- **`list_alert_rules`** - List all alert rules and their trigger conditions

### Heartbeat Monitoring
- **`list_heartbeats`** - List all heartbeat monitors for cron jobs and scheduled tasks
  - Parameters: `page`, `page_size`, `status`

### Incident Management
- **`list_incidents`** - List all incidents and their current status
  - Parameters: `page`, `page_size`, `status`

### Connection Testing
- **`test_pingera_connection`** - Test API connectivity

### Write Operations
Available only in read-write mode (`PINGERA_MODE=read_write`):

#### Pages Management
- **`create_page`** - Create a new status page
  - Parameters: `name` (required), `subdomain`, `domain`, `url`, `language`
- **`update_page`** - Update existing status page configuration
  - Parameters: `page_id` (required), `name`, `subdomain`, `domain`, `url`, `language`, additional kwargs
- **`patch_page`** - Partially update specific page fields
  - Parameters: `page_id` (required), kwargs for specific fields
- **`delete_page`** - Permanently delete a status page
  - Parameters: `page_id` (required)

#### Component Management
- **`create_component`** - Create new component or component group
  - Parameters: `page_id` (required), `name` (required), `description`, `group`, `group_id`, `only_show_if_degraded`, `position`, `showcase`, `status`
- **`update_component`** - Update existing component configuration
  - Parameters: `page_id` (required), `component_id` (required), `name`, `description`, `group`, `group_id`, `only_show_if_degraded`, `position`, `showcase`, `status`, additional kwargs
- **`patch_component`** - Partially update specific component fields
  - Parameters: `page_id` (required), `component_id` (required), kwargs for specific fields
- **`delete_component`** - Delete a component permanently
  - Parameters: `page_id` (required), `component_id` (required)

#### Monitoring Checks
- **`create_check`** - Create new monitoring check
  - Parameters: `check_data` (dict with check configuration)
- **`update_check`** - Update existing monitoring check
  - Parameters: `check_id` (required), `check_data` (dict with updated configuration)
- **`delete_check`** - Delete monitoring check permanently
  - Parameters: `check_id` (required)
- **`pause_check`** - Temporarily pause monitoring check
  - Parameters: `check_id` (required)
- **`resume_check`** - Resume paused monitoring check
  - Parameters: `check_id` (required)

#### Alert Rules
- **`create_alert`** - Create new alert rule
  - Parameters: `alert_data` (dict with alert configuration)
- **`update_alert`** - Update existing alert rule
  - Parameters: `alert_id` (required), `alert_data` (dict with updated configuration)
- **`delete_alert`** - Delete alert rule permanently
  - Parameters: `alert_id` (required)

#### Heartbeat Management
- **`create_heartbeat`** - Create new heartbeat monitor
  - Parameters: `heartbeat_data` (dict with heartbeat configuration)
- **`update_heartbeat`** - Update existing heartbeat monitor
  - Parameters: `heartbeat_id` (required), `heartbeat_data` (dict with updated configuration)
- **`delete_heartbeat`** - Delete heartbeat monitor permanently
  - Parameters: `heartbeat_id` (required)
- **`send_heartbeat_ping`** - Manually send ping to heartbeat
  - Parameters: `heartbeat_id` (required)

#### Incident Management
- **`create_incident`** - Create new incident on status page
  - Parameters: `page_id` (required), `incident_data` (dict with incident details)
- **`update_incident`** - Update existing incident details
  - Parameters: `page_id` (required), `incident_id` (required), `incident_data` (dict with updated details)
- **`delete_incident`** - Delete incident permanently
  - Parameters: `page_id` (required), `incident_id` (required)
- **`add_incident_update`** - Add status update to incident
  - Parameters: `page_id` (required), `incident_id` (required), `update_data` (dict with update details)
- **`update_incident_update`** - Edit existing incident update
  - Parameters: `page_id` (required), `incident_id` (required), `update_id` (required), `update_data` (dict with updated content)
- **`delete_incident_update`** - Delete specific incident update
  - Parameters: `page_id` (required), `incident_id` (required), `update_id` (required)

## Operation Modes

### Read-Only Mode (Default)
- Access monitoring data
- View status pages and their configurations
- Test API connectivity
- No modification capabilities

### Read-Write Mode
- All read-only features
- Create, update, and delete monitoring pages (future implementation)
- Manage incidents and notifications (future implementation)

Set `PINGERA_MODE=read_write` to enable write operations.

## Architecture

### Pingera API Client Library
Located in `pingera/`, this modular library provides:

- **PingeraClient**: Main API client with authentication and error handling
- **Models**: Pydantic data models for type-safe API responses
- **Exceptions**: Custom exception hierarchy for error handling

### MCP Server Implementation
- **FastMCP Framework**: Modern MCP server implementation
- **Resource Management**: Structured access to monitoring data
- **Tool Registration**: Executable operations for AI agents
- **Configuration**: Environment-based settings management

## Testing

### Running the Test Suite

Run all tests:
```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

Run specific test files:
```bash
uv run pytest tests/test_models.py
uv run pytest tests/test_config.py
uv run pytest tests/test_mcp_server.py
```

Run tests with coverage:
```bash
uv run pytest --cov=pingera --cov=config --cov=mcp_server
```

### Test Structure

The test suite includes:
- **Unit Tests**: Testing individual components (models, config, client)
- **Integration Tests**: Testing MCP server functionality 
- **Mock Tests**: Testing with simulated API responses

### Testing with MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is an official debugging tool that provides a web interface to test MCP servers interactively. It allows you to explore available resources, execute tools, and inspect the server's responses in real-time.

#### Setup Inspector

1. Create an `mcp.json` configuration file:

```json
{
  "mcpServers": {
    "pingera": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "pingera-mcp-server",
        "--python",
        "3.10",
        "python",
        "-m",
        "pingera_mcp"
      ],
      "env": {
        "PINGERA_API_KEY": "your_pingera_api_key",
        "PINGERA_MODE": "read_only",
        "PINGERA_BASE_URL": "https://api.pingera.ru/v1",
        "PINGERA_TIMEOUT": "30",
        "PINGERA_MAX_RETRIES": "3",
        "PINGERA_DEBUG": "false"
      }
    }
  }
}
```

2. Run the inspector:

```bash
npx @modelcontextprotocol/inspector --config mcp.json
```

3. Open your browser to the provided URL (typically `http://localhost:5173`)

#### Using Inspector

The inspector provides:
- **Resources Tab**: Browse available monitoring data resources
- **Tools Tab**: Execute MCP tools like `list_pages`, `get_page_details`, etc.
- **Logs Tab**: View detailed communication logs between the inspector and server
- **Interactive Testing**: Test tool parameters and see real-time responses

This is the recommended way to test your MCP server integration before deploying with Claude Desktop or other MCP clients.

### Manual Testing

Test the client library directly:
```bash
python -c "from pingera import PingeraClient; import os; client = PingeraClient(os.getenv('PINGERA_API_KEY')); print(f'Pages: {len(client.get_pages().pages)}')"
```

Test MCP server functionality:
```bash
python test_mcp_server.py
```

## Error Handling

The system includes comprehensive error handling:
- `PingeraError`: Base exception for all client errors
- `PingeraAPIError`: API response errors with status codes
- `PingeraAuthError`: Authentication failures
- `PingeraConnectionError`: Network connectivity issues
- `PingeraTimeoutError`: Request timeout handling
