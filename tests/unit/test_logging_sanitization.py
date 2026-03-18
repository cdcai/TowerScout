"""
Unit tests for logging sanitization functionality.

Tests that API keys and other sensitive data are properly redacted from log messages.
"""

import unittest
import logging
from io import StringIO
import sys
import os

# Add webapp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))

from ts_logging import sanitize_sensitive_data, TowerScoutLogger, TowerScoutFormatter


class TestLoggingSanitization(unittest.TestCase):
    """Test suite for sensitive data sanitization in logs."""
    
    def test_sanitize_google_api_key(self):
        """Test that Google API keys are redacted."""
        message = "Error: https://maps.googleapis.com/api?key=AIzaSyDEXAMPLE1234567890abcdefghijklmno"
        sanitized = sanitize_sensitive_data(message)
        
        # API key should be redacted (either as Google-specific or generic pattern)
        self.assertIn('***REDACTED***', sanitized)
        self.assertNotIn('AIzaSyDEXAMPLE1234567890abcdefghijklmno', sanitized)
    
    def test_sanitize_azure_subscription_key(self):
        """Test that Azure subscription keys are redacted."""
        message = "URL: https://atlas.microsoft.com/map?subscription-key=abc123xyz789"
        sanitized = sanitize_sensitive_data(message)
        
        self.assertIn('subscription-key=***REDACTED***', sanitized)
        self.assertNotIn('abc123xyz789', sanitized)
    
    def test_sanitize_generic_api_key_patterns(self):
        """Test that generic API key patterns are redacted."""
        test_cases = [
            ("url?key=secret123", "url?key=***REDACTED***"),
            ("url?apikey=secret456", "url?apikey=***REDACTED***"),
            ("url?api_key=secret789", "url?api_key=***REDACTED***"),
            ("url?token=bearer123", "url?token=***REDACTED***"),
            ("url?access_token=oauth456", "url?access_token=***REDACTED***"),
        ]
        
        for original, expected_pattern in test_cases:
            with self.subTest(original=original):
                sanitized = sanitize_sensitive_data(original)
                self.assertIn('***REDACTED***', sanitized)
                self.assertNotIn('secret', sanitized)
                self.assertNotIn('bearer', sanitized)
                self.assertNotIn('oauth', sanitized)
    
    def test_sanitize_authorization_header(self):
        """Test that Authorization headers are redacted."""
        message = "Request failed: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        sanitized = sanitize_sensitive_data(message)
        
        self.assertIn('Authorization: ***REDACTED***', sanitized)
        self.assertNotIn('Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9', sanitized)
    
    def test_sanitize_multiple_keys_in_url(self):
        """Test that multiple API keys in one URL are all redacted."""
        message = "Error: https://api.example.com?key=secret1&subscription-key=secret2&token=secret3"
        sanitized = sanitize_sensitive_data(message)
        
        # Check that all three keys are redacted
        self.assertEqual(sanitized.count('***REDACTED***'), 3)
        self.assertNotIn('secret1', sanitized)
        self.assertNotIn('secret2', sanitized)
        self.assertNotIn('secret3', sanitized)
    
    def test_sanitize_preserves_non_sensitive_content(self):
        """Test that non-sensitive parts of messages are preserved."""
        message = "Fetching tile from https://maps.example.com/tile?x=123&y=456&key=secret789"
        sanitized = sanitize_sensitive_data(message)
        
        # These should still be present
        self.assertIn('Fetching tile', sanitized)
        self.assertIn('x=123', sanitized)
        self.assertIn('y=456', sanitized)
        
        # API key should be redacted
        self.assertIn('key=***REDACTED***', sanitized)
        self.assertNotIn('secret789', sanitized)
    
    def test_formatter_sanitizes_log_records(self):
        """Test that the TowerScoutFormatter sanitizes log records."""
        # Create a logger with StringIO handler to capture output
        logger = logging.getLogger('test_sanitization')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(TowerScoutFormatter(json_format=False))
        logger.addHandler(handler)
        
        # Log a message with an API key
        logger.error("Failed to fetch: https://api.example.com?key=AIzaSyDEXAMPLE1234567890abcdefghijklmno")
        
        # Get the logged output
        log_output = stream.getvalue()
        
        # Verify API key is redacted (generic pattern catches it)
        self.assertIn('***REDACTED***', log_output)
        self.assertNotIn('AIzaSyDEXAMPLE1234567890abcdefghijklmno', log_output)
    
    def test_sanitize_handles_non_string_input(self):
        """Test that sanitize handles non-string inputs gracefully."""
        # Test with various types
        self.assertEqual(sanitize_sensitive_data(None), 'None')
        self.assertEqual(sanitize_sensitive_data(123), '123')
        self.assertEqual(sanitize_sensitive_data(['list', 'items']), "['list', 'items']")
    
    def test_real_world_error_message(self):
        """Test sanitization on a real error message from the logs."""
        message = (
            "Google Maps API error: HTTPSConnectionPool(host='maps.googleapis.com', port=443): "
            "Max retries exceeded with url: /maps/api/geocode/json?latlng=40.7&key=AIzaSyDEXAMPLE"
            "1234567890abcdefghijklmno&location_type=ROOFTOP"
        )
        
        sanitized = sanitize_sensitive_data(message)
        
        # API key should be redacted
        self.assertIn('key=***REDACTED***', sanitized)
        self.assertNotIn('AIzaSyDEXAMPLE1234567890abcdefghijklmno', sanitized)
        
        # Other parameters should remain
        self.assertIn('latlng=40.7', sanitized)
        self.assertIn('location_type=ROOFTOP', sanitized)


def suite():
    """Create test suite."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLoggingSanitization))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
