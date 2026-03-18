#!/usr/bin/env python3
"""
Azure Maps API Key Setup Guide and Verification
"""

def print_azure_maps_setup_guide():
    """Print comprehensive setup guide for Azure Maps"""
    print("🗝️  Azure Maps API Key Setup Guide")
    print("=" * 80)
    print()
    
    print("📋 STEP 1: Create Azure Maps Account")
    print("   1. Go to Azure Portal: https://portal.azure.com")
    print("   2. Click 'Create a resource' → Search for 'Azure Maps'")
    print("   3. Click 'Azure Maps' → Click 'Create'")
    print("   4. Fill in the form:")
    print("      - Subscription: Choose your Azure subscription")
    print("      - Resource Group: Create new or use existing")
    print("      - Name: Give your maps account a name (e.g., 'towerscout-maps')")
    print("      - Pricing Tier: Choose S0 (Standard) or S1 (Premium)")
    print("   5. Click 'Review + Create' → Click 'Create'")
    print()
    
    print("🔑 STEP 2: Get Primary Key")
    print("   1. Once created, go to your Azure Maps resource")
    print("   2. In the left menu, click 'Authentication'")
    print("   3. Copy the 'Primary Key' (should be ~32-64 characters)")
    print("   4. Format looks like: 'Ak1Bn2Cm3Dn4Ep5Fq6Gr7Hs8It9Ju0K' (example)")
    print()
    
    print("⚙️  STEP 3: Configure TowerScout")
    print("   1. Edit your webapp/.env file")
    print("   2. Update the line:")
    print("      AZURE_MAPS_SUBSCRIPTION_KEY=YOUR_PRIMARY_KEY_HERE")
    print("      (NO SPACES around the = sign)")
    print("   3. Save the file")
    print()
    
    print("🧪 STEP 4: Test Authentication")
    print("   Run: python test_azure_auth.py")
    print()
    
    print("📊 Key Format Comparison")
    print("=" * 50)
    print("✅ Valid Azure Maps Key Examples:")
    print("   - Length: 32-64 characters")
    print("   - Format: AlphanumericString (no special chars except maybe hyphens)")
    print("   - Example: 'Ak1Bn2Cm3Dn4Ep5Fq6Gr7Hs8It9Ju0K'")
    print()
    print("❌ Invalid Key Characteristics:")
    print("   - Very long (>80 characters)")
    print("   - Contains many hyphens or special characters")
    print("   - Looks like: '7G19RuHd...lots-of-chars...AZMP2nDj'")
    print()
    
    print("🆘 Troubleshooting")
    print("=" * 30)
    print("If you continue getting 401 errors:")
    print("1. ✅ Verify the key is exactly copied (no extra spaces)")
    print("2. ✅ Check Azure Portal → Azure Maps → Authentication")
    print("3. ✅ Ensure the Azure Maps service is not paused/suspended")
    print("4. ✅ Try regenerating the Primary Key")
    print("5. ✅ Check your Azure subscription is active")
    print()
    
    print("💡 Alternative: Use Google Maps")
    print("   TowerScout also supports Google Maps if Azure Maps doesn't work")
    print("   Set up Google Cloud Maps API key instead")

def analyze_current_key():
    """Analyze the current key format"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv('.env')
    key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
    
    print("\n🔍 Current Key Analysis")
    print("=" * 40)
    
    if not key:
        print("❌ No key configured")
        return
    
    print(f"Length: {len(key)} characters")
    print(f"Format: {key[:10]}...{key[-6:]}")
    
    # Analysis
    issues = []
    if len(key) > 70:
        issues.append("Key is unusually long (>70 chars)")
    if key.count('-') > 3:
        issues.append("Key contains many hyphens")
    if not key.replace('-', '').replace('_', '').isalnum():
        issues.append("Key contains non-alphanumeric characters")
    
    if issues:
        print("\n⚠️  Potential Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 This doesn't look like a standard Azure Maps subscription key")
        print("   Please follow the setup guide above to get a proper key")
    else:
        print("\n✅ Key format looks reasonable")
        print("   If it's still failing, the key might be expired or invalid")

if __name__ == "__main__":
    print_azure_maps_setup_guide()
    analyze_current_key()