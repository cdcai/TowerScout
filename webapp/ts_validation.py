"""
TowerScout Input Validation System

Provides comprehensive input validation and sanitization for all user inputs
to TowerScout. Prevents injection attacks and ensures data integrity.
"""

import json
import re
import os
from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import Polygon
from shapely.geometry.polygon import LinearRing
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class TowerScoutValidator:
    """Comprehensive input validation for TowerScout application"""
    
    # Constants
    MAX_POLYGON_POINTS = 1000
    MIN_POLYGON_POINTS = 3
    MAX_COORDINATE_PRECISION = 15  # decimal places
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'tif'}
    ALLOWED_DATASET_EXTENSIONS = {'zip'}
    ALLOWED_MODEL_EXTENSIONS = {'pt', 'pth'}
    
    # Geographic bounds (approximate world bounds with buffer)
    MIN_LATITUDE = -90.0
    MAX_LATITUDE = 90.0
    MIN_LONGITUDE = -180.0
    MAX_LONGITUDE = 180.0
    
    # Engine and provider validation
    VALID_ENGINES = {'yolo', 'efficientnet', 'both'}  # Legacy abstract types
    VALID_PROVIDERS = {'google', 'azure'}
    
    @staticmethod
    def get_available_engines():
        """Get list of available YOLOv5 model engines from filesystem"""
        engines = set()
        
        # Add abstract engine types for backwards compatibility
        engines.update(TowerScoutValidator.VALID_ENGINES)
        
        # Add dynamic model files from yolov5 directory
        model_dir = os.path.join(os.path.dirname(__file__), 'model_params', 'yolov5')
        if os.path.exists(model_dir):
            for filename in os.listdir(model_dir):
                if filename.endswith('.pt'):
                    # Remove .pt extension to get engine ID (case-sensitive as stored)
                    engine_id = filename[:-3]
                    engines.add(engine_id)
        
        return engines
    
    @staticmethod
    def normalize_engine_name(engine: str, available_engines: set) -> str:
        """Normalize engine name for case-insensitive matching"""
        # First try exact match
        if engine in available_engines:
            return engine
            
        # Try case-insensitive match
        engine_lower = engine.lower()
        for available in available_engines:
            if available.lower() == engine_lower:
                return available
                
        # No match found
        return None
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input by removing dangerous characters"""
        if not isinstance(value, str):
            raise ValidationError("Input must be a string")
        
        # Remove null bytes and other dangerous characters
        sanitized = value.replace('\x00', '').strip()
        
        # Limit length
        if len(sanitized) > max_length:
            raise ValidationError(f"String exceeds maximum length of {max_length} characters")
        
        return sanitized
    
    @staticmethod
    def validate_coordinate(coord: float, coord_type: str) -> float:
        """Validate a single coordinate (latitude or longitude)"""
        if not isinstance(coord, (int, float)):
            raise ValidationError(f"Invalid {coord_type}: must be a number")
        
        coord = float(coord)
        
        if coord_type.lower() == 'latitude':
            if not (TowerScoutValidator.MIN_LATITUDE <= coord <= TowerScoutValidator.MAX_LATITUDE):
                raise ValidationError(f"Latitude {coord} out of valid range ({TowerScoutValidator.MIN_LATITUDE}, {TowerScoutValidator.MAX_LATITUDE})")
        elif coord_type.lower() == 'longitude':
            if not (TowerScoutValidator.MIN_LONGITUDE <= coord <= TowerScoutValidator.MAX_LONGITUDE):
                raise ValidationError(f"Longitude {coord} out of valid range ({TowerScoutValidator.MIN_LONGITUDE}, {TowerScoutValidator.MAX_LONGITUDE})")
        
        # Check precision (prevent excessive decimal places)
        if len(str(coord).split('.')[-1]) > TowerScoutValidator.MAX_COORDINATE_PRECISION:
            raise ValidationError(f"Coordinate precision exceeds maximum of {TowerScoutValidator.MAX_COORDINATE_PRECISION} decimal places")
        
        return coord
    
    @staticmethod
    def validate_polygon_coordinates(polygon_data: List[List[float]]) -> List[Tuple[float, float]]:
        """Validate polygon coordinate data"""
        if not isinstance(polygon_data, list):
            raise ValidationError("Polygon must be a list of coordinates")
        
        if len(polygon_data) < TowerScoutValidator.MIN_POLYGON_POINTS:
            raise ValidationError(f"Polygon must have at least {TowerScoutValidator.MIN_POLYGON_POINTS} points")
        
        if len(polygon_data) > TowerScoutValidator.MAX_POLYGON_POINTS:
            raise ValidationError(f"Polygon cannot have more than {TowerScoutValidator.MAX_POLYGON_POINTS} points")
        
        validated_coords = []
        for i, point in enumerate(polygon_data):
            if not isinstance(point, list) or len(point) != 2:
                raise ValidationError(f"Polygon point {i} must be a list of [longitude, latitude]")
            
            try:
                lng = TowerScoutValidator.validate_coordinate(point[0], 'longitude')
                lat = TowerScoutValidator.validate_coordinate(point[1], 'latitude')
                validated_coords.append((lng, lat))
            except ValidationError as e:
                raise ValidationError(f"Polygon point {i}: {e.message}")
        
        return validated_coords
    
    @staticmethod
    def validate_polygon_geometry(coordinates: List[Tuple[float, float]]) -> Polygon:
        """Validate that coordinates form a valid polygon geometry"""
        try:
            # Ensure polygon is closed
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])
            
            # Create Shapely polygon
            polygon = Polygon(coordinates)
            
            if not polygon.is_valid:
                raise ValidationError("Polygon geometry is invalid (self-intersecting or malformed)")
            
            if polygon.area == 0:
                raise ValidationError("Polygon has zero area")
            
            # Check for reasonable size (not too small or too large)
            if polygon.area < 1e-10:
                raise ValidationError("Polygon area is too small")
            
            if polygon.area > 100:  # ~100 square degrees is very large
                raise ValidationError("Polygon area is too large")
            
            return polygon
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Failed to validate polygon geometry: {str(e)}")
    
    @staticmethod
    def validate_polygons_json(polygons_str: str) -> List[Polygon]:
        """Validate JSON string containing polygon data"""
        if not polygons_str:
            raise ValidationError("Polygons data is required")
        
        try:
            polygons_data = json.loads(polygons_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {str(e)}")
        
        if not isinstance(polygons_data, list):
            raise ValidationError("Polygons must be provided as a JSON list")
        
        if len(polygons_data) == 0:
            raise ValidationError("At least one polygon is required")
        
        if len(polygons_data) > 10:  # Reasonable limit
            raise ValidationError("Too many polygons (maximum 10 allowed)")
        
        validated_polygons = []
        for i, polygon_data in enumerate(polygons_data):
            try:
                coords = TowerScoutValidator.validate_polygon_coordinates(polygon_data)
                polygon = TowerScoutValidator.validate_polygon_geometry(coords)
                validated_polygons.append(polygon)
            except ValidationError as e:
                raise ValidationError(f"Polygon {i}: {e.message}")
        
        return validated_polygons
    
    @staticmethod
    def validate_bounds(bounds_str: str) -> Dict[str, float]:
        """Validate geographic bounds string"""
        if not bounds_str:
            raise ValidationError("Bounds are required")
        
        # Expected format: "lat1,lng1,lat2,lng2"
        try:
            parts = bounds_str.split(',')
            if len(parts) != 4:
                raise ValidationError("Bounds must contain exactly 4 coordinates: lat1,lng1,lat2,lng2")
            
            coords = [float(part.strip()) for part in parts]
            lat1, lng1, lat2, lng2 = coords
            
            # Validate individual coordinates
            TowerScoutValidator.validate_coordinate(lat1, 'latitude')
            TowerScoutValidator.validate_coordinate(lng1, 'longitude')
            TowerScoutValidator.validate_coordinate(lat2, 'latitude')
            TowerScoutValidator.validate_coordinate(lng2, 'longitude')
            
            # Ensure bounds are logical (min < max)
            if lat1 >= lat2:
                raise ValidationError("Invalid bounds: lat1 must be less than lat2")
            if lng1 >= lng2:
                raise ValidationError("Invalid bounds: lng1 must be less than lng2")
            
            # Check bounds size is reasonable
            lat_diff = lat2 - lat1
            lng_diff = lng2 - lng1
            
            if lat_diff > 10 or lng_diff > 10:  # ~10 degrees is very large
                raise ValidationError("Bounds area is too large (maximum ~10 degrees)")
            
            if lat_diff < 1e-6 or lng_diff < 1e-6:
                raise ValidationError("Bounds area is too small")
            
            return {
                'lat1': lat1, 'lng1': lng1,
                'lat2': lat2, 'lng2': lng2
            }
            
        except ValueError:
            raise ValidationError("Bounds must contain valid numbers")
    
    @staticmethod
    def validate_engine(engine: str) -> str:
        """Validate ML engine selection"""
        if not engine:
            raise ValidationError("Engine selection is required")
        
        engine = TowerScoutValidator.sanitize_string(engine)
        
        # Get available engines (includes both abstract types and model files)
        available_engines = TowerScoutValidator.get_available_engines()
        
        # Normalize engine name for case-insensitive matching
        normalized_engine = TowerScoutValidator.normalize_engine_name(engine, available_engines)
        
        if normalized_engine is None:
            raise ValidationError(f"Invalid engine '{engine}'. Valid options: {', '.join(sorted(available_engines))}")
        
        return normalized_engine
    
    @staticmethod
    def validate_provider(provider: str) -> str:
        """Validate map provider selection"""
        if not provider:
            raise ValidationError("Map provider is required")
        
        provider = TowerScoutValidator.sanitize_string(provider).lower()
        
        if provider not in TowerScoutValidator.VALID_PROVIDERS:
            raise ValidationError(f"Invalid provider '{provider}'. Valid options: {', '.join(TowerScoutValidator.VALID_PROVIDERS)}")
        
        return provider
    
    @staticmethod
    def validate_zipcode(zipcode: str) -> str:
        """Validate US zipcode format"""
        if not zipcode:
            raise ValidationError("Zipcode is required")
        
        zipcode = TowerScoutValidator.sanitize_string(zipcode)
        
        # US zipcode patterns: 12345 or 12345-6789
        zipcode_pattern = re.compile(r'^\d{5}(-\d{4})?$')
        if not zipcode_pattern.match(zipcode):
            raise ValidationError("Invalid zipcode format. Expected: 12345 or 12345-6789")
        
        return zipcode
    
    @staticmethod
    def validate_file_upload(file: FileStorage, allowed_extensions: set, max_size: int = None) -> FileStorage:
        """Validate file upload"""
        if not file:
            raise ValidationError("File is required")
        
        if not file.filename or file.filename == '':
            raise ValidationError("File must have a filename")
        
        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            raise ValidationError("Invalid filename")
        
        # Check file extension
        if '.' not in filename:
            raise ValidationError("File must have an extension")
        
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in allowed_extensions:
            raise ValidationError(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Check file size if provided
        if max_size:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if size > max_size:
                raise ValidationError(f"File too large. Maximum size: {max_size / (1024*1024):.1f}MB")
        
        return file
    
    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validate address search query input"""
        if not query or not isinstance(query, str):
            raise ValidationError("Search query is required and must be a string")
        
        # Length limits
        if len(query) > 500:
            raise ValidationError("Search query too long (max 500 characters)")
        
        if len(query.strip()) < 2:
            raise ValidationError("Search query too short (min 2 characters)")
        
        # Sanitize potentially malicious characters
        sanitized = re.sub(r'[<>"\']', '', query)
        sanitized = sanitized.strip()
        
        if not sanitized:
            raise ValidationError("Search query contains only invalid characters")
        
        return sanitized
    
    @staticmethod
    def validate_image_file(file: FileStorage) -> FileStorage:
        """Validate image file upload"""
        return TowerScoutValidator.validate_file_upload(
            file, 
            TowerScoutValidator.ALLOWED_IMAGE_EXTENSIONS,
            TowerScoutValidator.MAX_FILE_SIZE
        )
    
    @staticmethod
    def validate_dataset_file(file: FileStorage) -> FileStorage:
        """Validate dataset file upload"""
        return TowerScoutValidator.validate_file_upload(
            file,
            TowerScoutValidator.ALLOWED_DATASET_EXTENSIONS,
            TowerScoutValidator.MAX_FILE_SIZE
        )
    
    @staticmethod
    def validate_model_file(file: FileStorage) -> FileStorage:
        """Validate model file upload"""
        return TowerScoutValidator.validate_file_upload(
            file,
            TowerScoutValidator.ALLOWED_MODEL_EXTENSIONS,
            TowerScoutValidator.MAX_FILE_SIZE
        )
    
    @staticmethod
    def validate_json_field(json_str: str, field_name: str) -> Any:
        """Validate and parse JSON field"""
        if not json_str:
            raise ValidationError(f"{field_name} is required")
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {field_name}: {str(e)}")


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # {ip: [timestamp1, timestamp2, ...]}
    
    def is_allowed(self, ip: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """Check if request from IP is within rate limits"""
        import time
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Clean old requests
        if ip in self.requests:
            self.requests[ip] = [t for t in self.requests[ip] if t > window_start]
        else:
            self.requests[ip] = []
        
        # Check if under limit
        if len(self.requests[ip]) >= max_requests:
            return False
        
        # Add current request
        self.requests[ip].append(current_time)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def validate_detection_request(form_data: dict) -> dict:
    """Validate complete detection request"""
    validated = {}
    
    # Required fields
    validated['bounds'] = TowerScoutValidator.validate_bounds(form_data.get('bounds'))
    validated['engine'] = TowerScoutValidator.validate_engine(form_data.get('engine'))
    validated['provider'] = TowerScoutValidator.validate_provider(form_data.get('provider'))
    validated['polygons'] = TowerScoutValidator.validate_polygons_json(form_data.get('polygons'))
    
    # Optional fields
    estimate = form_data.get('estimate')
    if estimate:
        if estimate not in ['yes', 'no']:
            raise ValidationError("Estimate must be 'yes' or 'no'")
        validated['estimate'] = estimate
    
    return validated


def validate_zipcode_request(args: dict) -> dict:
    """Validate zipcode lookup request"""
    validated = {}
    validated['zipcode'] = TowerScoutValidator.validate_zipcode(args.get('zipcode'))
    return validated