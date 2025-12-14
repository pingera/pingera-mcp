
"""
Tool Registry for selective tool exposure.

This registry manages which tools are available based on:
1. Client-requested tool filters (--tools flag or X-MCP-Tools header)
2. Server operation mode (read-only vs read-write)
"""
import logging
from typing import Optional, Dict, Callable, List, Set

logger = logging.getLogger("pingera-mcp-server")


class ToolRegistry:
    """Central registry for managing tool registration and filtering."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, tuple[Callable, bool]] = {}
        # tool_name -> (registration_func, requires_write_mode)
    
    def register(self, name: str, requires_write: bool = False):
        """
        Decorator to register a tool registration function.
        
        Args:
            name: Unique tool name (used for filtering)
            requires_write: True if tool requires write mode, False for read-only
            
        Usage:
            @tool_registry.register("list_pages")
            def register_list_pages(mcp_instance):
                @mcp_instance.tool()
                async def list_pages(...):
                    ...
                return list_pages
        """
        def decorator(func: Callable) -> Callable:
            if name in self._tools:
                logger.warning(f"Tool '{name}' is already registered. Overwriting.")
            self._tools[name] = (func, requires_write)
            logger.debug(f"Registered tool: {name} (requires_write={requires_write})")
            return func
        return decorator
    
    def get_tools_to_register(
        self,
        requested_tools: Optional[List[str]],
        is_read_write_mode: bool
    ) -> Dict[str, Callable]:
        """
        Filter tools based on client request and server mode.
        
        Args:
            requested_tools: List of tool names requested (None = all tools)
            is_read_write_mode: Whether server is in read-write mode
            
        Returns:
            Dict of tool_name -> registration_func for tools that should be registered
        """
        result = {}
        
        # Convert requested_tools to set for faster lookup (case-insensitive)
        requested_set: Optional[Set[str]] = None
        if requested_tools is not None:
            requested_set = {t.lower().strip() for t in requested_tools}
            logger.info(f"Filtering tools to requested set: {requested_set}")
        
        for tool_name, (register_func, requires_write) in self._tools.items():
            # Skip if tool requires write mode but server is read-only
            if requires_write and not is_read_write_mode:
                logger.debug(f"Skipping write tool '{tool_name}' (server is read-only)")
                continue
            
            # Skip if client requested specific tools and this isn't one of them
            if requested_set is not None and tool_name.lower() not in requested_set:
                logger.debug(f"Skipping tool '{tool_name}' (not in requested list)")
                continue
            
            result[tool_name] = register_func
        
        logger.info(f"Selected {len(result)} tools for registration out of {len(self._tools)} total")
        return result
    
    def get_all_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def get_read_only_tool_names(self) -> List[str]:
        """Get list of all read-only tool names."""
        return [name for name, (_, requires_write) in self._tools.items() if not requires_write]
    
    def get_write_tool_names(self) -> List[str]:
        """Get list of all write tool names."""
        return [name for name, (_, requires_write) in self._tools.items() if requires_write]


# Global tool registry instance
tool_registry = ToolRegistry()
