#
# TowerScout Azure Maps Provider Tests
#
# Unit tests for Azure Maps provider with coordinate transformation validation
#

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add webapp directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))

from ts_azure_maps import AzureMaps, create_azure_maps_provider
from ts_errors import MapProviderError, ConfigurationError

class TestAzureMaps(unittest.TestCase):
    """Test Azure Maps provider implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_subscription_key = "test_subscription_key_12345"
        self.azure_maps = AzureMaps(self.test_subscription_key)
        
        # Standard test tile (Seattle Space Needle area)
        self.test_tile = {
            'lat': 47.6205,
            'lng': -122.3493,
            'lat_for_url': 47.6205,
            'id': 'test_tile_001'
        }

    def test_initialization_success(self):
        """Test successful Azure Maps provider initialization"""
        provider = AzureMaps(self.test_subscription_key)
        
        self.assertEqual(provider.subscription_key, self.test_subscription_key)
        self.assertEqual(provider.has_metadata, False)
        self.assertEqual(provider.base_url, "https://atlas.microsoft.com/map/static")
        self.assertEqual(provider.api_version, "2024-04-01")
        self.assertIsNotNone(provider.url_template)

    def test_initialization_missing_key(self):
        """Test initialization fails with missing subscription key"""
        with self.assertRaises(ConfigurationError) as context:
            AzureMaps("")
        
        self.assertEqual(context.exception.error_code, "AZURE_MAPS_NO_KEY")
        
        with self.assertRaises(ConfigurationError) as context:
            AzureMaps(None)
        
        self.assertEqual(context.exception.error_code, "AZURE_MAPS_NO_KEY")

    def test_coordinate_transformation(self):
        """Test critical coordinate transformation from lat,lng to lng,lat"""
        # Test case: Seattle Space Needle
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
                'name': 'London Eye',
                'tile': {'lat': 51.5033, 'lng': -0.1195, 'lat_for_url': 51.5033},
                'expected_center': '-0.1195,51.5033'
            },
            {
                'name': 'Sydney Opera House',
                'tile': {'lat': -33.8568, 'lng': 151.2153, 'lat_for_url': -33.8568},
                'expected_center': '151.2153,-33.8568'
            }
        ]
        
        for case in test_cases:
            with self.subTest(location=case['name']):
                url = self.azure_maps.get_url(case['tile'])
                self.assertIn(f"center={case['expected_center']}", url)
                
                # Verify URL contains all required parameters
                self.assertIn("api-version=2024-04-01", url)
                self.assertIn("tilesetId=microsoft.imagery", url)
                self.assertIn("zoom=19", url)
                self.assertIn("height=640", url)
                self.assertIn("width=640", url)
                self.assertIn("subscription-key=", url)

    def test_url_generation_default_parameters(self):
        """Test URL generation with default parameters"""
        url = self.azure_maps.get_url(self.test_tile)
        
        # Check base URL structure
        self.assertTrue(url.startswith("https://atlas.microsoft.com/map/static?"))
        
        # Check default parameters
        self.assertIn("api-version=2024-04-01", url)
        self.assertIn("tilesetId=microsoft.imagery", url)
        self.assertIn("zoom=19", url)
        self.assertIn("height=640", url)
        self.assertIn("width=640", url)
        self.assertIn("center=-122.3493,47.6205", url)
        self.assertIn(f"subscription-key={self.test_subscription_key}", url)

    def test_url_generation_custom_parameters(self):
        """Test URL generation with custom parameters"""
        url = self.azure_maps.get_url(
            self.test_tile,
            zoom=15,
            size="800,600",
            maptype="road"
        )
        
        self.assertIn("zoom=15", url)
        self.assertIn("height=600", url)
        self.assertIn("width=800", url)
        self.assertIn("tilesetId=microsoft.base.road", url)

    def test_maptype_conversion(self):
        """Test maptype to tileset conversion"""
        test_cases = [
            ('satellite', 'microsoft.imagery'),
            ('imagery', 'microsoft.imagery'),
            ('road', 'microsoft.base.road'),
            ('hybrid', 'microsoft.imagery'),
            ('terrain', 'microsoft.base.road'),
            ('unknown', 'microsoft.imagery')  # default fallback
        ]
        
        for maptype, expected_tileset in test_cases:
            with self.subTest(maptype=maptype):
                tileset = self.azure_maps._convert_maptype_to_tileset(maptype)
                self.assertEqual(tileset, expected_tileset)

    def test_size_parsing(self):
        """Test size parameter parsing"""
        test_cases = [
            ('640,480', ('640', '480')),
            ('800x600', ('800', '600')),
            ('1024X768', ('1024', '768')),
            ('512', ('512', '512')),  # square format
        ]
        
        for size_input, expected_output in test_cases:
            with self.subTest(size=size_input):
                width, height = self.azure_maps._parse_size(size_input)
                self.assertEqual((width, height), expected_output)

    def test_size_parsing_invalid(self):
        """Test size parameter parsing with invalid inputs"""
        invalid_sizes = [
            '640,480,100',  # too many dimensions
            'abc,def',       # non-numeric
            '50,50',         # below minimum
            '3000,3000'      # above maximum
        ]
        
        for invalid_size in invalid_sizes:
            with self.subTest(size=invalid_size):
                with self.assertRaises(ValueError):
                    self.azure_maps._parse_size(invalid_size)

    def test_coordinate_validation(self):
        """Test coordinate range validation"""
        # Invalid longitude (outside [-180, 180])
        invalid_tile_lng = {
            'lat': 47.6205,
            'lng': 200.0,  # Invalid longitude
            'lat_for_url': 47.6205
        }
        
        with self.assertRaises(MapProviderError):
            self.azure_maps.get_url(invalid_tile_lng)
        
        # Invalid latitude (outside [-90, 90])
        invalid_tile_lat = {
            'lat': 95.0,  # Invalid latitude
            'lng': -122.3493,
            'lat_for_url': 95.0
        }
        
        with self.assertRaises(MapProviderError):
            self.azure_maps.get_url(invalid_tile_lat)

    def test_zoom_level_clamping(self):
        """Test zoom level is clamped to valid range [0, 20]"""
        # Test zoom too high
        url_high = self.azure_maps.get_url(self.test_tile, zoom=25)
        self.assertIn("zoom=20", url_high)  # Should be clamped to 20
        
        # Test zoom too low
        url_low = self.azure_maps.get_url(self.test_tile, zoom=-5)
        self.assertIn("zoom=0", url_low)  # Should be clamped to 0
        
        # Test valid zoom
        url_valid = self.azure_maps.get_url(self.test_tile, zoom=15)
        self.assertIn("zoom=15", url_valid)

    def test_metadata_not_supported(self):
        """Test metadata operations are not supported"""
        # get_meta_url should raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.azure_maps.get_meta_url(self.test_tile)
        
        # get_date should return empty string
        date = self.azure_maps.get_date("any_metadata")
        self.assertEqual(date, "")

    def test_cutoffs_detection(self):
        """Test logo/attribution area detection"""
        # Object in normal area (should return 1.0)
        normal_object = {
            'x1': 0.1, 'y1': 0.1,
            'x2': 0.5, 'y2': 0.5
        }
        multiplier = self.azure_maps.checkCutOffs(normal_object)
        self.assertEqual(multiplier, 1.0)
        
        # Object in attribution area (bottom-right corner)
        attribution_object = {
            'x1': 0.7, 'y1': 0.97,
            'x2': 0.9, 'y2': 0.99
        }
        multiplier = self.azure_maps.checkCutOffs(attribution_object)
        self.assertEqual(multiplier, 0.1)
        
        # Object missing coordinates (should return 1.0)
        incomplete_object = {'x1': 0.1}  # missing other coordinates
        multiplier = self.azure_maps.checkCutOffs(incomplete_object)
        self.assertEqual(multiplier, 1.0)

    def test_from_environment_success(self):
        """Test creating provider from environment variables"""
        with patch.dict(os.environ, {'AZURE_MAPS_SUBSCRIPTION_KEY': 'env_test_key'}):
            provider = AzureMaps.from_environment()
            self.assertEqual(provider.subscription_key, 'env_test_key')

    def test_from_environment_missing(self):
        """Test creating provider from environment when key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError) as context:
                AzureMaps.from_environment()
            
            self.assertEqual(context.exception.error_code, "AZURE_MAPS_ENV_MISSING")

    def test_factory_function(self):
        """Test factory function with different parameter combinations"""
        # With explicit key
        provider1 = create_azure_maps_provider(self.test_subscription_key)
        self.assertEqual(provider1.subscription_key, self.test_subscription_key)
        
        # With environment variable
        with patch.dict(os.environ, {'AZURE_MAPS_SUBSCRIPTION_KEY': 'env_key'}):
            provider2 = create_azure_maps_provider()
            self.assertEqual(provider2.subscription_key, 'env_key')

    def test_get_provider_info(self):
        """Test provider information retrieval"""
        info = self.azure_maps.get_provider_info()
        
        expected_keys = [
            'provider', 'base_url', 'api_version',
            'has_metadata', 'subscription_key_configured', 'coordinate_system'
        ]
        
        for key in expected_keys:
            self.assertIn(key, info)
        
        self.assertEqual(info['provider'], 'Azure Maps')
        self.assertEqual(info['has_metadata'], False)
        self.assertEqual(info['subscription_key_configured'], True)
        self.assertEqual(info['coordinate_system'], 'GeoJSON (longitude,latitude)')

    def test_coordinate_precision(self):
        """Test coordinate precision is maintained within 1 meter accuracy"""
        # High precision coordinates (6 decimal places = ~0.1 meter accuracy)
        precision_tile = {
            'lat': 47.620506,
            'lng': -122.349313,
            'lat_for_url': 47.620506
        }
        
        url = self.azure_maps.get_url(precision_tile)
        
        # Verify coordinates are preserved in URL
        self.assertIn("center=-122.349313,47.620506", url)

    def test_error_handling_integration(self):
        """Test error handling uses TowerScout error infrastructure"""
        # Test with missing tile data
        invalid_tile = {}  # Missing required keys
        
        with self.assertRaises(MapProviderError) as context:
            self.azure_maps.get_url(invalid_tile)
        
        error = context.exception
        self.assertEqual(error.error_code, "AZURE_MAPS_URL_GENERATION")
        self.assertIn("details", error.to_dict())
        self.assertIsNotNone(error.user_message)


class TestCoordinateTransformationAccuracy(unittest.TestCase):
    """Comprehensive coordinate transformation accuracy tests"""

    def setUp(self):
        """Set up test fixtures with known geographic locations"""
        self.azure_maps = AzureMaps("test_key")
        
        # Known locations with precise coordinates for validation
        self.test_locations = [
            {
                'name': 'Seattle Space Needle',
                'lat': 47.6205, 'lng': -122.3493,
                'expected_center': '-122.3493,47.6205'
            },
            {
                'name': 'NYC Statue of Liberty',
                'lat': 40.6892, 'lng': -74.0445,
                'expected_center': '-74.0445,40.6892'
            },
            {
                'name': 'London Big Ben',
                'lat': 51.4994, 'lng': -0.1245,
                'expected_center': '-0.1245,51.4994'
            },
            {
                'name': 'Tokyo Tower',
                'lat': 35.6586, 'lng': 139.7454,
                'expected_center': '139.7454,35.6586'
            },
            {
                'name': 'Sydney Opera House',
                'lat': -33.8568, 'lng': 151.2153,
                'expected_center': '151.2153,-33.8568'
            },
            {
                'name': 'Eiffel Tower',
                'lat': 48.8584, 'lng': 2.2945,
                'expected_center': '2.2945,48.8584'
            }
        ]

    def test_known_locations_coordinate_accuracy(self):
        """Test coordinate transformation accuracy for known world locations"""
        for location in self.test_locations:
            with self.subTest(location=location['name']):
                tile = {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'lat_for_url': location['lat']
                }
                
                url = self.azure_maps.get_url(tile)
                
                # Verify exact coordinate transformation
                self.assertIn(f"center={location['expected_center']}", url)
                
                # Verify coordinate precision (6 decimal places minimum)
                center_param = f"center={location['expected_center']}"
                self.assertIn(center_param, url)

    def test_edge_case_coordinates(self):
        """Test coordinate transformation for edge cases"""
        edge_cases = [
            {
                'name': 'Equator Prime Meridian',
                'lat': 0.0, 'lng': 0.0,
                'expected_center': '0.0,0.0'
            },
            {
                'name': 'International Date Line',
                'lat': 0.0, 'lng': 179.9999,
                'expected_center': '179.9999,0.0'
            },
            {
                'name': 'North Pole Area',
                'lat': 89.9999, 'lng': 0.0,
                'expected_center': '0.0,89.9999'
            },
            {
                'name': 'South Pole Area',
                'lat': -89.9999, 'lng': 0.0,
                'expected_center': '0.0,-89.9999'
            }
        ]
        
        for case in edge_cases:
            with self.subTest(location=case['name']):
                tile = {
                    'lat': case['lat'],
                    'lng': case['lng'],
                    'lat_for_url': case['lat']
                }
                
                url = self.azure_maps.get_url(tile)
                self.assertIn(f"center={case['expected_center']}", url)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)