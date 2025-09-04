"""
MCP tools for monitoring checks.
"""
import json
from typing import Optional, List, Dict, Any

from datetime import datetime

from .base import BaseTools
from ..exceptions import PingeraError


class ChecksTools(BaseTools):
    """Tools for managing monitoring checks."""

    async def list_checks(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> str:
        """
        List monitoring checks.

        Args:
            page: Page number for pagination (default: 1)
            page_size: Number of items per page (default: 20, max: 100)
            type: Filter by check type ('web', 'api', 'ssl', 'tcp', 'synthetic', 'multistep')
            status: Filter by status (can specify multiple statuses separated by commas)
            group_id: Filter checks by group ID (use "ungrouped" for checks not in any group)
            name: Filter checks by name using case-insensitive partial matching

        Returns:
            JSON string containing checks data
        """
        try:
            self.logger.info(f"Listing checks (page={page}, page_size={page_size}, type={type}, status={status}, group_id={group_id}, name={name})")

            # Use the SDK client to get checks
            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size
                if type is not None:
                    kwargs['type'] = type
                if status is not None:
                    kwargs['status'] = status
                if group_id is not None:
                    kwargs['group_id'] = group_id
                if name is not None:
                    kwargs['name'] = name

                response = checks_api.v1_checks_get(**kwargs)

                # Convert response to dict format
                checks_data = self._format_checks_response(response)
                return self._success_response(checks_data)

        except Exception as e:
            self.logger.error(f"Error listing checks: {e}")
            return self._error_response(str(e))

    async def get_check_details(self, check_id: str) -> str:
        """
        Get detailed information about a specific check.

        Args:
            check_id: ID of the check to retrieve

        Returns:
            JSON string containing check details
        """
        try:
            self.logger.info(f"Getting check details for ID: {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                response = checks_api.v1_checks_check_id_get(check_id=check_id)

                check_data = self._format_check_response(response)
                return self._success_response(check_data)

        except Exception as e:
            self.logger.error(f"Error getting check details for {check_id}: {e}")
            return self._error_response(str(e))

    async def create_check(
        self,
        name: str,
        type: str,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        interval: int = 300,
        timeout: int = 10,
        active: bool = True,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        try:
            # 1. Collect all arguments into a dictionary
            check_data = {
                "name": name, "type": type, "url": url, "host": host,
                "port": port, "interval": interval, "timeout": timeout,
                "active": active, "parameters": parameters
            }

            # 2. Filter out optional arguments that were not provided (are None)
            filtered_check_data = {k: v for k, v in check_data.items() if v is not None}

            self.logger.info(f"Creating new check: {filtered_check_data.get('name', 'Unnamed')}")

            # 3. Use the clean dictionary with your SDK
            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                from pingera.models import MonitorCheck
                checks_api = ChecksApi(api_client)

                monitor_check = MonitorCheck(**filtered_check_data)
                response = checks_api.v1_checks_post(monitor_check)

                created_check = self._format_check_response(response)
                return self._success_response(created_check)

        except Exception as e:
            self.logger.error(f"Error creating check: {e}")
            return self._error_response(str(e))

    async def update_check(
        self,
        check_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        interval: Optional[int] = None,
        timeout: Optional[int] = None,
        active: Optional[bool] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        (Your docstring here)
        """
        try:
            update_data = {
                "name": name, "url": url, "host": host, "port": port,
                "interval": interval, "timeout": timeout, "active": active,
                "parameters": parameters
            }

            payload = {k: v for k, v in update_data.items() if v is not None}

            if not payload:
                return self._error_response("No update data provided. Please specify at least one field to update.")

            self.logger.info(f"Updating check {check_id} with data: {payload}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                from pingera.models import MonitorCheck1 
                checks_api = ChecksApi(api_client)

                update_model = MonitorCheck1(**payload)

                response = checks_api.v1_checks_check_id_patch(
                    check_id=check_id,
                    monitor_check1=update_model
                )

                updated_check = self._format_check_response(response)
                return self._success_response(updated_check)

        except Exception as e:
            self.logger.error(f"Error updating check {check_id}: {e}")
            return self._error_response(str(e))

    async def delete_check(self, check_id: str) -> str:
        """
        Delete a monitoring check.

        Args:
            check_id: ID of the check to delete

        Returns:
            JSON string confirming deletion
        """
        try:
            self.logger.info(f"Deleting check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                checks_api.v1_checks_check_id_delete(check_id=check_id)

                return self._success_response({
                    "message": f"Check {check_id} deleted successfully",
                    "check_id": check_id
                })

        except Exception as e:
            self.logger.error(f"Error deleting check {check_id}: {e}")
            return self._error_response(str(e))

    async def get_check_results(
        self,
        check_id: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        Get results for a specific check.

        Args:
            check_id: ID of the check
            from_date: Start date for results (ISO 8601 format)
            to_date: End date for results (ISO 8601 format)
            page: Page number for pagination
            page_size: Number of items per page

        Returns:
            JSON string containing check results
        """
        try:
            self.logger.info(f"Getting results for check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if from_date is not None:
                    kwargs['from_date'] = from_date
                if to_date is not None:
                    kwargs['to_date'] = to_date
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size

                response = checks_api.v1_checks_check_id_results_get(
                    check_id=check_id,
                    **kwargs
                )

                results_data = self._format_results_response(response)
                return self._success_response(results_data)

        except Exception as e:
            self.logger.error(f"Error getting results for check {check_id}: {e}")
            return self._error_response(str(e))

    async def get_check_statistics(self, check_id: str) -> str:
        """
        Get statistics for a specific check.

        Args:
            check_id: ID of the check

        Returns:
            JSON string containing check statistics
        """
        try:
            self.logger.info(f"Getting statistics for check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                response = checks_api.v1_checks_check_id_stats_get(check_id=check_id)

                stats_data = self._format_stats_response(response)
                return self._success_response(stats_data)

        except Exception as e:
            self.logger.error(f"Error getting statistics for check {check_id}: {e}")
            return self._error_response(str(e))

    async def pause_check(self, check_id: str) -> str:
        """
        Pause a monitoring check.

        Args:
            check_id: ID of the check to pause

        Returns:
            JSON string confirming check is paused
        """
        try:
            self.logger.info(f"Pausing check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                checks_api.v1_checks_check_id_pause_post(check_id=check_id)

                return self._success_response({
                    "message": f"Check {check_id} paused successfully",
                    "check_id": check_id,
                    "status": "paused"
                })

        except Exception as e:
            self.logger.error(f"Error pausing check {check_id}: {e}")
            return self._error_response(str(e))

    async def resume_check(self, check_id: str) -> str:
        """
        Resume a paused monitoring check.

        Args:
            check_id: ID of the check to resume

        Returns:
            JSON string confirming check is resumed
        """
        try:
            self.logger.info(f"Resuming check {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                checks_api.v1_checks_check_id_resume_post(check_id=check_id)

                return self._success_response({
                    "message": f"Check {check_id} resumed successfully",
                    "check_id": check_id,
                    "status": "active"
                })

        except Exception as e:
            self.logger.error(f"Error resuming check {check_id}: {e}")
            return self._error_response(str(e))

    async def list_check_jobs(self) -> str:
        """
        List all check jobs.

        Returns:
            JSON string containing check jobs data
        """
        try:
            self.logger.info("Listing check jobs")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                response = checks_api.v1_checks_jobs_get()

                jobs_data = self._format_jobs_response(response)
                return self._success_response(jobs_data)

        except Exception as e:
            self.logger.error(f"Error listing check jobs: {e}")
            return self._error_response(str(e))

    async def get_check_job_details(self, job_id: str) -> str:
        """
        Get details for a specific check job.

        Args:
            job_id: ID of the job to retrieve

        Returns:
            JSON string containing job details
        """
        try:
            self.logger.info(f"Getting job details for ID: {job_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import OnDemandChecksApi
                on_demand_api = OnDemandChecksApi(api_client)

                response = on_demand_api.v1_checks_jobs_job_id_get(job_id=job_id)

                job_data = self._format_job_response(response)
                return self._success_response(job_data)

        except Exception as e:
            self.logger.error(f"Error getting job details for {job_id}: {e}")
            return self._error_response(str(e))

    async def get_unified_results(
        self,
        check_ids: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        status: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        Get unified results across multiple checks.

        Args:
            check_ids: List of specific check IDs to query
            from_date: Start date for results (ISO 8601 format)
            to_date: End date for results (ISO 8601 format)
            status: Filter by result status
            page: Page number for pagination
            page_size: Number of items per page

        Returns:
            JSON string containing unified results
        """
        try:
            self.logger.info("Getting unified results from multiple checks")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if check_ids is not None:
                    kwargs['check_ids'] = check_ids
                if from_date is not None:
                    kwargs['from_date'] = from_date
                if to_date is not None:
                    kwargs['to_date'] = to_date
                if status is not None:
                    kwargs['status'] = status
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size

                response = checks_api.v1_checks_results_get(**kwargs)

                unified_data = self._format_unified_results_response(response)
                return self._success_response(unified_data)

        except Exception as e:
            self.logger.error(f"Error getting unified results: {e}")
            return self._error_response(str(e))

    async def get_unified_statistics(
        self,
        check_ids: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> str:
        """
        Get aggregated statistics for multiple checks.

        Args:
            check_ids: List of specific check IDs to query
            from_date: Start date for statistics (ISO 8601 format)
            to_date: End date for statistics (ISO 8601 format)

        Returns:
            JSON string containing aggregated statistics
        """
        try:
            self.logger.info("Getting unified statistics from multiple checks")

            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if check_ids is not None:
                    kwargs['check_ids'] = check_ids
                if from_date is not None:
                    kwargs['from_date'] = from_date
                if to_date is not None:
                    kwargs['to_date'] = to_date

                response = checks_api.v1_checks_statistics_get(**kwargs)

                stats_data = self._format_unified_stats_response(response)
                return self._success_response(stats_data)

        except Exception as e:
            self.logger.error(f"Error getting unified statistics: {e}")
            return self._error_response(str(e))

    def _format_checks_response(self, response) -> dict:
        """Format checks list response."""
        if hasattr(response, '__dict__'):
            # Handle the actual API response structure with pagination and checks
            checks_data = getattr(response, 'checks', [])
            pagination = getattr(response, 'pagination', {})

            # Convert model objects to dictionaries for JSON serialization
            if isinstance(checks_data, list):
                formatted_checks = []
                for item in checks_data:
                    if hasattr(item, '__dict__'):
                        # Convert datetime objects to strings for JSON serialization
                        check_dict = {}
                        for key, value in item.__dict__.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                check_dict[key] = value.isoformat()
                            else:
                                check_dict[key] = value
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

    def _format_check_response(self, response) -> dict:
        """Format single check response."""
        if hasattr(response, '__dict__'):
            return response.__dict__
        return response

    def _format_results_response(self, response) -> dict:
        """Format check results response."""
        if hasattr(response, '__dict__'):
            # SDK returns results in 'results' attribute, not 'data'
            results_data = getattr(response, 'results', [])
            pagination = getattr(response, 'pagination', {})

            if isinstance(results_data, list):
                formatted_data = []
                for item in results_data:
                    if hasattr(item, '__dict__'):
                        # Use the base class method to properly convert SDK objects
                        formatted_data.append(self._convert_sdk_object_to_dict(item))
                    else:
                        formatted_data.append(item)
            else:
                formatted_data = results_data

            # Extract pagination info properly
            if isinstance(pagination, dict):
                total = pagination.get('total_items', 0)
                page = pagination.get('page', 1)
                page_size = pagination.get('page_size', 50)
            else:
                total = getattr(response, 'total', 0)
                page = getattr(response, 'page', 1)
                page_size = getattr(response, 'page_size', 50)

            return {
                "results": formatted_data,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        return {"results": [], "total": 0}

    def _format_stats_response(self, response) -> dict:
        """Format check statistics response."""
        if hasattr(response, '__dict__'):
            return response.__dict__
        return response

    def _format_jobs_response(self, response) -> dict:
        """Format check jobs response."""
        if hasattr(response, '__dict__'):
            # Convert model objects to dictionaries for JSON serialization
            data = getattr(response, 'data', [])
            if isinstance(data, list):
                formatted_data = []
                for item in data:
                    if hasattr(item, '__dict__'):
                        formatted_data.append(item.__dict__)
                    else:
                        formatted_data.append(item)
            else:
                formatted_data = data

            return {
                "jobs": formatted_data,
                "total": getattr(response, 'total', 0)
            }
        return {"jobs": [], "total": 0}

    def _format_job_response(self, response) -> dict:
        """Format single job response."""
        if hasattr(response, '__dict__'):
            return response.__dict__
        return response

    def _format_unified_results_response(self, response) -> dict:
        """Format unified results response."""
        if hasattr(response, '__dict__'):
            # Convert model objects to dictionaries for JSON serialization
            data = getattr(response, 'data', [])
            if isinstance(data, list):
                formatted_data = []
                for item in data:
                    if hasattr(item, '__dict__'):
                        formatted_data.append(item.__dict__)
                    else:
                        formatted_data.append(item)
            else:
                formatted_data = data

            return {
                "results": formatted_data,
                "total": getattr(response, 'total', 0),
                "page": getattr(response, 'page', 1),
                "page_size": getattr(response, 'page_size', 100)
            }
        return {"results": [], "total": 0}

    def _format_unified_stats_response(self, response) -> dict:
        """Format unified statistics response."""
        if hasattr(response, '__dict__'):
            return response.__dict__
        return response

    # On-Demand Checks Methods

    async def execute_custom_check(
        self,
        type: str,
        name: str,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[int] = 30,
        parameters: Optional[dict] = None
    ) -> str:
        """
        Execute a custom check on demand.

        Args:
            type: Type of check ('web', 'api', 'ssl', 'tcp', 'synthetic', 'multistep')
            name: A user-friendly name for the custom check (max 100 characters)
            url: URL to check (required for web/api checks)
            host: Hostname or IP address (required for TCP/SSL checks, max 255 characters)
            port: Port number (required for TCP/SSL checks, range: 1-65535)
            timeout: Timeout in seconds (range: 1-30)
            parameters: Additional parameters (e.g., pw_script for synthetic checks)

        Returns:
            JSON string containing job information
        """
        try:
            self.logger.info(f"Executing custom check: {name} ({type})")

            # Build request data according to ExecuteCustomCheckRequest model
            request_data = {
                "type": type,
                "name": name
            }
            
            # Add optional parameters only if provided
            if url is not None:
                request_data["url"] = url
            if host is not None:
                request_data["host"] = host
            if port is not None:
                request_data["port"] = port
            if timeout is not None:
                request_data["timeout"] = timeout
            if parameters is not None:
                request_data["parameters"] = parameters

            with self.client._get_api_client() as api_client:
                from pingera.api import OnDemandChecksApi
                from pingera.models import ExecuteCustomCheckRequest
                on_demand_api = OnDemandChecksApi(api_client)

                # Create ExecuteCustomCheckRequest model
                check_request = ExecuteCustomCheckRequest(**request_data)
                
                response = on_demand_api.v1_checks_execute_post(execute_custom_check_request=check_request)

                job_data = self._format_job_response(response)
                return self._success_response(job_data)

        except Exception as e:
            self.logger.error(f"Error executing custom check: {e}")
            return self._error_response(str(e))

    async def execute_existing_check(self, check_id: str) -> str:
        """
        Execute an existing check on demand.

        Args:
            check_id: ID of the existing check to execute

        Returns:
            JSON string containing job information
        """
        try:
            self.logger.info(f"Executing existing check: {check_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import OnDemandChecksApi
                on_demand_api = OnDemandChecksApi(api_client)

                response = on_demand_api.v1_checks_check_id_execute_post(check_id=check_id)

                job_data = self._format_job_response(response)
                return self._success_response(job_data)

        except Exception as e:
            self.logger.error(f"Error executing existing check {check_id}: {e}")
            return self._error_response(str(e))

    async def get_on_demand_job_status(self, job_id: str) -> str:
        """
        Get the status of an on-demand check job.

        Args:
            job_id: ID of the job to check

        Returns:
            JSON string containing job status
        """
        try:
            self.logger.info(f"Getting job status for: {job_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import OnDemandChecksApi
                on_demand_api = OnDemandChecksApi(api_client)

                response = on_demand_api.v1_checks_jobs_job_id_get(job_id=job_id)

                job_data = self._format_job_response(response)
                return self._success_response(job_data)

        except Exception as e:
            self.logger.error(f"Error getting job status for {job_id}: {e}")
            return self._error_response(str(e))

    async def list_on_demand_checks(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        List on-demand checks.

        Args:
            page: Page number for pagination
            page_size: Number of items per page

        Returns:
            JSON string containing on-demand checks data
        """
        try:
            self.logger.info(f"Listing on-demand checks (page={page}, page_size={page_size})")

            with self.client._get_api_client() as api_client:
                from pingera.api import OnDemandChecksApi
                on_demand_api = OnDemandChecksApi(api_client)

                response = on_demand_api.v1_on_demand_checks_get(
                    page=page,
                    page_size=page_size
                )

                checks_data = self._format_on_demand_checks_response(response)
                return self._success_response(checks_data)

        except Exception as e:
            self.logger.error(f"Error listing on-demand checks: {e}")
            return self._error_response(str(e))

    def _format_on_demand_checks_response(self, response) -> dict:
        """Format on-demand checks response."""
        if hasattr(response, '__dict__'):
            # Convert model objects to dictionaries for JSON serialization
            data = getattr(response, 'data', [])
            if isinstance(data, list):
                formatted_data = []
                for item in data:
                    if hasattr(item, '__dict__'):
                        formatted_data.append(item.__dict__)
                    else:
                        formatted_data.append(item)
            else:
                formatted_data = data

            return {
                "checks": formatted_data,
                "total": getattr(response, 'total', 0),
                "page": getattr(response, 'page', 1),
                "page_size": getattr(response, 'page_size', 20)
            }
        return {"checks": [], "total": 0}