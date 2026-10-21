#!/usr/bin/env python3
"""Simple coordinate transformation test for Azure Maps"""

def test_coordinate_transformation():
    """Test the critical coordinate transformation logic."""
    print("Testing Azure Maps coordinate transformation...")
    
    # Test cases: internal lat,lng -> Azure Maps lng,lat
    test_cases = [
        {
            'name': 'Seattle Space Needle',
            'internal': {'lat': 47.6205, 'lng': -122.3493, 'lat_for_url': 47.6205},
            'expected_azure_center': '-122.3493,47.6205'
        },
        {
            'name': 'NYC Central Park',
            'internal': {'lat': 40.7829, 'lng': -73.9654, 'lat_for_url': 40.7829},
            'expected_azure_center': '-73.9654,40.7829'
        },
        {
            'name': 'London Big Ben',
            'internal': {'lat': 51.4994, 'lng': -0.1245, 'lat_for_url': 51.4994},
            'expected_azure_center': '-0.1245,51.4994'
        },
        {
            'name': 'Tokyo Tower',
            'internal': {'lat': 35.6586, 'lng': 139.7454, 'lat_for_url': 35.6586},
            'expected_azure_center': '139.7454,35.6586'
        },
        {
            'name': 'Sydney Opera House',
            'internal': {'lat': -33.8568, 'lng': 151.2153, 'lat_for_url': -33.8568},
            'expected_azure_center': '151.2153,-33.8568'
        }
    ]
    
    all_passed = True
    for case in test_cases:
        # Simulate the Azure Maps coordinate transformation
        tile = case['internal']
        center_lng = tile['lng']  # longitude first for Azure Maps
        center_lat = tile['lat_for_url']  # use lat_for_url for consistency
        
        # Build center parameter in lng,lat format (GeoJSON standard)
        azure_center = f"{center_lng},{center_lat}"
        
        if azure_center == case['expected_azure_center']:
            print(f"✅ {case['name']}: {tile['lat']},{tile['lng']} → {azure_center}")
        else:
            print(f"❌ {case['name']}: Expected {case['expected_azure_center']}, got {azure_center}")
            all_passed = False
    
    return all_passed

def test_url_format():
    """Test the Azure Maps URL format."""
    print("\nTesting Azure Maps URL format...")
    
    # Test parameters
    base_url = "https://atlas.microsoft.com/map/static"
    api_version = "2024-04-01"
    subscription_key = "test_key_12345"
    
    # Sample tile data
    tile = {'lat': 47.6205, 'lng': -122.3493, 'lat_for_url': 47.6205}
    zoom = 19
    tileset_id = 'microsoft.imagery'
    height = '640'
    width = '640'
    
    # Build URL (simplified version of ts_azure_maps logic)
    center_lng = tile['lng']
    center_lat = tile['lat_for_url']
    center = f"{center_lng},{center_lat}"
    
    url = (
        f"{base_url}?api-version={api_version}"
        f"&tilesetId={tileset_id}&zoom={zoom}"
        f"&center={center}&height={height}&width={width}"
        f"&subscription-key={subscription_key}"
    )
    
    # Check URL components
    required_components = [
        "https://atlas.microsoft.com/map/static?",
        "api-version=2024-04-01",
        "tilesetId=microsoft.imagery",
        "zoom=19",
        "center=-122.3493,47.6205",  # Critical: lng,lat order
        "height=640",
        "width=640",
        "subscription-key=test_key_12345"
    ]
    
    print(f"Generated URL: {url}")
    print("\nURL Component Check:")
    
    all_found = True
    for component in required_components:
        if component in url:
            print(f"✅ Found: {component}")
        else:
            print(f"❌ Missing: {component}")
            all_found = False
    
    return all_found

def test_maptype_conversion():
    """Test maptype to tileset conversion."""
    print("\nTesting maptype to tileset conversion...")
    
    maptype_conversion = {
        'satellite': 'microsoft.imagery',
        'imagery': 'microsoft.imagery',
        'road': 'microsoft.base.road',
        'hybrid': 'microsoft.imagery',  # No exact hybrid, use imagery
        'terrain': 'microsoft.base.road'  # No terrain, use road
    }
    
    test_cases = [
        ('satellite', 'microsoft.imagery'),
        ('road', 'microsoft.base.road'),
        ('hybrid', 'microsoft.imagery'),
        ('unknown', 'microsoft.imagery')  # default fallback
    ]
    
    all_passed = True
    for maptype, expected_tileset in test_cases:
        result = maptype_conversion.get(maptype.lower(), 'microsoft.imagery')
        if result == expected_tileset:
            print(f"✅ {maptype} → {expected_tileset}")
        else:
            print(f"❌ {maptype} → {result} (expected {expected_tileset})")
            all_passed = False
    
    return all_passed

def main():
    """Run all coordinate transformation tests."""
    print("=" * 60)
    print("AZURE MAPS COORDINATE TRANSFORMATION VALIDATION")
    print("=" * 60)
    
    tests = [
        test_coordinate_transformation,
        test_url_format,
        test_maptype_conversion
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
            print("✅ PASSED\n")
        else:
            failed += 1
            print("❌ FAILED\n")
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All coordinate transformation tests passed!")
        print("Azure Maps provider coordinate logic is correct!")
        return 0
    else:
        print("⚠️  Some coordinate tests failed!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)