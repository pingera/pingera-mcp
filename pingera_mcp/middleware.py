
"""
Middleware for filtering tools based on client requests and server mode.
"""
import logging
from typing import List, Optional
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger("pingera-mcp-server")


class ToolFilterMiddleware(Middleware):
    """
    Middleware that filters tools based on:
    1. X-MCP-Tools header (comma-separated list of tool names)
    2. Server read-only mode (filters out write-required tools)
    """
    
    def __init__(self, config, tool_registry):
        """
        Initialize the middleware.
        
        Args:
            config: Server configuration instance
            tool_registry: ToolRegistry instance with tool metadata
        """
        self.config = config
        self.tool_registry = tool_registry
        self._filtered_tools_cache = {}  # Cache per request
    
    def _get_requested_tools(self, context: MiddlewareContext) -> Optional[List[str]]:
        """
        Extract requested tools from:
        1. X-MCP-Tools header (SSE mode)
        2. --tools CLI flag (stdio mode, stored in config)
        """
        # In stdio mode, use tools from config (--tools flag)
        if self.config.transport_mode == "stdio" and self.config.requested_tools:
            return self.config.requested_tools
        
        # In SSE mode, get from request headers
        try:
            if hasattr(context, 'request') and context.request:
                tools_header = context.request.headers.get('X-MCP-Tools', '').strip()
                if tools_header:
                    return [t.strip() for t in tools_header.split(',') if t.strip()]
        except Exception as e:
            logger.warning(f"Failed to extract X-MCP-Tools header: {e}")
        
        return None
    
    def _should_include_tool(self, tool_name: str, requested_tools: Optional[List[str]]) -> bool:
        """
        Determine if a tool should be included based on:
        1. Client-requested tools (X-MCP-Tools header)
        2. Server mode (read-only vs read-write)
        
        Args:
            tool_name: Name of the tool to check
            requested_tools: List of requested tools from header, or None for all
        
        Returns:
            True if tool should be included, False otherwise
        """
        # Check if tool is in requested list (if specified)
        if requested_tools is not None and tool_name not in requested_tools:
            logger.debug(f"Filtering out tool '{tool_name}': not in requested tools")
            return False
        
        # Check if tool requires write mode and server is read-only
        if not self.config.is_read_write():
            # Get tool metadata from registry
            if tool_name in self.tool_registry._tools:
                _, requires_write = self.tool_registry._tools[tool_name]
                if requires_write:
                    logger.debug(f"Filtering out tool '{tool_name}': requires write mode")
                    return False
        
        return True
    
    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """Filter tools list based on request headers and server mode."""
        # Get all tools from server
        result = await call_next(context)
        
        # Get requested tools from header
        requested_tools = self._get_requested_tools(context)
        
        if requested_tools:
            logger.info(f"Client requested {len(requested_tools)} specific tools: {', '.join(requested_tools)}")
        
        # Filter tools
        filtered_tools = [
            tool for tool in result
            if self._should_include_tool(tool.name, requested_tools)
        ]
        
        # Cache filtered tool names for this request (for execution validation)
        allowed_tools = {tool.name for tool in filtered_tools}
        self._filtered_tools_cache[id(context)] = allowed_tools
        
        logger.info(f"Returning {len(filtered_tools)} tools (filtered from {len(result)})")
        
        return filtered_tools
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Prevent execution of filtered tools."""
        tool_name = context.params.get('name')
        
        # Check if this tool was filtered out in the list
        request_id = id(context)
        allowed_tools = self._filtered_tools_cache.get(request_id)
        
        if allowed_tools is not None and tool_name not in allowed_tools:
            logger.warning(f"Blocked execution of filtered tool: {tool_name}")
            raise ValueError(f"Tool '{tool_name}' is not available in current context")
        
        # Also check server mode restrictions
        if not self.config.is_read_write() and tool_name in self.tool_registry._tools:
            _, requires_write = self.tool_registry._tools[tool_name]
            if requires_write:
                logger.warning(f"Blocked execution of write tool in read-only mode: {tool_name}")
                raise ValueError(f"Tool '{tool_name}' requires write mode")
        
        # Tool is allowed, proceed with execution
        return await call_next(context)
