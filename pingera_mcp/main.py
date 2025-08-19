from pingera_mcp.mcp_server import create_mcp_server
from pingera_mcp.config import Config

def main():
    """Main entry point for the MCP server."""
    config = Config()
    server = create_mcp_server(config)
    server.run()

if __name__ == "__main__":
    main()