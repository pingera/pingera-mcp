"""Private locations and runner tokens for self-hosted check runners."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import PrivateLocationsApi
from pingera.models import PrivateLocationCreate, PrivateLocationUpdate, RunnerTokenCreate
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool

LocationId = Annotated[str, Field(description="Private location ID (see list_private_locations).")]


@tool("private_locations")
def list_private_locations() -> Any:
    """List private locations (self-hosted runners) with their status, check types and connected runners."""
    return api(PrivateLocationsApi).v1_private_locations_get()


@tool("private_locations")
def get_private_location(location_id: LocationId) -> Any:
    """Get a private location, its runners and runner tokens."""
    return api(PrivateLocationsApi).v1_private_locations_location_id_get(location_id=location_id)


model_tool(
    "private_locations",
    "create_private_location",
    model=PrivateLocationCreate,
    call=lambda body: api(PrivateLocationsApi).v1_private_locations_post(private_location_create=body),
    description=(
        "Create a private location so checks can run on your own infrastructure. Then create a runner token and "
        "start a runner with it; the location appears in list_check_regions."
    ),
)

model_tool(
    "private_locations",
    "update_private_location",
    model=PrivateLocationUpdate,
    partial=True,
    path=[("location_id", "ID of the private location.")],
    call=lambda body, location_id: api(PrivateLocationsApi).v1_private_locations_location_id_patch(
        location_id=location_id, private_location_update=body
    ),
    idempotent=True,
    description="Rename, enable/disable or change the check types of a private location.",
)


@tool("private_locations", access="write", destructive=True, idempotent=True)
def delete_private_location(location_id: LocationId) -> Any:
    """Delete a private location. Checks can no longer run there."""
    return api(PrivateLocationsApi).v1_private_locations_location_id_delete(location_id=location_id)


@tool("private_locations", access="write")
def create_runner_token(
    location_id: LocationId, name: Annotated[str, Field(description="Label for the token, e.g. the runner host.")]
) -> Any:
    """Create a token a runner uses to connect to a private location. The token is shown only once."""
    return api(PrivateLocationsApi).v1_private_locations_location_id_tokens_post(
        location_id=location_id, runner_token_create=RunnerTokenCreate(name=name)
    )


@tool("private_locations", access="write", destructive=True, idempotent=True)
def revoke_runner_token(location_id: LocationId, token_id: Annotated[str, Field(description="Runner token ID.")]) -> Any:
    """Revoke a runner token; runners using it are disconnected."""
    return api(PrivateLocationsApi).v1_private_locations_location_id_tokens_token_id_delete(
        location_id=location_id, token_id=token_id
    )
