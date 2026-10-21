#!/usr/bin/env python3
"""
Azure Maps Provider Integration Test
Tests the Azure Maps provider implementation and coordinate transformation accuracy.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Add webapp directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'webapp'))

def test_imports():
    """Test that all Azure Maps components can be imported."""
    print("Testing imports...")
    
    try:
        from ts_azure_maps import AzureMaps, create_azure_maps_provider
        print("✅ Azure Maps provider import successful")
    except Exception as e:
        print(f"❌ Azure Maps provider import failed: {e}")
        return False
    
    try:
        # Test that Azure Maps can be imported in towerscout.py context
        from ts_errors import MapProviderError, ConfigurationError
        from ts_logging import get_maps_logger
        print("✅ Error handling imports successful")
    except Exception as e:
        print(f"❌ Error handling imports failed: {e}")
        return False
    
    return True

def test_coordinate_transformation():
    """Test critical coordinate transformation accuracy."""
    print("\nTesting coordinate transformation...")
    
    try:
        from ts_azure_maps import AzureMaps
        
        # Known test locations
        test_locations = [
            {
                'name': 'Seattle Space Needle',
                'lat': 47.6205, 'lng': -122.3493,
                'expected_center': '-122.3493,47.6205'
            },
            {
                'name': 'NYC Central Park',
                'lat': 40.7829, 'lng': -73.9654,
                'expected_center': '-73.9654,40.7829'
            },
            {
                'name': 'London Big Ben',
                'lat': 51.4994, 'lng': -0.1245,
                'expected_center': '-0.1245,51.4994'
            }
        ]
        
        azure_maps = AzureMaps("test_subscription_key")
        
        all_passed = True
        for location in test_locations:
            tile = {
                'lat': location['lat'],
                'lng': location['lng'],
                'lat_for_url': location['lat']
            }
            
            url = azure_maps.get_url(tile)
            
            if f"center={location['expected_center']}" in url:
                print(f"✅ {location['name']}: Coordinate transformation correct")
            else:
                print(f"❌ {location['name']}: Coordinate transformation failed")
                print(f"   Expected: center={location['expected_center']}")
                print(f"   Got URL: {url}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Coordinate transformation test failed: {e}")
        return False

def test_url_generation():
    """Test URL generation with various parameters."""
    print("\nTesting URL generation...")
    
    try:
        from ts_azure_maps import AzureMaps
        
        azure_maps = AzureMaps("test_key_12345")
        test_tile = {
            'lat': 47.6205,
            'lng': -122.3493,
            'lat_for_url': 47.6205
        }
        
        # Test default URL generation
        url = azure_maps.get_url(test_tile)
        
        required_components = [
            "https://atlas.microsoft.com/map/static?",
            "api-version=2024-04-01",
            "tilesetId=microsoft.imagery",
            "zoom=19",
            "center=-122.3493,47.6205",
            "height=640",
            "width=640",
            "subscription-key=test_key_12345"
        ]
        
        all_passed = True
        for component in required_components:
            if component in url:
                print(f"✅ URL contains: {component}")
            else:
                print(f"❌ URL missing: {component}")
                all_passed = False
        
        print(f"Generated URL: {url}")
        return all_passed
        
    except Exception as e:
        print(f"❌ URL generation test failed: {e}")
        return False

def test_maptype_conversion():
    """Test maptype to tileset conversion."""
    print("\nTesting maptype conversion...")
    
    try:
        from ts_azure_maps import AzureMaps
        
        azure_maps = AzureMaps("test_key")
        
        test_cases = [
            ('satellite', 'microsoft.imagery'),
            ('road', 'microsoft.base.road'),
            ('hybrid', 'microsoft.imagery'),
            ('unknown', 'microsoft.imagery')
        ]
        
        all_passed = True
        for maptype, expected_tileset in test_cases:
            result = azure_maps._convert_maptype_to_tileset(maptype)
            if result == expected_tileset:
                print(f"✅ {maptype} → {expected_tileset}")
            else:
                print(f"❌ {maptype} → {result} (expected {expected_tileset})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Maptype conversion test failed: {e}")
        return False

def test_error_handling():
    """Test error handling integration."""
    print("\nTesting error handling...")
    
    try:
        from ts_azure_maps import AzureMaps
        from ts_errors import ConfigurationError, MapProviderError
        
        # Test missing subscription key
        try:
            AzureMaps("")
            print("❌ Should have raised ConfigurationError for empty key")
            return False
        except ConfigurationError as e:
            print("✅ ConfigurationError raised for empty key")
            if e.error_code == "AZURE_MAPS_NO_KEY":
                print("✅ Correct error code set")
            else:
                print(f"❌ Wrong error code: {e.error_code}")
        
        # Test invalid coordinates
        azure_maps = AzureMaps("test_key")
        invalid_tile = {
            'lat': 95.0,  # Invalid latitude
            'lng': -122.3493,
            'lat_for_url': 95.0
        }
        
        try:
            azure_maps.get_url(invalid_tile)
            print("❌ Should have raised MapProviderError for invalid coordinates")
            return False
        except MapProviderError as e:
            print("✅ MapProviderError raised for invalid coordinates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_metadata_handling():
    """Test metadata handling (should be disabled for Azure Maps)."""
    print("\nTesting metadata handling...")
    
    try:
        from ts_azure_maps import AzureMaps
        
        azure_maps = AzureMaps("test_key")
        
        # Check has_metadata flag
        if not azure_maps.has_metadata:
            print("✅ has_metadata correctly set to False")
        else:
            print("❌ has_metadata should be False for Azure Maps")
            return False
        
        # Test get_meta_url raises NotImplementedError
        try:
            azure_maps.get_meta_url({'lat': 47.6205, 'lng': -122.3493})
            print("❌ get_meta_url should raise NotImplementedError")
            return False
        except NotImplementedError:
            print("✅ get_meta_url correctly raises NotImplementedError")
        
        # Test get_date returns empty string
        date = azure_maps.get_date("any_metadata")
        if date == "":
            print("✅ get_date returns empty string")
        else:
            print(f"❌ get_date should return empty string, got: {date}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Metadata handling test failed: {e}")
        return False

def test_environment_integration():
    """Test environment variable integration."""
    print("\nTesting environment variable integration...")
    
    try:
        from ts_azure_maps import AzureMaps
        from ts_errors import ConfigurationError
        
        # Test from_environment with mock environment
        with patch.dict(os.environ, {'AZURE_MAPS_SUBSCRIPTION_KEY': 'env_test_key'}):
            provider = AzureMaps.from_environment()
            if provider.subscription_key == 'env_test_key':
                print("✅ from_environment works with environment variable")
            else:
                print(f"❌ Wrong subscription key from environment: {provider.subscription_key}")
                return False
        
        # Test from_environment without environment variable
        with patch.dict(os.environ, {}, clear=True):
            try:
                AzureMaps.from_environment()
                print("❌ Should have raised ConfigurationError for missing env var")
                return False
            except ConfigurationError as e:
                print("✅ ConfigurationError raised for missing environment variable")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment integration test failed: {e}")
        return False

def test_provider_info():
    """Test provider information retrieval."""
    print("\nTesting provider info...")
    
    try:
        from ts_azure_maps import AzureMaps
        
        azure_maps = AzureMaps("test_key")
        info = azure_maps.get_provider_info()
        
        expected_keys = [
            'provider', 'base_url', 'api_version',
            'has_metadata', 'subscription_key_configured', 'coordinate_system'
        ]
        
        all_passed = True
        for key in expected_keys:
            if key in info:
                print(f"✅ Info contains: {key} = {info[key]}")
            else:
                print(f"❌ Info missing: {key}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Provider info test failed: {e}")
        return False

def main():
    """Run all Azure Maps integration tests."""
    print("=" * 60)
    print("AZURE MAPS PROVIDER INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_coordinate_transformation,
        test_url_generation,
        test_maptype_conversion,
        test_error_handling,
        test_metadata_handling,
        test_environment_integration,
        test_provider_info
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                failed += 1
                print("❌ FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {e}\n")
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Azure Maps provider is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)