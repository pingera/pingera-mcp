# Deploying the Pingera MCP server

The Docker image runs the streamable HTTP transport with uvicorn. It is built from this repository's source:

```bash
docker build -t pingera-mcp-server .
docker run --rm -p 8000:8000 -e PINGERA_MODE=read_write pingera-mcp-server
curl http://localhost:8000/health
```

The MCP endpoint is `http://localhost:8000/mcp`. Configuration is the environment variables from the
[README](README.md#configuration); the image sets `MCP_TRANSPORT=http`, `MCP_HOST=0.0.0.0`, `MCP_PORT=8000` and
`WORKERS=2` (uvicorn worker processes).

## Multi-tenant or single account

**Multi-tenant (default, `MCP_HTTP_AUTH=request`).** The server holds no Pingera credentials. Every request must send
the user's own (`Authorization: Bearer <API key or JWT>` or `X-API-KEY: <API key>`); requests without them get
`401`. Credentials live only for the duration of the request. This is how `mcp.app.pingera.ru` runs.

**Single account (`MCP_HTTP_AUTH=env`).** The server acts with its `PINGERA_API_KEY` (or `PINGERA_JWT_TOKEN`) for every
client; requests that do send credentials use theirs instead. Anyone who can reach the port can use the key, so keep it
on a private network or behind your own authentication.

```bash
docker run --rm -p 127.0.0.1:8000:8000 \
  -e MCP_HTTP_AUTH=env -e PINGERA_API_KEY=... -e PINGERA_MODE=read_write \
  pingera-mcp-server
```

## Docker Compose

`docker compose up` builds and runs the image with the variables from `.env` (copy [.env.example](.env.example)).
`docker compose -f docker-compose.dev.yml up --build` mounts the source and reloads on changes.

## Kubernetes

- **Scaling.** The server is stateless (no MCP sessions, no local state), so run as many replicas and `WORKERS` as you
  need behind a plain Service; no sticky sessions are required.
- **Probes.** `GET /health` for readiness and liveness.
- **Security context.** The image runs as UID 1000 and works with `readOnlyRootFilesystem: true`.
- **Ingress.** Keep request and response buffering off and timeouts generous for clients that use SSE streams
  (`MCP_JSON_RESPONSE=false`); with the default JSON responses ordinary proxy settings work.
- **Resources.** Each uvicorn worker needs roughly 100-150 MiB of memory.

For `mcp.app.pingera.ru` the image is built inside the cluster with Kaniko, like the backend image:
`build/cluster-build/build-in-cluster.sh <version>` (see [build/cluster-build/README.md](build/cluster-build/README.md)).

Example manifests used for `mcp.app.pingera.ru` live in the backend repository
(`build_and_deploy/deploy_app/mcp/`), and its Tilt setup (`build_and_deploy/deploy_tilt/`) runs this server in a
local k3d cluster against a local backend.
