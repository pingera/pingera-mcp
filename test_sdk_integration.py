
#!/usr/bin/env python3
"""
Test script to verify Pingera SDK integration.
"""
import os
import sys
from pingera import PingeraClient

def test_sdk_integration():
    """Test the SDK integration."""
    print("🔧 Testing Pingera SDK integration...")
    
    # Check if API key is available
    api_key = os.getenv("PINGERA_API_KEY")
    if not api_key:
        print("❌ PINGERA_API_KEY environment variable is required")
        return False
    
    try:
        # Initialize client
        client = PingeraClient(api_key=api_key)
        print("✓ Pingera SDK client initialized")
        
        # Test connection
        is_connected = client.test_connection()
        if is_connected:
            print("✓ SDK connection test successful")
        else:
            print("⚠️ SDK connection test failed")
        
        # Get API info
        api_info = client.get_api_info()
        print(f"✓ API Info: {api_info.get('message', 'Unknown')} - Connected: {api_info.get('connected', False)}")
        print(f"  SDK Version: {api_info.get('sdk_version', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ SDK integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sdk_integration()
    sys.exit(0 if success else 1)
