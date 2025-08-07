# Pingera MCP Server

A Model Context Protocol (MCP) server for the Pingera monitoring service, providing seamless integration between AI models and monitoring data.

## Features

- **Modular Architecture**: Separate Pingera API client library with clean abstractions
- **Flexible Operation Modes**: Run in read-only or read-write mode
- **MCP Resources**: Access monitoring data as structured resources (`pingera://pages`, `pingera://status`)
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
# Add PINGERA_API_KEY to your environment or Replit secrets

# Run the server
python main.py
```

The server will start in read-only mode by default and connect to the Pingera API.

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

## MCP Resources

The server exposes the following resources:

- **`pingera://pages`** - List of all monitored status pages
- **`pingera://pages/{page_id}`** - Details for a specific status page
- **`pingera://status`** - Server and API connection status

## MCP Tools

Available tools for AI agents:

- **`list_pages`** - Get paginated list of monitored pages
  - Parameters: `page`, `per_page`, `status`
- **`get_page_details`** - Get detailed information about a specific page
  - Parameters: `page_id`
- **`test_pingera_connection`** - Test API connectivity
- **Write operations** - Available only in read-write mode (future implementation)

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

Test the client library directly:
```bash
python -c "from pingera import PingeraClient; import os; client = PingeraClient(os.getenv('PINGERA_API_KEY')); print(f'Pages: {len(client.get_pages().pages)}')"
```

## Error Handling

The system includes comprehensive error handling:
- `PingeraError`: Base exception for all client errors
- `PingeraAPIError`: API response errors with status codes
- `PingeraAuthError`: Authentication failures
- `PingeraConnectionError`: Network connectivity issues
- `PingeraTimeoutError`: Request timeout handling
