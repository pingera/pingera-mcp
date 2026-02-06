"""
Alternative startup script for Pingera MCP Server production deployment.
This file is kept for reference but is not used when running with uvicorn.

For production with uvicorn, adjust workers and settings via environment:
- UVICORN_WORKERS: Number of worker processes
- LOG_LEVEL: Logging level (debug, info, warning, error)

To use this as a custom startup script with gunicorn instead:
1. Install gunicorn: pip install gunicorn
2. Update Dockerfile CMD to: gunicorn pingera_mcp.asgi:app -c gunicorn.conf.py
3. Ensure uvicorn workers: worker_class = 'uvicorn.workers.UvicornWorker'
"""
