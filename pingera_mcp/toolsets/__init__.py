"""Toolsets group related tools so a deployment (or a single client) can expose only what it needs."""

from __future__ import annotations

import importlib

CORE_TOOLSET = "core"
"""Always enabled: connection check and reference documentation."""

TOOLSETS: dict[str, str] = {
    CORE_TOOLSET: "Connection check and reference documentation (always enabled)",
    "account": "Organization details and usage",
    "pages": "Status pages",
    "components": "Status page components, component groups and component uptime",
    "incidents": "Status page incidents, incident updates, scheduled maintenance and postmortems",
    "checks": "Monitoring checks: configuration, regions and on-demand runs",
    "results": "Check results, uptime, response times, status history and multi-region executions",
    "alerts": "Alerts, alert rules and alert channels",
    "heartbeats": "Heartbeat (cron job) monitors and their pings",
    "check_groups": "Check groups",
    "secrets": "Organization secrets and the secrets injected into checks",
    "page_access": "Status page passwords and custom sender email domains",
    "private_locations": "Private locations and runner tokens for self-hosted check runners",
    "reports": "PDF uptime reports",
    "audit": "Organization audit log",
}

DEFAULT_TOOLSETS: tuple[str, ...] = (
    "account",
    "pages",
    "components",
    "incidents",
    "checks",
    "results",
    "alerts",
)

_loaded = False


def load_all() -> None:
    """Import every toolset module so its tools are registered."""
    global _loaded
    if _loaded:
        return
    for name in TOOLSETS:
        importlib.import_module(f"{__name__}.{name}")
    _loaded = True


def resolve(names: list[str] | tuple[str, ...]) -> frozenset[str]:
    """Expand toolset names; 'default' and 'all' are accepted. Unknown names raise ValueError."""
    selected: set[str] = {CORE_TOOLSET}
    for raw in names:
        name = raw.strip().lower()
        if name == "all":
            selected.update(TOOLSETS)
        elif name == "default":
            selected.update(DEFAULT_TOOLSETS)
        elif name in TOOLSETS:
            selected.add(name)
        else:
            known = ", ".join(["default", "all", *TOOLSETS])
            raise ValueError(f"Unknown toolset {raw!r}. Known toolsets: {known}")
    return frozenset(selected)
