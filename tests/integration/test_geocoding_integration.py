"""
Integration tests for TowerScout geocoding functionality.

Tests the end-to-end geocoding workflow including Flask routes,
detection processing, and frontend integration.

Author: TowerScout Development Team
Date: January 2026
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from requests.exceptions import ConnectionError
import json
import tempfile
import os
import sys

# Add webapp to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))

# Test imports
try:
    from ts_geocoding import GeocodingService, GeocodingResult, GeocodingProvider
    from ts_geocache import GeocodingCache
    GEOCODING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Geocoding imports failed: {e}")
    GEOCODING_AVAILABLE = False


class TestGeocodingEndToEnd(unittest.TestCase):
    """Test complete geocoding workflow from detection to frontend display."""

    def setUp(self):
        """Set up test fixtures."""
        if not GEOCODING_AVAILABLE:
            self.skipTest("Geocoding modules not available")

        self.app = Flask(__name__)
        self.app.secret_key = "synthetic-session-key"
        self.cache_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.cache_dir.cleanup)
        cache_path = patch('ts_geocache.get_geocoding_cache_dir', return_value=self.cache_dir.name)
        cache_path.start()
        self.addCleanup(cache_path.stop)
            
        self.test_detection_results = [
            {
                'x1': -122.3503, 'y1': 47.6215, 'x2': -122.3493, 'y2': 47.6195,
                'class': 0, 'class_name': 'cooling_tower', 'conf': 0.85,
                'tile': 0, 'id_in_tile': 0, 'inside': True, 'selected': True, 'secondary': 0.9
            },
            {
                'x1': -122.3523, 'y1': 47.6225, 'x2': -122.3513, 'y2': 47.6205,
                'class': 0, 'class_name': 'cooling_tower', 'conf': 0.75,
                'tile': 0, 'id_in_tile': 1, 'inside': True, 'selected': True, 'secondary': 0.8
            }
        ]

    @patch('ts_geocoding.provider_get')
    def test_detection_address_lookup_workflow(self, mock_get):
        """Test complete workflow from detection results to address lookup."""
        # Mock successful Azure Maps response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'summary': {'numResults': 1},
            'addresses': [{
                'address': {'freeformAddress': '123 Enterprise Building, Seattle, WA'},
                'matchType': 'AddressPoint'
            }]
        }
        mock_get.return_value = mock_response
        
        # Initialize geocoding service
        service = GeocodingService(azure_key="test_azure_key")
        cache = GeocodingCache(clustering_radius_meters=50.0)
        
        # Simulate the workflow from towerscout.py get_objects route
        detection_results = self.test_detection_results.copy()
        
        with self.app.test_request_context():
            for detection in detection_results:
                if detection.get('class') == 0:  # Only geocode actual detections
                    # Calculate center coordinates
                    center_lat = (detection['y1'] + detection['y2']) / 2
                    center_lng = (detection['x1'] + detection['x2']) / 2
                    
                    result = service.reverse_geocode(center_lat, center_lng)
                    self.assertTrue(result.success)
                    detection['address'] = result.address
                    detection['address_confidence'] = result.confidence
                    detection['address_provider'] = result.provider.value
                    cache.put(center_lat, center_lng, result, provider=GeocodingProvider.AZURE_MAPS)

        self.assertEqual(mock_get.call_count, len(detection_results))
        
        # Verify results
        for detection in detection_results:
            if detection.get('class') == 0:
                self.assertIn('address', detection)
                self.assertIn('address_confidence', detection)
                self.assertIn('address_provider', detection)
                
                self.assertEqual(detection['address'], '123 Enterprise Building, Seattle, WA')
                self.assertEqual(detection['address_provider'], 'azure_maps')
                self.assertGreater(detection['address_confidence'], 0.0)

    def test_spatial_clustering_workflow(self):
        """Test spatial clustering reduces API calls for nearby detections."""
        cache = GeocodingCache(clustering_radius_meters=100.0)  # 100m clustering
        
        # Create nearby detections (within clustering radius)
        nearby_detections = [
            {'lat': 47.6205, 'lng': -122.3493},  # Base location
            {'lat': 47.6206, 'lng': -122.3494},  # ~15m away
            {'lat': 47.6207, 'lng': -122.3495},  # ~30m away  
        ]
        
        # Create test geocoding result
        test_result = GeocodingResult(
            address="Microsoft Building 99, Redmond, WA",
            provider=GeocodingProvider.AZURE_MAPS,
            confidence=0.9,
            coordinates=(47.6205, -122.3493),
            success=True
        )
        
        # Store first result in cache
        cache.put(nearby_detections[0]['lat'], nearby_detections[0]['lng'], test_result)
        
        # Check that nearby locations get cached result
        for detection in nearby_detections[1:]:
            cached_result = cache.get(detection['lat'], detection['lng'], provider=GeocodingProvider.AZURE_MAPS)
            self.assertIsNotNone(cached_result)
            self.assertEqual(cached_result.address, test_result.address)
            self.assertIsNone(cache.get(detection['lat'], detection['lng'], provider=GeocodingProvider.GOOGLE_MAPS))

    def test_radius_parameter_integration(self):
        """Test radius parameter affects clustering behavior."""
        # Test different clustering radii
        test_cases = [
            {'radius': 25.0, 'should_cluster': False},  # Smaller radius, no clustering
            {'radius': 100.0, 'should_cluster': True},   # Larger radius, clustering
        ]
        
        base_lat, base_lng = 47.6205, -122.3493
        nearby_lat, nearby_lng = 47.62095, -122.3493  # ~50m away: between 25m and 100m
        
        test_result = GeocodingResult(
            address="Test Building, Seattle, WA",
            provider=GeocodingProvider.AZURE_MAPS,
            confidence=0.85,
            coordinates=(base_lat, base_lng),
            success=True
        )
        
        for case in test_cases:
            with self.subTest(radius=case['radius']):
                cache = GeocodingCache(cache_dir=os.path.join(self.cache_dir.name, str(case['radius'])),
                                       clustering_radius_meters=case['radius'])
                
                # Store result for base location
                cache.put(base_lat, base_lng, test_result)
                
                # Check nearby location
                cached_result = cache.get(nearby_lat, nearby_lng, provider=GeocodingProvider.AZURE_MAPS)
                
                if case['should_cluster']:
                    self.assertIsNotNone(cached_result, f"Should cluster at {case['radius']}m radius")
                else:
                    self.assertIsNone(cached_result, f"Should not cluster at {case['radius']}m radius")

    def test_api_usage_tracking(self):
        """Test API usage tracking for session display."""
        service = GeocodingService(azure_key="test_key", google_key="test_key")
        
        with self.app.test_request_context():
            # Simulate successful request
            service._update_session_usage(GeocodingProvider.AZURE_MAPS, True)
            service._update_session_usage(GeocodingProvider.GOOGLE_MAPS, True)
            service._update_session_usage(GeocodingProvider.AZURE_MAPS, False)
            
            # Check usage tracking
            usage = service.get_session_usage()
            
            self.assertEqual(usage.azure_requests, 2)
            self.assertEqual(usage.google_requests, 1)
            self.assertEqual(usage.total_requests, 3)
            self.assertEqual(usage.successful_requests, 2)
            self.assertEqual(usage.failed_requests, 1)

    def test_error_fallback_workflow(self):
        """Test graceful fallback when geocoding fails."""
        # Simulate complete geocoding failure
        with patch('ts_geocoding.provider_get', side_effect=ConnectionError("Synthetic network error")) as provider_get:
            service = GeocodingService(azure_key="test_key", google_key="test_key")
            
            test_lat, test_lng = 47.6205, -122.3493
            
            with self.app.test_request_context():
                result = service.reverse_geocode(test_lat, test_lng)
            
            # The service returns structured failure; the application attaches
            # coordinate text for display. Exercise both current boundaries.
            self.assertFalse(result.success)
            self.assertEqual(result.address, "")
            self.assertEqual(result.coordinates, (test_lat, test_lng))
            self.assertTrue(result.error_message)
            self.assertEqual(provider_get.call_count, 2)

            import towerscout
            detections = [dict(self.test_detection_results[0])]
            with self.app.test_request_context(), patch.object(towerscout, 'create_geocoding_service', return_value=service):
                towerscout._attach_detection_addresses(detections, 'azure')
            self.assertEqual(detections[0]['address_provider'], 'fallback')
            self.assertEqual(detections[0]['address_confidence'], 0.0)
            center_lat = (detections[0]['y1'] + detections[0]['y2']) / 2
            center_lng = (detections[0]['x1'] + detections[0]['x2']) / 2
            self.assertIn(f'{center_lat:.6f}', detections[0]['address'])
            self.assertIn(f'{center_lng:.6f}', detections[0]['address'])

    def test_frontend_data_format(self):
        """Test that geocoded results match expected frontend format."""
        # This tests the data structure that would be sent to frontend
        detection_with_address = {
            'x1': -122.3503, 'y1': 47.6215, 'x2': -122.3493, 'y2': 47.6195,
            'class': 0, 'class_name': 'cooling_tower', 'conf': 0.85,
            'tile': 0, 'id_in_tile': 0, 'inside': True, 'selected': True, 'secondary': 0.9,
            'address': 'Microsoft Building 127, Redmond, WA 98052',
            'address_confidence': 0.95,
            'address_provider': 'azure_maps'
        }
        
        # Verify required fields are present
        required_fields = ['address', 'address_confidence', 'address_provider']
        for field in required_fields:
            self.assertIn(field, detection_with_address)
        
        # Verify data types
        self.assertIsInstance(detection_with_address['address'], str)
        self.assertIsInstance(detection_with_address['address_confidence'], (int, float))
        self.assertIsInstance(detection_with_address['address_provider'], str)
        
        # Verify confidence range
        self.assertGreaterEqual(detection_with_address['address_confidence'], 0.0)
        self.assertLessEqual(detection_with_address['address_confidence'], 1.0)
        
        # Verify provider values
        valid_providers = ['azure_maps', 'google_maps', 'fallback', 'error', 'none']
        self.assertIn(detection_with_address['address_provider'], valid_providers)


class TestGeocodingConfiguration(unittest.TestCase):
    """Test geocoding configuration and environment variables."""

    def setUp(self):
        cache_dir = tempfile.TemporaryDirectory()
        self.addCleanup(cache_dir.cleanup)
        cache_path = patch('ts_geocache.get_geocoding_cache_dir', return_value=cache_dir.name)
        cache_path.start()
        self.addCleanup(cache_path.stop)

    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables."""
        if not GEOCODING_AVAILABLE:
            self.skipTest("Geocoding modules not available")
            
        # Test with environment variables
        test_env = {
            'AZURE_MAPS_SUBSCRIPTION_KEY': 'env_azure_key',
            'GOOGLE_API_KEY': 'env_google_key',
            'GEOCODING_RATE_LIMIT': '60',
            'GEOCODING_CLUSTERING_RADIUS': '75'
        }
        
        with patch.dict(os.environ, test_env):
            # Service should pick up environment variables
            service = GeocodingService()
            self.assertEqual(service.azure_key, 'env_azure_key')
            self.assertEqual(service.google_key, 'env_google_key')
            
            # Cache should use environment radius
            cache = GeocodingCache(
                clustering_radius_meters=float(os.getenv('GEOCODING_CLUSTERING_RADIUS', 50))
            )
            self.assertEqual(cache.clustering_radius, 75.0)

    def test_configuration_defaults(self):
        """Test default configuration values."""
        if not GEOCODING_AVAILABLE:
            self.skipTest("Geocoding modules not available")
            
        # Test default values
        with patch.dict(os.environ, {'AZURE_MAPS_SUBSCRIPTION_KEY': 'test_key'}):
            service = GeocodingService()
            self.assertEqual(service.rate_limit, 30)  # Default rate limit
            
        cache = GeocodingCache()
        self.assertEqual(cache.clustering_radius, 50.0)  # Default clustering radius
        self.assertEqual(cache.max_cache_age, 24 * 3600)  # Default 24 hours


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2)
