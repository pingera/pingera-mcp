.PHONY: help install test e2e run-stdio run-http docker-build docker-run

IMAGE ?= pingera-mcp-server:local

help:
	@echo "install       Install the package with dev dependencies (uv)"
	@echo "test          Run the unit and integration tests"
	@echo "e2e           Run end-to-end tests (needs PINGERA_E2E_URL and PINGERA_E2E_API_KEY)"
	@echo "run-stdio     Run the server over stdio (needs PINGERA_API_KEY)"
	@echo "run-http      Run the server over HTTP on :8000 (per-request credentials)"
	@echo "docker-build  Build the Docker image ($(IMAGE))"
	@echo "docker-run    Run the Docker image on :8000"

install:
	uv sync --extra dev

test:
	uv run pytest --ignore=tests/e2e

e2e:
	uv run pytest tests/e2e

run-stdio:
	uv run pingera-mcp

run-http:
	uv run pingera-mcp --transport http

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env $(IMAGE)
