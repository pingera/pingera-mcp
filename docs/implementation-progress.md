
# Selective Tool Exposure - Implementation Progress

## Completed (Phase 1-3 PoC)

### 1. Tool Registry Infrastructure ✅
- Created `pingera_mcp/tool_registry.py` with `ToolRegistry` class
- Supports tool registration with `@tool_registry.register()` decorator
- Filters tools based on:
  - Client-requested tool list (--tools flag or X-MCP-Tools header)
  - Server operation mode (read-only vs read-write)

### 2. Configuration Enhancement ✅
- Updated `Config` class to accept CLI args
- Added `requested_tools` field to parse --tools flag
- Added `_parse_tools()` method for parsing comma-separated tool names

### 3. CLI Argument Parsing ✅
- Updated `__main__.py` to define argparse setup
- Updated `mcp_server.py` to parse CLI args early for config
- Added `--tools` flag support

### 4. Proof of Concept Tools ✅
Refactored 3 tools to demonstrate the pattern:

**Read-only tools:**
- `list_pages` - registered with `requires_write=False`
- `get_page_details` - registered with `requires_write=False`

**Write tools:**
- `create_page` - registered with `requires_write=True`

Each tool now follows the pattern:
```python
@tool_registry.register("tool_name", requires_write=False)
def register_tool_name(mcp_instance):
    @mcp_instance.tool()
    async def tool_name(...):
        # implementation
    return tool_name
```

### 5. Conditional Registration Logic ✅
- Added `register_tools()` function in `mcp_server.py`
- Implements different strategies for stdio vs SSE mode:
  - **stdio mode**: Only registers requested tools
  - **SSE mode**: Registers all compatible tools (runtime filtering happens via headers)
- Called at end of file after all tool definitions

## Testing the PoC

### Test 1: No Filter (Default Behavior)
```bash
python -m pingera_mcp
# Should register all 3 PoC tools (if in read-write mode) or 2 (if read-only)
```

### Test 2: Selective Tools
```bash
python -m pingera_mcp --tools=list_pages,get_page_details
# Should only register the 2 read-only tools
```

### Test 3: Write Tool Filtering (Read-Only Mode)
```bash
PINGERA_MODE=read_only python -m pingera_mcp --tools=list_pages,create_page
# Should only register list_pages (create_page filtered due to mode)
```

### Test 4: Write Tool Allowed (Read-Write Mode)
```bash
PINGERA_MODE=read_write python -m pingera_mcp --tools=create_page
# Should only register create_page
```

## Next Steps

Once the PoC is validated:

1. **Refactor remaining ~50 tools** - Apply same pattern to all tools in mcp_server.py
2. **HTTP/SSE header support** - Add X-MCP-Tools header parsing in auth.py
3. **Runtime filtering for SSE mode** - Implement per-request tool filtering
4. **Documentation** - Update README with tool filtering examples
5. **Tests** - Add unit and integration tests for tool registry

## Known Limitations

- Currently only 3 tools are refactored (PoC)
- SSE mode runtime filtering not yet implemented
- No validation for invalid tool names (will be silently skipped)
- All remaining ~47 tools still use old direct registration pattern
