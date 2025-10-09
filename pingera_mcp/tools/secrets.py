
"""
MCP tools for secrets management.
"""
from typing import Optional, List

from .base import BaseTools
from ..exceptions import PingeraError


class SecretsTools(BaseTools):
    """Tools for managing organization secrets."""

    async def list_secrets(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        List all organization secrets.

        Args:
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 20, max: 100)

        Returns:
            JSON string containing secrets data (values are excluded for security)
        """
        try:
            self.logger.info(f"Listing secrets (page={page}, page_size={page_size})")

            with self.client._get_api_client() as api_client:
                from pingera.api import SecretsApi
                secrets_api = SecretsApi(api_client)

                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size

                response = secrets_api.v1_secrets_get(**kwargs)

                secrets_data = self._format_secrets_response(response)
                return self._success_response(secrets_data)

        except Exception as e:
            self.logger.error(f"Error listing secrets: {e}")
            return self._error_response(str(e))

    async def get_secret_details(self, secret_id: str) -> str:
        """
        Get detailed information about a specific secret.

        Args:
            secret_id: ID of the secret to retrieve

        Returns:
            JSON string containing secret details (including value)
        """
        try:
            self.logger.info(f"Getting secret details for ID: {secret_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import SecretsApi
                secrets_api = SecretsApi(api_client)

                response = secrets_api.v1_secrets_secret_id_get(secret_id=secret_id)

                secret_data = self._format_secret_response(response)
                return self._success_response(secret_data)

        except Exception as e:
            self.logger.error(f"Error getting secret details for {secret_id}: {e}")
            return self._error_response(str(e))

    async def create_secret(
        self,
        name: str,
        value: str
    ) -> str:
        """
        Create a new organization secret.

        Args:
            name: Name of the secret
            value: Secret value (will be encrypted in storage)

        Returns:
            JSON string containing created secret details
        """
        try:
            self.logger.info(f"Creating new secret: {name}")

            with self.client._get_api_client() as api_client:
                from pingera.api import SecretsApi
                from pingera.models import Secret1
                secrets_api = SecretsApi(api_client)

                secret = Secret1(name=name, value=value)
                response = secrets_api.v1_secrets_post(secret1=secret)

                created_secret = self._format_secret_response(response)
                return self._success_response(created_secret)

        except Exception as e:
            self.logger.error(f"Error creating secret: {e}")
            return self._error_response(str(e))

    async def update_secret(
        self,
        secret_id: str,
        value: str
    ) -> str:
        """
        Update a secret value.

        Args:
            secret_id: ID of the secret to update
            value: New secret value

        Returns:
            JSON string containing updated secret details
        """
        try:
            self.logger.info(f"Updating secret {secret_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import SecretsApi
                from pingera.models import Secret2
                secrets_api = SecretsApi(api_client)

                secret = Secret2(value=value)
                response = secrets_api.v1_secrets_secret_id_patch(
                    secret_id=secret_id,
                    secret2=secret
                )

                updated_secret = self._format_secret_response(response)
                return self._success_response(updated_secret)

        except Exception as e:
            self.logger.error(f"Error updating secret {secret_id}: {e}")
            return self._error_response(str(e))

    async def delete_secret(self, secret_id: str) -> str:
        """
        Delete a secret.

        Args:
            secret_id: ID of the secret to delete

        Returns:
            JSON string confirming deletion
        """
        try:
            self.logger.info(f"Deleting secret {secret_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import SecretsApi
                secrets_api = SecretsApi(api_client)

                secrets_api.v1_secrets_secret_id_delete(secret_id=secret_id)

                return self._success_response({
                    "message": f"Secret {secret_id} deleted successfully",
                    "secret_id": secret_id
                })

        except Exception as e:
            self.logger.error(f"Error deleting secret {secret_id}: {e}")
            return self._error_response(str(e))

    async def get_check_secrets(self, check_id: str) -> str:
        """
        Get all secrets associated with a check.

        Args:
            check_id: ID of the check

        Returns:
            JSON string containing check's secrets
        """
        try:
            self.logger.info(f"Getting secrets for check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckSecretsApi
                check_secrets_api = CheckSecretsApi(api_client)

                response = check_secrets_api.v1_checks_check_id_secrets_get(check_id=check_id)

                secrets_data = self._format_check_secrets_response(response)
                return self._success_response(secrets_data)

        except Exception as e:
            self.logger.error(f"Error getting secrets for check {check_id}: {e}")
            return self._error_response(str(e))

    async def add_secret_to_check(
        self,
        check_id: str,
        secret_id: str,
        env_var_name: str
    ) -> str:
        """
        Associate a secret with a check using an environment variable name.

        Args:
            check_id: ID of the check
            secret_id: ID of the secret to associate
            env_var_name: Environment variable name to use in the check

        Returns:
            JSON string containing the association details
        """
        try:
            self.logger.info(f"Adding secret {secret_id} to check {check_id} as {env_var_name}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckSecretsApi
                from pingera.models import CheckSecret
                check_secrets_api = CheckSecretsApi(api_client)

                check_secret = CheckSecret(secret_id=secret_id, env_var_name=env_var_name)
                response = check_secrets_api.v1_checks_check_id_secrets_post(
                    check_id=check_id,
                    check_secret=check_secret
                )

                association_data = self._format_check_secret_response(response)
                return self._success_response(association_data)

        except Exception as e:
            self.logger.error(f"Error adding secret to check: {e}")
            return self._error_response(str(e))

    async def update_check_secrets(
        self,
        check_id: str,
        secrets: List[dict]
    ) -> str:
        """
        Replace all secret associations for a check.

        Args:
            check_id: ID of the check
            secrets: List of secret associations with 'secret_id' and 'env_var_name'

        Returns:
            JSON string containing updated associations
        """
        try:
            self.logger.info(f"Updating all secrets for check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckSecretsApi
                from pingera.models import CheckSecret
                check_secrets_api = CheckSecretsApi(api_client)

                check_secrets = [
                    CheckSecret(secret_id=s['secret_id'], env_var_name=s['env_var_name'])
                    for s in secrets
                ]
                
                response = check_secrets_api.v1_checks_check_id_secrets_put(
                    check_id=check_id,
                    check_secret=check_secrets
                )

                associations_data = self._format_check_secrets_response(response)
                return self._success_response(associations_data)

        except Exception as e:
            self.logger.error(f"Error updating check secrets: {e}")
            return self._error_response(str(e))

    async def remove_secret_from_check(
        self,
        check_id: str,
        secret_id: str
    ) -> str:
        """
        Remove a secret association from a check.

        Args:
            check_id: ID of the check
            secret_id: ID of the secret to remove

        Returns:
            JSON string confirming removal
        """
        try:
            self.logger.info(f"Removing secret {secret_id} from check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckSecretsApi
                check_secrets_api = CheckSecretsApi(api_client)

                check_secrets_api.v1_checks_check_id_secrets_secret_id_delete(
                    check_id=check_id,
                    secret_id=secret_id
                )

                return self._success_response({
                    "message": f"Secret {secret_id} removed from check {check_id}",
                    "check_id": check_id,
                    "secret_id": secret_id
                })

        except Exception as e:
            self.logger.error(f"Error removing secret from check: {e}")
            return self._error_response(str(e))

    def _format_secrets_response(self, response) -> dict:
        """Format secrets list response."""
        if hasattr(response, '__dict__'):
            secrets_data = getattr(response, 'secrets', [])
            pagination = getattr(response, 'pagination', {})

            if isinstance(secrets_data, list):
                formatted_secrets = []
                for item in secrets_data:
                    if hasattr(item, '__dict__'):
                        formatted_secrets.append(self._convert_sdk_object_to_dict(item))
                    else:
                        formatted_secrets.append(item)
            else:
                formatted_secrets = secrets_data

            if isinstance(pagination, dict):
                total = pagination.get('total_items', 0)
                page = pagination.get('page', 1)
                page_size = pagination.get('page_size', 20)
            else:
                total = getattr(response, 'total', 0)
                page = getattr(response, 'page', 1)
                page_size = getattr(response, 'page_size', 20)

            return {
                "secrets": formatted_secrets,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        return {"secrets": [], "total": 0}

    def _format_secret_response(self, response) -> dict:
        """Format single secret response."""
        if hasattr(response, '__dict__'):
            return self._convert_sdk_object_to_dict(response)
        return response

    def _format_check_secrets_response(self, response) -> dict:
        """Format check secrets list response."""
        if isinstance(response, list):
            formatted_data = []
            for item in response:
                if hasattr(item, '__dict__'):
                    formatted_data.append(self._convert_sdk_object_to_dict(item))
                else:
                    formatted_data.append(item)
            return {"secrets": formatted_data}
        return {"secrets": []}

    def _format_check_secret_response(self, response) -> dict:
        """Format single check secret association response."""
        if hasattr(response, '__dict__'):
            return self._convert_sdk_object_to_dict(response)
        return response
