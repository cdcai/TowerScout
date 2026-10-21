#!/usr/bin/env python3
"""
Azure Maps SAS Token Authentication Debug Test
Detailed analysis of SAS token format and authentication
"""

import os
import sys
sys.path.append('.')

import requests
from urllib.parse import quote_plus, urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from webapp directory
load_dotenv('.env')  # Load from current directory (webapp)

def analyze_sas_token(token):
    """Analyze SAS token structure and parameters"""
    print("🔍 SAS Token Analysis")
    print("=" * 50)
    
    # Check if token starts with common SAS patterns
    if token.startswith('sv='):
        print("✅ Token starts with 'sv=' (valid SAS pattern)")
    elif token.startswith('sig='):
        print("✅ Token starts with 'sig=' (signature format)")
    else:
        print(f"⚠️  Token starts with: '{token[:10]}...' (unusual pattern)")
    
    # Parse SAS token parameters
    try:
        # Treat the entire string as query parameters
        parsed = parse_qs(token)
        print(f"📊 Found {len(parsed)} parameters in SAS token:")
        
        for key, values in parsed.items():
            if key in ['sig', 'se', 'sv', 'sr', 'sp', 'sip', 'spr']:
                print(f"   {key}: {values[0][:20]}..." if len(values[0]) > 20 else f"   {key}: {values[0]}")
            else:
                print(f"   {key}: {values[0]}")
                
    except Exception as e:
        print(f"❌ Error parsing SAS token: {e}")
        
    print()

def test_different_auth_methods(subscription_key):
    """Test multiple authentication approaches"""
    print("🧪 Testing Different Authentication Methods")
    print("=" * 50)
    
    # Method 1: As direct query parameter
    url1 = f"https://atlas.microsoft.com/search/address/json?api-version=1.0&{subscription_key}&query=Seattle"
    print("Method 1: Direct SAS token in URL")
    print(f"URL: {url1[:100]}...")
    
    try:
        response = requests.get(url1, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
        else:
            print(f"❌ Failed: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # Method 2: As subscription-key parameter
    url2 = "https://atlas.microsoft.com/search/address/json"
    params2 = {
        'api-version': '1.0',
        'subscription-key': subscription_key,
        'query': 'Seattle'
    }
    print("Method 2: SAS token as subscription-key parameter")
    print(f"URL: {url2}")
    print(f"Params: subscription-key={subscription_key[:20]}...")
    
    try:
        response = requests.get(url2, params=params2, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
        else:
            print(f"❌ Failed: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # Method 3: In Authorization header
    url3 = "https://atlas.microsoft.com/search/address/json?api-version=1.0&query=Seattle"
    headers3 = {
        'Authorization': f'Bearer {subscription_key}'
    }
    print("Method 3: SAS token in Authorization header")
    print(f"URL: {url3}")
    print(f"Header: Authorization=Bearer {subscription_key[:20]}...")
    
    try:
        response = requests.get(url3, headers=headers3, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
        else:
            print(f"❌ Failed: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    subscription_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    
    if not subscription_key:
        print("❌ No Azure Maps subscription key found in environment")
        return
    
    print("Azure Maps SAS Token Debug Analysis")
    print("=" * 60)
    print(f"Key length: {len(subscription_key)} characters")
    print(f"Key preview: {subscription_key[:20]}...{subscription_key[-10:]}")
    print()
    
    # Analyze token structure
    analyze_sas_token(subscription_key)
    
    # Test different authentication methods
    test_different_auth_methods(subscription_key)
    
    print("=" * 60)
    print("🔍 Debug Complete")

if __name__ == "__main__":
    main()