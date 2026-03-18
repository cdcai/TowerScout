#!/usr/bin/env python3
"""
Azure Maps Provider Direct Test
Tests Azure Maps provider functionality by running it directly in the webapp environment.
"""

import sys
import os

# Mock the dependencies that aren't available
class MockLogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def debug(self, msg): print(f"[DEBUG] {msg}")
    def warning(self, msg): print(f"[WARN] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")

class MockMap:
    def __init__(self):
        self.has_metadata = False

class MockTowerScoutError(Exception):
    def __init__(self, message, error_code=None, details=None, user_message=None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or "An error occurred."
    
    def to_dict(self):
        return {
            "error": True,
            "message": self.user_message,
            "technical_message": self.message,
            "details": self.details
        }

class MockConfigurationError(MockTowerScoutError): pass
class MockMapProviderError(MockTowerScoutError): pass

# Mock the imports
sys.modules['ts_maps'] = type('module', (), {'Map': MockMap})()
sys.modules['ts_errors'] = type('module', (), {
    'MapProviderError': MockMapProviderError,
    'ConfigurationError': MockConfigurationError,
    'NetworkError': MockTowerScoutError
})()

def mock_get_maps_logger():
    return MockLogger()

sys.modules['ts_logging'] = type('module', (), {
    'get_maps_logger': mock_get_maps_logger
})()

def test_azure_maps_direct():
    """Test Azure Maps provider by importing and running it directly."""
    print("Testing Azure Maps provider directly...")
    
    try:
        # Now import Azure Maps after mocking dependencies
        from ts_azure_maps import AzureMaps, create_azure_maps_provider
        
        print("✅ Successfully imported Azure Maps provider")
        
        # Test initialization
        azure_maps = AzureMaps("test_subscription_key_12345")
        print("✅ Successfully initialized Azure Maps provider")
        
        # Test URL generation with known coordinates
        test_tile = {
            'lat': 47.6205,  # Seattle Space Needle
            'lng': -122.3493,
            'lat_for_url': 47.6205,
            'id': 'test_tile_001'
        }
        
        url = azure_maps.get_url(test_tile)
        print(f"✅ Successfully generated URL: {url[:80]}...")
        
        # Validate URL components
        required_components = [
            "https://atlas.microsoft.com/map/static?",
            "api-version=2024-04-01",
            "tilesetId=microsoft.imagery",
            "zoom=19",
            "center=-122.3493,47.6205",  # Critical: lng,lat order
            "height=640",
            "width=640",
            "subscription-key=test_subscription_key_12345"
        ]
        
        all_found = True
        for component in required_components:
            if component in url:
                print(f"✅ URL contains: {component}")
            else:
                print(f"❌ URL missing: {component}")
                all_found = False
        
        if not all_found:
            return False
            
        # Test coordinate transformation accuracy
        test_locations = [
            {'name': 'NYC Central Park', 'lat': 40.7829, 'lng': -73.9654, 'expected': '-73.9654,40.7829'},
            {'name': 'London Big Ben', 'lat': 51.4994, 'lng': -0.1245, 'expected': '-0.1245,51.4994'},
            {'name': 'Tokyo Tower', 'lat': 35.6586, 'lng': 139.7454, 'expected': '139.7454,35.6586'}
        ]
        
        for location in test_locations:
            tile = {'lat': location['lat'], 'lng': location['lng'], 'lat_for_url': location['lat']}
            url = azure_maps.get_url(tile)
            if f"center={location['expected']}" in url:
                print(f"✅ {location['name']}: Coordinate transformation correct")
            else:
                print(f"❌ {location['name']}: Coordinate transformation failed")
                return False
        
        # Test maptype conversion
        print("\nTesting maptype conversions...")
        maptype_tests = [
            ('satellite', 'microsoft.imagery'),
            ('road', 'microsoft.base.road'),
            ('hybrid', 'microsoft.imagery')
        ]
        
        for maptype, expected_tileset in maptype_tests:
            url = azure_maps.get_url(test_tile, maptype=maptype)
            if f"tilesetId={expected_tileset}" in url:
                print(f"✅ {maptype} → {expected_tileset}")
            else:
                print(f"❌ {maptype} conversion failed")
                return False
        
        # Test custom parameters
        print("\nTesting custom parameters...")
        custom_url = azure_maps.get_url(test_tile, zoom=15, size="800,600")
        if "zoom=15" in custom_url and "height=600" in custom_url and "width=800" in custom_url:
            print("✅ Custom parameters work correctly")
        else:
            print("❌ Custom parameters failed")
            return False
        
        # Test error handling
        print("\nTesting error handling...")
        try:
            AzureMaps("")  # Empty subscription key
            print("❌ Should have raised ConfigurationError")
            return False
        except MockConfigurationError:
            print("✅ ConfigurationError raised for empty subscription key")
        
        # Test invalid coordinates
        try:
            invalid_tile = {'lat': 95.0, 'lng': -122.3493, 'lat_for_url': 95.0}  # Invalid lat
            azure_maps.get_url(invalid_tile)
            print("❌ Should have raised MapProviderError for invalid coordinates")
            return False
        except MockMapProviderError:
            print("✅ MapProviderError raised for invalid coordinates")
        
        # Test metadata handling
        print("\nTesting metadata handling...")
        if not azure_maps.has_metadata:
            print("✅ has_metadata correctly set to False")
        else:
            print("❌ has_metadata should be False")
            return False
        
        try:
            azure_maps.get_meta_url(test_tile)
            print("❌ get_meta_url should raise NotImplementedError")
            return False
        except NotImplementedError:
            print("✅ get_meta_url correctly raises NotImplementedError")
        
        date = azure_maps.get_date("any_metadata")
        if date == "":
            print("✅ get_date returns empty string")
        else:
            print("❌ get_date should return empty string")
            return False
        
        # Test provider info
        print("\nTesting provider info...")
        info = azure_maps.get_provider_info()
        expected_keys = ['provider', 'base_url', 'api_version', 'has_metadata', 'subscription_key_configured', 'coordinate_system']
        for key in expected_keys:
            if key in info:
                print(f"✅ Info contains {key}: {info[key]}")
            else:
                print(f"❌ Info missing key: {key}")
                return False
        
        print("\n🎉 All Azure Maps provider tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Azure Maps provider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the Azure Maps direct test."""
    print("=" * 60)
    print("AZURE MAPS PROVIDER DIRECT TEST")
    print("=" * 60)
    
    if test_azure_maps_direct():
        print("\n✅ SUCCESS: Azure Maps provider is fully functional!")
        return 0
    else:
        print("\n❌ FAILURE: Azure Maps provider has issues!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)