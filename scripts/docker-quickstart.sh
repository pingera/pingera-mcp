#!/bin/bash
# Quick start script for testing Pingera MCP Server Docker deployment
# This script helps verify your Docker setup is working correctly

set -e

echo "🚀 Pingera MCP Server - Docker Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docker.com"
    exit 1
fi

echo "✅ Docker is installed"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Warning: docker-compose is not installed"
    echo "You can still use 'docker' commands, but 'docker-compose' is recommended"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from .env.docker..."
    cp .env.docker .env
    echo "✅ .env file created"
    echo ""
    echo "ℹ️  For SSE mode (default), clients provide credentials via Authorization headers."
    echo "   Server-side credentials are optional and only needed for:"
    echo "   - STDIO mode"
    echo "   - Fallback authentication when REQUIRE_AUTH_HEADER=false"
    echo ""
    echo "   Current setting: REQUIRE_AUTH_HEADER=true (clients must provide credentials)"
    echo ""
fi

echo "✅ .env file configured"
echo ""

# Ask user how they want to proceed
echo "How would you like to start the server?"
echo "  1) Docker Compose (recommended)"
echo "  2) Docker build + run"
echo "  3) Skip and show manual commands"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🏗️  Building and starting with docker-compose..."
        docker-compose up -d
        echo ""
        echo "✅ Server started!"
        echo ""
        echo "📊 View logs with:"
        echo "   docker-compose logs -f"
        echo ""
        echo "🔍 Check status with:"
        echo "   docker-compose ps"
        echo ""
        echo "🛑 Stop server with:"
        echo "   docker-compose down"
        ;;
    2)
        echo ""
        echo "🏗️  Building Docker image..."
        docker build -t pingera-mcp-server .
        echo ""
        echo "🚀 Starting container..."
        docker run -d \
            --name pingera-mcp \
            -p 8000:8000 \
            --env-file .env \
            pingera-mcp-server
        echo ""
        echo "✅ Server started!"
        echo ""
        echo "📊 View logs with:"
        echo "   docker logs -f pingera-mcp"
        echo ""
        echo "🔍 Check status with:"
        echo "   docker ps"
        echo ""
        echo "🛑 Stop server with:"
        echo "   docker stop pingera-mcp && docker rm pingera-mcp"
        ;;
    3)
        echo ""
        echo "📚 Manual commands:"
        echo ""
        echo "Build image:"
        echo "  docker build -t pingera-mcp-server ."
        echo ""
        echo "Run container:"
        echo "  docker run -d -p 8000:8000 --env-file .env pingera-mcp-server"
        echo ""
        echo "Or with docker-compose:"
        echo "  docker-compose up -d"
        echo ""
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Wait for server to start
echo "⏳ Waiting for server to be ready..."
sleep 5

# Test health endpoint
echo "🔍 Testing server health..."
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is healthy and responding!"
else
    echo "⚠️  Health check failed. Server might still be starting or there's an issue."
    echo "   Check logs with: docker logs pingera-mcp"
    echo "   Or: docker-compose logs"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📍 Server is running at: http://localhost:8000"
echo ""
echo "Next steps:"
echo "  • Test the connection with your MCP client"
echo "  • View logs to monitor activity"
echo "  • See DOCKER.md for advanced configuration"
echo ""
echo "For help, visit: https://github.com/pingera/pingera-mcp"
