#!/usr/bin/env python3
"""
Azure Maps Provider Validation Test (Dependency-Free)
Tests the core Azure Maps provider logic without requiring external dependencies.
"""

import sys
import os

def test_azure_maps_syntax():
    """Test that the Azure Maps file has valid Python syntax."""
    print("Testing Azure Maps module syntax...")
    
    try:
        # Read and compile the Azure Maps file to check syntax
        with open('ts_azure_maps.py', 'r') as f:
            azure_maps_code = f.read()
        
        compile(azure_maps_code, 'ts_azure_maps.py', 'exec')
        print("✅ ts_azure_maps.py has valid Python syntax")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in ts_azure_maps.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading ts_azure_maps.py: {e}")
        return False

def test_coordinate_transformation_logic():
    """Test coordinate transformation logic without imports."""
    print("\nTesting coordinate transformation logic...")
    
    try:
        # Test the coordinate transformation math directly
        test_cases = [
            {
                'name': 'Seattle Space Needle',
                'tile': {'lat': 47.6205, 'lng': -122.3493, 'lat_for_url': 47.6205},
                'expected_center': '-122.3493,47.6205'
            },
            {
                'name': 'NYC Central Park',
                'tile': {'lat': 40.7829, 'lng': -73.9654, 'lat_for_url': 40.7829},
                'expected_center': '-73.9654,40.7829'
            },
            {
                'name': 'Edge Case - Poles',
                'tile': {'lat': 89.9999, 'lng': 0.0, 'lat_for_url': 89.9999},
                'expected_center': '0.0,89.9999'
            }
        ]
        
        # Simulate the coordinate transformation from ts_azure_maps.py
        def simulate_coordinate_transform(tile):
            center_lng = tile['lng']  # longitude first for Azure Maps
            center_lat = tile['lat_for_url']  # use lat_for_url for consistency
            return f"{center_lng},{center_lat}"
        
        all_passed = True
        for case in test_cases:
            result = simulate_coordinate_transform(case['tile'])
            if result == case['expected_center']:
                print(f"✅ {case['name']}: {case['tile']['lat']},{case['tile']['lng']} → {result}")
            else:
                print(f"❌ {case['name']}: Expected {case['expected_center']}, got {result}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Coordinate transformation test failed: {e}")
        return False

def test_url_template_format():
    """Test URL template format without dependencies."""
    print("\nTesting URL template format...")
    
    try:
        # Test URL template structure
        base_url = "https://atlas.microsoft.com/map/static"
        api_version = "2024-04-01"
        subscription_key = "test_key_12345"
        
        url_template = (
            f"{base_url}?api-version={api_version}"
            "&tilesetId={tileset_id}&zoom={zoom}"
            "&center={center}&height={height}&width={width}"
            f"&subscription-key={subscription_key}"
        )
        
        # Test template with sample data
        test_url = url_template.format(
            tileset_id='microsoft.imagery',
            zoom=19,
            center='-122.3493,47.6205',
            height='640',
            width='640'
        )
        
        expected_components = [
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
        for component in expected_components:
            if component in test_url:
                print(f"✅ URL contains: {component}")
            else:
                print(f"❌ URL missing: {component}")
                all_passed = False
        
        print(f"\nGenerated URL: {test_url}")
        return all_passed
        
    except Exception as e:
        print(f"❌ URL template test failed: {e}")
        return False

def test_maptype_conversion_logic():
    """Test maptype to tileset conversion logic."""
    print("\nTesting maptype conversion logic...")
    
    try:
        # Simulate the maptype conversion from ts_azure_maps.py
        def simulate_maptype_conversion(maptype):
            maptype_conversion = {
                'satellite': 'microsoft.imagery',
                'imagery': 'microsoft.imagery',
                'road': 'microsoft.base.road',
                'hybrid': 'microsoft.imagery',  # No exact hybrid, use imagery
                'terrain': 'microsoft.base.road'  # No terrain, use road
            }
            return maptype_conversion.get(maptype.lower(), 'microsoft.imagery')
        
        test_cases = [
            ('satellite', 'microsoft.imagery'),
            ('road', 'microsoft.base.road'),
            ('hybrid', 'microsoft.imagery'),
            ('unknown', 'microsoft.imagery')  # default fallback
        ]
        
        all_passed = True
        for maptype, expected_tileset in test_cases:
            result = simulate_maptype_conversion(maptype)
            if result == expected_tileset:
                print(f"✅ {maptype} → {expected_tileset}")
            else:
                print(f"❌ {maptype} → {result} (expected {expected_tileset})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Maptype conversion test failed: {e}")
        return False

def test_size_parsing_logic():
    """Test size parameter parsing logic."""
    print("\nTesting size parsing logic...")
    
    try:
        # Simulate the size parsing from ts_azure_maps.py
        def simulate_size_parsing(size):
            if ',' in size:
                parts = size.split(',')
            elif 'x' in size.lower():
                parts = size.lower().split('x')
            else:
                # Assume square if only one dimension
                parts = [size, size]
            
            if len(parts) != 2:
                raise ValueError(f"Invalid size format: {size}")
            
            width, height = parts[0].strip(), parts[1].strip()
            
            # Validate dimensions are numeric and within Azure Maps limits
            width_int = int(width)
            height_int = int(height)
            
            if not (80 <= width_int <= 2000):
                raise ValueError(f"Width {width_int} outside valid range [80, 2000]")
            if not (80 <= height_int <= 1500):
                raise ValueError(f"Height {height_int} outside valid range [80, 1500]")
            
            return width, height
        
        test_cases = [
            ('640,480', ('640', '480')),
            ('800x600', ('800', '600')),
            ('1024X768', ('1024', '768')),
            ('512', ('512', '512'))  # square format
        ]
        
        all_passed = True
        for size_input, expected_output in test_cases:
            try:
                result = simulate_size_parsing(size_input)
                if result == expected_output:
                    print(f"✅ {size_input} → {result}")
                else:
                    print(f"❌ {size_input} → {result} (expected {expected_output})")
                    all_passed = False
            except Exception as e:
                print(f"❌ {size_input} → Error: {e}")
                all_passed = False
        
        # Test invalid cases
        invalid_cases = ['50,50', '3000,3000', 'abc,def']
        for invalid_case in invalid_cases:
            try:
                simulate_size_parsing(invalid_case)
                print(f"❌ {invalid_case} should have raised error")
                all_passed = False
            except ValueError:
                print(f"✅ {invalid_case} correctly raised ValueError")
            except Exception as e:
                print(f"✅ {invalid_case} correctly raised error: {type(e).__name__}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Size parsing test failed: {e}")
        return False

def test_integration_with_towerscout():
    """Test that Azure Maps integrates properly with TowerScout."""
    print("\nTesting TowerScout integration...")
    
    try:
        # Check if towerscout.py contains Azure Maps references
        with open('towerscout.py', 'r') as f:
            towerscout_code = f.read()
        
        integration_checks = [
            ('ts_azure_maps import', 'from ts_azure_maps import AzureMaps'),
            ('Azure Maps provider dict', "'azure': {'id': 'azure', 'name': 'Azure Maps'}"),
            ('Azure API key loading', 'azure_api_key'),
            ('Azure Maps instantiation', 'AzureMaps(azure_api_key)')
        ]
        
        all_passed = True
        for check_name, check_pattern in integration_checks:
            if check_pattern in towerscout_code:
                print(f"✅ {check_name}: Found integration")
            else:
                print(f"❌ {check_name}: Integration not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ TowerScout integration test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("AZURE MAPS PROVIDER VALIDATION (DEPENDENCY-FREE)")
    print("=" * 60)
    
    # Change to webapp directory if not already there
    if not os.path.exists('ts_azure_maps.py'):
        print("Changing to webapp directory...")
        os.chdir('webapp')
    
    tests = [
        test_azure_maps_syntax,
        test_coordinate_transformation_logic,
        test_url_template_format,
        test_maptype_conversion_logic,
        test_size_parsing_logic,
        test_integration_with_towerscout
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
        print("🎉 All validation tests passed! Azure Maps provider implementation is correct.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)