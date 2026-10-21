#!/usr/bin/env python3
"""
TowerScout Development Test Script

This script tests the error handling and logging system without requiring
all ML dependencies, helping to isolate configuration issues.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_error_handling():
    """Test the error handling and logging system."""
    try:
        print("🔧 Testing TowerScout Error Handling System")
        print("=" * 50)
        
        # Test 1: Basic imports
        print("1. Testing basic imports...")
        from ts_errors import (
            TowerScoutError, ConfigurationError, ModelLoadError, 
            MapProviderError, create_error_response
        )
        from ts_logging import (
            TowerScoutLogger, get_main_logger, get_maps_logger, 
            get_ml_logger, get_api_logger
        )
        print("   ✅ All error handling modules imported successfully")
        
        # Test 2: Logger initialization
        print("2. Testing logger initialization...")
        logger = get_main_logger()
        api_logger = get_api_logger() 
        ml_logger = get_ml_logger()
        maps_logger = get_maps_logger()
        print("   ✅ All loggers initialized successfully")
        
        # Test 3: Environment variable loading
        print("3. Testing environment variables...")
        google_key = os.getenv('GOOGLE_API_KEY')
        bing_key = os.getenv('BING_API_KEY')
        flask_secret = os.getenv('FLASK_SECRET_KEY')
        
        if google_key:
            print(f"   ✅ GOOGLE_API_KEY: {google_key[:10]}...")
        else:
            print("   ⚠️  GOOGLE_API_KEY not found")
            
        if bing_key:
            print(f"   ✅ BING_API_KEY: {bing_key[:10]}...")
        else:
            print("   ⚠️  BING_API_KEY not found")
            
        if flask_secret:
            print(f"   ✅ FLASK_SECRET_KEY: {flask_secret[:10]}...")
        else:
            print("   ⚠️  FLASK_SECRET_KEY not found")
        
        # Test 4: Error creation and serialization
        print("4. Testing error creation...")
        test_error = ConfigurationError(
            "Test configuration error",
            missing_config="TEST_KEY"
        )
        error_dict = test_error.to_dict()
        print(f"   ✅ Error serialized: {error_dict['type']}")
        
        # Test 5: Logging functionality
        print("5. Testing logging functionality...")
        logger.info("Test info message")
        logger.warning("Test warning message") 
        logger.error("Test error message")
        print("   ✅ Logging messages written successfully")
        
        # Test 6: API key loading function
        print("6. Testing API key loading logic...")
        def load_api_keys_test():
            google_key = os.getenv('GOOGLE_API_KEY')
            bing_key = os.getenv('BING_API_KEY')
            
            if not google_key:
                raise ConfigurationError(
                    "GOOGLE_API_KEY environment variable is required",
                    missing_config="GOOGLE_API_KEY"
                )
            
            if not bing_key:
                logger.warning("BING_API_KEY not configured. Bing Maps provider will be unavailable.")
                bing_key = ""
            
            return google_key, bing_key
        
        try:
            google_api_key, bing_api_key = load_api_keys_test()
            print("   ✅ API key loading successful")
        except ConfigurationError as e:
            print(f"   ⚠️  Configuration error: {e.message}")
            print("   💡 To fix: Add GOOGLE_API_KEY to your .env file")
        
        print("\n" + "=" * 50)
        print("🎉 Error Handling System Test Completed")
        
        # Summary
        missing_deps = []
        if not google_key:
            missing_deps.append("GOOGLE_API_KEY")
        if not flask_secret:
            missing_deps.append("FLASK_SECRET_KEY")
            
        if missing_deps:
            print(f"⚠️  Missing environment variables: {', '.join(missing_deps)}")
            print("💡 Please check your .env file configuration")
        else:
            print("✅ All required environment variables configured")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_ml_dependencies():
    """Check if ML dependencies are available."""
    print("\n🔬 Checking ML Dependencies")
    print("=" * 30)
    
    deps = ['torch', 'torchvision', 'efficientnet_pytorch', 'PIL']
    available = []
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
            available.append(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            missing.append(dep)
            print(f"   ❌ {dep}")
    
    if missing:
        print(f"\n⚠️  Missing ML dependencies: {', '.join(missing)}")
        print("💡 Install with: pip install torch torchvision efficientnet_pytorch Pillow")
    else:
        print("\n✅ All ML dependencies available")
        
    return len(missing) == 0

if __name__ == "__main__":
    print("TowerScout Development Test")
    print("Testing error handling system...")
    
    # Test core error handling
    error_system_ok = test_error_handling()
    
    # Test ML dependencies
    ml_deps_ok = check_ml_dependencies()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Error Handling System: {'✅ PASS' if error_system_ok else '❌ FAIL'}")
    print(f"ML Dependencies: {'✅ PASS' if ml_deps_ok else '⚠️  MISSING'}")
    
    if error_system_ok and not ml_deps_ok:
        print("\n💡 The error handling system works correctly!")
        print("   Install ML dependencies to run the full application:")
        print("   pip install torch torchvision efficientnet_pytorch Pillow")
    elif error_system_ok and ml_deps_ok:
        print("\n🚀 Everything looks good! You should be able to run TowerScout.")
    else:
        print("\n🔧 Fix the error handling issues before proceeding.")
        
    sys.exit(0 if error_system_ok else 1)