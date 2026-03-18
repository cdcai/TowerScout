# Decision Record 007: Coordinate System Transformation Strategy

**Date**: December 10, 2025  
**Status**: Approved  
**Decision Maker**: Development Team  

## Decision

Implement coordinate system transformation to handle the lng,lat vs lat,lng order difference between Azure Maps (GeoJSON standard) and existing Google Maps/Bing Maps providers, with comprehensive validation to ensure ML detection accuracy is preserved.

## Context

Azure Maps migration introduces a critical coordinate system difference:
- **Existing Providers**: Use lat,lng order (37.7749, -122.4194)
- **Azure Maps**: Uses lng,lat order (-122.4194, 37.7749) following GeoJSON standard
- **Impact**: Incorrect coordinate handling could completely break geographic accuracy of cooling tower detection

The TowerScout ML pipeline depends on precise coordinate transformations:
1. User polygon coordinates → Tile generation
2. Tile coordinates → Image download 
3. YOLO detection coordinates → Geographic lat/lng output
4. Geographic coordinates → Frontend map display

Any coordinate system errors would result in:
- Detections appearing in wrong geographic locations
- Tiles downloaded for incorrect areas
- Complete failure of detection pipeline geographic accuracy

## Options Evaluated

### Option A: Transform at Provider Interface (Selected)
**Implementation**: Each provider handles its own coordinate format internally
```python
class AzureMapsProvider:
    def get_tile_url(self, tile: TileInfo) -> str:
        # Azure Maps expects lng,lat order
        return f"...&center={tile.lng},{tile.lat}&..."

class GoogleMapsProvider:
    def get_tile_url(self, tile: TileInfo) -> str:
        # Google Maps expects lat,lng order  
        return f"...{tile.lat},{tile.lng}..."
```

**Pros**:
- Encapsulates coordinate handling within provider
- No changes to core application logic
- Provider-specific optimizations possible
- Clear separation of concerns

**Cons**:
- Requires validation in each provider
- Risk of inconsistent implementations
- Provider-specific debugging complexity

### Option B: Central Coordinate Transformation Service
**Implementation**: Single service handles all coordinate transformations
```python
class CoordinateTransformService:
    @staticmethod
    def transform_for_provider(provider: str, lat: float, lng: float):
        if provider == "azure":
            return (lng, lat)
        else:
            return (lat, lng)
```

**Pros**:
- Centralized coordinate handling logic
- Consistent transformation across providers
- Easier testing and validation
- Single point of control

**Cons**:
- Additional abstraction layer
- All providers must use service
- Potential performance overhead

### Option C: Standardize on Single Format
**Implementation**: Convert all providers to use lng,lat (GeoJSON) internally
**Pros**:
- No transformation overhead
- Industry standard format
- Consistent throughout application

**Cons**:
- Breaking changes to existing providers
- Extensive validation required across entire codebase
- Higher risk of introducing bugs

## Rationale

Option A was selected because:

1. **Minimal Risk**: Encapsulates coordinate handling changes within new Azure Maps provider without affecting existing Google Maps implementation

2. **Incremental Validation**: Each provider can be validated independently, reducing risk of cross-provider coordinate bugs

3. **Performance**: No additional transformation layers or service calls

4. **Maintainability**: Provider-specific coordinate handling is more intuitive for debugging and maintenance

5. **Backward Compatibility**: Existing Google Maps provider requires no changes, reducing regression risk

## Implementation Strategy

### Provider Interface Contract
```python
class TileInfo:
    """Standardized tile information - always lat,lng internally"""
    def __init__(self, lat: float, lng: float, zoom: int):
        self.lat = lat
        self.lng = lng
        self.zoom = zoom

class MapProvider(ABC):
    @abstractmethod
    def get_tile_url(self, tile: TileInfo) -> str:
        """Provider handles internal coordinate transformation"""
        pass
```

### Azure Maps Implementation
```python
class AzureMapsProvider(MapProvider):
    def get_tile_url(self, tile: TileInfo) -> str:
        # Transform lat,lng → lng,lat for Azure Maps API
        url = f"https://atlas.microsoft.com/map/static?"
        url += f"center={tile.lng},{tile.lat}"  # Note: lng,lat order
        url += f"&zoom={tile.zoom}&width=640&height=640"
        url += f"&subscription-key={self.subscription_key}"
        return url
```

### Validation Strategy
```python
class CoordinateValidator:
    @staticmethod
    def validate_tile_accuracy(providers: List[MapProvider], 
                             test_coordinates: List[Tuple[float, float]]):
        """Validate all providers return imagery for same geographic location"""
        for lat, lng in test_coordinates:
            tile = TileInfo(lat, lng, zoom=19)
            
            for provider in providers:
                url = provider.get_tile_url(tile)
                image_data = download_image(url)
                
                # Validate image represents expected geographic location
                # (Implementation specific - could use image similarity, 
                #  known landmarks, or coordinate metadata validation)
                assert validate_geographic_accuracy(image_data, lat, lng)
```

## Validation Requirements

### Test Coordinate Set
```python
VALIDATION_COORDINATES = [
    (37.7749, -122.4194),  # San Francisco
    (40.7128, -74.0060),   # New York City  
    (51.5074, -0.1278),    # London
    (35.6762, 139.6503),   # Tokyo
    (-33.8688, 151.2093),  # Sydney
    (90.0, 0.0),           # North Pole (edge case)
    (-90.0, 0.0),          # South Pole (edge case)
    (0.0, 180.0),          # Date line (edge case)
    (0.0, -180.0),         # Date line (edge case)
]
```

### Validation Methods
1. **Cross-Provider Comparison**: Same coordinates should return imagery of same geographic location
2. **Known Landmark Validation**: Test coordinates with known landmarks (Golden Gate Bridge, etc.)
3. **Edge Case Testing**: Poles, date line, equator crossing
4. **ML Pipeline Testing**: Run detection pipeline and verify geographic output accuracy

### Acceptance Criteria
- [ ] All test coordinates return geographically accurate imagery across all providers
- [ ] Edge cases (poles, date line) handled correctly
- [ ] ML detection pipeline geographic output maintains accuracy within 10-meter precision
- [ ] Cross-provider imagery comparison shows same geographic locations
- [ ] No coordinate transformation errors in application logs

## Risk Mitigation

### High-Risk Scenarios
1. **Silent Coordinate Swap**: Code appears to work but coordinates are swapped
   - **Mitigation**: Comprehensive automated testing with known landmarks
   - **Detection**: Visual validation and geographic accuracy checks

2. **Edge Case Failures**: Coordinate transformations fail at poles or date line
   - **Mitigation**: Extensive edge case testing
   - **Detection**: Boundary value testing and error monitoring

3. **Provider-Specific Bugs**: Different providers handle coordinates inconsistently
   - **Mitigation**: Standardized validation across all providers
   - **Detection**: Cross-provider comparison testing

### Monitoring and Validation
- **Automated Testing**: Coordinate accuracy tests run on every provider change
- **Production Monitoring**: Log coordinate transformations and validate ranges
- **User Feedback**: Detection result validation by users familiar with geographic areas
- **Regression Testing**: Compare detection results before/after migration

## Impact Assessment

**Development Impact**:
- **Timeline**: Additional 2-3 days for comprehensive coordinate validation
- **Testing**: Extensive geographic accuracy validation required
- **Documentation**: Clear documentation of coordinate handling per provider

**User Impact**:  
- **Positive**: No user-visible changes if implemented correctly
- **Risk**: Complete failure of geographic accuracy if implemented incorrectly
- **Mitigation**: Extensive testing and gradual rollout with validation

**System Impact**:
- **Performance**: Minimal - coordinate transformation is lightweight
- **Reliability**: Enhanced through comprehensive validation
- **Maintainability**: Clear per-provider coordinate handling

## Review Criteria

This decision will be validated through:

1. **Automated Testing**: All validation tests pass with 100% success rate
2. **Manual Validation**: Visual confirmation of imagery accuracy for test coordinates  
3. **ML Pipeline Testing**: Detection pipeline maintains geographic accuracy
4. **Cross-Provider Comparison**: Consistent results across Google Maps and Azure Maps
5. **Edge Case Validation**: Proper handling of geographic edge cases

**Success Metrics**:
- Geographic accuracy within 10-meter precision across all providers
- Zero coordinate transformation errors in production logs
- ML detection results maintain existing geographic accuracy standards
- User-reported geographic accuracy issues remain at baseline levels

**Review Timeline**: Coordinate validation must be completed and verified before Azure Maps provider integration (TASK-008) is considered complete.