
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-08-07

### Added
- Initial release of Pingera MCP Server
- Model Context Protocol (MCP) server implementation
- Pingera API client library with comprehensive error handling
- Support for read-only and read-write operation modes
- MCP Resources: `pingera://pages`, `pingera://pages/{id}`, `pingera://status`
- MCP Tools: `list_pages`, `get_page_details`, `test_pingera_connection`
- Pydantic models for type-safe API responses
- Environment-based configuration management
- Comprehensive test suite with pytest
- FastMCP framework integration
- Custom exception hierarchy for robust error handling
