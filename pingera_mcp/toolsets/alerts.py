"""Alerts, alert rules and alert channels."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pingera.api import AlertsApi
from pingera.models import AlertChannel, AlertChannel1, AlertChannelTestRequest, AlertRule, AlertRule1
from pydantic import Field

from .. import reference
from ..api import api
from ..registry import model_tool, tool
from ._types import PageNumber, PageSize

AlertId = Annotated[str, Field(description="Alert ID (see list_alerts).")]
RuleId = Annotated[str, Field(description="Alert rule ID (see list_alert_rules).")]
ChannelId = Annotated[str, Field(description="Alert channel ID (see list_alert_channels).")]

_RULE_DESCRIPTIONS = {
    "condition_parameters": reference.ALERT_RULE_CONDITIONS_SHORT,
    "channel_ids": "Alert channels to notify (see list_alert_channels). At least one when creating a rule.",
}
_RULE_EXCLUDE = {"check_name", "channels"}
_CHANNEL_DESCRIPTIONS = {"configuration": reference.CHANNEL_CONFIGURATION_SHORT}
_CHANNEL_EXCLUDE = {"last_used_at"}


def _alerts():
    return api(AlertsApi)


@tool("alerts")
def list_alerts(
    status: Annotated[
        Literal["active", "firing", "acknowledged", "resolved", "suppressed"] | None,
        Field(description="'active' means firing or acknowledged."),
    ] = None,
    check_id: Annotated[str | None, Field(description="Only alerts of this check.")] = None,
    severity: Literal["low", "medium", "high", "critical"] | None = None,
    page: PageNumber = None,
    per_page: PageSize = None,
) -> Any:
    """List fired alerts, newest first, with their check, rule, severity and status."""
    return _alerts().v1_alerts_get(status=status, check_id=check_id, severity=severity, page=page, per_page=per_page)


@tool("alerts")
def get_alert(alert_id: AlertId) -> Any:
    """Get an alert with its rule, check, timeline and the results that triggered it."""
    return _alerts().v1_alerts_alert_id_get(alert_id=alert_id)


@tool("alerts")
def list_alert_notifications(alert_id: AlertId) -> Any:
    """List the notifications sent for an alert, per channel, with delivery status and errors."""
    return _alerts().v1_alerts_alert_id_notifications_get(alert_id=alert_id)


@tool("alerts")
def get_alert_stats() -> Any:
    """Get alert statistics: active and recent alerts, severity breakdown and enabled rules and channels."""
    return _alerts().v1_alerts_stats_get()


@tool("alerts", access="write", idempotent=True)
def acknowledge_alert(alert_id: AlertId) -> Any:
    """Acknowledge a firing alert (someone is working on it)."""
    return _alerts().v1_alerts_alert_id_acknowledge_post(alert_id=alert_id)


@tool("alerts", access="write", idempotent=True)
def resolve_alert(alert_id: AlertId) -> Any:
    """Resolve an active alert manually."""
    return _alerts().v1_alerts_alert_id_resolve_post(alert_id=alert_id)


@tool("alerts")
def list_alert_rules() -> Any:
    """List alert rules: which check each watches, the trigger condition, severity and channels."""
    return _alerts().v1_alerts_rules_get()


@tool("alerts")
def get_alert_rule(rule_id: RuleId) -> Any:
    """Get an alert rule: its check, condition, severity, multi-region mode and channels."""
    return _alerts().v1_alerts_rules_rule_id_get(rule_id=rule_id)


model_tool(
    "alerts",
    "create_alert_rule",
    model=AlertRule,
    exclude=_RULE_EXCLUDE,
    descriptions=_RULE_DESCRIPTIONS,
    call=lambda body: _alerts().v1_alerts_rules_post(alert_rule=body),
    description=(
        "Create an alert rule that notifies channels when a check meets a condition, e.g. condition "
        "'consecutive_failures' with condition_parameters {'count': 3}. See get_reference('alerts')."
    ),
)

model_tool(
    "alerts",
    "update_alert_rule",
    model=AlertRule1,
    partial=True,
    exclude=_RULE_EXCLUDE | {"check_id"},
    descriptions=_RULE_DESCRIPTIONS,
    path=[("rule_id", "ID of the alert rule.")],
    call=lambda body, rule_id: _alerts().v1_alerts_rules_rule_id_put(rule_id=rule_id, alert_rule1=body),
    idempotent=True,
    description="Change an alert rule; enable or pause it with `enabled`. Only the fields you pass are changed.",
)


@tool("alerts", access="write", destructive=True, idempotent=True)
def delete_alert_rule(rule_id: RuleId) -> Any:
    """Delete an alert rule and its alert history."""
    return _alerts().v1_alerts_rules_rule_id_delete(rule_id=rule_id)


@tool("alerts")
def list_alert_channels() -> Any:
    """List alert channels (email, webhook, Telegram, MAX, SMS, status page); secrets are masked."""
    return _alerts().v1_alerts_channels_get()


@tool("alerts")
def get_alert_channel(channel_id: ChannelId) -> Any:
    """Get an alert channel and its configuration (secrets masked)."""
    return _alerts().v1_alerts_channels_channel_id_get(channel_id=channel_id)


model_tool(
    "alerts",
    "create_alert_channel",
    model=AlertChannel,
    exclude=_CHANNEL_EXCLUDE,
    descriptions=_CHANNEL_DESCRIPTIONS,
    call=lambda body: _alerts().v1_alerts_channels_post(alert_channel=body),
    description="Create an alert channel. Try the settings first with test_alert_channel_settings.",
)

model_tool(
    "alerts",
    "update_alert_channel",
    model=AlertChannel1,
    partial=True,
    exclude=_CHANNEL_EXCLUDE | {"type"},
    descriptions=_CHANNEL_DESCRIPTIONS,
    path=[("channel_id", "ID of the alert channel.")],
    call=lambda body, channel_id: _alerts().v1_alerts_channels_channel_id_put(channel_id=channel_id, alert_channel1=body),
    idempotent=True,
    description="Change an alert channel. Only the fields you pass are changed; `configuration` replaces the whole object.",
)


@tool("alerts", access="write", destructive=True, idempotent=True)
def delete_alert_channel(channel_id: ChannelId) -> Any:
    """Delete an alert channel. It must not be used by any alert rule."""
    return _alerts().v1_alerts_channels_channel_id_delete(channel_id=channel_id)


@tool("alerts", access="run")
def test_alert_channel(channel_id: ChannelId) -> Any:
    """Send a test notification through a saved channel (email, webhook, Telegram and MAX channels)."""
    return _alerts().v1_alerts_channels_channel_id_test_post(channel_id=channel_id)


model_tool(
    "alerts",
    "test_alert_channel_settings",
    model=AlertChannelTestRequest,
    exclude=_CHANNEL_EXCLUDE | {"enabled"},
    descriptions=_CHANNEL_DESCRIPTIONS,
    call=lambda body: _alerts().v1_alerts_channels_test_post(alert_channel_test_request=body),
    access="run",
    description="Send a test notification using channel settings that are not saved yet.",
)
