
"""
MCP tools for monitoring checks management.
"""
import json
from typing import Optional, List
from datetime import datetime

from .base import BaseTools
from ..exceptions import PingeraError


class ChecksTools(BaseTools):
    """Tools for managing monitoring checks."""

    async def list_checks(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        check_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List monitoring checks.

        Args:
            page: Page number for pagination
            page_size: Number of items per page
            check_type: Filter by check type (e.g., 'web', 'api', 'ping')
            status: Filter by status (e.g., 'active', 'paused')

        Returns:
            JSON string containing checks data
        """
        try:
            self.logger.info(f"Listing checks (page={page}, page_size={page_size}, type={check_type}, status={status})")
            
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
                if check_type is not None:
                    kwargs['type'] = check_type
                if status is not None:
                    kwargs['status'] = status
                
                self.logger.info(f"🔧 API call parameters: {kwargs}")
                self.logger.info(f"🔧 API client base URL: {getattr(api_client.configuration, 'host', 'Unknown')}")
                
                response = checks_api.v1_checks_get(**kwargs)
                
                # Debug the raw response
                self.logger.info(f"🔍 Raw API response type: {type(response)}")
                self.logger.info(f"🔍 Response has __dict__: {hasattr(response, '__dict__')}")
                
                if hasattr(response, '__dict__'):
                    self.logger.info(f"🔍 Response __dict__: {response.__dict__}")
                    
                # Check for common response attributes
                for attr in ['data', 'checks', 'items', 'results', 'total', 'page', 'page_size', 'count']:
                    if hasattr(response, attr):
                        attr_value = getattr(response, attr)
                        self.logger.info(f"🔍 Response.{attr}: {attr_value} (type: {type(attr_value)})")
                        if isinstance(attr_value, list):
                            self.logger.info(f"🔍 Response.{attr} length: {len(attr_value)}")
                
                # Try to inspect the response structure more deeply
                try:
                    # Check if response is iterable
                    if hasattr(response, '__iter__') and not isinstance(response, (str, bytes)):
                        response_list = list(response)
                        self.logger.info(f"🔍 Response as list: {response_list} (length: {len(response_list)})")
                except Exception as iter_error:
                    self.logger.info(f"🔍 Response not iterable: {iter_error}")
                
                # Convert response to dict format
                checks_data = self._format_checks_response(response)
                self.logger.info(f"🔍 Formatted checks data: {checks_data}")
                
                return self._success_response(checks_data)
                
        except Exception as e:
            self.logger.error(f"Error listing checks: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
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

    async def create_check(self, check_data: dict) -> str:
        """
        Create a new monitoring check.

        Args:
            check_data: Dictionary containing check configuration

        Returns:
            JSON string containing created check data
        """
        try:
            self.logger.info(f"Creating new check: {check_data.get('name', 'Unnamed')}")
            
            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)
                
                response = checks_api.v1_checks_post(check_data)
                
                created_check = self._format_check_response(response)
                return self._success_response(created_check)
                
        except Exception as e:
            self.logger.error(f"Error creating check: {e}")
            return self._error_response(str(e))

    async def update_check(self, check_id: str, check_data: dict) -> str:
        """
        Update an existing monitoring check.

        Args:
            check_id: ID of the check to update
            check_data: Dictionary containing updated check configuration

        Returns:
            JSON string containing updated check data
        """
        try:
            self.logger.info(f"Updating check {check_id}")
            
            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)
                
                response = checks_api.v1_checks_check_id_put(
                    check_id=check_id,
                    check_data=check_data
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
                
                response = checks_api.v1_checks_check_id_results_get(
                    check_id=check_id,
                    from_date=from_date,
                    to_date=to_date,
                    page=page,
                    page_size=page_size
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
                from pingera.api import ChecksApi
                checks_api = ChecksApi(api_client)
                
                response = checks_api.v1_checks_jobs_job_id_get(job_id=job_id)
                
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
            self.logger.info(f"Getting unified results for checks: {check_ids}")
            
            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksUnifiedResultsApi
                unified_api = ChecksUnifiedResultsApi(api_client)
                
                response = unified_api.v1_checks_unified_results_get(
                    check_ids=check_ids,
                    from_date=from_date,
                    to_date=to_date,
                    status=status,
                    page=page,
                    page_size=page_size
                )
                
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
            self.logger.info(f"Getting unified statistics for checks: {check_ids}")
            
            with self.client._get_api_client() as api_client:
                from pingera.api import ChecksUnifiedResultsApi
                unified_api = ChecksUnifiedResultsApi(api_client)
                
                response = unified_api.v1_checks_unified_results_stats_get(
                    check_ids=check_ids,
                    from_date=from_date,
                    to_date=to_date
                )
                
                stats_data = self._format_unified_stats_response(response)
                return self._success_response(stats_data)
                
        except Exception as e:
            self.logger.error(f"Error getting unified statistics: {e}")
            return self._error_response(str(e))

    def _format_checks_response(self, response) -> dict:
        """Format checks list response."""
        self.logger.info(f"🔧 Formatting checks response: {type(response)}")
        
        if hasattr(response, '__dict__'):
            # Try different possible attribute names for checks data
            checks_data = None
            for attr_name in ['data', 'checks', 'items', 'results']:
                if hasattr(response, attr_name):
                    checks_data = getattr(response, attr_name)
                    self.logger.info(f"🔧 Found checks data in response.{attr_name}: {checks_data}")
                    break
            
            if checks_data is None:
                checks_data = []
                self.logger.warning("🔧 No checks data found in response attributes")
            
            # Get pagination info
            total = getattr(response, 'total', len(checks_data) if isinstance(checks_data, list) else 0)
            page = getattr(response, 'page', 1)
            page_size = getattr(response, 'page_size', getattr(response, 'per_page', 20))
            
            formatted_result = {
                "checks": checks_data if isinstance(checks_data, list) else [],
                "total": total,
                "page": page,
                "page_size": page_size
            }
            
            self.logger.info(f"🔧 Formatted result: {formatted_result}")
            return formatted_result
        
        self.logger.warning(f"🔧 Response has no __dict__ attribute, returning empty result")
        return {"checks": [], "total": 0}

    def _format_check_response(self, response) -> dict:
        """Format single check response."""
        if hasattr(response, '__dict__'):
            return response.__dict__
        return response

    def _format_results_response(self, response) -> dict:
        """Format check results response."""
        if hasattr(response, '__dict__'):
            return {
                "results": getattr(response, 'data', []),
                "total": getattr(response, 'total', 0),
                "page": getattr(response, 'page', 1),
                "page_size": getattr(response, 'page_size', 50)
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
            return {
                "jobs": getattr(response, 'data', []),
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
            return {
                "results": getattr(response, 'data', []),
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
        url: str,
        check_type: str = "web",
        timeout: Optional[int] = 30,
        name: Optional[str] = None,
        parameters: Optional[dict] = None
    ) -> str:
        """
        Execute a custom check on demand.

        Args:
            url: URL to check
            check_type: Type of check ('web', 'synthetic', 'api')
            timeout: Timeout in seconds
            name: Name for the check
            parameters: Additional parameters (e.g., pw_script for synthetic checks)

        Returns:
            JSON string containing job information
        """
        try:
            self.logger.info(f"Executing custom check for URL: {url}")
            
            # Prepare check request data
            check_request = {
                "url": url,
                "type": check_type,
                "timeout": timeout,
                "name": name or f"On-demand check for {url}",
                "parameters": parameters or {}
            }
            
            with self.client._get_api_client() as api_client:
                from pingera.api import OnDemandChecksApi
                on_demand_api = OnDemandChecksApi(api_client)
                
                response = on_demand_api.v1_checks_execute_post(check_request)
                
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
            return {
                "checks": getattr(response, 'data', []),
                "total": getattr(response, 'total', 0),
                "page": getattr(response, 'page', 1),
                "page_size": getattr(response, 'page_size', 20)
            }
        return {"checks": [], "total": 0}
