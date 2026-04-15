#!/usr/bin/env python3
"""
Test Azure Maps with proper subscription key format
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from webapp directory
load_dotenv('.env')

def test_azure_subscription_key():
    """Test Azure Maps with proper subscription-key parameter"""
    subscription_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    
    if not subscription_key:
        print("❌ No Azure Maps subscription key found")
        return False
    
    print(f"🧪 Testing Azure Maps with subscription key format")
    print(f"Key: {subscription_key[:10]}...{subscription_key[-6:]} (length: {len(subscription_key)})")
    print("=" * 60)
    
    # Test with proper subscription-key parameter
    test_endpoints = [
        {
            'name': 'Search API - Geocoding',
            'url': 'https://atlas.microsoft.com/search/address/json',
            'params': {
                'api-version': '1.0',
                'subscription-key': subscription_key,
                'query': 'Seattle, WA'
            }
        },
        {
            'name': 'Map Tile API - Satellite Imagery', 
            'url': 'https://atlas.microsoft.com/map/tile',
            'params': {
                'api-version': '2.1',
                'subscription-key': subscription_key,
                'tilesetId': 'microsoft.imagery',
                'zoom': '10',
                'x': '301', 
                'y': '385'
            }
        },
        {
            'name': 'Map Tile API - Road Map',
            'url': 'https://atlas.microsoft.com/map/tile', 
            'params': {
                'api-version': '2.1',
                'subscription-key': subscription_key,
                'tilesetId': 'microsoft.base.road',
                'zoom': '10',
                'x': '301',
                'y': '385'
            }
        }
    ]
    
    success_count = 0
    
    for endpoint in test_endpoints:
        print(f"Testing: {endpoint['name']}")
        
        try:
            response = requests.get(endpoint['url'], params=endpoint['params'], timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                success_count += 1
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    print(f"   📄 JSON response received")
                elif 'image' in content_type:
                    print(f"   🖼️  Image tile received ({len(response.content)} bytes)")
                    
            elif response.status_code == 401:
                print(f"   ❌ AUTHENTICATION FAILED (401)")
                print(f"   🔍 Response: {response.text[:100]}...")
                
            elif response.status_code == 403:
                print(f"   ❌ FORBIDDEN (403) - Check service permissions")
                print(f"   🔍 Response: {response.text[:100]}...")
                
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   🔍 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print()
    
    print("=" * 60)
    if success_count > 0:
        print(f"✅ SUCCESS: {success_count}/3 Azure Maps endpoints working!")
        return True
    else:
        print("❌ All Azure Maps endpoints failed")
        return False

def main():
    success = test_azure_subscription_key()
    
    if not success:
        print("\n💡 NEXT STEPS:")
        print("1. Check Azure Portal → Azure Maps → Authentication")
        print("2. Verify the subscription key is correct")
        print("3. Ensure Azure Maps service is active")
        print("4. Try regenerating the primary key")
        print("5. Check subscription billing status")

if __name__ == "__main__":
    main()