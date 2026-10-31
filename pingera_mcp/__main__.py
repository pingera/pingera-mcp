"""Command line entry point: `pingera-mcp` or `python -m pingera_mcp`."""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .config import HttpAuth, Mode, Settings, Transport


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pingera-mcp",
        description="Pingera MCP server. Options override the matching environment variables.",
    )
    parser.add_argument("--transport", choices=["stdio", "http"], help="Transport (MCP_TRANSPORT, default stdio)")
    parser.add_argument("--host", help="HTTP bind address (MCP_HOST, default 127.0.0.1)")
    parser.add_argument("--port", type=int, help="HTTP port (MCP_PORT, default 8000)")
    parser.add_argument("--mode", choices=["read_only", "read_write"], help="PINGERA_MODE (default read_only)")
    parser.add_argument("--toolsets", help="Comma-separated toolsets (PINGERA_TOOLSETS, default 'default')")
    parser.add_argument("--tools", help="Comma-separated tool names; overrides --toolsets (PINGERA_TOOLS)")
    parser.add_argument(
        "--http-auth",
        choices=["request", "env"],
        help="HTTP credentials: per request (default) or the server's PINGERA_API_KEY/PINGERA_JWT_TOKEN",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def load_settings(args: argparse.Namespace) -> Settings:
    settings = Settings.from_env()
    if args.transport:
        settings.transport = Transport.parse(args.transport)
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.mode:
        settings.mode = Mode.parse(args.mode, settings.mode)
    if args.toolsets:
        settings.toolsets = [item.strip() for item in args.toolsets.split(",") if item.strip()]
    if args.tools:
        settings.tools = [item.strip() for item in args.tools.split(",") if item.strip()]
    if args.http_auth:
        settings.http_auth = HttpAuth.parse(args.http_auth)
    return settings


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        settings = load_settings(args)
        settings.validate()
    except ValueError as error:
        sys.exit(f"pingera-mcp: {error}")

    # stdout carries the stdio protocol, so logs always go to stderr.
    logging.basicConfig(
        level=settings.log_level,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if settings.transport is Transport.STDIO:
        from .server import create_server

        create_server(settings).run("stdio")
        return

    import uvicorn

    from .server import create_http_app

    uvicorn.run(
        create_http_app(settings),
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
