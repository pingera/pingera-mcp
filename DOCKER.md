# Docker Deployment Guide

This guide explains how to deploy Pingera MCP Server using Docker in production.

## Quick Start

### Production Deployment (from PyPI)

The standard Dockerfile installs pingera-mcp-server from PyPI - use this for production deployments.

#### Using Docker Compose (Recommended)

1. **Copy the environment file:**
   ```bash
   cp .env.docker .env
   ```

2. **(Optional) Edit `.env` to customize settings:**
   
   **Note:** In SSE mode (default for Docker), API credentials are typically provided by clients via Authorization headers, not in the server environment. You only need to set `PINGERA_API_KEY` or `PINGERA_JWT_TOKEN` in `.env` if:
   - You want the server to have a fallback credential when clients don't provide auth headers
   - You set `REQUIRE_AUTH_HEADER=false` (not recommended for production)
   
   For most production deployments, clients will provide their own credentials via the `Authorization` header in each request.

3. **Start the server:**
   ```bash
   docker-compose up -d
   ```

4. **Check the logs:**
   ```bash
   docker-compose logs -f pingera-mcp
   ```

5. **Access the server:**
   ```
   http://localhost:8000
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t pingera-mcp-server .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name pingera-mcp \
     -p 8000:8000 \
     -e TRANSPORT_MODE=sse \
     -e MCP_MODE=read-write \
     pingera-mcp-server
   ```
   
   **Note:** Credentials are provided by clients via Authorization headers in SSE mode

### Development Deployment (from source)

If you're developing pingera-mcp locally and want to test changes:

```bash
# Use the development docker-compose
docker-compose -f docker-compose.dev.yml up -d

# Or build manually with hot-reload
docker build -f Dockerfile.dev -t pingera-mcp-dev .
docker run -d -p 8000:8000 \
  -v $(pwd)/pingera_mcp:/app/pingera_mcp:ro \
  pingera-mcp-dev
```

**Development features:**
- Builds from local source code
- Hot-reload enabled (changes reflected immediately)
- Debug logging enabled
- Can mount source code as volume
- Includes development dependencies

**When to use:**
- Contributing to pingera-mcp development
- Testing local changes before publishing
- Debugging issues in the codebase

## Configuration

### Environment Variables

#### Authentication (SSE Mode)
In SSE mode, credentials are typically provided by **clients** via the `Authorization` header:
- `Authorization: YOUR_API_KEY`
- `Authorization: Bearer YOUR_JWT_TOKEN`

The server environment variables below are only needed for:
- **STDIO mode** (credentials required in environment)
- **Fallback authentication** when `REQUIRE_AUTH_HEADER=false` (not recommended for production)

**Optional** server-side credentials:
- `PINGERA_API_KEY` - Fallback API key for server use
- `PINGERA_JWT_TOKEN` - Fallback JWT token for server use
- `REQUIRE_AUTH_HEADER` - Set to `true` to require client auth headers (recommended)

#### Server Configuration
- `TRANSPORT_MODE` - Set to `sse` for HTTP mode (default in Docker)
- `HTTP_HOST` - Listen address (default: `0.0.0.0`)
- `HTTP_PORT` - Listen port (default: `8000`)
- `MCP_MODE` - `read-only` or `read-write` (default: `read-write`)

#### Performance Tuning
- `UVICORN_WORKERS` - Number of worker processes (default: `4`)
- `LOG_LEVEL` - Logging level: `debug`, `info`, `warning`, `error` (default: `info`)

#### API Configuration
- `PINGERA_BASE_URL` - Pingera API endpoint (default: `https://api.pingera.ru/v1`)
- `PINGERA_TIMEOUT` - Request timeout in seconds (default: `30`)
- `PINGERA_MAX_RETRIES` - Maximum retry attempts (default: `3`)

### Resource Limits

The docker-compose.yml includes sensible defaults:
- **CPU**: 0.5-2 cores
- **Memory**: 256MB-1GB

Adjust these based on your load:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

## Production Considerations

### Security

1. **Use JWT tokens instead of API keys** when possible
2. **Enable authentication headers:**
   ```bash
   REQUIRE_AUTH_HEADER=true
   ```
3. **Use SSL/TLS** for production (see SSL Configuration below)
4. **Run behind a reverse proxy** (nginx, Caddy, Traefik)

### SSL/TLS Configuration

#### Option 1: Reverse Proxy (Recommended)
Use nginx or Caddy as a reverse proxy with automatic SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 2: Direct SSL in Container
Mount certificates and configure:

```yaml
services:
  pingera-mcp:
    volumes:
      - ./certs:/certs:ro
    environment:
      - SSL_KEYFILE=/certs/key.pem
      - SSL_CERTFILE=/certs/cert.pem
```

### Monitoring

#### Available Endpoints
The server exposes several HTTP endpoints:

- **`/`** - Root endpoint with service information
  ```bash
  curl http://localhost:8000/
  ```
  Returns service name, version, mode, and available endpoints

- **`/health`** - Health check endpoint for monitoring
  ```bash
  curl http://localhost:8000/health
  ```
  Returns detailed health status including timestamp and configuration

- **`/mcp/`** - MCP protocol endpoint (for MCP clients)
  This is where your MCP clients should connect

#### Health Checks
The container includes a built-in health check endpoint:
```bash
curl http://localhost:8000/health
```

#### Logs
Access logs in real-time:
```bash
docker-compose logs -f pingera-mcp
```

Or view with timestamps:
```bash
docker logs --timestamps pingera-mcp-server
```

### Scaling

#### Horizontal Scaling
Run multiple instances behind a load balancer:

```bash
docker-compose up -d --scale pingera-mcp=3
```

#### Vertical Scaling
Increase workers for CPU-bound workloads:

```yaml
environment:
  - UVICORN_WORKERS=8  # 2x CPU cores recommended
```

## Maintenance

### Update the container

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup configuration

```bash
# Backup .env file (contains credentials)
cp .env .env.backup

# Backup docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup
```

### View container stats

```bash
docker stats pingera-mcp-server
```

## Troubleshooting

### Container won't start
Check logs:
```bash
docker-compose logs pingera-mcp
```

Common issues:
- Missing API credentials
- Port 8000 already in use
- Insufficient resources

### Connection refused
Verify the container is running:
```bash
docker ps | grep pingera-mcp
```

Check port binding:
```bash
docker port pingera-mcp-server
```

### High memory usage
Reduce workers or increase memory limits:
```yaml
environment:
  - UVICORN_WORKERS=2
deploy:
  resources:
    limits:
      memory: 2G
```

### Slow response times
Increase timeout and workers:
```yaml
environment:
  - PINGERA_TIMEOUT=60
  - UVICORN_WORKERS=8
```

## Examples

### Development/Testing Mode (with fallback credentials)
```bash
# Use read-only mode with single worker and fallback credentials
docker run -d \
  -p 8000:8000 \
  -e PINGERA_API_KEY=$PINGERA_API_KEY \
  -e MCP_MODE=read-only \
  -e UVICORN_WORKERS=1 \
  -e REQUIRE_AUTH_HEADER=false \
  -e LOG_LEVEL=debug \
  pingera-mcp-server
```

### Production Setup with Client Authentication
```bash
docker run -d \
  --name pingera-mcp-prod \
  -p 8000:8000 \
  -e TRANSPORT_MODE=sse \
  -e MCP_MODE=read-write \
  -e REQUIRE_AUTH_HEADER=true \
  -e UVICORN_WORKERS=8 \
  --restart unless-stopped \
  pingera-mcp-server
```

### Production with SSL (behind reverse proxy)
```bash
# The MCP server runs on port 8000
# Reverse proxy (nginx/Caddy) handles SSL and forwards to :8000
docker run -d \
  --name pingera-mcp-prod \
  -p 8000:8000 \
  -e REQUIRE_AUTH_HEADER=true \
  -e UVICORN_WORKERS=8 \
  --restart unless-stopped \
  pingera-mcp-server
```

## Support

For issues or questions:
- GitHub: https://github.com/pingera/pingera-mcp
- Email: privet@pingera.ru
- Docs: https://pingera.ru/docs
