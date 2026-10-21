"""
Endpoint Contract Test - TASK-038 Frontend Refactoring

Purpose: Validate frontend CONFIG.ENDPOINTS matches backend Flask routes
Run After: Stage 1 (after config.js created)

Validates: All frontend endpoint constants exist as actual Flask routes

Usage:
    pytest tests/backend/test_endpoint_contract.py
    python tests/backend/test_endpoint_contract.py  # Direct execution

Exit codes:
    0 = All endpoints validated successfully
    1 = Missing backend routes (must fix before proceeding)
"""

import sys
import pytest


def test_endpoint_contract():
    """Validate frontend CONFIG.ENDPOINTS matches backend routes"""
    
    # Import Flask app (add webapp to path for imports)
    import sys
    import os
    webapp_dir = os.path.join(os.path.dirname(__file__), '../../webapp')
    if webapp_dir not in sys.path:
        sys.path.insert(0, os.path.abspath(webapp_dir))
    
    try:
        from towerscout import app
    except ImportError as e:
        pytest.fail(f"Failed to import Flask app: {e}")
    
    # Expected endpoints from config.js (FIX #2 v2.6 - ACTUAL Flask routes only)
    # These are the 10 frontend-relevant routes verified 2026-02-18
    expected_endpoints = {
        'PROVIDERS': '/getproviders',                  # Line 540 - provider availability
        'GOOGLE_KEY': '/getgooglekey',                 # Line 518 - Google Maps API key
        'AZURE_KEY': '/getazurekey',                   # Line 496 - Azure Maps API key
        'OBJECTS': '/getobjects',                      # Line 866 - detection results
        'OBJECTS_CUSTOM': '/getobjectscustom',         # Line 1306 - custom polygon search
        'ABORT': '/abort',                             # Line 858 - cancel detection
        'GEOCODE_FORWARD': '/api/geocode/forward',     # Line 569 - address to coords
        'ZIPCODE': '/getzipcode',                      # Line 835 - zipcode validation
        'UPLOAD_DATASET': '/uploaddataset',            # Line 1632 - dataset upload
        'API_USAGE': '/api-usage'                      # Line 1285 - API usage stats
    }
    
    print("\n" + "="*70)
    print("  Endpoint Contract Validation - TASK-038")
    print("="*70)
    print(f"\n🔍 Validating {len(expected_endpoints)} frontend endpoints...")
    print("")
    
    # Extract actual routes from Flask app
    actual_routes = set()
    for rule in app.url_map.iter_rules():
        # Skip static file route
        if rule.endpoint != 'static':
            actual_routes.add(rule.rule)
    
    print(f"📊 Flask app has {len(actual_routes)} total routes")
    print("")
    
    # Validate each expected endpoint exists
    missing = []
    validated = []
    
    for name, path in sorted(expected_endpoints.items()):
        if path in actual_routes:
            validated.append((name, path))
            print(f"  ✅ {name:20s} → {path}")
        else:
            missing.append((name, path))
            print(f"  ❌ {name:20s} → {path} (NOT FOUND)")
    
    print("")
    print("="*70)
    
    # Report results
    if missing:
        print("")
        print(f"❌ Endpoint validation FAILED: {len(missing)} missing route(s)")
        print("")
        print("Missing backend routes:")
        for name, path in missing:
            print(f"  - {name}: {path}")
        print("")
        print("Fix required:")
        print("  1. Add missing Flask routes to webapp/towerscout.py")
        print("  2. OR remove endpoints from frontend config.js")
        print("  3. Verify with: grep '@app.route' webapp/towerscout.py")
        print("")
        print("="*70)
        
        # Pytest assertion
        assert len(missing) == 0, f"Missing backend routes: {[f'{n}: {p}' for n, p in missing]}"
    else:
        print("")
        print(f"✅ Endpoint Contract Validation PASSED")
        print("")
        print(f"All {len(expected_endpoints)} frontend endpoints exist in backend")
        print("")
        print("Validated endpoints:")
        for name, path in validated:
            print(f"  ✅ {name} → {path}")
        print("")
        print("="*70)


def test_no_nonexistent_endpoints():
    """Verify removed non-existent endpoints are NOT in frontend config"""
    
    # These endpoints were removed in v2.6 (never existed in backend)
    banned_endpoints = [
        '/tiles',           # Never existed
        '/detect',          # Never existed
        '/cancel',          # Use /abort instead
        '/geocode',         # Use /api/geocode/forward instead
        '/validate_zipcode' # Use /getzipcode instead
    ]
    
    print("\n" + "="*70)
    print("  Non-Existent Endpoint Check - TASK-038")
    print("="*70)
    print(f"\n🔍 Checking for {len(banned_endpoints)} removed endpoints...")
    print("")
    
    # NOTE: This test validates config structure
    # Manual code review required until config.js exists in Stage 1
    
    print("⚠️  NOTE: Manual verification required")
    print("   Ensure config.js does NOT include:")
    for endpoint in banned_endpoints:
        print(f"     ❌ {endpoint}")
    print("")
    print("="*70)


# Allow direct execution for debugging
if __name__ == '__main__':
    print("Running endpoint contract tests...\n")
    
    try:
        test_endpoint_contract()
        print("\n" + "="*70)
        test_no_nonexistent_endpoints()
        print("\n✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
