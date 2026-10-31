import inspect
import json
from typing import get_args

import pytest
from mcp.server.mcpserver.exceptions import ToolError
from pingera.models import AlertRule, MonitorCheck, MonitorCheck1, Page

from pingera_mcp import toolsets
from pingera_mcp.registry import (
    MAX_SCHEMA_ENUM,
    TOOLS,
    compact,
    enum_values,
    input_model,
    model_parameters,
    readonly_fields,
    to_text,
)

toolsets.load_all()


def test_readonly_fields_come_from_sdk_to_dict():
    readonly = readonly_fields(MonitorCheck)
    assert {"id", "status", "created_at", "updated_at"} <= readonly
    assert "name" not in readonly


def test_enum_values_come_from_sdk_validators():
    enums = enum_values(MonitorCheck)
    assert enums["type"] == ["web", "api", "ssl", "tcp", "synthetic", "multistep", "icmp", "dns", "portscan"]
    assert enums["scheduling_type"] == ["interval", "cron"]
    assert set(enum_values(AlertRule)["severity"]) >= {"low", "critical"}


def test_model_parameters_for_create_and_update():
    create = {p.name: p for p in model_parameters(MonitorCheck, partial=False)}
    assert "id" not in create and "status" not in create
    assert create["name"].default is inspect.Parameter.empty
    assert create["url"].default is None

    update = {p.name: p for p in model_parameters(MonitorCheck1, partial=True)}
    assert all(p.default is None for p in update.values())


def test_large_enums_are_described_not_listed():
    assert len(enum_values(Page)["time_zone"]) > MAX_SCHEMA_ENUM
    parameter = {p.name: p for p in model_parameters(Page, partial=True)}["time_zone"]
    field = get_args(parameter.annotation)[1]
    assert "allowed values" in field.description


def test_input_model_drops_readonly_nested_fields():
    from pingera.models import CheckSecret

    model = input_model(CheckSecret)
    assert set(model.model_fields) == {"env_variable", "secret_id"}


def test_every_tool_is_documented_and_classified():
    assert len(TOOLS) > 100
    for spec in TOOLS.values():
        assert spec.toolset in toolsets.TOOLSETS, spec.name
        assert spec.access in ("read", "run", "write")
        assert spec.fn.__doc__ and len(spec.fn.__doc__) > 20, spec.name
        if spec.destructive:
            assert spec.access == "write", spec.name
        if spec.name.startswith(("create_", "update_", "delete_")):
            assert spec.access == "write", spec.name
        if spec.name.startswith(("list_", "get_")):
            assert spec.access == "read", spec.name


def test_compact_and_to_text():
    data = {"a": 1, "b": None, "c": [{"d": None, "e": 2}], "f": {"g": None}}
    assert compact(data) == {"a": 1, "c": [{"e": 2}], "f": {}}
    assert json.loads(to_text(data)) == compact(data)
    assert to_text("plain") == "plain"


def test_update_tool_requires_a_field():
    with pytest.raises(ToolError, match="Nothing to change"):
        TOOLS["update_check"].fn(check_id="abc")


def test_advanced_rejects_unknown_keys():
    with pytest.raises(ToolError, match="Unknown keys in advanced"):
        TOOLS["update_status_page"].fn(page_id="p", advanced={"nope": 1})


def test_resolve_toolsets():
    assert toolsets.resolve(["default"]) == frozenset({"core", *toolsets.DEFAULT_TOOLSETS})
    assert toolsets.resolve(["all"]) == frozenset(toolsets.TOOLSETS)
    assert toolsets.resolve(["checks"]) == frozenset({"core", "checks"})
    with pytest.raises(ValueError, match="Unknown toolset"):
        toolsets.resolve(["nope"])
