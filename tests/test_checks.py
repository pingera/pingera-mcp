
"""
Tests for ChecksTools.
"""
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock

from pingera_mcp.tools import ChecksTools
from pingera_mcp.exceptions import PingeraError


class TestChecksTools:
    """Test cases for ChecksTools."""

    @pytest.fixture
    def checks_tools(self, mock_pingera_client):
        """Create ChecksTools instance for testing."""
        return ChecksTools(mock_pingera_client)

    @pytest.fixture
    def mock_check_data(self):
        """Mock check data."""
        return {
            "id": "check_123",
            "name": "Test Website Check",
            "type": "web",
            "url": "https://example.com",
            "status": "active",
            "interval": 60,
            "created_at": "2024-01-01T00:00:00Z"
        }

    @pytest.fixture
    def mock_checks_list(self, mock_check_data):
        """Mock checks list response."""
        mock_response = Mock()
        mock_response.data = [mock_check_data]
        mock_response.total = 1
        mock_response.page = 1
        mock_response.page_size = 20
        return mock_response

    @pytest.fixture
    def mock_check_results(self):
        """Mock check results response."""
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "result_1",
                "check_id": "check_123",
                "status": "success",
                "response_time": 150,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ]
        mock_response.total = 1
        mock_response.page = 1
        mock_response.page_size = 50
        return mock_response

    @pytest.mark.asyncio
    async def test_list_checks_success(self, checks_tools, mock_checks_list):
        """Test successful checks listing."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_get.return_value = mock_checks_list
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.list_checks(page=1, page_size=20)
                
                # Parse and validate result
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert "checks" in result_data["data"]
                assert len(result_data["data"]["checks"]) == 1
                assert result_data["data"]["total"] == 1

    @pytest.mark.asyncio
    async def test_get_check_details_success(self, checks_tools, mock_check_data):
        """Test successful check details retrieval."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_get.return_value = mock_check_data
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.get_check_details("check_123")
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["data"]["id"] == "check_123"
                assert result_data["data"]["name"] == "Test Website Check"

    @pytest.mark.asyncio
    async def test_create_check_success(self, checks_tools, mock_check_data):
        """Test successful check creation."""
        check_input = {
            "name": "New Check",
            "type": "web",
            "url": "https://newsite.com",
            "interval": 300
        }

        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_post.return_value = mock_check_data
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.create_check(check_input)
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["data"]["id"] == "check_123"

    @pytest.mark.asyncio
    async def test_update_check_success(self, checks_tools, mock_check_data):
        """Test successful check update."""
        update_data = {"name": "Updated Check Name"}

        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_put.return_value = mock_check_data
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.update_check("check_123", update_data)
                
                result_data = json.loads(result)
                assert result_data["success"] is True

    @pytest.mark.asyncio
    async def test_delete_check_success(self, checks_tools):
        """Test successful check deletion."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_delete.return_value = None
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.delete_check("check_123")
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert "deleted successfully" in result_data["data"]["message"]

    @pytest.mark.asyncio
    async def test_get_check_results_success(self, checks_tools, mock_check_results):
        """Test successful check results retrieval."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_results_get.return_value = mock_check_results
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.get_check_results("check_123")
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert "results" in result_data["data"]
                assert len(result_data["data"]["results"]) == 1

    @pytest.mark.asyncio
    async def test_get_check_statistics_success(self, checks_tools):
        """Test successful check statistics retrieval."""
        mock_stats = {
            "uptime_percentage": 99.5,
            "average_response_time": 200,
            "total_checks": 1440,
            "successful_checks": 1433,
            "failed_checks": 7
        }

        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_stats_get.return_value = mock_stats
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.get_check_statistics("check_123")
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["data"]["uptime_percentage"] == 99.5

    @pytest.mark.asyncio
    async def test_pause_check_success(self, checks_tools):
        """Test successful check pause."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_pause_post.return_value = None
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.pause_check("check_123")
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["data"]["status"] == "paused"

    @pytest.mark.asyncio
    async def test_resume_check_success(self, checks_tools):
        """Test successful check resume."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_check_id_resume_post.return_value = None
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.resume_check("check_123")
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["data"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_list_check_jobs_success(self, checks_tools):
        """Test successful check jobs listing."""
        mock_jobs_response = Mock()
        mock_jobs_response.data = [
            {"id": "job_1", "status": "running", "check_id": "check_123"}
        ]
        mock_jobs_response.total = 1

        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksApi') as mock_checks_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_jobs_get.return_value = mock_jobs_response
                mock_checks_api.return_value = mock_api_instance

                result = await checks_tools.list_check_jobs()
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert "jobs" in result_data["data"]
                assert len(result_data["data"]["jobs"]) == 1

    @pytest.mark.asyncio
    async def test_get_unified_results_success(self, checks_tools):
        """Test successful unified results retrieval."""
        mock_unified_response = Mock()
        mock_unified_response.data = [
            {"check_id": "check_1", "status": "success"},
            {"check_id": "check_2", "status": "success"}
        ]
        mock_unified_response.total = 2
        mock_unified_response.page = 1
        mock_unified_response.page_size = 100

        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_api_client = Mock()
            mock_context.return_value.__enter__.return_value = mock_api_client
            mock_context.return_value.__exit__.return_value = None
            
            with patch('pingera.api.ChecksUnifiedResultsApi') as mock_unified_api:
                mock_api_instance = Mock()
                mock_api_instance.v1_checks_unified_results_get.return_value = mock_unified_response
                mock_unified_api.return_value = mock_api_instance

                result = await checks_tools.get_unified_results(
                    check_ids=["check_1", "check_2"]
                )
                
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert "results" in result_data["data"]
                assert len(result_data["data"]["results"]) == 2

    @pytest.mark.asyncio
    async def test_error_handling(self, checks_tools):
        """Test error handling in checks tools."""
        with patch.object(checks_tools.client, '_get_api_client') as mock_context:
            mock_context.side_effect = Exception("API connection failed")

            result = await checks_tools.list_checks()
            
            result_data = json.loads(result)
            assert result_data["success"] is False
            assert "API connection failed" in result_data["error"]

    @pytest.mark.asyncio
    async def test_format_methods(self, checks_tools, mock_checks_list):
        """Test response formatting methods."""
        # Test format_checks_response
        formatted = checks_tools._format_checks_response(mock_checks_list)
        assert "checks" in formatted
        assert "total" in formatted
        assert formatted["total"] == 1

        # Test format_check_response with dict-like object
        check_obj = Mock()
        check_obj.__dict__ = {"id": "test", "name": "Test Check"}
        formatted_check = checks_tools._format_check_response(check_obj)
        assert formatted_check["id"] == "test"
        assert formatted_check["name"] == "Test Check"
