# Overview

The Pingera MCP Server is a fully functional Model Context Protocol (MCP) server that provides seamless integration between AI models and the Pingera monitoring service. The project acts as a bridge, allowing AI agents to access and interact with website monitoring data through standardized MCP resources and tools. Currently operational in read-only mode with live data integration, successfully connecting to the Pingera API v1 and serving 6 monitored status pages with comprehensive configuration data.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture Pattern
The project follows a modular, layered architecture with clear separation of concerns:

**Configuration Layer**: Environment-based configuration management using a centralized Config class that handles API keys, operation modes, timeouts, and other runtime parameters.

**API Client Layer**: A dedicated Pingera client library (`pingera/`) that abstracts all HTTP communication with the Pingera monitoring service. This layer includes robust error handling, request retry logic, and response parsing.

**MCP Server Layer**: The main server implementation that exposes monitoring data and operations through the Model Context Protocol standard, using FastMCP as the underlying framework.

**Data Models**: Pydantic-based models for type-safe data validation and serialization of monitoring entities like pages and API responses.

## Operation Modes
The server supports two distinct operation modes:
- **Read-Only Mode**: Provides access to monitoring data without modification capabilities
- **Read-Write Mode**: Full access including the ability to create, update, and delete monitoring resources

## Error Handling Strategy
Comprehensive error handling with custom exception hierarchy:
- Base `PingeraError` for all client-related errors
- Specific exceptions for API errors, authentication failures, connection issues, and timeouts
- Structured error responses with status codes and additional context

## HTTP Client Configuration
The Pingera client uses a configured requests session with:
- Retry strategy for handling transient failures
- Configurable timeouts to prevent hanging requests
- Session reuse for connection pooling
- Custom headers for API authentication

## MCP Integration
The server exposes monitoring functionality through:
- **MCP Resources**: Structured access to monitoring data (e.g., `pingera://pages`)
- **MCP Tools**: Executable operations for monitoring management
- **Standardized Responses**: JSON-formatted responses compatible with MCP specifications

# External Dependencies

## Core Framework Dependencies
- **FastMCP**: Primary framework for implementing the Model Context Protocol server
- **Pydantic**: Data validation and serialization for API models and configuration
- **Requests**: HTTP client library for communicating with the Pingera API

## Configuration and Environment
- **python-dotenv**: Environment variable management from .env files
- **Standard Library**: Uses built-in modules for logging, configuration, and async operations

## External Service Integration
- **Pingera Monitoring API**: Primary external dependency at `https://api.pingera.ru/v1`
  - Requires API key authentication via Authorization header
  - Successfully serving live data from 6 monitored status pages
  - RESTful API with JSON responses containing comprehensive page configuration
  - Validated data model supports all current API fields including CSS styling, subscription settings, and localization

## Runtime Dependencies
- **Python 3.x**: Modern Python runtime with async/await support
- **UV Package Manager**: Used for dependency management and virtual environment handling
- **Environment Variables**: Configuration through PINGERA_* environment variables