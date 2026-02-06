# Docker Deployment - Quick Reference

## Files Created

### Core Docker Files
- **Dockerfile** - Multi-stage production build with uvicorn
- **docker-compose.yml** - Easy orchestration with docker-compose
- **.dockerignore** - Optimized build context (excludes tests, docs, etc.)
- **pingera_mcp/asgi.py** - ASGI app entry point for production servers

### Documentation
- **DOCKER.md** - Comprehensive Docker deployment guide
- **Makefile** - Convenient commands for Docker operations

### Utilities
- **scripts/docker-quickstart.sh** - Interactive setup script
- **scripts/test_docker_deployment.py** - Deployment verification script

## Quick Commands

### Build & Run
```bash
# Using Makefile (easiest)
make build
make start

# Using docker-compose (recommended)
docker-compose up -d

# Using Docker directly
docker build -t pingera-mcp-server .
docker run -d -p 8000:8000 --env-file .env pingera-mcp-server
```

### Testing
```bash
# Interactive quick start
./scripts/docker-quickstart.sh

# Automated testing
python scripts/test_docker_deployment.py

# Manual health check
curl http://localhost:8000/health
```

### Monitoring
```bash
# View logs
make logs
docker-compose logs -f
docker logs -f pingera-mcp

# Check status
make ps
docker ps

# View statistics
make stats
docker stats pingera-mcp
```

### Management
```bash
# Stop
make stop
docker-compose down

# Restart
make restart

# Clean up
make clean
```

## Configuration

### Required Environment Variables
Set in `.env` file:
```bash
# Server Configuration
TRANSPORT_MODE=sse
HTTP_PORT=8000
MCP_MODE=read-write

# Authentication (optional for SSE mode)
# Credentials are provided by clients via Authorization headers
# Only set these if you need fallback credentials:
# PINGERA_API_KEY=your_key
# PINGERA_JWT_TOKEN=your_token

# Recommended: Require client authentication
REQUIRE_AUTH_HEADER=true
```

### Production Settings
```bash
UVICORN_WORKERS=4           # Number of worker processes
MCP_MODE=read-write         # or read-only
LOG_LEVEL=info              # debug, info, warning, error
```

## Architecture

### Container Details
- **Base Image**: python:3.11-slim
- **Installation**: PyPI package (pingera-mcp-server)
- **Server**: Uvicorn with 4 workers (configurable)
- **Port**: 8000 (exposed)
- **User**: Non-root (mcpuser, UID 1000)
- **Health Check**: Built-in at /health endpoint

### Resource Limits (default)
- **CPU**: 0.5-2 cores
- **Memory**: 256MB-1GB

### Security Features
- Multi-stage build for minimal image size
- Non-root user execution
- .dockerignore to exclude sensitive files
- Environment-based secrets (not in image)
- SSL/TLS support via environment variables

## Production Deployment Checklist

- [ ] Copy `.env.docker` to `.env`
- [ ] Set `REQUIRE_AUTH_HEADER=true` in `.env` (recommended)
- [ ] Clients configured to send Authorization headers with their credentials
- [ ] Set `TRANSPORT_MODE=sse` in `.env` (default)
- [ ] Adjust `UVICORN_WORKERS` based on CPU cores
- [ ] Configure reverse proxy (nginx/Caddy) for SSL
- [ ] Set up monitoring and log aggregation
- [ ] Configure resource limits in docker-compose.yml
- [ ] Enable authentication with `REQUIRE_AUTH_HEADER=true`
- [ ] Test with `./scripts/test_docker_deployment.py`
- [ ] Set up automated backups of `.env` configuration

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs pingera-mcp

# Common issues:
# - Missing API key in .env
# - Port 8000 already in use
# - Insufficient memory
```

### Can't connect to server
```bash
# Verify container is running
docker ps | grep pingera-mcp

# Check port mapping
docker port pingera-mcp

# Test locally
curl http://localhost:8000/health
```

### Performance issues
```bash
# Check resource usage
docker stats pingera-mcp

# Increase workers
# Edit .env: UVICORN_WORKERS=8

# Increase memory limit
# Edit docker-compose.yml: memory: 2G
```

## Next Steps

1. **Build the image**: `make build`
2. **Configure credentials**: Edit `.env` file
3. **Start server**: `make start` or `docker-compose up -d`
4. **Test deployment**: `python scripts/test_docker_deployment.py`
5. **Configure client**: Point your MCP client to `http://localhost:8000`
6. **Monitor**: `make logs` to watch activity
7. **Production**: Set up reverse proxy with SSL (see DOCKER.md)

## Support

- Full documentation: [DOCKER.md](DOCKER.md)
- GitHub: https://github.com/pingera/pingera-mcp
- Issues: https://github.com/pingera/pingera-mcp/issues
