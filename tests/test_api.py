from datetime import datetime, timedelta, timezone

import pytest

from pingera_mcp import api
from pingera_mcp.api import PingeraApiError, PingeraToolError, parse_time
from pingera_mcp.context import Credentials, RequestScope, reset_scope, set_scope


def test_parse_time():
    now = datetime.now(timezone.utc)
    assert parse_time(None) is None
    assert parse_time("") is None
    assert abs(parse_time("now") - now) < timedelta(seconds=5)
    assert abs(parse_time("24h") - (now - timedelta(hours=24))) < timedelta(seconds=5)
    assert abs(parse_time("7d ago") - (now - timedelta(days=7))) < timedelta(seconds=5)
    assert parse_time("2026-01-31T12:00:00Z") == datetime(2026, 1, 31, 12, tzinfo=timezone.utc)
    assert parse_time("2026-01-31").tzinfo is timezone.utc
    with pytest.raises(PingeraToolError, match="Invalid time"):
        parse_time("yesterday")


@pytest.fixture
def scope():
    def use(credentials: Credentials | None):
        token = set_scope(RequestScope(credentials=credentials, read_only=False, toolsets=frozenset()))
        tokens.append(token)

    tokens = []
    yield use
    for token in reversed(tokens):
        reset_scope(token)


def test_api_sends_request_credentials_and_parses_json(fake_api, settings, scope):
    from pingera.api import ChecksApi

    fake_api.route("GET", "/v1/checks", body={"checks": [{"id": "c1"}]})
    api.configure(settings)

    scope(Credentials("api_key", "key-1"))
    assert api.api(ChecksApi).v1_checks_get(page=2, name=None) == {"checks": [{"id": "c1"}]}
    request = fake_api.last("/v1/checks")
    assert request.headers["authorization"] == "key-1"
    assert "page=2" in request.path and "name" not in request.path
    assert request.headers["user-agent"].startswith("pingera-mcp/")

    scope(Credentials("jwt", "token-1"))
    api.api(ChecksApi).v1_checks_get()
    assert fake_api.last("/v1/checks").headers["authorization"] == "Bearer token-1"


def test_api_errors(fake_api, settings, scope):
    from pingera.api import ChecksApi

    fake_api.route("GET", "/v1/checks/missing", status=404, body={"message": "Check not found."})
    fake_api.route("DELETE", "/v1/checks/c1", status=204)
    api.configure(settings)
    scope(Credentials("api_key", "key"))

    with pytest.raises(PingeraApiError) as error:
        api.api(ChecksApi).v1_checks_check_id_get(check_id="missing")
    assert error.value.status == 404
    assert str(error.value).startswith("Pingera API error (HTTP 404): Check not found. Not found.")

    assert api.api(ChecksApi).v1_checks_check_id_delete(check_id="c1") == {"success": True}


def test_api_without_credentials(settings, scope):
    from pingera.api import ChecksApi

    api.configure(settings)
    scope(None)
    with pytest.raises(PingeraToolError, match="No Pingera credentials"):
        api.api(ChecksApi)


def test_unreachable_api(scope):
    from pingera.api import ChecksApi
    from pingera_mcp.config import Settings

    api.configure(Settings(base_url="http://127.0.0.1:9", max_retries=0, timeout=2))
    scope(Credentials("api_key", "key"))
    with pytest.raises(PingeraToolError, match="Could not reach"):
        api.api(ChecksApi).v1_checks_get()
