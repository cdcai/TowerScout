"""
Unit tests for TowerScout geocoding service.

Tests the geocoding functionality including provider fallback,
caching, rate limiting, and integration with the Flask application.

Author: TowerScout Development Team  
Date: January 2026
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
import tempfile
import os
from pathlib import Path

# Import modules under test
import sys
sys.path.append(os.path.dirname(__file__) + '/../../webapp')

from ts_geocoding import (
    GeocodingService, GeocodingProvider, GeocodingResult, GeocodingError, 
    RateLimitError, create_geocoding_service
)
from ts_geocache import GeocodingCache, CacheEntry, create_geocoding_cache


class TestGeocodingService(unittest.TestCase):
    """Test geocoding service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_lat = 47.6205
        self.test_lng = -122.3493
        self.azure_key = "test_azure_key_12345"
        self.google_key = "test_google_key_12345"

    def test_service_initialization_with_azure_key(self):
        """Test service initialization with Azure Maps key."""
        service = GeocodingService(azure_key=self.azure_key)
        
        self.assertEqual(service.azure_key, self.azure_key)
        self.assertIsNone(service.google_key)
        self.assertIn(GeocodingProvider.AZURE_MAPS, service.providers)
        self.assertNotIn(GeocodingProvider.GOOGLE_MAPS, service.providers)

    def test_service_initialization_with_google_key(self):
        """Test service initialization with Google Maps key."""
        service = GeocodingService(google_key=self.google_key)
        
        self.assertIsNone(service.azure_key)
        self.assertEqual(service.google_key, self.google_key)
        self.assertNotIn(GeocodingProvider.AZURE_MAPS, service.providers)
        self.assertIn(GeocodingProvider.GOOGLE_MAPS, service.providers)

    def test_service_initialization_with_both_keys(self):
        """Test service initialization with both keys (Azure Maps priority)."""
        service = GeocodingService(azure_key=self.azure_key, google_key=self.google_key)
        
        self.assertEqual(service.azure_key, self.azure_key)
        self.assertEqual(service.google_key, self.google_key)
        self.assertIn(GeocodingProvider.AZURE_MAPS, service.providers)
        self.assertIn(GeocodingProvider.GOOGLE_MAPS, service.providers)
        # Azure Maps should be first (higher priority)
        self.assertEqual(service.providers[0], GeocodingProvider.AZURE_MAPS)

    def test_service_initialization_no_keys_raises_error(self):
        """Test service initialization without keys raises ConfigurationError."""
        with self.assertRaises(Exception):  # ConfigurationError not imported
            GeocodingService()

    @patch('requests.get')
    def test_azure_maps_geocoding_success(self, mock_get):
        """Test successful Azure Maps geocoding."""
        # Mock successful Azure Maps response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'summary': {'numResults': 1},
            'results': [{
                'address': {'freeformAddress': '123 Test Street, Seattle, WA'},
                'matchType': 'AddressPoint'
            }]
        }
        mock_get.return_value = mock_response
        
        service = GeocodingService(azure_key=self.azure_key)
        
        with patch('flask.session', {}):
            result = service.reverse_geocode(self.test_lat, self.test_lng)
        
        self.assertTrue(result.success)
        self.assertEqual(result.address, '123 Test Street, Seattle, WA')
        self.assertEqual(result.provider, GeocodingProvider.AZURE_MAPS)
        self.assertEqual(result.confidence, 0.95)  # AddressPoint confidence

    @patch('requests.get')
    def test_google_maps_geocoding_success(self, mock_get):
        """Test successful Google Maps geocoding."""
        # Mock successful Google Maps response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [{
                'formatted_address': '456 Test Avenue, Seattle, WA',
                'geometry': {'location_type': 'ROOFTOP'}
            }]
        }
        mock_get.return_value = mock_response
        
        service = GeocodingService(google_key=self.google_key)
        
        with patch('flask.session', {}):
            result = service.reverse_geocode(self.test_lat, self.test_lng)
        
        self.assertTrue(result.success)
        self.assertEqual(result.address, '456 Test Avenue, Seattle, WA')
        self.assertEqual(result.provider, GeocodingProvider.GOOGLE_MAPS)
        self.assertEqual(result.confidence, 0.95)  # ROOFTOP confidence

    @patch('requests.get')
    def test_provider_fallback(self, mock_get):
        """Test fallback from Azure Maps to Google Maps on failure."""
        # Mock Azure Maps failure and Google Maps success
        def mock_get_side_effect(url, **kwargs):
            if 'atlas.microsoft.com' in url:
                # Azure Maps fails
                mock_response = Mock()
                mock_response.raise_for_status.side_effect = Exception("Azure API Error")
                return mock_response
            else:
                # Google Maps succeeds
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status = Mock()
                mock_response.json.return_value = {
                    'status': 'OK',
                    'results': [{
                        'formatted_address': 'Fallback Address, Seattle, WA',
                        'geometry': {'location_type': 'RANGE_INTERPOLATED'}
                    }]
                }
                return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        service = GeocodingService(azure_key=self.azure_key, google_key=self.google_key)
        
        with patch('flask.session', {}):
            result = service.reverse_geocode(self.test_lat, self.test_lng)
        
        self.assertTrue(result.success)
        self.assertEqual(result.address, 'Fallback Address, Seattle, WA')
        self.assertEqual(result.provider, GeocodingProvider.GOOGLE_MAPS)

    @patch('requests.get')
    def test_all_providers_fail(self, mock_get):
        """Test behavior when all providers fail."""
        # Mock all providers failing
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        service = GeocodingService(azure_key=self.azure_key, google_key=self.google_key)
        
        with patch('flask.session', {}):
            result = service.reverse_geocode(self.test_lat, self.test_lng)
        
        self.assertFalse(result.success)
        self.assertIn("Address unavailable", result.address)
        self.assertIn(str(self.test_lat), result.address)
        self.assertIn(str(self.test_lng), result.address)

    def test_rate_limiting(self):
        """Test session-based rate limiting."""
        service = GeocodingService(azure_key=self.azure_key, rate_limit_requests_per_minute=2)
        
        # Mock session with high request count
        mock_session = {
            'geocoding_usage': {
                'google_requests': 0,
                'azure_requests': 3,  # Exceeds rate limit of 2
                'total_requests': 3,
                'successful_requests': 2,
                'failed_requests': 1,
                'last_request_time': time.time() - 30  # Recent request
            }
        }
        
        with patch('flask.session', mock_session):
            with self.assertRaises(Exception):  # RateLimitError
                service.reverse_geocode(self.test_lat, self.test_lng)


class TestGeocodingCache(unittest.TestCase):
    """Test geocoding cache functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_lat = 47.6205
        self.test_lng = -122.3493
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample geocoding result
        self.test_result = GeocodingResult(
            address="123 Test Street, Seattle, WA",
            provider=GeocodingProvider.AZURE_MAPS,
            confidence=0.9,
            coordinates=(self.test_lat, self.test_lng),
            success=True
        )

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = GeocodingCache(cache_dir=self.temp_dir)
        
        self.assertEqual(cache.clustering_radius, 50.0)  # Default
        self.assertEqual(cache.max_cache_age, 24 * 3600)  # 24 hours in seconds
        self.assertTrue(cache.cache_dir.exists())
        self.assertIsInstance(cache.file_cache, dict)

    def test_cache_put_and_get(self):
        """Test storing and retrieving from cache."""
        cache = GeocodingCache(cache_dir=self.temp_dir)
        
        # Store result in cache
        cache.put(self.test_lat, self.test_lng, self.test_result)
        
        # Retrieve from cache
        retrieved = cache.get(self.test_lat, self.test_lng)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.address, self.test_result.address)
        self.assertEqual(retrieved.provider, self.test_result.provider)
        self.assertTrue(retrieved.success)

    def test_cache_clustering(self):
        """Test spatial clustering functionality."""
        cache = GeocodingCache(cache_dir=self.temp_dir, clustering_radius_meters=100.0)
        
        # Store result for one location
        cache.put(self.test_lat, self.test_lng, self.test_result)
        
        # Request nearby location (within clustering radius)
        nearby_lat = self.test_lat + 0.0005  # ~50m north
        nearby_lng = self.test_lng + 0.0005  # ~50m east
        
        retrieved = cache.get(nearby_lat, nearby_lng)
        
        # Should retrieve cached result due to clustering
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.address, self.test_result.address)

    def test_cache_miss_outside_radius(self):
        """Test cache miss for locations outside clustering radius."""
        cache = GeocodingCache(cache_dir=self.temp_dir, clustering_radius_meters=50.0)
        
        # Store result for one location
        cache.put(self.test_lat, self.test_lng, self.test_result)
        
        # Request distant location (outside clustering radius)
        distant_lat = self.test_lat + 0.01  # ~1km north
        distant_lng = self.test_lng + 0.01  # ~1km east
        
        retrieved = cache.get(distant_lat, distant_lng)
        
        # Should be cache miss
        self.assertIsNone(retrieved)

    def test_cache_expiration(self):
        """Test cache entry expiration."""
        cache = GeocodingCache(cache_dir=self.temp_dir, max_cache_age_hours=1)
        
        # Create expired cache entry
        entry = CacheEntry.from_geocoding_result(self.test_result)
        entry.timestamp = time.time() - 7200  # 2 hours ago
        
        # Manually add expired entry
        cache_key = cache._generate_cache_key(self.test_lat, self.test_lng)
        cache.file_cache[cache_key] = entry
        
        # Should not retrieve expired entry
        retrieved = cache.get(self.test_lat, self.test_lng)
        self.assertIsNone(retrieved)

    def test_cache_persistence(self):
        """Test cache persistence across instances."""
        cache1 = GeocodingCache(cache_dir=self.temp_dir)
        
        # Store result in first cache instance
        cache1.put(self.test_lat, self.test_lng, self.test_result)
        
        # Create second cache instance (should load from file)
        cache2 = GeocodingCache(cache_dir=self.temp_dir)
        
        # Should retrieve from persisted cache
        retrieved = cache2.get(self.test_lat, self.test_lng)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.address, self.test_result.address)

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = GeocodingCache(cache_dir=self.temp_dir)
        
        # Add some entries
        cache.put(self.test_lat, self.test_lng, self.test_result)
        
        stats = cache.get_cache_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertGreaterEqual(stats['file_cache_entries'], 1)
        self.assertEqual(stats['clustering_radius_meters'], 50.0)
        self.assertFalse(stats['redis_enabled'])  # No Redis in test


class TestGeocodingIntegration(unittest.TestCase):
    """Test geocoding integration with Flask application."""

    def setUp(self):
        """Set up Flask test client."""
        # This would require setting up the Flask app for testing
        # For now, we'll focus on unit tests of the geocoding components
        pass

    def test_factory_functions(self):
        """Test factory function creation."""
        with patch.dict(os.environ, {'AZURE_MAPS_SUBSCRIPTION_KEY': 'test_key'}):
            service = create_geocoding_service()
            self.assertIsNotNone(service)
            
        cache = create_geocoding_cache(clustering_radius_meters=100.0)
        self.assertIsNotNone(cache)
        self.assertEqual(cache.clustering_radius, 100.0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)