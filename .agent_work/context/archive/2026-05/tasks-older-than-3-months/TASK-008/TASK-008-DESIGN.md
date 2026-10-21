# TASK-008: Azure Maps Provider - Technical Design

## Overview

Design comprehensive Azure Maps provider implementation to replace Bing Maps with coordinate system transformation and enterprise authentication support.

## Critical Requirements Analysis

### Coordinate System Transformation ⚠️ **CRITICAL**

**Problem**: Azure Maps uses GeoJSON standard (longitude,latitude) while existing TowerScout uses geographic standard (latitude,longitude)

**Current Flow**:
```python
# Existing: lat,lng order (Google/Bing Maps)
tile = {'lat': 47.613079, 'lng': -122.177621}
url = f".../{tile['lat']},{tile['lng']}/..."  # lat,lng
```

**Required Flow**:
```python
# Azure Maps: lng,lat order (GeoJSON standard)
tile = {'lat': 47.613079, 'lng': -122.177621}  # Internal representation unchanged
url = f"...?center={tile['lng']},{tile['lat']}..."  # lng,lat for Azure API
```

**Design Decision**: Keep internal tile data structure unchanged (`lat`, `lng` properties) but transform coordinates only at URL generation time to minimize application impact.

## Architecture Design

### Azure Maps Provider Class

```python
class AzureMaps(Map):
    """Azure Maps provider with GeoJSON coordinate transformation"""
    
    def __init__(self, subscription_key: str):
        super().__init__()
        self.subscription_key = subscription_key
        self.has_metadata = False  # Azure Maps has no metadata endpoint
        self.base_url = "https://atlas.microsoft.com/map/static"
        self.api_version = "2024-04-01"
        
    def get_url(self, tile: dict, zoom: int = 19, size: str = "640,640", 
                fmt: str = "jpeg", tileset_id: str = "microsoft.imagery") -> str:
        """
        Generate Azure Maps Static API URL with coordinate transformation
        
        CRITICAL: Transforms lat,lng → lng,lat for GeoJSON compliance
        """
        # Transform coordinates: internal lat,lng → Azure lng,lat
        center_lng = tile['lng']  # longitude first for Azure
        center_lat = tile['lat_for_url']  # use lat_for_url for consistency
        
        # Query-based URL construction (not path-based like Bing)
        params = {
            'api-version': self.api_version,
            'tilesetId': tileset_id,
            'zoom': zoom,
            'center': f"{center_lng},{center_lat}",  # lng,lat order
            'height': size.split(',')[1] if ',' in size else size.split('x')[1],
            'width': size.split(',')[0] if ',' in size else size.split('x')[0],
            'subscription-key': self.subscription_key
        }
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}?{query_string}"
```

### URL Format Comparison

**Bing Maps (Current)**:
```
http://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/47.613079,-122.177621/19?mapSize=640,640&format=jpeg&key={key}
```

**Azure Maps (Target)**:
```
https://atlas.microsoft.com/map/static?api-version=2024-04-01&tilesetId=microsoft.imagery&zoom=19&center=-122.177621,47.613079&height=640&width=640&subscription-key={key}
```

### Metadata Handling Strategy

**Problem**: Azure Maps has no metadata endpoint (no vintage dates)

**Solution**: Remove metadata dependencies gracefully
```python
class AzureMaps(Map):
    def __init__(self, subscription_key: str):
        self.has_metadata = False  # Signal no metadata support
    
    def get_meta_url(self, tile: dict) -> str:
        """Not supported in Azure Maps"""
        raise NotImplementedError("Azure Maps does not support metadata endpoints")
    
    def get_date(self, md: str) -> str:
        """Return empty string - no vintage date available"""
        return ""
```

### Error Handling Integration

Integrate with existing TowerScout error handling infrastructure:

```python
from ts_errors import MapProviderError, NetworkError, ConfigurationError
from ts_logging import get_maps_logger

class AzureMaps(Map):
    def __init__(self, subscription_key: str):
        self.logger = get_maps_logger()
        
        if not subscription_key:
            raise ConfigurationError(
                "Azure Maps subscription key is required",
                error_code="AZURE_MAPS_NO_KEY",
                user_message="Azure Maps configuration is missing. Please check your subscription key."
            )
    
    def get_url(self, tile: dict, **kwargs) -> str:
        try:
            # URL generation logic
            url = self._build_url(tile, **kwargs)
            self.logger.debug(f"Generated Azure Maps URL: {url[:100]}...")
            return url
            
        except Exception as e:
            raise MapProviderError(
                f"Failed to generate Azure Maps URL: {str(e)}",
                error_code="AZURE_MAPS_URL_GENERATION",
                details={'tile': tile, 'params': kwargs},
                user_message="Map service temporarily unavailable. Please try again."
            ) from e
```

### Authentication Configuration

Support multiple authentication methods:

```python
# Environment variable configuration
AZURE_MAPS_SUBSCRIPTION_KEY = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')

# Header-based authentication (alternative)
def get_headers(self) -> Dict[str, str]:
    """Optional header-based authentication"""
    return {
        'subscription-key': self.subscription_key,
        'Accept': 'image/jpeg'  # or image/png
    }
```

## Coordinate Transformation Validation

### Test Cases for Coordinate Accuracy

```python
# Known location test cases
COORDINATE_TEST_CASES = [
    {
        'name': 'Seattle Space Needle',
        'lat': 47.6205, 'lng': -122.3493,
        'expected_azure_center': '-122.3493,47.6205'
    },
    {
        'name': 'NYC Central Park',
        'lat': 40.7829, 'lng': -73.9654,
        'expected_azure_center': '-73.9654,40.7829'
    },
    {
        'name': 'International Date Line Edge Case',
        'lat': 0.0, 'lng': 179.9999,
        'expected_azure_center': '179.9999,0.0'
    }
]

def test_coordinate_transformation():
    """Validate coordinate transformation accuracy"""
    azure_maps = AzureMaps(subscription_key="test_key")
    
    for test_case in COORDINATE_TEST_CASES:
        tile = {
            'lat': test_case['lat'],
            'lng': test_case['lng'], 
            'lat_for_url': test_case['lat']
        }
        
        url = azure_maps.get_url(tile)
        assert test_case['expected_azure_center'] in url
        
        # Validate coordinates are within 1 meter precision
        # (approximately 0.00001 degrees at equator)
        coordinate_precision = 0.00001
        assert abs(extracted_lng - test_case['lng']) < coordinate_precision
        assert abs(extracted_lat - test_case['lat']) < coordinate_precision
```

## Integration Points

### 1. Map Provider Factory Pattern

```python
# In ts_maps.py or new ts_map_factory.py
class MapProviderFactory:
    @staticmethod
    def create_provider(provider_type: str, **config) -> Map:
        if provider_type == 'google':
            return GoogleMap(config['api_key'])
        elif provider_type == 'bing':
            return BingMap(config['api_key'])  
        elif provider_type == 'azure':
            return AzureMaps(config['subscription_key'])
        else:
            raise ConfigurationError(f"Unknown map provider: {provider_type}")
```

### 2. Configuration Management

```python
# Environment-based provider selection
MAP_PROVIDER = os.getenv('MAP_PROVIDER', 'google')  # default to google
AZURE_MAPS_SUBSCRIPTION_KEY = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')

# Provider configuration
PROVIDER_CONFIG = {
    'google': {'api_key': os.getenv('GOOGLE_API_KEY')},
    'azure': {'subscription_key': AZURE_MAPS_SUBSCRIPTION_KEY},
    'bing': {'api_key': os.getenv('BING_API_KEY')}  # legacy support
}
```

### 3. Flask Route Integration

```python
# In towerscout.py
@app.route('/api/maps/provider', methods=['POST'])
def set_map_provider():
    """Allow users to select map provider"""
    provider_type = request.json.get('provider', 'google')
    
    try:
        # Validate provider is available and configured
        provider = MapProviderFactory.create_provider(provider_type, **PROVIDER_CONFIG[provider_type])
        session['map_provider'] = provider_type
        return jsonify({'success': True, 'provider': provider_type})
        
    except ConfigurationError as e:
        return jsonify({'error': True, 'message': str(e)}), 400
```

## Performance Considerations

### 1. URL Generation Optimization
```python
# Cache URL templates for performance
class AzureMaps(Map):
    def __init__(self, subscription_key: str):
        # Pre-build URL template
        self.url_template = (
            f"{self.base_url}?api-version={self.api_version}"
            f"&tilesetId={{tileset_id}}&zoom={{zoom}}"
            f"&center={{center}}&height={{height}}&width={{width}}"
            f"&subscription-key={subscription_key}"
        )
    
    def get_url(self, tile: dict, **kwargs) -> str:
        # Fast string formatting vs building query params each time
        return self.url_template.format(
            tileset_id=kwargs.get('tileset_id', 'microsoft.imagery'),
            zoom=kwargs.get('zoom', 19),
            center=f"{tile['lng']},{tile['lat_for_url']}",
            height=kwargs.get('size', '640,640').split(',')[1],
            width=kwargs.get('size', '640,640').split(',')[0]
        )
```

### 2. Network Resilience Integration
```python
# Integrate with existing retry logic in ts_maps.py
async def fetch_azure_maps_tile(session: aiohttp.ClientSession, url: str, **kwargs):
    """Fetch Azure Maps tile with retry logic"""
    try:
        return await fetch_with_retry(session, url, **kwargs)
    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            raise MapProviderError(
                "Azure Maps authentication failed",
                error_code="AZURE_MAPS_AUTH_FAILED",
                user_message="Map service authentication error. Please check subscription key."
            )
        elif e.status == 429:
            raise MapProviderError(
                "Azure Maps rate limit exceeded", 
                error_code="AZURE_MAPS_RATE_LIMIT",
                user_message="Map service temporarily busy. Please try again in a moment."
            )
        else:
            raise NetworkError(f"Azure Maps service error: {e.status}") from e
```

## Migration Strategy

### Phase 1: Parallel Implementation
1. Implement AzureMaps class alongside existing providers
2. Add provider selection UI
3. Test coordinate transformation accuracy
4. Validate ML model compatibility

### Phase 2: Default Migration  
1. Set Azure Maps as default for new sessions
2. Maintain Google Maps as user option
3. Deprecate Bing Maps (legacy support only)

### Phase 3: Full Migration
1. Remove Bing Maps dependencies 
2. Update documentation
3. Clean up legacy code

## Risk Mitigation

### 1. Coordinate Precision Loss
- **Risk**: Coordinate transformation introduces floating-point errors
- **Mitigation**: Use high-precision arithmetic, validate within 1-meter accuracy
- **Testing**: Side-by-side comparison with existing providers

### 2. ML Model Compatibility
- **Risk**: Azure Maps imagery differs from Google/Bing, affecting model accuracy
- **Mitigation**: A/B testing with existing detection datasets
- **Fallback**: Maintain Google Maps option for critical applications

### 3. Service Availability
- **Risk**: Azure Maps service outages or quota limits
- **Mitigation**: Implement graceful degradation to Google Maps
- **Monitoring**: Add service health checks and alerting

### 4. Authentication Complexity
- **Risk**: Multiple auth methods (subscription key, header-based, Key Vault)
- **Mitigation**: Start with subscription key, add Key Vault in separate task
- **Configuration**: Environment-based configuration for flexibility

## Implementation Files

### New Files
- `webapp/ts_azure_maps.py` - Azure Maps provider implementation
- `tests/unit/test_azure_maps.py` - Unit tests for provider
- `tests/integration/test_coordinate_validation.py` - Coordinate accuracy tests

### Modified Files  
- `webapp/ts_maps.py` - Enhanced base class if needed
- `webapp/towerscout.py` - Provider selection endpoints
- `webapp/requirements.txt` - No additional dependencies needed

## Success Criteria

1. ✅ **Coordinate Transformation**: Azure Maps URLs generated with correct lng,lat order
2. ✅ **Geographic Accuracy**: Coordinate precision within 1 meter (0.00001 degrees)
3. ✅ **API Compatibility**: URL format matches Azure Maps Static API specification  
4. ✅ **Error Integration**: Comprehensive error handling using TowerScout error infrastructure
5. ✅ **Performance**: URL generation performance equivalent to existing providers
6. ✅ **ML Compatibility**: Detection accuracy maintained with Azure Maps imagery
7. ✅ **Graceful Degradation**: Application functions without metadata features

## Next Steps

Ready for **IMPLEMENT** phase:
1. Create `ts_azure_maps.py` with coordinate transformation
2. Integrate error handling and logging
3. Add provider selection configuration
4. Create comprehensive test suite
5. Validate coordinate accuracy with real-world test cases

---

**Design Confidence**: 85% - Ready for implementation
**Critical Success Factor**: Coordinate transformation accuracy
**Risk Mitigation**: Comprehensive testing with known geographic locations