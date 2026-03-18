#!/usr/bin/env python3
"""
Test Flask server accessibility on port 5001
"""

import requests

def test_flask_server():
    """Test if Flask server is responding"""
    print("🧪 Testing Flask server on port 5001...")
    
    # Test basic access
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        print(f"✅ Main page: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {e}")
        return False
    
    # Test providers endpoint
    try:
        response = requests.get('http://localhost:5001/getproviders', timeout=5)
        print(f"✅ Providers endpoint: HTTP {response.status_code}")
        if response.status_code == 200:
            providers = response.json()
            print(f"   Providers: {providers}")
            
            # Check if Azure Maps is available
            azure_available = any(p['id'] == 'azure' for p in providers)
            print(f"   Azure Maps available: {azure_available}")
            
            return azure_available
    except Exception as e:
        print(f"❌ Providers endpoint error: {e}")
        return False

if __name__ == "__main__":
    success = test_flask_server()
    if success:
        print("\n🎉 SUCCESS: Flask server is running with Azure Maps!")
    else:
        print("\n❌ ISSUE: Flask server is not responding properly")