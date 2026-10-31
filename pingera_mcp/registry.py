"""Tool registry: tools are grouped into toolsets and tagged with the kind of access they need.

Tools that create or change Pingera objects are generated from the SDK's request models, so their
input schemas (fields, descriptions, constraints and enum values) follow the SDK.
"""

from __future__ import annotations

import functools
import inspect
import json
import re
import types
from dataclasses import dataclass
from typing import Annotated, Any, Callable, Literal, Optional, Union, get_args, get_origin

from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field, ValidationError, create_model

from .api import PingeraToolError, format_validation_error
from .context import current_scope

Access = Literal["read", "run", "write"]
"""read: only reads data. run: runs checks or sends test messages without changing configuration.
write: creates, changes or deletes data (hidden in read-only mode)."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    fn: Callable[..., str]
    toolset: str
    access: Access
    destructive: bool
    idempotent: bool
    title: str

    @property
    def allowed_in_read_only(self) -> bool:
        return self.access != "write"


TOOLS: dict[str, ToolSpec] = {}


def compact(value: Any) -> Any:
    """Drop null fields: API objects carry many unset optional fields that only cost the model tokens."""
    if isinstance(value, dict):
        return {key: compact(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [compact(item) for item in value]
    return value


def to_text(result: Any) -> str:
    if isinstance(result, str):
        return result
    return json.dumps(compact(result), ensure_ascii=False, indent=1, default=str)


def _wrap(fn: Callable[..., Any], name: str) -> Callable[..., str]:
    @functools.wraps(fn)
    def wrapper(**kwargs: Any) -> str:
        scope = current_scope()
        spec = TOOLS[name]
        if scope is not None and not scope.allows(spec):
            if scope.read_only and not spec.allowed_in_read_only:
                raise ToolError(f"{name} changes data and this session is read-only.")
            if scope.tools is not None:
                raise ToolError(f"{name} is not among the tools enabled for this session.")
            raise ToolError(f"{name} belongs to the '{spec.toolset}' toolset, which is not enabled for this session.")
        try:
            return to_text(fn(**kwargs))
        except PingeraToolError as error:
            raise ToolError(str(error)) from error
        except ValidationError as error:
            raise ToolError(format_validation_error(error)) from error

    return wrapper


def _title(name: str) -> str:
    return name.replace("_", " ").capitalize()


def register(
    fn: Callable[..., Any],
    *,
    toolset: str,
    access: Access = "read",
    destructive: bool = False,
    idempotent: bool | None = None,
    name: str | None = None,
    title: str | None = None,
) -> ToolSpec:
    tool_name = name or fn.__name__
    if tool_name in TOOLS:
        raise ValueError(f"Duplicate tool {tool_name!r}")
    if not (fn.__doc__ or "").strip():
        raise ValueError(f"Tool {tool_name!r} needs a description")
    spec = ToolSpec(
        name=tool_name,
        fn=_wrap(fn, tool_name),
        toolset=toolset,
        access=access,
        destructive=destructive,
        idempotent=access == "read" if idempotent is None else idempotent,
        title=title or _title(tool_name),
    )
    TOOLS[tool_name] = spec
    return spec


def tool(
    toolset: str,
    *,
    access: Access = "read",
    destructive: bool = False,
    idempotent: bool | None = None,
    title: str | None = None,
):
    """Register a hand-written tool. Its signature and docstring become the MCP tool schema."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        register(fn, toolset=toolset, access=access, destructive=destructive, idempotent=idempotent, title=title)
        return fn

    return decorator


# --- Tools generated from SDK request models ---------------------------------------------------

_SENTINEL = "\x00not-an-enum-value\x00"
MAX_SCHEMA_ENUM = 40
"""Longer enums (e.g. every IANA timezone) are described instead of listed; the SDK still validates them."""
_ENUM_VALUES = re.compile(r"enum values \((.*)\)")


def readonly_fields(model: type[BaseModel]) -> set[str]:
    """Fields the SDK never sends (ids, timestamps...), as listed in the generated to_dict()."""
    try:
        source = inspect.getsource(model.to_dict)  # type: ignore[attr-defined]
    except (AttributeError, OSError, TypeError):
        return set()
    match = re.search(r"excluded_fields: Set\[str\] = set\(\[(.*?)\]\)", source, re.S)
    return set(re.findall(r'"([^"]+)"', match.group(1))) if match else set()


def enum_values(model: type[BaseModel]) -> dict[str, list[str]]:
    """Allowed values of enum fields, taken from the SDK's generated validators."""
    found: dict[str, list[str]] = {}
    for decorator in model.__pydantic_decorators__.field_validators.values():
        if not decorator.func.__name__.endswith("_validate_enum"):
            continue
        for probe in (_SENTINEL, [_SENTINEL]):
            try:
                decorator.func(probe)
            except ValueError as error:
                match = _ENUM_VALUES.search(str(error))
                if match:
                    values = re.findall(r"'([^']*)'", match.group(1))
                    for field_name in decorator.info.fields:
                        found[field_name] = values
                    break
            except Exception:  # noqa: BLE001 - a probe of the wrong shape; try the next one
                continue
    return found


def _strip_optional(annotation: Any) -> Any:
    if get_origin(annotation) in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return args[0]
    return annotation


_INPUT_MODELS: dict[type[BaseModel], type[BaseModel]] = {}


def input_model(model: type[BaseModel]) -> type[BaseModel]:
    """A copy of a nested SDK model without its read-only fields, for tool input schemas."""
    if model not in _INPUT_MODELS:
        skip = readonly_fields(model)
        fields: dict[str, Any] = {}
        for field_name, info in model.model_fields.items():
            if field_name in skip:
                continue
            annotation = input_annotation(info.annotation)
            field = Field(default=None if not info.is_required() else ..., description=info.description)
            fields[field_name] = (Annotated[tuple([annotation, *info.metadata])] if info.metadata else annotation, field)  # type: ignore[misc]
        _INPUT_MODELS[model] = create_model(f"{model.__name__}Input", __doc__=model.__doc__, **fields)
    return _INPUT_MODELS[model]


def input_annotation(annotation: Any) -> Any:
    """Replace nested SDK models in an annotation with their input-only copies."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return input_model(annotation)
    origin = get_origin(annotation)
    if origin is None:
        return annotation
    args = get_args(annotation)
    if origin is Annotated:
        return Annotated[tuple([input_annotation(args[0]), *args[1:]])]  # type: ignore[misc]
    converted = tuple(input_annotation(arg) for arg in args)
    if converted == args:
        return annotation
    if origin in (Union, types.UnionType):
        return Union[converted]  # type: ignore[return-value]
    return origin[converted]


def _plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, exclude_none=True)
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


def _with_enum(annotation: Any, values: list[str]) -> Any:
    literal = Literal[tuple(values)]  # type: ignore[valid-type]
    base = _strip_optional(annotation)
    if get_origin(base) is Annotated:
        base = get_args(base)[0]
    return list[literal] if get_origin(base) is list else literal


def model_parameters(
    model: type[BaseModel],
    *,
    partial: bool,
    exclude: set[str] = frozenset(),
    descriptions: dict[str, str] | None = None,
    required: set[str] = frozenset(),
) -> list[inspect.Parameter]:
    """Keyword parameters mirroring the writable fields of an SDK model."""
    skip = readonly_fields(model) | set(exclude)
    enums = enum_values(model)
    descriptions = descriptions or {}
    parameters = []
    for field_name, info in model.model_fields.items():
        if field_name in skip:
            continue
        description = descriptions.get(field_name, info.description or "")
        values = enums.get(field_name)
        if values and len(values) <= MAX_SCHEMA_ENUM:
            base = _with_enum(info.annotation, values)
        else:
            base = _strip_optional(input_annotation(info.annotation))
            if info.metadata:
                base = Annotated[tuple([base, *info.metadata])]  # type: ignore[misc]
            if values:
                description += f" One of {len(values)} allowed values, e.g. {', '.join(values[:5])}."
        is_required = (info.is_required() and not partial) or field_name in required
        annotated = Annotated[base if is_required else Optional[base], Field(description=description)]
        parameters.append(
            inspect.Parameter(
                field_name,
                inspect.Parameter.KEYWORD_ONLY,
                annotation=annotated,
                default=inspect.Parameter.empty if is_required else None,
            )
        )
    return sorted(parameters, key=lambda p: p.default is not inspect.Parameter.empty)


def model_tool(
    toolset: str,
    name: str,
    *,
    model: type[BaseModel],
    call: Callable[..., Any],
    description: str,
    path: list[tuple[str, str]] | None = None,
    partial: bool = False,
    exclude: set[str] = frozenset(),
    descriptions: dict[str, str] | None = None,
    required: set[str] = frozenset(),
    advanced: set[str] = frozenset(),
    access: Access = "write",
    destructive: bool = False,
    idempotent: bool = False,
    title: str | None = None,
) -> ToolSpec:
    """Register a tool whose arguments are path IDs plus the fields of an SDK request model.

    `call(body, **path_ids)` sends the request. With `partial=True` (updates) every field is
    optional and only the fields that were passed are sent. Rarely used fields listed in
    `advanced` are taken from a single `advanced` object argument to keep the schema small.
    """
    path = path or []
    path_parameters = [
        inspect.Parameter(
            path_name,
            inspect.Parameter.KEYWORD_ONLY,
            annotation=Annotated[str, Field(description=path_description)],
        )
        for path_name, path_description in path
    ]
    body_parameters = model_parameters(
        model, partial=partial, exclude=set(exclude) | set(advanced), descriptions=descriptions, required=required
    )
    if advanced:
        listed = "; ".join(
            f"{field_name}: {model.model_fields[field_name].description or ''}".rstrip(": ")
            for field_name in model.model_fields
            if field_name in advanced
        )
        body_parameters.append(
            inspect.Parameter(
                "advanced",
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Annotated[
                    Optional[dict[str, Any]], Field(description=f"Rarely needed fields, as an object. Allowed keys - {listed}.")
                ],
                default=None,
            )
        )
    aliases = {field_name: (info.alias or field_name) for field_name, info in model.model_fields.items()}

    def implementation(**kwargs: Any) -> Any:
        ids = {path_name: kwargs.pop(path_name) for path_name, _ in path}
        extra = kwargs.pop("advanced", None) or {}
        unknown = sorted(set(extra) - set(advanced))
        if unknown:
            raise PingeraToolError(f"Unknown keys in advanced: {', '.join(unknown)}. Allowed: {', '.join(sorted(advanced))}.")
        kwargs.update(extra)
        values = {aliases[key]: _plain(value) for key, value in kwargs.items() if value is not None}
        if partial and not values:
            raise PingeraToolError("Nothing to change: pass at least one field to update.")
        return call(model.model_validate(values), **ids)

    implementation.__name__ = name
    implementation.__qualname__ = name
    implementation.__doc__ = description
    implementation.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        [*path_parameters, *body_parameters], return_annotation=str
    )
    return register(
        implementation,
        toolset=toolset,
        access=access,
        destructive=destructive,
        idempotent=idempotent,
        name=name,
        title=title,
    )
