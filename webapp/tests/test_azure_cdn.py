"""
Azure Maps CDN connectivity test
This script tests if the Azure Maps CDN is accessible from the current environment.
"""

import requests
import sys

def test_azure_maps_cdn():
    """Test Azure Maps CDN connectivity"""
    
    test_urls = [
        'https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.js',
        'https://atlas.microsoft.com/sdk/javascript/drawing/1.0/atlas-drawing.min.js',
        'https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.css',
        'https://atlas.microsoft.com/sdk/javascript/drawing/1.0/atlas-drawing.min.css'
    ]
    
    print("Testing Azure Maps CDN connectivity...")
    print("=" * 50)
    
    all_success = True
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - OK (Size: {len(response.content)} bytes)")
            else:
                print(f"❌ {url} - HTTP {response.status_code}")
                all_success = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - Error: {e}")
            all_success = False
    
    print("=" * 50)
    if all_success:
        print("✅ All Azure Maps CDN resources are accessible!")
        return True
    else:
        print("❌ Some Azure Maps CDN resources are not accessible.")
        print("   This could be due to network restrictions, firewall, or CDN issues.")
        return False

if __name__ == "__main__":
    success = test_azure_maps_cdn()
    sys.exit(0 if success else 1)