#
# TowerScout
# A tool for identifying cooling towers from satellite and aerial imagery
#
# TowerScout Team:
# Karen Wong, Gunnar Mein, Thaddeus Segura, Jia Lu
#
# Licensed under CC-BY-NC-SA-4.0
# (see LICENSE.TXT in the root of the repository for details)
#

#
# Azure Maps provider class with coordinate transformation
#

from ts_maps import Map
from ts_errors import MapProviderError, ConfigurationError, NetworkError
from ts_logging import get_maps_logger
import os
from typing import Dict, Any, Optional

class AzureMaps(Map):
    """
    Azure Maps provider implementation with GeoJSON coordinate transformation.
    
    Critical: Azure Maps uses longitude,latitude order (GeoJSON standard)
    while TowerScout internally uses latitude,longitude order.
    This class handles the coordinate transformation at URL generation time.
    """

    def __init__(self, subscription_key: str):
        """
        Initialize Azure Maps provider with subscription key authentication.
        
        Args:
            subscription_key: Azure Maps subscription key from environment or config
            
        Raises:
            ConfigurationError: If subscription key is missing or invalid
        """
        super().__init__()
        
        # Initialize logger
        self.logger = get_maps_logger()
        
        # Validate subscription key
        if not subscription_key or not subscription_key.strip():
            self.logger.error("Azure Maps subscription key is missing")
            raise ConfigurationError(
                "Azure Maps subscription key is required",
                error_code="AZURE_MAPS_NO_KEY",
                details={'required_env_var': 'AZURE_MAPS_SUBSCRIPTION_KEY'},
                user_message="Azure Maps configuration is missing. Please check your subscription key."
            )
        
        self.subscription_key = subscription_key.strip()
        
        # Azure Maps configuration
        self.has_metadata = False  # Azure Maps has no metadata endpoint
        self.base_url = "https://atlas.microsoft.com/map/static"
        self.api_version = "2024-04-01"
        
        # Performance optimization: pre-build URL template
        self.url_template = (
            f"{self.base_url}?api-version={self.api_version}"
            "&tilesetId={tileset_id}&zoom={zoom}"
            "&center={center}&height={height}&width={width}"
            f"&subscription-key={self.subscription_key}"
        )
        
        self.logger.info("Azure Maps provider initialized successfully")
        self.logger.debug(f"Base URL: {self.base_url}")

    def get_url(self, tile: Dict[str, Any], zoom: int = 19, size: str = "640,640", 
                sc: int = 2, fmt: str = "jpeg", maptype: str = "satellite") -> str:
        """
        Generate Azure Maps Static API URL with coordinate transformation.
        
        CRITICAL: Transforms internal lat,lng coordinates to Azure lng,lat format
        
        Args:
            tile: Dictionary with 'lat', 'lng', and 'lat_for_url' keys
            zoom: Zoom level (0-20, default 19)
            size: Image size as "width,height" or "widthxheight" (default "640,640")
            sc: Scale factor (unused in Azure Maps, kept for compatibility)
            fmt: Image format - "jpeg" or "png" (default "jpeg")
            maptype: Map type - converts to Azure tileset (default "satellite")
            
        Returns:
            Complete Azure Maps Static API URL
            
        Raises:
            MapProviderError: If URL generation fails
        """
        try:
            # CRITICAL: Coordinate transformation lat,lng -> lng,lat
            center_lng = tile['lng']  # longitude first for Azure Maps
            center_lat = tile['lat_for_url']  # use lat_for_url for consistency with existing code
            
            # Validate coordinates are within valid ranges
            if not (-180 <= center_lng <= 180):
                raise ValueError(f"Longitude {center_lng} outside valid range [-180, 180]")
            if not (-90 <= center_lat <= 90):
                raise ValueError(f"Latitude {center_lat} outside valid range [-90, 90]")
            
            # Convert maptype to Azure tileset
            tileset_id = self._convert_maptype_to_tileset(maptype)
            
            # Parse size parameter (handle both "640,640" and "640x640" formats)
            width, height = self._parse_size(size)
            
            # CRITICAL FIX: Double resolution to match 1280x1280 training data
            # Google Maps uses scale=2 parameter to get 1280x1280 from 640x640 spec
            # Azure Maps requires explicit width/height doubling
            width_original = width
            height_original = height
            width = str(int(width) * 2)
            height = str(int(height) * 2)
            self.logger.debug(f"Resolution doubled for model compatibility: {width_original}x{height_original} -> {width}x{height}")
            
            # Validate zoom level
            if not (0 <= zoom <= 20):
                zoom = min(max(zoom, 0), 20)  # Clamp to valid range
                self.logger.warning(f"Zoom level clamped to valid range: {zoom}")
            
            # Build center parameter in lng,lat format (GeoJSON standard)
            center = f"{center_lng},{center_lat}"
            
            # Generate URL using template for performance
            url = self.url_template.format(
                tileset_id=tileset_id,
                zoom=zoom,
                center=center,
                height=height,
                width=width
            )
            
            self.logger.debug(f"Generated Azure Maps URL for tile {tile.get('id', '?')}: {url[:100]}...")
            self.logger.debug(f"Coordinate transformation: lat={center_lat}, lng={center_lng} -> center={center}")
            
            return url
            
        except Exception as e:
            self.logger.error(f"Failed to generate Azure Maps URL: {str(e)}")
            raise MapProviderError(
                f"Failed to generate Azure Maps URL: {str(e)}",
                error_code="AZURE_MAPS_URL_GENERATION",
                details={
                    'tile': tile,
                    'zoom': zoom,
                    'size': size,
                    'maptype': maptype,
                    'error': str(e)
                },
                user_message="Map service temporarily unavailable. Please try again."
            ) from e

    def get_meta_url(self, tile: Dict[str, Any]) -> str:
        """
        Azure Maps does not support metadata endpoints.
        
        Raises:
            NotImplementedError: Always, as Azure Maps has no metadata API
        """
        self.logger.debug("Metadata request attempted - Azure Maps does not support metadata")
        raise NotImplementedError(
            "Azure Maps does not support metadata endpoints. "
            "Vintage date information is not available."
        )

    def get_date(self, md: str) -> str:
        """
        Return empty string as Azure Maps has no vintage date information.
        
        Args:
            md: Metadata string (unused)
            
        Returns:
            Empty string (no date information available)
        """
        self.logger.debug("Date extraction requested - returning empty (no metadata support)")
        return ""

    def checkCutOffs(self, object: Dict[str, Any]) -> float:
        """
        Check if object was detected in Azure Maps logo/attribution area.
        
        Azure Maps attribution is typically in bottom-right corner.
        Reduce confidence for detections in that area.
        
        Args:
            object: Detection object with 'x1', 'y1', 'x2', 'y2' coordinates (normalized 0-1)
            
        Returns:
            Confidence multiplier (1.0 for normal areas, 0.1 for attribution areas)
        """
        try:
            # Azure Maps attribution is in bottom-right corner
            # Reduce confidence for detections in bottom 4% and right 33% of image
            if object['y2'] > 0.96 and object['x2'] > 0.67:
                self.logger.debug(f"Object detection in attribution area, reducing confidence")
                return 0.1
            
            return 1.0
            
        except KeyError as e:
            self.logger.warning(f"Object missing required coordinates for cutoff check: {e}")
            return 1.0  # Default to no reduction if coordinates missing

    def _convert_maptype_to_tileset(self, maptype: str) -> str:
        """
        Convert TowerScout maptype parameter to Azure Maps tileset ID.
        
        Args:
            maptype: TowerScout map type ("satellite", "road", etc.)
            
        Returns:
            Azure Maps tileset ID
        """
        maptype_conversion = {
            'satellite': 'microsoft.imagery',
            'imagery': 'microsoft.imagery',
            'road': 'microsoft.base.road',
            'hybrid': 'microsoft.imagery',  # No exact hybrid, use imagery
            'terrain': 'microsoft.base.road'  # No terrain, use road
        }
        
        tileset = maptype_conversion.get(maptype.lower(), 'microsoft.imagery')
        
        if tileset != maptype_conversion.get('satellite'):
            self.logger.debug(f"Maptype '{maptype}' converted to tileset '{tileset}'")
        
        return tileset

    def _parse_size(self, size: str) -> tuple[str, str]:
        """
        Parse size parameter and return width, height as strings.
        
        Args:
            size: Size string like "640,640" or "640x640"
            
        Returns:
            Tuple of (width, height) as strings
            
        Raises:
            ValueError: If size format is invalid
        """
        try:
            if ',' in size:
                parts = size.split(',')
            elif 'x' in size.lower():
                parts = size.lower().split('x')
            else:
                # Assume square if only one dimension
                parts = [size, size]
            
            if len(parts) != 2:
                raise ValueError(f"Invalid size format: {size}")
            
            width, height = parts[0].strip(), parts[1].strip()
            
            # Validate dimensions are numeric and within Azure Maps limits
            width_int = int(width)
            height_int = int(height)
            
            if not (80 <= width_int <= 2000):
                raise ValueError(f"Width {width_int} outside valid range [80, 2000]")
            if not (80 <= height_int <= 1500):
                raise ValueError(f"Height {height_int} outside valid range [80, 1500]")
            
            return width, height
            
        except (ValueError, IndexError) as e:
            self.logger.error(f"Invalid size parameter '{size}': {e}")
            raise ValueError(f"Invalid size format '{size}'. Expected 'width,height' or 'widthxheight'") from e

    @classmethod
    def from_environment(cls) -> 'AzureMaps':
        """
        Create Azure Maps provider from environment variables.
        
        Returns:
            Configured AzureMaps instance
            
        Raises:
            ConfigurationError: If required environment variables are missing
        """
        subscription_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
        
        if not subscription_key:
            raise ConfigurationError(
                "AZURE_MAPS_SUBSCRIPTION_KEY environment variable is required",
                error_code="AZURE_MAPS_ENV_MISSING",
                details={'required_env_var': 'AZURE_MAPS_SUBSCRIPTION_KEY'},
                user_message="Azure Maps is not configured. Please set the AZURE_MAPS_SUBSCRIPTION_KEY environment variable."
            )
        
        return cls(subscription_key)

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider for debugging and monitoring.
        
        Returns:
            Dictionary with provider information
        """
        return {
            'provider': 'Azure Maps',
            'base_url': self.base_url,
            'api_version': self.api_version,
            'has_metadata': self.has_metadata,
            'subscription_key_configured': bool(self.subscription_key),
            'coordinate_system': 'GeoJSON (longitude,latitude)'
        }


# Provider factory helper for easy integration
def create_azure_maps_provider(subscription_key: Optional[str] = None) -> AzureMaps:
    """
    Factory function to create Azure Maps provider with automatic environment fallback.
    
    Args:
        subscription_key: Optional subscription key, falls back to environment variable
        
    Returns:
        Configured AzureMaps instance
        
    Raises:
        ConfigurationError: If no subscription key available
    """
    if subscription_key:
        return AzureMaps(subscription_key)
    else:
        return AzureMaps.from_environment()