import base64
import json

import pytest

from pingera_mcp.context import (
    Credentials,
    credentials_from_headers,
    env_credentials,
    looks_like_jwt,
    read_only_requested,
    tools_requested,
    toolsets_requested,
)


def make_jwt(payload: dict | None = None) -> str:
    def part(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()

    return f"{part({'alg': 'HS256', 'typ': 'JWT'})}.{part(payload or {'sub': 'user'})}.signature"


def test_looks_like_jwt():
    assert looks_like_jwt(make_jwt())
    assert not looks_like_jwt("aed809b8c1f24e51a1f0")
    assert not looks_like_jwt("a.b.c")
    assert not looks_like_jwt("")


@pytest.mark.parametrize(
    "headers, expected",
    [
        ({"authorization": "Bearer api-key-123"}, Credentials("api_key", "api-key-123")),
        ({"authorization": "bearer api-key-123"}, Credentials("api_key", "api-key-123")),
        ({"authorization": "api-key-123"}, Credentials("api_key", "api-key-123")),
        ({"x-api-key": "api-key-123"}, Credentials("api_key", "api-key-123")),
        ({"authorization": "Bearer api-key-1", "x-api-key": "api-key-2"}, Credentials("api_key", "api-key-1")),
        ({"authorization": "Basic dXNlcjpwYXNz", "x-api-key": "api-key-2"}, Credentials("api_key", "api-key-2")),
        ({"authorization": "Bearer "}, None),
        ({}, None),
    ],
)
def test_credentials_from_headers(headers, expected):
    assert credentials_from_headers(headers) == expected


def test_bearer_jwt_is_detected():
    token = make_jwt()
    assert credentials_from_headers({"authorization": f"Bearer {token}"}) == Credentials("jwt", token)


def test_request_auth_and_repr_hide_secret():
    assert Credentials("api_key", "k").request_auth() == {
        "in": "header",
        "key": "Authorization",
        "type": "api_key",
        "value": "k",
    }
    assert Credentials("jwt", "t").request_auth()["value"] == "Bearer t"
    assert "k3y" not in repr(Credentials("api_key", "k3y"))


def test_env_credentials_prefers_jwt():
    assert env_credentials("key", "jwt") == Credentials("jwt", "jwt")
    assert env_credentials("key", None) == Credentials("api_key", "key")
    assert env_credentials(None, None) is None


def test_mode_and_toolset_headers():
    assert read_only_requested({"x-pingera-mode": "read-only"})
    assert read_only_requested({"x-pingera-mode": "READ_ONLY"})
    assert not read_only_requested({"x-pingera-mode": "read_write"})
    assert not read_only_requested({})
    assert toolsets_requested({"x-pingera-toolsets": "checks, alerts,"}) == ["checks", "alerts"]
    assert toolsets_requested({}) is None
    assert tools_requested({"x-pingera-tools": "list_checks,get_check"}) == ["list_checks", "get_check"]
    assert tools_requested({"x-mcp-tools": "list_checks"}) == ["list_checks"]
    assert tools_requested({}) is None
