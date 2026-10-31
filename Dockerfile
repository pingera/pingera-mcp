# Pingera MCP server, streamable HTTP transport (multi-tenant by default: every request
# carries its own Pingera credentials). Built from this repository's source.

FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --frozen --no-dev --no-install-project
COPY pingera_mcp ./pingera_mcp
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim
RUN useradd --create-home --uid 1000 mcp
COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    WORKERS=2
USER mcp
WORKDIR /app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
# Stateless HTTP: any worker (or replica) can serve any request.
CMD ["sh", "-c", "exec uvicorn pingera_mcp.asgi:app --host \"$MCP_HOST\" --port \"$MCP_PORT\" --workers \"$WORKERS\" --proxy-headers --forwarded-allow-ips '*' --no-server-header"]
