
# Pingera MCP Server Overview

## What is it?

The Pingera MCP Server is a **Model Context Protocol (MCP) server** that connects AI models (like Claude) directly to the [Pingera monitoring service](https://pingera.ru). It allows AI assistants to read and manage your monitoring infrastructure through natural language conversations.

## Key Features

- **Direct API Integration**: Real-time access to your Pingera monitoring data
- **AI-Friendly Interface**: Works seamlessly with Claude Desktop and other MCP-compatible AI tools
- **Two Operation Modes**: 
  - **Read-only**: View monitoring data safely
  - **Read-write**: Full management capabilities
- **Comprehensive Coverage**: Status pages, monitoring checks, incidents, alerts, heartbeats, and more

## When to Use It

### Perfect for:
- **DevOps Teams**: "Show me all failed checks from last week"
- **Site Reliability Engineers**: "Create an incident for the API outage"
- **Monitoring Management**: "List all my status pages and their components"
- **Incident Response**: "What's the current status of our payment service?"
- **Automated Reporting**: "Generate a summary of this month's uptime"

### Use Cases:
- Query monitoring data through natural language
- Manage status pages and incidents via AI conversations
- Automate monitoring setup and configuration
- Generate monitoring reports and insights
- Troubleshoot service issues with AI assistance

## Quick Start

1. **Install**: `uv tool install pingera-mcp-server`
2. **Configure**: Add your Pingera API key to Claude Desktop config
3. **Use**: Ask Claude about your monitoring data!

Example queries:
- "List my monitored services"
- "Show details for the main website status page"
- "Create a new incident for database maintenance"
- "What checks are currently failing?"

## Safety

- Starts in **read-only mode** by default
- Requires explicit configuration for write operations
- Comprehensive error handling and validation
- Secure API key management through environment variables

Transform your monitoring workflow with AI-powered infrastructure management!
