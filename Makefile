.PHONY: help build run start stop restart logs clean test shell dev-build dev-up

# Default target
help:
	@echo "Pingera MCP Server - Docker Management"
	@echo ""
	@echo "Production commands (PyPI install):"
	@echo "  make build       - Build production Docker image from PyPI"
	@echo "  make run         - Run production container in foreground"
	@echo "  make start       - Start production container in background"
	@echo "  make stop        - Stop running container"
	@echo "  make restart     - Restart container"
	@echo "  make logs        - View container logs (follow)"
	@echo "  make clean       - Remove container and image"
	@echo "  make shell       - Open shell in running container"
	@echo ""
	@echo "Development commands (build from source):"
	@echo "  make dev-build   - Build development Docker image from source"
	@echo "  make dev-run     - Run development container with hot-reload"
	@echo "  make dev-start   - Start development container in background"
	@echo "  make dev-stop    - Stop development container"
	@echo ""
	@echo "Docker Compose commands:"
	@echo "  make up          - Start production services with docker-compose"
	@echo "  make down        - Stop production services"
	@echo "  make dev-up      - Start development services (hot-reload enabled)"
	@echo "  make dev-down    - Stop development services"
	@echo "  make ps          - Show running services"
	@echo ""
	@echo "Utility commands:"
	@echo "  make test        - Run tests in container"
	@echo "  make health      - Check server health"
	@echo "  make stats       - View container statistics"

# Production Docker commands (PyPI install)
build:
	@echo "Building production Docker image from PyPI..."
	docker build -t pingera-mcp-server:latest .

run:
	@echo "Running container (foreground)..."
	docker run --rm -it \
		--name pingera-mcp \
		-p 8000:8000 \
		--env-file .env \
		pingera-mcp-server:latest

start:
	@echo "Starting container (background)..."
	docker run -d \
		--name pingera-mcp \
		-p 8000:8000 \
		--env-file .env \
		--restart unless-stopped \
		pingera-mcp-server:latest
	@echo "Container started. View logs with: make logs"

stop:
	@echo "Stopping container..."
	docker stop pingera-mcp || true
	docker rm pingera-mcp || true

restart: stop start

logs:
	@echo "Showing logs (Ctrl+C to exit)..."
	docker logs -f pingera-mcp

clean:
	@echo "Cleaning up..."
	docker stop pingera-mcp || true
	docker rm pingera-mcp || true
	docker rmi pingera-mcp-server:latest || true

shell:
	@echo "Opening shell in container..."
	docker exec -it pingera-mcp /bin/bash

test:
	@echo "Running tests in container..."
	docker run --rm \
		--env-file .env \
		pingera-mcp-server:latest \
		python -m pytest tests/

# Docker Compose commands (production)
up:
	@echo "Starting production services with docker-compose..."
	docker-compose up -d
	@echo "Production services started. View logs with: docker-compose logs -f"

down:
	@echo "Stopping production services..."
	docker-compose down

ps:
	@echo "Running services:"
	docker-compose ps

# Development commands
dev-build:
	@echo "Building development Docker image from source..."
	docker build -f Dockerfile.dev -t pingera-mcp-dev:latest .

dev-run:
	@echo "Running development container (foreground, hot-reload)..."
	docker run --rm -it \
		--name pingera-mcp-dev \
		-p 8000:8000 \
		-v $(PWD)/pingera_mcp:/app/pingera_mcp:ro \
		--env-file .env \
		pingera-mcp-dev:latest

dev-start:
	@echo "Starting development container (background, hot-reload)..."
	docker run -d \
		--name pingera-mcp-dev \
		-p 8000:8000 \
		-v $(PWD)/pingera_mcp:/app/pingera_mcp:ro \
		--env-file .env \
		--restart unless-stopped \
		pingera-mcp-dev:latest
	@echo "Development container started. View logs with: make logs"

dev-stop:
	@echo "Stopping development container..."
	docker stop pingera-mcp-dev || true
	docker rm pingera-mcp-dev || true

dev-logs:
	@echo "Showing development logs (Ctrl+C to exit)..."
	docker logs -f pingera-mcp-dev

dev-compose-up:
	@echo "Starting development services with docker-compose..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development services started. View logs with: docker-compose -f docker-compose.dev.yml logs -f"

dev-compose-down:
	@echo "Stopping development services..."
	docker-compose -f docker-compose.dev.yml down

# Docker Compose commands (production)
prod-deploy: build
	@echo "Deploying to production..."
	@echo "Stopping old container..."
	@make stop || true
	@echo "Starting new container..."
	@make start
	@echo "Deployment complete!"

# Health check
health:
	@echo "Checking server health..."
	@curl -f http://localhost:8000/health || (echo "Server is not healthy!" && exit 1)
	@echo "Server is healthy!"

# View stats
stats:
	@echo "Container statistics:"
	docker stats pingera-mcp --no-stream
