
# Dual-Mode MCP Architecture: Local and HTTP/SSE

## Overview

This document outlines the architecture and implementation plan for enabling the Pingera MCP Server to operate in two modes:
1. **Local Mode (stdio)** - Current implementation for Claude Desktop and local clients
2. **HTTP/SSE Mode** - Web-accessible mode with authentication header forwarding

## Key Requirements

1. **Single Tool Implementation** - Reuse existing tool logic for both modes
2. **Authentication Forwarding** - Pass `Authorization` header from HTTP requests to PingeraClient
3. **Backward Compatibility** - Maintain existing local mode functionality
4. **Minimal Code Duplication** - Maximize code reuse between modes

## Architecture Design

### Current Architecture
```
Claude Desktop (stdio) → MCP Server → PingeraClient (with env API_KEY) → Pingera API
```

### Target Architecture
```
# Local Mode (unchanged)
Claude Desktop (stdio) → MCP Server → PingeraClient (env API_KEY) → Pingera API

# HTTP/SSE Mode (new)
HTTP Client (with Auth header) → MCP Server (SSE) → PingeraClient (from header) → Pingera API
```

## Authentication Flow

### Local Mode
- Uses environment variables: `PINGERA_API_KEY` or `PINGERA_JWT_TOKEN`
- Configuration loaded at startup
- Single shared PingeraClient instance

### HTTP/SSE Mode
- Client sends `Authorization: Bearer <token>` or `Authorization: <api_key>` header
- Server extracts auth from header using `get_http_request().headers`
- Creates PingeraClient instance per request with extracted credentials
- No credentials in environment variables required for HTTP mode

## Implementation Phases

### Phase 1: Dependency Injection Setup
**Goal**: Prepare tools to accept dynamic PingeraClient instances

**Changes**:
1. Modify tool classes to accept optional `client_override` parameter
2. Update all tool methods to use `client_override` if provided, else use `self.client`
3. Keep backward compatibility with existing tool initialization

**Files to modify**:
- `pingera_mcp/tools/base.py` - Add client override logic to base class
- All tool classes in `pingera_mcp/tools/` - Inherit override behavior

### Phase 2: Authentication Extraction Utility
**Goal**: Create helper to extract and validate auth from HTTP headers

**Changes**:
1. Create `pingera_mcp/auth.py` module
2. Implement functions:
   - `extract_auth_from_request()` - Gets auth from fastMCP HTTP request headers
   - `create_client_from_auth()` - Creates PingeraClient from extracted auth
   - `get_auth_type()` - Determines if Bearer token or API key

**New file**: `pingera_mcp/auth.py`

### Phase 3: Dual-Mode Server Configuration
**Goal**: Configure server to run in both modes based on environment

**Changes**:
1. Add configuration in `pingera_mcp/config.py`:
   - `TRANSPORT_MODE` - "stdio" or "sse"
   - `HTTP_HOST` - Host for HTTP mode (default: "0.0.0.0")
   - `HTTP_PORT` - Port for HTTP mode (default: 5000)
   - `REQUIRE_AUTH_HEADER` - Boolean for HTTP auth requirement

2. Update `pingera_mcp/mcp_server.py`:
   - Conditionally initialize global client only for stdio mode
   - Add transport configuration logic

**Files to modify**:
- `pingera_mcp/config.py` - Add transport config options
- `pingera_mcp/mcp_server.py` - Add mode selection logic

### Phase 4: Tool Wrapper for HTTP Mode
**Goal**: Wrap tool execution to inject per-request client in HTTP mode

**Changes**:
1. Create tool wrapper decorator or middleware
2. In HTTP mode:
   - Extract auth from request headers
   - Create PingeraClient instance
   - Pass to tool as `client_override`
3. In stdio mode:
   - Use existing global client (no override)

**Implementation approach**:
```python
from fastmcp.server.dependencies import get_http_request

def get_request_client(config: Config, default_client: PingeraClient):
    """Get client for current request context"""
    if config.transport_mode == "sse":
        try:
            request = get_http_request()
            auth_header = request.headers.get('Authorization')
            if auth_header:
                # Parse and create client from header
                return create_client_from_auth(auth_header, config)
        except:
            pass
    return default_client
```

**Files to modify**:
- `pingera_mcp/mcp_server.py` - Add request context client resolution

### Phase 5: Update Tool Registration
**Goal**: Modify all `@mcp.tool()` decorated functions to use dynamic client

**Changes**:
1. Update each tool function to:
   - Get appropriate client using `get_request_client()`
   - Pass to tool class methods
2. Maintain existing function signatures
3. No duplication of tool logic

**Example transformation**:
```python
# Before
@mcp.tool()
async def list_pages(...):
    return await pages_tools.list_pages(...)

# After
@mcp.tool()
async def list_pages(...):
    client = get_request_client(config, pingera_client)
    return await pages_tools.list_pages(..., client_override=client)
```

**Files to modify**:
- `pingera_mcp/mcp_server.py` - Update all 50+ tool registrations

### Phase 6: Server Startup Logic
**Goal**: Start server in appropriate mode based on configuration

**Changes**:
1. Update `__main__.py` to check transport mode
2. Call `mcp.run()` with appropriate parameters:
   - stdio mode: `mcp.run()` (default)
   - SSE mode: `mcp.run(transport="sse", host=config.http_host, port=config.http_port)`

**Files to modify**:
- `pingera_mcp/__main__.py` - Add conditional transport logic

### Phase 7: Documentation and Examples
**Goal**: Provide clear examples for both modes

**Changes**:
1. Update `README.md`:
   - Add HTTP/SSE mode setup instructions
   - Document authentication header format
   - Provide client examples (Python, curl, etc.)

2. Create example clients:
   - `examples/http_client.py` - Python HTTP client
   - `examples/sse_client.py` - SSE streaming client

**New files**:
- `examples/http_client.py`
- `examples/sse_client.py`
- Update `README.md`

## Security Considerations

1. **HTTPS Requirement**: For production, HTTP/SSE mode should use HTTPS to protect auth headers
2. **Token Validation**: Server should validate auth tokens before creating client
3. **Rate Limiting**: Consider implementing rate limiting for HTTP mode
4. **CORS Configuration**: Configure CORS headers appropriately for web clients

## Testing Strategy

### Unit Tests
1. Test auth extraction from headers
2. Test client creation from different auth types
3. Test tool execution with client override

### Integration Tests
1. Test stdio mode (existing tests)
2. Test HTTP/SSE mode with auth headers
3. Test fallback behavior when auth missing
4. Test both Bearer token and API key formats

### Manual Testing
1. Local stdio mode with Claude Desktop
2. HTTP mode with curl/httpie
3. HTTP mode with Python client
4. SSE streaming with example client

## Configuration Examples

### Local Mode (Current)
```bash
PINGERA_API_KEY=your_api_key
PINGERA_MODE=read_write
TRANSPORT_MODE=stdio  # default
```

### HTTP/SSE Mode (New)
```bash
# Server doesn't need API key - comes from client headers
PINGERA_MODE=read_write
TRANSPORT_MODE=sse
HTTP_HOST=0.0.0.0
HTTP_PORT=5000
REQUIRE_AUTH_HEADER=true
```

### Client Usage (HTTP Mode)
```python
import asyncio
from fastmcp.client import Client
from fastmcp.client.transports import SSETransport

async def main():
    transport = SSETransport(
        url="http://0.0.0.0:5000/sse",
        headers={"Authorization": "Bearer your_jwt_token"}
    )
    
    async with Client(transport) as client:
        result = await client.call_tool("list_pages", {})
        print(result[0].text)
```

## Migration Path

1. **Phase 1-2**: Internal refactoring (no breaking changes)
2. **Phase 3-4**: Add HTTP support (stdio still works)
3. **Phase 5-6**: Complete HTTP implementation
4. **Phase 7**: Documentation and examples

## Rollback Strategy

- All phases maintain backward compatibility
- Can abort HTTP mode development at any phase
- Stdio mode remains functional throughout
- Use feature flags to enable/disable HTTP mode

## Success Criteria

1. ✅ Both stdio and HTTP/SSE modes work
2. ✅ Single tool implementation serves both modes
3. ✅ Auth headers properly forwarded to PingeraClient
4. ✅ All existing tests pass
5. ✅ New HTTP mode tests pass
6. ✅ Documentation complete with examples
7. ✅ Zero code duplication for tool logic

## Open Questions

1. Should HTTP mode support both Bearer tokens and API keys?
2. Do we need rate limiting in HTTP mode?
3. Should we support WebSocket transport in addition to SSE?
4. How to handle client disconnections in SSE mode?

## Next Steps

1. Review this architecture with team
2. Create GitHub issues for each phase
3. Begin Phase 1 implementation
4. Set up CI/CD for dual-mode testing
