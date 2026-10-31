"""ASGI app for production servers: `uvicorn pingera_mcp.asgi:app --workers 4`.

Configured from the environment like the CLI, but always uses the streamable HTTP transport.
"""

from __future__ import annotations

import logging

from .config import Settings, Transport
from .server import create_http_app

settings = Settings.from_env()
settings.transport = Transport.HTTP
logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = create_http_app(settings)
