
"""
Tests for component functionality.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json

from pingera.models import Component, ComponentStatus
from pingera.endpoints import ComponentEndpoints
from pingera.tools import ComponentTools
from pingera.resources import ComponentResources
from pingera import PingeraError, PingeraAPIError


class TestComponentModel:
    """Test cases for Component model."""

    def test_component_model_creation_minimal(self):
        """Test Component model creation with minimal required fields."""
        component_data = {
            "name": "API Server"
        }

        component = Component(**component_data)

        assert component.name == "API Server"
        assert component.group is False
        assert component.id is None
        assert component.status is None

    def test_component_model_creation_complete(self):
        """Test Component model creation with all fields."""
        component_data = {
            "id": "comp123abc456",
            "name": "API Server",
            "description": "Main REST API server handling user requests",
            "group": False,
            "group_id": "grp123abc456",
            "only_show_if_degraded": False,
            "position": 1,
            "showcase": True,
            "start_date": "2024-01-01T00:00:00Z",
            "status": "operational",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T14:00:00Z",
            "page_id": "page123def789"
        }

        component = Component(**component_data)

        assert component.id == "comp123abc456"
        assert component.name == "API Server"
        assert component.description == "Main REST API server handling user requests"
        assert component.group is False
        assert component.group_id == "grp123abc456"
        assert component.only_show_if_degraded is False
        assert component.position == 1
        assert component.showcase is True
        assert component.status == ComponentStatus.OPERATIONAL
        assert component.page_id == "page123def789"

    def test_component_status_enum(self):
        """Test ComponentStatus enum values."""
        assert ComponentStatus.OPERATIONAL == "operational"
        assert ComponentStatus.UNDER_MAINTENANCE == "under_maintenance"
        assert ComponentStatus.DEGRADED_PERFORMANCE == "degraded_performance"
        assert ComponentStatus.PARTIAL_OUTAGE == "partial_outage"
        assert ComponentStatus.MAJOR_OUTAGE == "major_outage"

    def test_component_model_validation(self):
        """Test Component model field validation."""
        # Test missing required 'name' field
        with pytest.raises(ValueError):
            Component()

    def test_component_model_as_group(self):
        """Test Component model when configured as a group."""
        component_data = {
            "name": "Infrastructure",
            "group": True,
            "description": "Infrastructure components group"
        }

        component = Component(**component_data)

        assert component.name == "Infrastructure"
        assert component.group is True
        assert component.description == "Infrastructure components group"


class TestComponentEndpoints:
    """Test cases for ComponentEndpoints."""

    def test_get_component_groups_success(self, mock_pingera_client):
        """Test successful component groups retrieval."""
        mock_response = [
            {
                "id": "group1",
                "name": "Infrastructure",
                "group": True,
                "status": "operational"
            },
            {
                "id": "group2", 
                "name": "Services",
                "group": True,
                "status": "degraded_performance"
            }
        ]

        # Mock the _make_request method
        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=mock_response)

        result = endpoints.get_component_groups("page123")

        assert len(result) == 2
        assert all(isinstance(comp, Component) for comp in result)
        assert result[0].name == "Infrastructure"
        assert result[1].name == "Services"
        endpoints._make_request.assert_called_once_with(
            "GET", "pages/page123/component-groups", params={}
        )

    def test_get_component_groups_with_deleted(self, mock_pingera_client):
        """Test component groups retrieval including deleted ones."""
        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=[])

        endpoints.get_component_groups("page123", show_deleted=True)

        endpoints._make_request.assert_called_once_with(
            "GET", "pages/page123/component-groups", params={"show_deleted": True}
        )

    def test_create_component_success(self, mock_pingera_client):
        """Test successful component creation."""
        component_data = {"name": "API Server", "status": "operational"}
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "comp123",
            "name": "API Server",
            "status": "operational"
        }

        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=mock_response)

        result = endpoints.create_component("page123", component_data)

        assert isinstance(result, Component)
        assert result.id == "comp123"
        assert result.name == "API Server"
        endpoints._make_request.assert_called_once_with(
            "POST", "pages/page123/components", data=component_data
        )

    def test_get_component_success(self, mock_pingera_client):
        """Test successful component retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "comp123",
            "name": "API Server",
            "status": "operational"
        }

        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=mock_response)

        result = endpoints.get_component("page123", "comp123")

        assert isinstance(result, Component)
        assert result.id == "comp123"
        assert result.name == "API Server"
        endpoints._make_request.assert_called_once_with(
            "GET", "pages/page123/components/comp123"
        )

    def test_update_component_success(self, mock_pingera_client):
        """Test successful component update."""
        component_data = {"name": "Updated API Server", "status": "under_maintenance"}
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "comp123",
            "name": "Updated API Server",
            "status": "under_maintenance"
        }

        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=mock_response)

        result = endpoints.update_component("page123", "comp123", component_data)

        assert isinstance(result, Component)
        assert result.name == "Updated API Server"
        assert result.status == ComponentStatus.UNDER_MAINTENANCE
        endpoints._make_request.assert_called_once_with(
            "PUT", "pages/page123/components/comp123", data=component_data
        )

    def test_patch_component_success(self, mock_pingera_client):
        """Test successful component patch."""
        component_data = {"status": "operational"}
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "comp123",
            "name": "API Server",
            "status": "operational"
        }

        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=mock_response)

        result = endpoints.patch_component("page123", "comp123", component_data)

        assert isinstance(result, Component)
        assert result.status == ComponentStatus.OPERATIONAL
        endpoints._make_request.assert_called_once_with(
            "PATCH", "pages/page123/components/comp123", data=component_data
        )

    def test_delete_component_success(self, mock_pingera_client):
        """Test successful component deletion."""
        endpoints = ComponentEndpoints(mock_pingera_client)
        endpoints._make_request = Mock(return_value=None)

        result = endpoints.delete_component("page123", "comp123")

        assert result is True
        endpoints._make_request.assert_called_once_with(
            "DELETE", "pages/page123/components/comp123"
        )


class TestComponentTools:
    """Test cases for ComponentTools."""

    @pytest.fixture
    def mock_component_tools(self, mock_pingera_client):
        """Create ComponentTools instance with mock client."""
        return ComponentTools(mock_pingera_client)

    @pytest.mark.asyncio
    async def test_list_component_groups_success(self, mock_component_tools):
        """Test successful component groups listing."""
        mock_components = [
            Component(id="group1", name="Infrastructure", group=True),
            Component(id="group2", name="Services", group=True)
        ]

        mock_component_tools.client.components.get_component_groups = Mock(
            return_value=mock_components
        )

        result = await mock_component_tools.list_component_groups("page123")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["data"]) == 2
        assert result_data["data"][0]["name"] == "Infrastructure"
        assert result_data["data"][1]["name"] == "Services"

    @pytest.mark.asyncio
    async def test_list_component_groups_with_deleted(self, mock_component_tools):
        """Test component groups listing with deleted components."""
        mock_component_tools.client.components.get_component_groups = Mock(
            return_value=[]
        )

        await mock_component_tools.list_component_groups("page123", show_deleted=True)

        mock_component_tools.client.components.get_component_groups.assert_called_once_with(
            "page123", True
        )

    @pytest.mark.asyncio
    async def test_list_component_groups_error(self, mock_component_tools):
        """Test component groups listing with error."""
        mock_component_tools.client.components.get_component_groups = Mock(
            side_effect=PingeraAPIError("API Error", 500)
        )

        result = await mock_component_tools.list_component_groups("page123")

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "API Error" in result_data["error"]

    @pytest.mark.asyncio
    async def test_get_component_details_success(self, mock_component_tools):
        """Test successful component details retrieval."""
        mock_component = Component(
            id="comp123",
            name="API Server",
            status=ComponentStatus.OPERATIONAL,
            description="Main API server"
        )

        mock_component_tools.client.components.get_component = Mock(
            return_value=mock_component
        )

        result = await mock_component_tools.get_component_details("page123", "comp123")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["name"] == "API Server"
        assert result_data["data"]["status"] == "operational"

    @pytest.mark.asyncio
    async def test_get_component_details_error(self, mock_component_tools):
        """Test component details retrieval with error."""
        mock_component_tools.client.components.get_component = Mock(
            side_effect=PingeraError("Component not found")
        )

        result = await mock_component_tools.get_component_details("page123", "comp123")

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "Component not found" in result_data["error"]

    @pytest.mark.asyncio
    async def test_create_component_success(self, mock_component_tools):
        """Test successful component creation."""
        mock_component = Component(
            id="comp123",
            name="New API Server",
            status=ComponentStatus.OPERATIONAL
        )

        mock_component_tools.client.components.create_component = Mock(
            return_value=mock_component
        )

        result = await mock_component_tools.create_component(
            "page123", "New API Server", description="Test API", status="operational"
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["name"] == "New API Server"

    @pytest.mark.asyncio
    async def test_update_component_success(self, mock_component_tools):
        """Test successful component update."""
        mock_component = Component(
            id="comp123",
            name="Updated API Server",
            status=ComponentStatus.UNDER_MAINTENANCE
        )

        mock_component_tools.client.components.update_component = Mock(
            return_value=mock_component
        )

        result = await mock_component_tools.update_component(
            "page123", "comp123", name="Updated API Server", status="under_maintenance"
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["name"] == "Updated API Server"
        assert result_data["data"]["status"] == "under_maintenance"

    @pytest.mark.asyncio
    async def test_patch_component_success(self, mock_component_tools):
        """Test successful component patch."""
        mock_component = Component(
            id="comp123",
            name="API Server",
            status=ComponentStatus.OPERATIONAL
        )

        mock_component_tools.client.components.patch_component = Mock(
            return_value=mock_component
        )

        result = await mock_component_tools.patch_component(
            "page123", "comp123", status="operational"
        )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["data"]["status"] == "operational"

    @pytest.mark.asyncio
    async def test_delete_component_success(self, mock_component_tools):
        """Test successful component deletion."""
        mock_component_tools.client.components.delete_component = Mock(
            return_value=True
        )

        result = await mock_component_tools.delete_component("page123", "comp123")

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["message"] == "Component comp123 deleted successfully"


class TestComponentResources:
    """Test cases for ComponentResources."""

    @pytest.fixture
    def mock_component_resources(self, mock_pingera_client):
        """Create ComponentResources instance with mock client."""
        return ComponentResources(mock_pingera_client)

    @pytest.mark.asyncio
    async def test_get_component_groups_resource_success(self, mock_component_resources):
        """Test successful component groups resource retrieval."""
        mock_components = [
            Component(id="group1", name="Infrastructure", group=True),
            Component(id="group2", name="Services", group=True)
        ]

        mock_component_resources.client.components.get_component_groups = Mock(
            return_value=mock_components
        )

        result = await mock_component_resources.get_component_groups_resource("page123")

        result_data = json.loads(result)
        assert result_data["page_id"] == "page123"
        assert len(result_data["component_groups"]) == 2
        assert result_data["component_groups"][0]["name"] == "Infrastructure"

    @pytest.mark.asyncio
    async def test_get_component_groups_resource_error(self, mock_component_resources):
        """Test component groups resource retrieval with error."""
        mock_component_resources.client.components.get_component_groups = Mock(
            side_effect=PingeraError("API Error")
        )

        result = await mock_component_resources.get_component_groups_resource("page123")

        result_data = json.loads(result)
        assert "error" in result_data
        assert "API Error" in result_data["error"]

    @pytest.mark.asyncio
    async def test_get_component_resource_success(self, mock_component_resources):
        """Test successful component resource retrieval."""
        mock_component = Component(
            id="comp123",
            name="API Server",
            status=ComponentStatus.OPERATIONAL,
            description="Main API server"
        )

        mock_component_resources.client.components.get_component = Mock(
            return_value=mock_component
        )

        result = await mock_component_resources.get_component_resource("page123", "comp123")

        result_data = json.loads(result)
        assert result_data["page_id"] == "page123"
        assert result_data["component"]["name"] == "API Server"
        assert result_data["component"]["status"] == "operational"

    @pytest.mark.asyncio
    async def test_get_component_resource_error(self, mock_component_resources):
        """Test component resource retrieval with error."""
        mock_component_resources.client.components.get_component = Mock(
            side_effect=PingeraError("Component not found")
        )

        result = await mock_component_resources.get_component_resource("page123", "comp123")

        result_data = json.loads(result)
        assert "error" in result_data
        assert "Component not found" in result_data["error"]
