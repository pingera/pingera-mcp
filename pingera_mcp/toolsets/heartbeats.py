"""Heartbeat (cron job) monitors and their pings."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import HeartbeatsApi
from pingera.models import HeartbeatCheck, HeartbeatCheck1, HeartbeatCheckChannelAssignment
from pydantic import Field

from ..api import api, parse_time
from ..registry import model_tool, tool
from ._types import PageNumber, PageSize, Time

HeartbeatId = Annotated[str, Field(description="Heartbeat ID (see list_heartbeats).")]
_EXCLUDE = {"ping_url", "status", "last_ping_at", "next_expected_ping"}


def _heartbeats():
    return api(HeartbeatsApi)


@tool("heartbeats")
def list_heartbeats(page: PageNumber = None, per_page: PageSize = None) -> Any:
    """List heartbeat monitors with their ping URL, expected period, status and last ping."""
    return _heartbeats().v1_heartbeats_get(page=page, per_page=per_page)


@tool("heartbeats")
def get_heartbeat(heartbeat_id: HeartbeatId) -> Any:
    """Get a heartbeat monitor, including the URL the monitored job must ping."""
    return _heartbeats().v1_heartbeats_check_id_get(check_id=heartbeat_id)


@tool("heartbeats")
def list_heartbeat_pings(
    heartbeat_id: HeartbeatId, start: Time = None, end: Time = None, page: PageNumber = None, per_page: PageSize = None
) -> Any:
    """List the pings a heartbeat received (time, source IP, method, payload)."""
    return _heartbeats().v1_heartbeats_check_id_pings_get(
        check_id=heartbeat_id, start_date=parse_time(start), end_date=parse_time(end), page=page, per_page=per_page
    )


@tool("heartbeats")
def count_heartbeat_pings(heartbeat_id: HeartbeatId, start: Time = None, end: Time = None) -> Any:
    """Count the pings a heartbeat received in a period."""
    return _heartbeats().v1_heartbeats_check_id_pings_count_get(
        check_id=heartbeat_id, start_date=parse_time(start), end_date=parse_time(end)
    )


model_tool(
    "heartbeats",
    "create_heartbeat",
    model=HeartbeatCheck,
    exclude=_EXCLUDE,
    call=lambda body: _heartbeats().v1_heartbeats_post(heartbeat_check=body),
    description=(
        "Create a heartbeat monitor for a cron job or worker. The response has the `ping_url` the job must call "
        "every `period_seconds`; it goes down after `grace_seconds` without a ping."
    ),
)

model_tool(
    "heartbeats",
    "update_heartbeat",
    model=HeartbeatCheck1,
    partial=True,
    exclude=_EXCLUDE,
    path=[("heartbeat_id", "ID of the heartbeat.")],
    call=lambda body, heartbeat_id: _heartbeats().v1_heartbeats_check_id_patch(check_id=heartbeat_id, heartbeat_check1=body),
    idempotent=True,
    description="Change a heartbeat monitor; pause or resume it with `active`. Only the fields you pass are changed.",
)


@tool("heartbeats", access="write", destructive=True, idempotent=True)
def delete_heartbeat(heartbeat_id: HeartbeatId) -> Any:
    """Delete a heartbeat monitor and its ping history."""
    return _heartbeats().v1_heartbeats_check_id_delete(check_id=heartbeat_id)


@tool("heartbeats", access="write")
def send_heartbeat_ping(heartbeat_id: HeartbeatId) -> Any:
    """Send a ping to a heartbeat, as the monitored job would, e.g. to test the setup.

    This records a real ping: a heartbeat that is down is marked up again.
    """
    return _heartbeats().v1_heartbeats_check_id_ping_get(check_id=heartbeat_id)


@tool("heartbeats")
def list_heartbeat_channels(heartbeat_id: HeartbeatId) -> Any:
    """List the alert channels notified when a heartbeat goes down."""
    return _heartbeats().v1_heartbeats_check_id_channels_get(check_id=heartbeat_id)


@tool("heartbeats", access="write", idempotent=True)
def set_heartbeat_channels(
    heartbeat_id: HeartbeatId,
    channel_ids: Annotated[
        list[str], Field(description="All alert channel IDs to notify (see list_alert_channels); replaces the current list.")
    ],
) -> Any:
    """Set the alert channels notified when a heartbeat goes down, replacing the current ones."""
    return _heartbeats().v1_heartbeats_check_id_channels_post(
        check_id=heartbeat_id,
        heartbeat_check_channel_assignment=HeartbeatCheckChannelAssignment(channel_ids=channel_ids),
    )


@tool("heartbeats", access="write", idempotent=True)
def remove_heartbeat_channel(
    heartbeat_id: HeartbeatId, channel_id: Annotated[str, Field(description="Alert channel ID.")]
) -> Any:
    """Stop notifying an alert channel about a heartbeat."""
    return _heartbeats().v1_heartbeats_check_id_channels_channel_id_delete(check_id=heartbeat_id, channel_id=channel_id)
