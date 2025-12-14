
# Selective Tool Exposure Feature

## Overview

This feature allows clients to request only a subset of available MCP tools, reducing context window usage and improving performance. The server will conditionally register tools based on client configuration.

## Requirements

### Local (stdio) Mode
- Command-line flag: `--tools=tool1,tool2,toolN`
- Example: `python -m pingera_mcp --tools=list_pages,create_page,list_checks`

### HTTP/SSE Mode
- HTTP Header: `X-MCP-Tools: tool1,tool2,toolN`
- Example: `X-MCP-Tools: list_pages,create_page,list_checks`

### Default Behavior
- If no tools are specified, expose all tools as currently implemented
- Invalid tool names should be logged but not cause errors

## Design Approach

### Phase 1: Tool Registry System

**Goal**: Create a central registry that maps tool names to their registration functions

**Strategy**:
1. Create a `ToolRegistry` class that maintains a mapping of tool names to registration callables
2. Use a decorator pattern to automatically register tools during definition
3. Support conditional registration based on configuration

**Key Components**:
```python
# pingera_mcp/tool_registry.py

class ToolRegistry:
    def __init__(self):
        self._tools = {}  # tool_name -> (registration_func, read_only_flag)
    
    def register(self, name: str, read_only: bool = True):
        """Decorator to register a tool registration function"""
        def decorator(func):
            self._tools[name] = (func, read_only)
            return func
        return decorator
    
    def get_tools_to_register(self, requested_tools: list, is_read_write: bool):
        """Filter tools based on request and mode"""
        pass
```

**Advantages**:
- Centralized tool management
- Easy to add/remove tools
- Clear separation between tool definition and registration
- No manual lists to maintain

### Phase 2: Tool Registration Refactoring

**Goal**: Wrap each `@mcp.tool()` function in a registration function

**Current Pattern**:
```python
@mcp.tool()
async def list_pages(...):
    # implementation
```

**New Pattern**:
```python
@tool_registry.register("list_pages", read_only=True)
def register_list_pages(mcp_instance):
    @mcp_instance.tool()
    async def list_pages(...):
        # implementation
    return list_pages

# This registration happens conditionally later
```

**Alternative Pattern (Cleaner)**:
```python
# Define tool function separately
async def _list_pages_impl(...):
    # implementation

# Register with metadata
@tool_registry.register("list_pages", read_only=True)
def register_list_pages(mcp_instance):
    return mcp_instance.tool()(_list_pages_impl)
```

**Files to Modify**:
- `pingera_mcp/mcp_server.py` - All ~50+ tool definitions

### Phase 3: Configuration Enhancement

**Goal**: Extend Config class to handle tool filtering

**Changes to `pingera_mcp/config.py`**:
```python
class Config:
    def __init__(self, cli_args=None):
        # ... existing config ...
        
        # Tool filtering
        self.requested_tools: Optional[List[str]] = self._parse_tools(cli_args)
    
    def _parse_tools(self, cli_args):
        """Parse --tools flag from CLI args"""
        if cli_args and hasattr(cli_args, 'tools'):
            return cli_args.tools.split(',') if cli_args.tools else None
        return None
    
    def should_expose_tool(self, tool_name: str) -> bool:
        """Check if a tool should be exposed"""
        if self.requested_tools is None:
            return True  # No filter, expose all
        return tool_name in self.requested_tools
```

### Phase 4: HTTP Header Processing

**Goal**: Extract tool list from HTTP headers in SSE mode

**Changes to `pingera_mcp/auth.py`**:
```python
def get_requested_tools_from_request() -> Optional[List[str]]:
    """Extract X-MCP-Tools header from HTTP request"""
    try:
        request = get_http_request()
        tools_header = request.headers.get('X-MCP-Tools')
        if tools_header:
            return [t.strip() for t in tools_header.split(',')]
    except:
        pass
    return None
```

**Key Consideration**: In SSE mode, tool filtering needs to be per-request, but tool registration happens at server startup. This creates a challenge.

### Phase 5: SSE Mode Tool Filtering Strategy

**Challenge**: In SSE mode, different clients may request different tool subsets, but FastMCP registers tools globally at startup.

**Solution Options**:

#### Option A: Per-Connection Tool Filtering (Recommended)
- Register all tools at startup
- Filter tool list in `list_tools()` MCP method based on request header
- Reject tool calls for non-requested tools
- Pros: Simpler, follows MCP protocol, works with existing FastMCP
- Cons: Tools still registered (minimal overhead)

#### Option B: Dynamic MCP Instance per Connection
- Create separate MCP instances per client connection
- Each instance registers only requested tools
- Pros: True selective registration
- Cons: Complex, may not work with FastMCP architecture

**Recommendation**: Implement Option A for SSE mode

### Phase 6: Command-Line Argument Parsing

**Goal**: Add `--tools` flag to CLI

**Changes to `pingera_mcp/__main__.py`**:
```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Pingera MCP Server')
    parser.add_argument(
        '--tools',
        type=str,
        help='Comma-separated list of tools to expose (e.g., list_pages,create_page)'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    config = Config(cli_args=args)
    
    # ... rest of startup
```

### Phase 7: Conditional Tool Registration

**Goal**: Register only requested tools in stdio mode

**Changes to `pingera_mcp/mcp_server.py`**:
```python
def register_tools(mcp_instance, config, tool_registry):
    """Register tools based on configuration"""
    
    if config.transport_mode == "stdio":
        # In stdio mode, only register requested tools
        for tool_name, (register_func, is_read_only) in tool_registry.items():
            # Check if tool should be exposed
            if not config.should_expose_tool(tool_name):
                logger.info(f"Skipping tool: {tool_name}")
                continue
            
            # Check read/write mode compatibility
            if not is_read_only and config.is_read_only():
                logger.info(f"Skipping write tool in read-only mode: {tool_name}")
                continue
            
            # Register the tool
            logger.info(f"Registering tool: {tool_name}")
            register_func(mcp_instance)
    
    else:  # SSE mode
        # In SSE mode, register all tools (filter at list_tools level)
        for tool_name, (register_func, is_read_only) in tool_registry.items():
            if not is_read_only and config.is_read_only():
                continue
            register_func(mcp_instance)
```

### Phase 8: SSE Mode Runtime Filtering

**Goal**: Filter tools at runtime based on request headers

**Implementation Strategy**:
Since we can't modify FastMCP's core `list_tools()` method directly, we need to:

1. Hook into request context
2. Store requested tools in thread-local or context variable
3. Filter in tool execution phase

**Alternative**: Implement custom MCP protocol handler that wraps FastMCP

```python
# In mcp_server.py

from contextvars import ContextVar

_request_tools = ContextVar('request_tools', default=None)

def before_request_hook():
    """Called before processing MCP request in SSE mode"""
    if config.transport_mode == "sse":
        tools = get_requested_tools_from_request()
        _request_tools.set(tools)

def should_expose_tool_for_request(tool_name: str) -> bool:
    """Check if tool should be exposed for current request"""
    requested = _request_tools.get()
    if requested is None:
        return True
    return tool_name in requested
```

## Implementation Order

1. **Phase 1**: Create `ToolRegistry` class and basic infrastructure
2. **Phase 2**: Refactor existing tools to use registration pattern (start with a few tools as proof of concept)
3. **Phase 3**: Add tool filtering to `Config` class
4. **Phase 6**: Add CLI argument parsing
5. **Phase 7**: Implement conditional registration for stdio mode
6. **Phase 4**: Add HTTP header extraction
7. **Phase 5 & 8**: Implement SSE mode filtering strategy
8. **Testing**: Verify both modes work correctly

## Testing Strategy

### Unit Tests
1. Test `ToolRegistry.register()` decorator
2. Test `Config.should_expose_tool()` logic
3. Test CLI argument parsing
4. Test header extraction

### Integration Tests
1. **stdio mode**: Start server with `--tools=list_pages,create_page`
   - Verify only those tools are registered
   - Verify other tools return "not found"

2. **SSE mode**: Send request with `X-MCP-Tools` header
   - Verify filtered tool list in response
   - Verify tool execution respects filter

3. **Default behavior**: Start without filters
   - Verify all tools available as before

### Manual Testing
1. Test with Claude Desktop (stdio mode)
2. Test with Python HTTP client (SSE mode)
3. Test with invalid tool names
4. Test with empty tool list

## Edge Cases to Handle

1. **Empty tool list**: `--tools=` or `X-MCP-Tools: `
   - Behavior: Expose no tools or expose all tools?
   - Recommendation: Expose all tools (treat as "not specified")

2. **Invalid tool names**: `--tools=list_pages,fake_tool,create_page`
   - Behavior: Log warning, expose only valid tools

3. **Wildcard patterns**: `--tools=list_*,create_*`
   - Behavior: Could support in future, for now exact matches only

4. **Case sensitivity**: `--tools=List_Pages` vs `list_pages`
   - Behavior: Case-insensitive matching recommended

5. **Read-only mode + write tools requested**:
   - Behavior: Silently skip write tools, log warning

## Configuration Examples

### stdio Mode - Selective Tools
```bash
python -m pingera_mcp --tools=list_pages,get_page_details,list_components
```

### SSE Mode - Selective Tools
```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "pingera": {
            "url": "http://0.0.0.0:5000/mcp/",
            "transport": "streamable_http",
            "headers": {
                "Authorization": "YOUR_API_KEY",
                "X-MCP-Tools": "list_pages,create_page,list_checks"
            }
        }
    })
```

### Environment Variables (All Tools)
```bash
# No changes - default behavior
PINGERA_MODE=read_write
TRANSPORT_MODE=stdio
```

## Benefits

1. **Reduced Context Window**: Clients can request only needed tools
2. **Performance**: Faster tool listing and discovery
3. **Security**: Limit exposed capabilities per client
4. **Flexibility**: Different clients can use different tool subsets
5. **Backward Compatible**: No changes needed for existing clients

## Potential Issues

1. **Tool Dependencies**: Some tools may depend on others
   - Solution: Document dependencies, let clients handle
2. **Discovery**: Clients need to know tool names upfront
   - Solution: Provide full tool list in documentation
3. **SSE Mode Complexity**: Per-request filtering is more complex
   - Solution: Accept all-tools registration, filter at protocol level

## Future Enhancements

1. **Tool Groups**: `--tools=@readonly` expands to all read-only tools
2. **Wildcard Support**: `--tools=list_*` matches all list tools
3. **Tool Dependencies**: Auto-include dependent tools
4. **Configuration File**: JSON/YAML config for complex tool sets
5. **Dynamic Tool Loading**: Load tool modules on-demand
