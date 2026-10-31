"""Shared fixtures: a fake Pingera API and a Pingera MCP server running over HTTP."""

from __future__ import annotations

import json
import socket
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

import httpx2
import pytest
import uvicorn
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from pingera_mcp.config import Mode, Settings, Transport


@dataclass
class RecordedRequest:
    method: str
    path: str
    headers: dict[str, str]
    body: Any


@dataclass
class FakePingeraApi:
    """Answers Pingera API calls from `routes` and records every request."""

    url: str = ""
    requests: list[RecordedRequest] = field(default_factory=list)
    routes: dict[tuple[str, str], Callable[[RecordedRequest], tuple[int, Any]]] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def route(self, method: str, path: str, status: int = 200, body: Any = None, handler=None) -> None:
        self.routes[(method, path)] = handler or (lambda request: (status, body))

    def last(self, path: str | None = None) -> RecordedRequest:
        matching = [r for r in self.requests if path is None or r.path.split("?")[0] == path]
        assert matching, f"no request to {path}"
        return matching[-1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def fake_api():
    api = FakePingeraApi()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silence the default stderr logging
            pass

        def _handle(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            request = RecordedRequest(
                method=self.command,
                path=self.path,
                headers={key.lower(): value for key, value in self.headers.items()},
                body=json.loads(raw) if raw else None,
            )
            with api.lock:
                api.requests.append(request)
            handler = api.routes.get((self.command, self.path.split("?")[0]))
            status, body = handler(request) if handler else (404, {"message": f"no route for {self.path}"})
            payload = b"" if body is None else json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = do_POST = do_PATCH = do_PUT = do_DELETE = _handle

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    api.url = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield api
    server.shutdown()


@pytest.fixture
def settings(fake_api) -> Settings:
    return Settings(base_url=fake_api.url, max_retries=0, timeout=10, mode=Mode.READ_WRITE)


class RunningServer:
    def __init__(self, url: str):
        self.url = url
        self.base = url.rsplit("/", 1)[0]

    @asynccontextmanager
    async def client(self, headers: dict[str, str] | None = None):
        async with httpx2.AsyncClient(headers=headers or {}, timeout=30) as http:
            async with Client(streamable_http_client(self.url, http_client=http)) as client:
                yield client


@pytest.fixture
def http_server(settings):
    """Start the HTTP app (per-request credentials unless the test changes `settings`) on a free port."""
    from pingera_mcp.server import create_http_app

    def start(**overrides) -> RunningServer:
        for key, value in overrides.items():
            setattr(settings, key, value)
        settings.transport = Transport.HTTP
        port = _free_port()
        config = uvicorn.Config(create_http_app(settings), host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        deadline = time.time() + 10
        while not server.started:
            if time.time() > deadline:
                raise RuntimeError("MCP server did not start")
            time.sleep(0.05)
        servers.append((server, thread))
        return RunningServer(f"http://127.0.0.1:{port}{settings.path}")

    servers: list[tuple[uvicorn.Server, threading.Thread]] = []
    yield start
    for server, thread in servers:
        server.should_exit = True
        thread.join(timeout=10)


async def call(client: Client, tool: str, **arguments: Any) -> tuple[bool, str]:
    result = await client.call_tool(tool, arguments)
    return bool(result.is_error), "".join(getattr(block, "text", "") for block in result.content)
