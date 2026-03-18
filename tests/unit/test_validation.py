"""
Unit tests for TowerScout input validation system
"""

import unittest
import json
import tempfile
import os
from werkzeug.datastructures import FileStorage
from io import BytesIO

# Add webapp directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))

from ts_validation import (
    TowerScoutValidator, ValidationError, RateLimiter,
    validate_detection_request, validate_zipcode_request
)


class TestTowerScoutValidator(unittest.TestCase):
    """Test cases for TowerScoutValidator class"""

    def test_sanitize_string_valid(self):
        """Test string sanitization with valid input"""
        result = TowerScoutValidator.sanitize_string("  hello world  ")
        self.assertEqual(result, "hello world")

    def test_sanitize_string_null_bytes(self):
        """Test string sanitization removes null bytes"""
        result = TowerScoutValidator.sanitize_string("hello\x00world")
        self.assertEqual(result, "helloworld")

    def test_sanitize_string_too_long(self):
        """Test string length validation"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.sanitize_string("x" * 256)

    def test_sanitize_string_not_string(self):
        """Test non-string input rejection"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.sanitize_string(123)

    def test_validate_coordinate_latitude_valid(self):
        """Test valid latitude validation"""
        result = TowerScoutValidator.validate_coordinate(45.5, 'latitude')
        self.assertEqual(result, 45.5)

    def test_validate_coordinate_latitude_out_of_range(self):
        """Test latitude out of range"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_coordinate(91.0, 'latitude')
        
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_coordinate(-91.0, 'latitude')

    def test_validate_coordinate_longitude_valid(self):
        """Test valid longitude validation"""
        result = TowerScoutValidator.validate_coordinate(-122.4, 'longitude')
        self.assertEqual(result, -122.4)

    def test_validate_coordinate_longitude_out_of_range(self):
        """Test longitude out of range"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_coordinate(181.0, 'longitude')
        
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_coordinate(-181.0, 'longitude')

    def test_validate_coordinate_not_number(self):
        """Test non-numeric coordinate"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_coordinate("not a number", 'latitude')

    def test_validate_polygon_coordinates_valid(self):
        """Test valid polygon coordinate validation"""
        coords = [[-122.4, 37.8], [-122.3, 37.8], [-122.3, 37.9], [-122.4, 37.9]]
        result = TowerScoutValidator.validate_polygon_coordinates(coords)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], (-122.4, 37.8))

    def test_validate_polygon_coordinates_too_few_points(self):
        """Test polygon with too few points"""
        coords = [[-122.4, 37.8], [-122.3, 37.8]]
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_polygon_coordinates(coords)

    def test_validate_polygon_coordinates_invalid_point(self):
        """Test polygon with invalid point format"""
        coords = [[-122.4, 37.8], [-122.3], [-122.3, 37.9]]
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_polygon_coordinates(coords)

    def test_validate_polygons_json_valid(self):
        """Test valid polygon JSON validation"""
        polygon_data = [[[-122.4, 37.8], [-122.3, 37.8], [-122.3, 37.9], [-122.4, 37.9], [-122.4, 37.8]]]
        json_str = json.dumps(polygon_data)
        result = TowerScoutValidator.validate_polygons_json(json_str)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].is_valid)

    def test_validate_polygons_json_invalid_json(self):
        """Test invalid JSON format"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_polygons_json("invalid json")

    def test_validate_polygons_json_empty(self):
        """Test empty polygon data"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_polygons_json("")

    def test_validate_bounds_valid(self):
        """Test valid bounds validation"""
        bounds = "37.7,-122.5,37.8,-122.4"
        result = TowerScoutValidator.validate_bounds(bounds)
        self.assertIn('lat1', result)
        self.assertIn('lng1', result)
        self.assertIn('lat2', result)
        self.assertIn('lng2', result)

    def test_validate_bounds_invalid_format(self):
        """Test bounds with wrong number of coordinates"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_bounds("37.7,−122.5,37.8")

    def test_validate_bounds_invalid_order(self):
        """Test bounds with invalid ordering (min >= max)"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_bounds("37.8,−122.5,37.7,−122.4")

    def test_validate_engine_valid(self):
        """Test valid engine validation"""
        result = TowerScoutValidator.validate_engine("yolo")
        self.assertEqual(result, "yolo")
        
        result = TowerScoutValidator.validate_engine("EFFICIENTNET")
        self.assertEqual(result, "efficientnet")

    def test_validate_engine_invalid(self):
        """Test invalid engine"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_engine("invalid_engine")

    def test_validate_provider_valid(self):
        """Test valid provider validation"""
        result = TowerScoutValidator.validate_provider("google")
        self.assertEqual(result, "google")
        
        result = TowerScoutValidator.validate_provider("BING")
        self.assertEqual(result, "bing")

    def test_validate_provider_invalid(self):
        """Test invalid provider"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_provider("invalid_provider")

    def test_validate_zipcode_valid(self):
        """Test valid zipcode formats"""
        result = TowerScoutValidator.validate_zipcode("12345")
        self.assertEqual(result, "12345")
        
        result = TowerScoutValidator.validate_zipcode("12345-6789")
        self.assertEqual(result, "12345-6789")

    def test_validate_zipcode_invalid(self):
        """Test invalid zipcode formats"""
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_zipcode("123")
        
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_zipcode("12345-67")
        
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_zipcode("abcde")


class TestFileValidation(unittest.TestCase):
    """Test cases for file upload validation"""

    def create_test_file(self, filename, content=b"test content", content_type="text/plain"):
        """Helper to create test FileStorage object"""
        return FileStorage(
            stream=BytesIO(content),
            filename=filename,
            content_type=content_type
        )

    def test_validate_image_file_valid(self):
        """Test valid image file"""
        file = self.create_test_file("test.jpg", b"fake jpeg content", "image/jpeg")
        result = TowerScoutValidator.validate_image_file(file)
        self.assertEqual(result.filename, "test.jpg")

    def test_validate_image_file_invalid_extension(self):
        """Test image file with invalid extension"""
        file = self.create_test_file("test.txt", b"text content", "text/plain")
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_image_file(file)

    def test_validate_image_file_no_extension(self):
        """Test image file without extension"""
        file = self.create_test_file("test", b"content", "image/jpeg")
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_image_file(file)

    def test_validate_dataset_file_valid(self):
        """Test valid dataset file"""
        file = self.create_test_file("dataset.zip", b"fake zip content", "application/zip")
        result = TowerScoutValidator.validate_dataset_file(file)
        self.assertEqual(result.filename, "dataset.zip")

    def test_validate_model_file_valid(self):
        """Test valid model file"""
        file = self.create_test_file("model.pt", b"fake pytorch model", "application/octet-stream")
        result = TowerScoutValidator.validate_model_file(file)
        self.assertEqual(result.filename, "model.pt")

    def test_validate_file_too_large(self):
        """Test file size validation"""
        # Create a file that's too large
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        file = self.create_test_file("large.jpg", large_content, "image/jpeg")
        
        with self.assertRaises(ValidationError):
            TowerScoutValidator.validate_image_file(file)


class TestRateLimiter(unittest.TestCase):
    """Test cases for rate limiter"""

    def setUp(self):
        """Set up test rate limiter"""
        self.rate_limiter = RateLimiter()

    def test_rate_limiter_allows_under_limit(self):
        """Test rate limiter allows requests under limit"""
        for i in range(5):
            self.assertTrue(self.rate_limiter.is_allowed("127.0.0.1", max_requests=10))

    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit"""
        # Make requests up to the limit
        for i in range(5):
            self.rate_limiter.is_allowed("127.0.0.1", max_requests=5)
        
        # Next request should be blocked
        self.assertFalse(self.rate_limiter.is_allowed("127.0.0.1", max_requests=5))

    def test_rate_limiter_different_ips(self):
        """Test rate limiter treats different IPs separately"""
        # Max out one IP
        for i in range(5):
            self.rate_limiter.is_allowed("127.0.0.1", max_requests=5)
        
        # Different IP should still be allowed
        self.assertTrue(self.rate_limiter.is_allowed("192.168.1.1", max_requests=5))


class TestRequestValidation(unittest.TestCase):
    """Test cases for complete request validation"""

    def test_validate_detection_request_valid(self):
        """Test valid detection request validation"""
        form_data = {
            'bounds': '37.7,-122.5,37.8,-122.4',
            'engine': 'yolo',
            'provider': 'google',
            'polygons': json.dumps([[[-122.5, 37.7], [-122.4, 37.7], [-122.4, 37.8], [-122.5, 37.8], [-122.5, 37.7]]]),
            'estimate': 'yes'
        }
        
        result = validate_detection_request(form_data)
        self.assertIn('bounds', result)
        self.assertIn('engine', result)
        self.assertIn('provider', result)
        self.assertIn('polygons', result)
        self.assertEqual(result['estimate'], 'yes')

    def test_validate_detection_request_missing_required(self):
        """Test detection request missing required fields"""
        form_data = {
            'bounds': '37.7,-122.5,37.8,-122.4',
            # Missing engine, provider, polygons
        }
        
        with self.assertRaises(ValidationError):
            validate_detection_request(form_data)

    def test_validate_zipcode_request_valid(self):
        """Test valid zipcode request validation"""
        args = {'zipcode': '12345'}
        result = validate_zipcode_request(args)
        self.assertEqual(result['zipcode'], '12345')

    def test_validate_zipcode_request_invalid(self):
        """Test invalid zipcode request"""
        args = {'zipcode': 'invalid'}
        with self.assertRaises(ValidationError):
            validate_zipcode_request(args)


if __name__ == '__main__':
    unittest.main()