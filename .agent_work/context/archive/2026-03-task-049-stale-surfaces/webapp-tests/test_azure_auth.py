"""
Azure Maps Authentication Test
This script tests Azure Maps API key validity and permissions.
"""

import requests
import os
from dotenv import load_dotenv

def test_azure_maps_authentication():
    """Test Azure Maps API key authentication and permissions"""
    
    # Load environment variables
    load_dotenv()
    
    subscription_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    
    if not subscription_key:
        print("❌ No Azure Maps subscription key found in environment variables")
        return False
    
    print(f"Testing Azure Maps authentication...")
    print(f"Key: {subscription_key[:8]}...{subscription_key[-4:]} (length: {len(subscription_key)})")
    
    # Determine if this is a subscription key or SAS token
    if len(subscription_key) > 50:
        print("🔍 Detected: Long key (likely SAS token)")
        auth_method = "sas_token"
    else:
        print("🔍 Detected: Short key (likely subscription key)")
        auth_method = "subscription_key"
    
    print("=" * 60)
    
    # Test different endpoint formats based on key type
    test_endpoints = []
    
    if auth_method == "sas_token":
        # For SAS tokens, the token contains all authentication info
        test_endpoints = [
            {
                'name': 'Search Address (SAS Token)',
                'url': f'https://atlas.microsoft.com/search/address/json?api-version=1.0&{subscription_key}&query=New York, NY',
                'params': {}
            },
            {
                'name': 'Get Map Tile Road (SAS Token)',
                'url': f'https://atlas.microsoft.com/map/tile?api-version=2.1&{subscription_key}&tilesetId=microsoft.base.road&zoom=10&x=301&y=385',
                'params': {}
            }
        ]
    else:
        # For subscription keys, use subscription-key parameter
        test_endpoints = [
            {
                'name': 'Search Address (Subscription Key)',
                'url': 'https://atlas.microsoft.com/search/address/json',
                'params': {
                    'api-version': '1.0',
                    'subscription-key': subscription_key,
                    'query': 'New York, NY'
                }
            },
            {
                'name': 'Get Map Tile (Road)',
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
    
    all_success = True
    
    for test in test_endpoints:
        try:
            response = requests.get(test['url'], params=test['params'], timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {test['name']}: SUCCESS")
            elif response.status_code == 401:
                print(f"❌ {test['name']}: AUTHENTICATION FAILED (401 Unauthorized)")
                print(f"   This indicates the subscription key is invalid or expired")
                all_success = False
            elif response.status_code == 403:
                print(f"⚠️  {test['name']}: FORBIDDEN (403 - No permission for this service)")
                print(f"   The key is valid but doesn't have access to this specific service")
            else:
                print(f"⚠️  {test['name']}: HTTP {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']}: Network error - {e}")
            all_success = False
    
    print("=" * 60)
    
    if all_success:
        print("✅ Azure Maps authentication is working properly!")
        print("   The subscription key has the necessary permissions.")
    else:
        print("❌ Azure Maps authentication has issues.")
        print("\nTroubleshooting:")
        print("1. Verify the subscription key is correct in your .env file")
        print("2. Check if the Azure Maps account is active and not suspended")
        print("3. Ensure the subscription includes the required services")
        print("4. Try regenerating the subscription key in Azure Portal")
    
    return all_success

if __name__ == "__main__":
    test_azure_maps_authentication()