import pytest

from pingera_mcp.config import DEFAULT_BASE_URL, HttpAuth, Mode, Settings, Transport


def test_defaults():
    settings = Settings.from_env({})
    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.mode is Mode.READ_ONLY
    assert settings.transport is Transport.STDIO
    assert settings.http_auth is HttpAuth.REQUEST
    assert settings.toolsets == ["default"]
    assert (settings.host, settings.port, settings.path) == ("127.0.0.1", 8000, "/mcp")


def test_from_env():
    settings = Settings.from_env(
        {
            "PINGERA_API_KEY": "key",
            "PINGERA_BASE_URL": "https://api.example.com/v1/",
            "PINGERA_MODE": "read-only",
            "PINGERA_TOOLSETS": "checks, alerts",
            "PINGERA_TOOLS": "list_checks,get_check",
            "MCP_TRANSPORT": "streamable-http",
            "MCP_HOST": "0.0.0.0",
            "MCP_PORT": "9000",
            "MCP_HTTP_AUTH": "env",
            "MCP_ALLOWED_HOSTS": "mcp.example.com, localhost:*",
            "PINGERA_DEBUG": "true",
        }
    )
    assert settings.base_url == "https://api.example.com"
    assert settings.mode is Mode.READ_ONLY
    assert settings.toolsets == ["checks", "alerts"]
    assert settings.tools == ["list_checks", "get_check"]
    assert settings.transport is Transport.HTTP
    assert (settings.host, settings.port) == ("0.0.0.0", 9000)
    assert settings.http_auth is HttpAuth.ENV
    assert settings.allowed_hosts == ["mcp.example.com", "localhost:*"]
    assert settings.log_level == "DEBUG"


def test_mcp_mode_alias():
    assert Settings.from_env({"MCP_MODE": "read-write"}).mode is Mode.READ_WRITE
    assert Settings.from_env({"MCP_MODE": "read_write", "PINGERA_MODE": "read_only"}).mode is Mode.READ_ONLY


@pytest.mark.parametrize(
    "env",
    [{"PINGERA_MODE": "admin"}, {"MCP_TRANSPORT": "sse"}, {"MCP_HTTP_AUTH": "none"}],
)
def test_invalid_values(env):
    with pytest.raises(ValueError):
        Settings.from_env(env)


def test_validate_requires_credentials_when_server_uses_its_own():
    with pytest.raises(ValueError, match="stdio"):
        Settings(transport=Transport.STDIO).validate()
    with pytest.raises(ValueError, match="MCP_HTTP_AUTH=env"):
        Settings(transport=Transport.HTTP, http_auth=HttpAuth.ENV).validate()
    Settings(transport=Transport.HTTP).validate()
    Settings(transport=Transport.STDIO, jwt_token="jwt").validate()
