#!/usr/bin/env python3
"""
Test script to verify Pingera MCP Server is running correctly in Docker.
Usage: python scripts/test_docker_deployment.py [server_url]
"""
import sys
import urllib.request
import urllib.error
import json
from typing import Optional

def test_health(base_url: str) -> bool:
    """Test the health endpoint."""
    try:
        url = f"{base_url}/health"
        print(f"Testing health endpoint: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            print(f"✅ Health check passed: {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_root(base_url: str) -> bool:
    """Test the root endpoint."""
    try:
        url = f"{base_url}/"
        print(f"\nTesting root endpoint: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            print(f"✅ Root endpoint accessible: {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_mcp_endpoint(base_url: str, api_key: Optional[str] = None) -> bool:
    """Test the MCP endpoint (requires authentication)."""
    try:
        url = f"{base_url}/mcp/"
        print(f"\nTesting MCP endpoint: {url}")
        
        headers = {}
        if api_key:
            headers['Authorization'] = api_key
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ MCP endpoint accessible: {response.status}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"⚠️  Authentication required (401). This is expected if no API key provided.")
            print(f"   Add your API key as second argument to test with auth:")
            print(f"   python {sys.argv[0]} {base_url} YOUR_API_KEY")
            return True  # This is actually ok - server is running
        else:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            return False
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Pingera MCP Server - Docker Deployment Test")
    print("=" * 50)
    print()
    
    # Get server URL from args or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Testing server at: {base_url}")
    if api_key:
        print(f"Using API key: {api_key[:10]}...")
    print()
    
    # Run tests
    root_ok = test_root(base_url)
    health_ok = test_health(base_url)
    mcp_ok = test_mcp_endpoint(base_url, api_key)
    
    print()
    print("=" * 50)
    if health_ok and root_ok:
        print("✅ Overall Status: Server is running correctly!")
        print()
        print("Next steps:")
        print("  • Configure your MCP client to connect to:", base_url)
        print("  • Use the /mcp/ endpoint for MCP protocol")
        print("  • Check logs with: docker logs pingera-mcp")
        print()
        return 0
    else:
        print("❌ Overall Status: Server is not running or not accessible")
        print()
        print("Troubleshooting:")
        print("  • Check if container is running: docker ps")
        print("  • View logs: docker logs pingera-mcp")
        print("  • Verify port 8000 is not in use: lsof -i :8000")
        print("  • Check .env file has valid credentials")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
