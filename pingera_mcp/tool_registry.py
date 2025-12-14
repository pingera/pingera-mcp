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
        requested_tools: Optional[List[str]] = None,
        is_read_write_mode: bool = False
    ) -> Dict[str, callable]:
        """
        Get tools to register based on requested tools and server mode.

        Args:
            requested_tools: Optional list of tool names to expose. If None, all tools are returned.
            is_read_write_mode: Whether the server is in read-write mode

        Returns:
            Dictionary mapping tool names to their registration functions
        """
        tools_to_register = {}

        for tool_name, tool_info in self._tools.items():
            # If specific tools are requested, only include those (regardless of mode)
            if requested_tools is not None and tool_name not in requested_tools:
                continue

            # Check if tool requires write mode and we're in read-only mode
            if tool_info.requires_write and not is_read_write_mode:
                continue

            tools_to_register[tool_name] = tool_info.register_func

        return tools_to_register

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