
"""
MCP tools for check groups management.
"""
import json
from typing import Optional

from .base import BaseTools
from ..exceptions import PingeraError


class CheckGroupsTools(BaseTools):
    """Tools for managing check groups."""

    async def list_check_groups(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        List all check groups in your account.

        Args:
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 20, max: 100)

        Returns:
            JSON string containing check groups data
        """
        try:
            self.logger.info(f"Listing check groups (page={page}, page_size={page_size})")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size

                response = check_groups_api.v1_check_groups_get(**kwargs)

                groups_data = self._format_check_groups_response(response)
                return self._success_response(groups_data)

        except Exception as e:
            self.logger.error(f"Error listing check groups: {e}")
            return self._error_response(str(e))

    async def get_check_group_details(self, group_id: str) -> str:
        """
        Get detailed information about a specific check group.

        Args:
            group_id: The unique identifier of the check group

        Returns:
            JSON string containing check group details
        """
        try:
            self.logger.info(f"Getting check group details for ID: {group_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                response = check_groups_api.v1_check_groups_group_id_get(group_id=group_id)

                group_data = self._format_check_group_response(response)
                return self._success_response(group_data)

        except Exception as e:
            self.logger.error(f"Error getting check group details for {group_id}: {e}")
            return self._error_response(str(e))

    async def get_checks_in_group(
        self,
        group_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        Get all checks that belong to a specific check group.

        Args:
            group_id: The unique identifier of the check group
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 20, max: 100)

        Returns:
            JSON string containing checks data for the group
        """
        try:
            self.logger.info(f"Getting checks for group {group_id} (page={page}, page_size={page_size})")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size

                response = check_groups_api.v1_check_groups_group_id_checks_get(
                    group_id=group_id,
                    **kwargs
                )

                checks_data = self._format_group_checks_response(response)
                return self._success_response(checks_data)

        except Exception as e:
            self.logger.error(f"Error getting checks for group {group_id}: {e}")
            return self._error_response(str(e))

    async def create_check_group(self, group_data: dict) -> str:
        """
        Create a new check group.

        Args:
            group_data: Dictionary containing check group configuration

        Returns:
            JSON string containing created check group data
        """
        try:
            self.logger.info(f"Creating new check group: {group_data.get('name', 'Unnamed')}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                response = check_groups_api.v1_check_groups_post(group_data)

                created_group = self._format_check_group_response(response)
                return self._success_response(created_group)

        except Exception as e:
            self.logger.error(f"Error creating check group: {e}")
            return self._error_response(str(e))

    async def update_check_group(self, group_id: str, group_data: dict) -> str:
        """
        Update an existing check group.

        Args:
            group_id: ID of the check group to update
            group_data: Dictionary containing updated group configuration

        Returns:
            JSON string containing updated check group data
        """
        try:
            self.logger.info(f"Updating check group {group_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                response = check_groups_api.v1_check_groups_group_id_patch(
                    group_id=group_id,
                    check_group2=group_data
                )

                updated_group = self._format_check_group_response(response)
                return self._success_response(updated_group)

        except Exception as e:
            self.logger.error(f"Error updating check group {group_id}: {e}")
            return self._error_response(str(e))

    async def delete_check_group(self, group_id: str) -> str:
        """
        Delete a check group. All checks in the group will be moved to ungrouped.

        Args:
            group_id: ID of the check group to delete

        Returns:
            JSON string confirming deletion
        """
        try:
            self.logger.info(f"Deleting check group {group_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                check_groups_api.v1_check_groups_group_id_delete(group_id=group_id)

                return self._success_response({
                    "message": f"Check group {group_id} deleted successfully",
                    "group_id": group_id
                })

        except Exception as e:
            self.logger.error(f"Error deleting check group {group_id}: {e}")
            return self._error_response(str(e))

    async def assign_check_to_group(self, check_id: str, group_id: Optional[str] = None) -> str:
        """
        Assign a check to a group or remove it from a group.

        Args:
            check_id: ID of the check to assign
            group_id: ID of the group to assign to (or None to ungroup)

        Returns:
            JSON string confirming assignment
        """
        try:
            action = f"Assigning check {check_id} to group {group_id}" if group_id else f"Removing check {check_id} from group"
            self.logger.info(action)

            with self.client._get_api_client() as api_client:
                from pingera.api import CheckGroupsApi
                check_groups_api = CheckGroupsApi(api_client)

                assignment_data = {"group_id": group_id}
                response = check_groups_api.v1_checks_check_id_group_patch(
                    check_id=check_id,
                    generated=assignment_data
                )

                assignment_result = self._format_assignment_response(response)
                return self._success_response(assignment_result)

        except Exception as e:
            self.logger.error(f"Error assigning check {check_id} to group {group_id}: {e}")
            return self._error_response(str(e))

    def _format_check_groups_response(self, response) -> dict:
        """Format check groups list response."""
        if hasattr(response, '__dict__'):
            # Handle the actual API response structure with pagination and groups
            groups_data = getattr(response, 'groups', [])
            pagination = getattr(response, 'pagination', {})

            # Convert model objects to dictionaries for JSON serialization
            if isinstance(groups_data, list):
                formatted_groups = []
                for item in groups_data:
                    if hasattr(item, '__dict__'):
                        # Convert datetime objects to strings for JSON serialization
                        group_dict = self._convert_sdk_object_to_dict(item)
                        formatted_groups.append(group_dict)
                    else:
                        formatted_groups.append(item)
            else:
                formatted_groups = groups_data

            # Extract pagination info
            total = pagination.get('total_items', 0) if isinstance(pagination, dict) else 0
            page = pagination.get('page', 1) if isinstance(pagination, dict) else 1
            page_size = pagination.get('page_size', 20) if isinstance(pagination, dict) else 20

            return {
                "groups": formatted_groups,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        return {"groups": [], "total": 0}

    def _format_check_group_response(self, response) -> dict:
        """Format single check group response."""
        if hasattr(response, '__dict__'):
            return self._convert_sdk_object_to_dict(response)
        return response

    def _format_group_checks_response(self, response) -> dict:
        """Format checks in group response."""
        if hasattr(response, '__dict__'):
            # Handle the actual API response structure with pagination and checks
            checks_data = getattr(response, 'checks', [])
            pagination = getattr(response, 'pagination', {})

            # Convert model objects to dictionaries for JSON serialization
            if isinstance(checks_data, list):
                formatted_checks = []
                for item in checks_data:
                    if hasattr(item, '__dict__'):
                        check_dict = self._convert_sdk_object_to_dict(item)
                        formatted_checks.append(check_dict)
                    else:
                        formatted_checks.append(item)
            else:
                formatted_checks = checks_data

            # Extract pagination info
            total = pagination.get('total_items', 0) if isinstance(pagination, dict) else 0
            page = pagination.get('page', 1) if isinstance(pagination, dict) else 1
            page_size = pagination.get('page_size', 20) if isinstance(pagination, dict) else 20

            return {
                "checks": formatted_checks,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        return {"checks": [], "total": 0}

    def _format_assignment_response(self, response) -> dict:
        """Format check assignment response."""
        if hasattr(response, '__dict__'):
            return self._convert_sdk_object_to_dict(response)
        return response
