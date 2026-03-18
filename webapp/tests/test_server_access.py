#!/usr/bin/env python3
"""
Simple test to check if TowerScout server is accessible
"""

import requests
import time

def test_server():
    """Test if TowerScout server is responding"""
    print("🧪 Testing TowerScout server accessibility...")
    
    # Test basic access
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        print(f"✅ Main page: HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"   Content length: {len(response.text)} characters")
    except Exception as e:
        print(f"❌ Main page error: {e}")
        return False
    
    # Test providers endpoint
    try:
        response = requests.get('http://localhost:5000/getproviders', timeout=5)
        print(f"✅ Providers endpoint: HTTP {response.status_code}")
        if response.status_code == 200:
            providers = response.json()
            print(f"   Available providers: {[p['id'] for p in providers]}")
            
            # Check if Azure Maps is available
            azure_available = any(p['id'] == 'azure' for p in providers)
            print(f"   Azure Maps available: {azure_available}")
            
            return azure_available
    except Exception as e:
        print(f"❌ Providers endpoint error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 SUCCESS: TowerScout is running with Azure Maps!")
    else:
        print("\n❌ ISSUE: TowerScout server is not responding properly")