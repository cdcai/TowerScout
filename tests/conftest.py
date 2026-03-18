"""
TowerScout Testing Configuration and Shared Fixtures

This module provides shared pytest configuration and fixtures for all tests.
It handles module imports and provides common test fixtures.
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch

# Add webapp directory to Python path for all tests
WEBAPP_DIR = Path(__file__).parent.parent / 'webapp'
sys.path.insert(0, str(WEBAPP_DIR))


# =============================
# Test Fixtures - File System
# =============================

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_env_vars():
    """Set up test environment variables."""
    return {
        'GOOGLE_API_KEY': 'test_google_key_123',
        'AZURE_MAPS_SUBSCRIPTION_KEY': 'test_azure_key_456',
        'BING_MAPS_API_KEY': 'test_bing_key_789',
        'FLASK_SECRET_KEY': 'test_secret_key_for_sessions',
        'FLASK_ENV': 'testing',
        'FLASK_DEBUG': '0'
    }


# =============================
# ML Model Mock Fixtures
# =============================

@pytest.fixture
def mock_yolov5():
    """Mock YOLOv5 detector to prevent loading actual model weights."""
    mock_detector = Mock()
    mock_detector.detect.return_value = [
        {
            'lat': 47.6205,
            'lng': -122.3493,
            'conf': 0.85,
            'primary_score': 0.85,
            'secondary_score': 0.72,
            'id': 'test_detection_001'
        }
    ]
    mock_detector.get_engine.return_value = mock_detector
    return mock_detector


@pytest.fixture
def mock_efficientnet():
    """Mock EfficientNet classifier to prevent loading actual model weights."""
    mock_classifier = Mock()
    mock_classifier.classify.return_value = [
        {'confidence': 0.72, 'classification': 'cooling_tower'}
    ]
    mock_classifier.get_engine.return_value = mock_classifier
    return mock_classifier


# =============================
# Map Provider Mock Fixtures  
# =============================

@pytest.fixture
def mock_google_maps():
    """Mock Google Maps provider for testing without API consumption."""
    mock_provider = Mock()
    mock_provider.get_url.return_value = "https://maps.googleapis.com/test_url"
    mock_provider.make_tiles.return_value = [
        {
            'lat': 47.6205,
            'lng': -122.3493,
            'lat_for_url': 47.6205,
            'id': 'test_tile_001'
        }
    ]
    mock_provider.has_metadata = False
    return mock_provider


@pytest.fixture
def mock_azure_maps():
    """Mock Azure Maps provider for testing without API consumption."""
    mock_provider = Mock()
    mock_provider.get_url.return_value = "https://atlas.microsoft.com/test_url"
    mock_provider.make_tiles.return_value = [
        {
            'lat': 47.6205,
            'lng': -122.3493,  
            'lat_for_url': 47.6205,
            'id': 'test_tile_002'
        }
    ]
    mock_provider.has_metadata = True
    return mock_provider


# =============================
# Test Data Fixtures
# =============================

@pytest.fixture
def test_polygon():
    """Standard test polygon for Seattle Space Needle area."""
    return [
        {'lat': 47.6195, 'lng': -122.3503},
        {'lat': 47.6215, 'lng': -122.3503}, 
        {'lat': 47.6215, 'lng': -122.3483},
        {'lat': 47.6195, 'lng': -122.3483}
    ]


@pytest.fixture
def test_coordinates():
    """Test coordinate sets for various validation scenarios."""
    return {
        'valid': [
            {'lat': 47.6205, 'lng': -122.3493},  # Seattle
            {'lat': 40.7589, 'lng': -73.9851},   # New York
            {'lat': 51.5074, 'lng': -0.1278}     # London
        ],
        'edge_cases': [
            {'lat': 89.99, 'lng': 0},            # Near North Pole
            {'lat': -89.99, 'lng': 0},           # Near South Pole
            {'lat': 0, 'lng': 179.99},           # Near Date Line
            {'lat': 0, 'lng': -179.99}           # Near Date Line
        ],
        'invalid': [
            {'lat': 95, 'lng': 0},               # Invalid latitude
            {'lat': 0, 'lng': 185},              # Invalid longitude
            {'lat': None, 'lng': 0},             # Null values
            {'lat': 'invalid', 'lng': 0}         # Non-numeric
        ]
    }


# =============================
# Flask App Test Fixtures
# =============================

@pytest.fixture
def mock_flask_app():
    """Mock Flask application for route testing."""
    mock_app = Mock()
    mock_app.config = {
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key',
        'SESSION_TYPE': 'filesystem'
    }
    return mock_app


@pytest.fixture
def test_session_data():
    """Standard test session data structure."""
    return {
        'polygon': [
            {'lat': 47.6195, 'lng': -122.3503},
            {'lat': 47.6215, 'lng': -122.3503},
            {'lat': 47.6215, 'lng': -122.3483}, 
            {'lat': 47.6195, 'lng': -122.3483}
        ],
        'tiles': [
            {
                'lat': 47.6205,
                'lng': -122.3493,
                'lat_for_url': 47.6205,
                'id': 'test_tile_001'
            }
        ],
        'results': [
            {
                'lat': 47.6205,
                'lng': -122.3493,
                'conf': 0.85,
                'id': 'detection_001'
            }
        ]
    }


# =============================
# Performance Test Fixtures
# =============================

@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    start_time = time.time()
    
    def get_elapsed():
        return time.time() - start_time
    
    return get_elapsed


# =============================
# Auto-use Fixtures
# =============================

@pytest.fixture(autouse=True)
def mock_environment_setup(monkeypatch):
    """Automatically set up test environment for all tests."""
    # Mock environment variables
    test_env = {
        'GOOGLE_API_KEY': 'test_google_key_123',
        'AZURE_MAPS_SUBSCRIPTION_KEY': 'test_azure_key_456', 
        'BING_MAPS_API_KEY': 'test_bing_key_789',
        'FLASK_SECRET_KEY': 'test_secret_key_for_sessions'
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture(autouse=True)
def prevent_model_loading():
    """Prevent actual ML model loading in all tests."""
    with patch('torch.load') as mock_load:
        mock_load.return_value = Mock()
        yield mock_load