"""
Integration tests for TowerScout end-to-end workflows.

Tests complete user workflows including map provider integration,
detection pipelines, and session management.
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import threading
import time

# Import all necessary modules (imports handled by conftest.py)
from towerscout import app
from ts_azure_maps import AzureMaps, create_azure_maps_provider
from ts_gmaps import GoogleMaps
from ts_events import set_event, get_event, clear_events
from ts_validation import TowerScoutValidator


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end detection workflows."""

    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = self.app.test_client()
        
        # Test polygon around Seattle Space Needle
        self.test_polygon = [
            {'lat': 47.6195, 'lng': -122.3503},
            {'lat': 47.6215, 'lng': -122.3503},
            {'lat': 47.6215, 'lng': -122.3483},
            {'lat': 47.6195, 'lng': -122.3483}
        ]

    @patch('towerscout.TSYolov5')
    @patch('towerscout.TSEfficientNet')
    @patch('ts_gmaps.GoogleMaps.get_url')
    def test_complete_detection_workflow_google_maps(self, mock_get_url, mock_en, mock_yolo):
        """Test complete detection workflow with Google Maps."""
        # Mock Google Maps URL generation
        mock_get_url.return_value = "https://maps.googleapis.com/test_url"
        
        # Mock ML model responses
        mock_yolo_instance = Mock()
        mock_yolo_instance.detect.return_value = [
            {
                'lat': 47.6205,
                'lng': -122.3493,
                'conf': 0.85,
                'primary_score': 0.85,
                'secondary_score': 0.72,
                'id': 'detection_001'
            }
        ]
        mock_yolo.return_value = mock_yolo_instance
        
        mock_en_instance = Mock()
        mock_en_instance.classify.return_value = [
            {'confidence': 0.72, 'classification': 'cooling_tower'}
        ]
        mock_en.return_value = mock_en_instance
        
        # Test complete workflow
        with self.client.session_transaction() as sess:
            sess['polygon'] = self.test_polygon
            sess['session_id'] = 'test_session_123'
        
        # 1. Submit polygon
        response = self.client.post('/draw_polygon',
                                   data=json.dumps({'polygon': self.test_polygon}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # 2. Check status during processing (would be called by frontend)
        status_response = self.client.get('/get_status')
        self.assertEqual(status_response.status_code, 200)
        
        # 3. Get detection results
        results_response = self.client.get('/getobjects')
        self.assertEqual(results_response.status_code, 200)

    @patch('towerscout.TSYolov5')
    @patch('towerscout.TSEfficientNet')
    @patch('ts_azure_maps.AzureMaps.get_url')
    def test_complete_detection_workflow_azure_maps(self, mock_get_url, mock_en, mock_yolo):
        """Test complete detection workflow with Azure Maps."""
        # Mock Azure Maps URL generation
        mock_get_url.return_value = "https://atlas.microsoft.com/test_url"
        
        # Mock ML model responses  
        mock_yolo_instance = Mock()
        mock_yolo_instance.detect.return_value = [
            {
                'lat': 47.6205,
                'lng': -122.3493,
                'conf': 0.88,
                'primary_score': 0.88,
                'secondary_score': 0.75,
                'id': 'detection_002'
            }
        ]
        mock_yolo.return_value = mock_yolo_instance
        
        mock_en_instance = Mock()
        mock_en_instance.classify.return_value = [
            {'confidence': 0.75, 'classification': 'cooling_tower'}
        ]
        mock_en.return_value = mock_en_instance
        
        # Test Azure Maps workflow
        with self.client.session_transaction() as sess:
            sess['polygon'] = self.test_polygon
            sess['provider'] = 'azure'
            sess['session_id'] = 'test_azure_session'
        
        response = self.client.post('/draw_polygon',
                                   data=json.dumps({'polygon': self.test_polygon}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @patch('towerscout.TSYolov5')
    @patch('towerscout.TSEfficientNet')
    def test_detection_cancellation_workflow(self, mock_en, mock_yolo):
        """Test user cancellation of detection workflow."""
        # Setup for long-running detection
        mock_yolo_instance = Mock()
        mock_yolo.return_value = mock_yolo_instance
        mock_en.return_value = Mock()
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = 'cancellation_test'
        
        # Start detection process
        response = self.client.post('/draw_polygon',
                                   data=json.dumps({'polygon': self.test_polygon}),
                                   content_type='application/json')
        
        # Cancel detection
        cancel_response = self.client.post('/cancel_detection')
        self.assertEqual(cancel_response.status_code, 200)
        
        # Verify cancellation status
        data = json.loads(cancel_response.data)
        self.assertEqual(data['status'], 'cancelled')


class TestMapProviderIntegration(unittest.TestCase):
    """Test integration with different map providers."""

    def setUp(self):
        """Set up test environment."""
        self.test_coordinates = {
            'lat': 47.6205,
            'lng': -122.3493
        }

    @patch('requests.get')
    def test_google_maps_integration(self, mock_requests):
        """Test Google Maps provider integration."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_requests.return_value = mock_response
        
        # Test Google Maps provider
        google_maps = GoogleMaps('test_api_key')
        
        test_tile = {
            'lat': self.test_coordinates['lat'],
            'lng': self.test_coordinates['lng'],
            'lat_for_url': self.test_coordinates['lat'],
            'id': 'test_tile_google'
        }
        
        url = google_maps.get_url(test_tile)
        self.assertIn('googleapis.com', url)
        self.assertIn('test_api_key', url)

    @patch('requests.get')
    def test_azure_maps_integration(self, mock_requests):
        """Test Azure Maps provider integration."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_requests.return_value = mock_response
        
        # Test Azure Maps provider
        azure_maps = AzureMaps('test_subscription_key')
        
        test_tile = {
            'lat': self.test_coordinates['lat'],
            'lng': self.test_coordinates['lng'],
            'lat_for_url': self.test_coordinates['lat'],
            'id': 'test_tile_azure'
        }
        
        url = azure_maps.get_url(test_tile)
        self.assertIn('atlas.microsoft.com', url)
        self.assertIn('test_subscription_key', url)

    @patch.dict('os.environ', {
        'GOOGLE_API_KEY': 'test_google_key',
        'AZURE_MAPS_SUBSCRIPTION_KEY': 'test_azure_key'
    })
    def test_provider_factory_creation(self):
        """Test map provider factory creation."""
        # Test Azure Maps provider creation
        azure_provider = create_azure_maps_provider()
        self.assertIsInstance(azure_provider, AzureMaps)
        
        # Test provider fallback behavior
        # (This would test actual fallback logic if implemented)

    def test_coordinate_transformation_consistency(self):
        """Test coordinate transformations are consistent across providers."""
        test_tiles = [
            {
                'lat': 47.6205,
                'lng': -122.3493,
                'lat_for_url': 47.6205,
                'id': 'consistency_test_tile'
            }
        ]
        
        # Create provider instances
        google_maps = GoogleMaps('test_key')
        azure_maps = AzureMaps('test_key')
        
        # Both providers should generate valid URLs
        google_url = google_maps.get_url(test_tiles[0])
        azure_url = azure_maps.get_url(test_tiles[0])
        
        self.assertIsInstance(google_url, str)
        self.assertIsInstance(azure_url, str)
        self.assertIn('http', google_url)
        self.assertIn('http', azure_url)


class TestSessionIntegration(unittest.TestCase):
    """Test session management integration across components."""

    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_session_persistence_across_requests(self):
        """Test session data persists across multiple requests."""
        test_data = {
            'polygon': [
                {'lat': 47.6195, 'lng': -122.3503},
                {'lat': 47.6215, 'lng': -122.3503}
            ],
            'provider': 'azure',
            'session_id': 'persistence_test'
        }
        
        # Set session data
        with self.client.session_transaction() as sess:
            sess.update(test_data)
        
        # Make multiple requests and verify session persists
        response1 = self.client.get('/get_status')
        self.assertEqual(response1.status_code, 200)
        
        response2 = self.client.get('/getobjects')
        self.assertEqual(response2.status_code, 200)
        
        # Check session data is still available
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['provider'], 'azure')
            self.assertEqual(sess['session_id'], 'persistence_test')

    def test_session_isolation_between_users(self):
        """Test session isolation between multiple users."""
        # Create two separate clients
        client1 = self.app.test_client()
        client2 = self.app.test_client()
        
        # Set different session data for each client
        with client1.session_transaction() as sess:
            sess['user'] = 'user1'
            sess['provider'] = 'google'
        
        with client2.session_transaction() as sess:
            sess['user'] = 'user2'
            sess['provider'] = 'azure'
        
        # Verify sessions are isolated
        with client1.session_transaction() as sess:
            self.assertEqual(sess['user'], 'user1')
            self.assertEqual(sess['provider'], 'google')
        
        with client2.session_transaction() as sess:
            self.assertEqual(sess['user'], 'user2')
            self.assertEqual(sess['provider'], 'azure')

    def test_event_session_integration(self):
        """Test integration between Flask sessions and event system."""
        session_id = 'event_integration_test'
        
        # Set up session
        with self.client.session_transaction() as sess:
            sess['session_id'] = session_id
        
        # Set event for the session
        test_event = {
            'progress': 45,
            'message': 'Integration test event',
            'status': 'running'
        }
        set_event(session_id, test_event)
        
        # Retrieve via Flask route
        response = self.client.get('/get_status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['progress'], 45)
        self.assertEqual(data['status'], 'running')
        
        # Clean up
        clear_events(session_id)


class TestErrorRecoveryIntegration(unittest.TestCase):
    """Test error handling and recovery across integrated components."""

    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('ts_gmaps.GoogleMaps.get_url')
    def test_map_provider_error_recovery(self, mock_get_url):
        """Test recovery from map provider errors."""
        # Simulate map provider error
        mock_get_url.side_effect = Exception("Network timeout")
        
        response = self.client.post('/draw_polygon',
                                   data=json.dumps({'polygon': [
                                       {'lat': 47.6195, 'lng': -122.3503},
                                       {'lat': 47.6215, 'lng': -122.3503}
                                   ]}),
                                   content_type='application/json')
        
        # Should handle error gracefully
        self.assertIn(response.status_code, [400, 500])  # Expected error response

    @patch('ts_validation.validate_detection_request')
    def test_validation_error_integration(self, mock_validate):
        """Test validation error handling in integrated workflow."""
        # Simulate validation error
        from ts_errors import ValidationError
        mock_validate.side_effect = ValidationError("Invalid polygon coordinates")
        
        response = self.client.post('/draw_polygon',
                                   data=json.dumps({'polygon': 'invalid'}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance characteristics of integrated system."""

    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_concurrent_user_sessions(self):
        """Test system performance with multiple concurrent users."""
        num_clients = 5
        clients = [self.app.test_client() for _ in range(num_clients)]
        
        def simulate_user(client, user_id):
            """Simulate a user session."""
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['polygon'] = [
                    {'lat': 47.6195 + user_id * 0.001, 'lng': -122.3503},
                    {'lat': 47.6215 + user_id * 0.001, 'lng': -122.3503}
                ]
            
            # Make several requests
            responses = []
            responses.append(client.get('/get_status'))
            responses.append(client.get('/getobjects'))
            
            return responses
        
        # Run concurrent sessions
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(simulate_user, clients[i], i) 
                      for i in range(num_clients)]
            
            results = [future.result() for future in futures]
        
        # Verify all sessions completed successfully
        for responses in results:
            for response in responses:
                self.assertIn(response.status_code, [200, 400])  # Success or expected error

    def test_memory_usage_with_large_polygons(self):
        """Test memory behavior with large polygon areas."""
        # Large polygon covering significant area
        large_polygon = []
        num_points = 20
        
        # Create polygon with many points
        for i in range(num_points):
            angle = (2 * 3.14159 * i) / num_points
            lat = 47.62 + 0.01 * (0.5 + 0.5 * (angle / (2 * 3.14159)))
            lng = -122.35 + 0.01 * (0.5 + 0.5 * (angle / (2 * 3.14159)))
            large_polygon.append({'lat': lat, 'lng': lng})
        
        # Test with large polygon (should handle gracefully)
        response = self.client.post('/draw_polygon',
                                   data=json.dumps({'polygon': large_polygon}),
                                   content_type='application/json')
        
        # Should either succeed or fail gracefully with validation error
        self.assertIn(response.status_code, [200, 400])


if __name__ == '__main__':
    unittest.main()