
"""Tool registration functions for secrets domain."""

from typing import Optional, List
from ..tool_registry import tool_registry


def register_secrets_tools():
    """Register all secrets-related tools."""
    
    @tool_registry.register("list_secrets", requires_write=False)
    def register_list_secrets(mcp_instance):
        @mcp_instance.tool()
        async def list_secrets(
            page: Optional[int] = None,
            page_size: Optional[int] = None
        ) -> str:
            """
            List all organization secrets.
        
            Secrets are encrypted values that can be used in monitoring checks
            for sensitive data like API keys, passwords, or tokens.
        
            Args:
                page: Page number for pagination (default: 1)
                page_size: Number of items per page (default: 20, max: 100)
        
            Returns:
                JSON with list of secrets (values are excluded for security).
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.list_secrets(page, page_size)
        return list_secrets
    
    @tool_registry.register("get_secret_details", requires_write=False)
    def register_get_secret_details(mcp_instance):
        @mcp_instance.tool()
        async def get_secret_details(secret_id: str) -> str:
            """
            Get detailed information about a specific secret.
        
            Args:
                secret_id: The unique identifier of the secret
        
            Returns:
                JSON with secret details including the decrypted value.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.get_secret_details(secret_id)
        return get_secret_details
    
    @tool_registry.register("get_check_secrets", requires_write=False)
    def register_get_check_secrets(mcp_instance):
        @mcp_instance.tool()
        async def get_check_secrets(check_id: str) -> str:
            """
            Get all secrets associated with a monitoring check.
        
            This shows which secrets are available to a check as environment
            variables during execution.
        
            Args:
                check_id: The unique identifier of the check
        
            Returns:
                JSON with list of secrets and their environment variable names.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.get_check_secrets(check_id)
        return get_check_secrets
    
    @tool_registry.register("create_secret", requires_write=True)
    def register_create_secret(mcp_instance):
        @mcp_instance.tool()
        async def create_secret(name: str, value: str) -> str:
            """
            Create a new organization secret.
        
            Secrets are encrypted values that can be used in monitoring checks
            for sensitive data like API keys, passwords, or tokens.
        
            Args:
                name: Name of the secret (used for identification)
                value: Secret value (will be encrypted in storage)
        
            Returns:
                JSON with created secret details.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.create_secret(name, value)
        return create_secret
    
    @tool_registry.register("update_secret", requires_write=True)
    def register_update_secret(mcp_instance):
        @mcp_instance.tool()
        async def update_secret(secret_id: str, value: str) -> str:
            """
            Update a secret's value.
        
            Args:
                secret_id: The unique identifier of the secret to update
                value: New secret value (will be encrypted)
        
            Returns:
                JSON with updated secret details.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.update_secret(secret_id, value)
        return update_secret
    
    @tool_registry.register("delete_secret", requires_write=True)
    def register_delete_secret(mcp_instance):
        @mcp_instance.tool()
        async def delete_secret(secret_id: str) -> str:
            """
            Delete a secret permanently.
        
            WARNING: This will remove the secret from all checks that use it.
            Checks using this secret may fail if they depend on it.
        
            Args:
                secret_id: The unique identifier of the secret to delete
        
            Returns:
                JSON confirming successful deletion.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.delete_secret(secret_id)
        return delete_secret
    
    @tool_registry.register("add_secret_to_check", requires_write=True)
    def register_add_secret_to_check(mcp_instance):
        @mcp_instance.tool()
        async def add_secret_to_check(
            check_id: str,
            secret_id: str,
            env_var_name: str
        ) -> str:
            """
            Associate a secret with a monitoring check.
        
            The secret will be available to the check as an environment variable
            during execution.
        
            Args:
                check_id: The unique identifier of the check
                secret_id: The unique identifier of the secret
                env_var_name: Environment variable name to use (e.g., 'API_KEY')
        
            Returns:
                JSON with the association details.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.add_secret_to_check(check_id, secret_id, env_var_name)
        return add_secret_to_check
    
    @tool_registry.register("update_check_secrets", requires_write=True)
    def register_update_check_secrets(mcp_instance):
        @mcp_instance.tool()
        async def update_check_secrets(
            check_id: str,
            secrets: List[dict]
        ) -> str:
            """
            Replace all secret associations for a check.
        
            This overwrites all existing secret associations with the new list.
            Use this to reorganize which secrets a check can access.
        
            Args:
                check_id: The unique identifier of the check
                secrets: List of dicts with 'secret_id' and 'env_var_name'
        
            Returns:
                JSON with updated secret associations.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.update_check_secrets(check_id, secrets)
        return update_check_secrets
    
    @tool_registry.register("remove_secret_from_check", requires_write=True)
    def register_remove_secret_from_check(mcp_instance):
        @mcp_instance.tool()
        async def remove_secret_from_check(
            check_id: str,
            secret_id: str
        ) -> str:
            """
            Remove a secret association from a check.
        
            The secret will no longer be available to the check. If the check
            depends on this secret, it may fail.
        
            Args:
                check_id: The unique identifier of the check
                secret_id: The unique identifier of the secret to remove
        
            Returns:
                JSON confirming successful removal.
            """
            from ..mcp_server import _update_tools_client, secrets_tools
            _update_tools_client()
            return await secrets_tools.remove_secret_from_check(check_id, secret_id)
        return remove_secret_from_check
