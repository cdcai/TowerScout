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

"""
TowerScout Geocoding Service

Multi-provider reverse geocoding service for converting coordinates to building addresses.
Supports Azure Maps Search API (primary) and Google Geocoding API (fallback) with
session-based rate limiting and request counting.

Author: TowerScout Development Team
Date: January 2026
"""

import requests
import time
import os
import urllib3
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from flask import session

from ts_errors import TowerScoutError, ConfigurationError, NetworkError
from ts_logging import get_api_logger

# Suppress SSL warnings for local development on Windows
# Note: For production deployment, proper SSL certificates should be configured
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GeocodingProvider(Enum):
    """Supported geocoding service providers."""
    AZURE_MAPS = "azure_maps"
    GOOGLE_MAPS = "google_maps"


@dataclass
@dataclass
class GeocodingResult:
    """Result from geocoding operation."""
    address: str
    provider: GeocodingProvider
    confidence: float  # 0.0 to 1.0
    coordinates: Tuple[float, float]  # (lat, lng)
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'address': self.address,
            'provider': self.provider.value,
            'confidence': self.confidence,
            'coordinates': {
                'lat': self.coordinates[0],
                'lng': self.coordinates[1]
            },
            'success': self.success,
            'error_message': self.error_message
        }


@dataclass
class SessionApiUsage:
    """Tracking API usage per session."""
    google_requests: int = 0
    azure_requests: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0


class GeocodingError(TowerScoutError):
    """Raised when geocoding operations fail."""
    
    def __init__(self, message: str, provider: GeocodingProvider = None, 
                 coordinates: Tuple[float, float] = None, **kwargs):
        # Don't pass provider/coordinates to parent - they're not in parent signature
        # Remove them from kwargs to avoid "unexpected keyword argument" errors
        kwargs.pop('provider', None)
        kwargs.pop('coordinates', None)
        
        super().__init__(
            message=message,
            error_code="GEOCODING_ERROR",
            user_message="Unable to determine address for this location.",
            **kwargs
        )
        # Add provider and coordinates to details AFTER parent init
        if provider:
            self.details["provider"] = provider.value if isinstance(provider, GeocodingProvider) else provider
        if coordinates:
            self.details["coordinates"] = {"lat": coordinates[0], "lng": coordinates[1]}


class RateLimitError(GeocodingError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, provider: GeocodingProvider, **kwargs):
        # Don't pass user_message explicitly - parent GeocodingError already sets it
        message = f"Rate limit exceeded for {provider.value if isinstance(provider, GeocodingProvider) else provider}"
        super().__init__(
            message=message,
            provider=provider,
            **kwargs
        )


class GeocodingService:
    """
    Multi-provider geocoding service with session-based rate limiting.
    
    Provides reverse geocoding (coordinates → addresses) for cooling tower detections
    with automatic provider fallback and session tracking.
    """
    
    def __init__(self, azure_key: Optional[str] = None, google_key: Optional[str] = None,
                 rate_limit_requests_per_minute: int = 30, preferred_provider: str = "auto"):
        """
        Initialize geocoding service with API keys and rate limiting.
        
        Args:
            azure_key: Azure Maps subscription key (optional, falls back to env var)
            google_key: Google Maps API key (optional, falls back to env var)
            rate_limit_requests_per_minute: Maximum requests per minute per session
            preferred_provider: Preferred geocoding provider ('auto', 'azure', or 'google')
            
        Raises:
            ConfigurationError: If no API keys are available
        """
        self.logger = get_api_logger()
        self.rate_limit = rate_limit_requests_per_minute
        self.preferred_provider = preferred_provider
        
        # Load API keys from parameters or environment
        self.azure_key = azure_key or os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
        self.google_key = google_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.azure_key and not self.google_key:
            raise ConfigurationError(
                "At least one geocoding provider API key is required",
                details={"required_env_vars": ["AZURE_MAPS_SUBSCRIPTION_KEY", "GOOGLE_API_KEY"]}
            )
        
        # Provider priority: Azure Maps first, then Google Maps
        self.providers = []
        if self.azure_key:
            self.providers.append(GeocodingProvider.AZURE_MAPS)
            self.logger.info("Azure Maps geocoding enabled")
        if self.google_key:
            self.providers.append(GeocodingProvider.GOOGLE_MAPS)
            self.logger.info("Google Maps geocoding enabled")
        
        self.logger.info(f"Geocoding service initialized with {len(self.providers)} provider(s)")
    
    def _get_session_usage(self) -> SessionApiUsage:
        """Get or create session API usage tracking."""
        if 'geocoding_usage' not in session:
            session['geocoding_usage'] = {
                'google_requests': 0,
                'azure_requests': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'last_request_time': 0
            }
        
        usage_dict = session['geocoding_usage']
        return SessionApiUsage(
            google_requests=usage_dict['google_requests'],
            azure_requests=usage_dict['azure_requests'],
            total_requests=usage_dict['total_requests'],
            successful_requests=usage_dict['successful_requests'],
            failed_requests=usage_dict['failed_requests']
        )
    
    def _update_session_usage(self, provider: GeocodingProvider, success: bool):
        """Update session API usage counters."""
        if 'geocoding_usage' not in session:
            self._get_session_usage()  # Initialize
        
        usage = session['geocoding_usage']
        usage['total_requests'] += 1
        usage['last_request_time'] = time.time()
        
        if provider == GeocodingProvider.AZURE_MAPS:
            usage['azure_requests'] += 1
        elif provider == GeocodingProvider.GOOGLE_MAPS:
            usage['google_requests'] += 1
        
        if success:
            usage['successful_requests'] += 1
        else:
            usage['failed_requests'] += 1
        
        session['geocoding_usage'] = usage
        session.permanent = True  # Ensure session persists
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits for this session."""
        usage = self._get_session_usage()
        current_time = time.time()
        
        # Get last request time
        last_request_time = session.get('geocoding_usage', {}).get('last_request_time', 0)
        time_since_last_request = current_time - last_request_time
        
        # If more than 60 seconds have passed, reset the counter
        if time_since_last_request >= 60:
            self.logger.debug("Rate limit window expired, resetting counter")
            session['geocoding_usage']['total_requests'] = 0
            session['geocoding_usage']['last_request_time'] = current_time
            return True
        
        # Within the 60-second window, check if limit exceeded
        if usage.total_requests >= self.rate_limit:
            self.logger.warning(f"Rate limit exceeded: {usage.total_requests}/{self.rate_limit} requests in last {time_since_last_request:.1f}s")
            return False
        
        return True
    
    def _geocode_azure_maps(self, lat: float, lng: float) -> GeocodingResult:
        """
        Reverse geocode using Azure Maps Search API.
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            
        Returns:
            GeocodingResult with address information
        """
        try:
            # Azure Maps reverse geocoding endpoint
            url = "https://atlas.microsoft.com/search/address/reverse/json"
            params = {
                'api-version': '1.0',
                'subscription-key': self.azure_key,
                'query': f"{lat},{lng}",
                'radius': '100',  # Search within 100m radius
                'returnRoadUse': 'true',
                'returnMatchType': 'true'
            }
            
            self.logger.debug(f"Azure Maps geocoding request: {lat}, {lng}")
            # Note: verify=False bypasses SSL verification for local development
            # For production, ensure proper SSL certificates are installed
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Azure Maps response (uses 'addresses' key, not 'results')
            if data.get('summary', {}).get('numResults', 0) > 0 and 'addresses' in data:
                result = data['addresses'][0]
                address = result.get('address', {}).get('freeformAddress', '')
                
                # Calculate confidence based on match type and distance
                confidence = 0.8  # Default for Azure Maps
                if result.get('matchType') == 'AddressPoint':
                    confidence = 0.95
                elif result.get('matchType') == 'Street':
                    confidence = 0.7
                
                self.logger.debug(f"Azure Maps success: {address}")
                return GeocodingResult(
                    address=address,
                    provider=GeocodingProvider.AZURE_MAPS,
                    confidence=confidence,
                    coordinates=(lat, lng),
                    success=True
                )
            else:
                self.logger.debug("Azure Maps: No results found")
                return GeocodingResult(
                    address="",
                    provider=GeocodingProvider.AZURE_MAPS,
                    confidence=0.0,
                    coordinates=(lat, lng),
                    success=False,
                    error_message="No address found"
                )
        
        except requests.RequestException as e:
            self.logger.error(f"Azure Maps API error: {e}")
            # NetworkError accepts url and timeout, not provider/coordinates
            raise NetworkError(
                f"Azure Maps API request failed: {e}",
                url=f"https://atlas.microsoft.com/search/address/reverse/json?query={lat},{lng}"
            )
        except Exception as e:
            self.logger.error(f"Azure Maps processing error: {e}")
            raise GeocodingError(
                f"Azure Maps geocoding failed: {e}",
                provider=GeocodingProvider.AZURE_MAPS,
                coordinates=(lat, lng)
            )
    
    def _geocode_google_maps(self, lat: float, lng: float) -> GeocodingResult:
        """
        Reverse geocode using Google Geocoding API.
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            
        Returns:
            GeocodingResult with address information
        """
        try:
            # Google Geocoding API reverse geocoding endpoint
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lng}",
                'key': self.google_key,
                'location_type': 'ROOFTOP|RANGE_INTERPOLATED',
                'result_type': 'street_address|premise|subpremise'
            }
            
            self.logger.debug(f"Google Maps geocoding request: {lat}, {lng}")
            # Note: verify=False bypasses SSL verification for local development
            # For production, ensure proper SSL certificates are installed
            response = requests.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Google Maps response
            if data.get('status') == 'OK' and data.get('results'):
                result = data['results'][0]
                address = result.get('formatted_address', '')
                
                # Calculate confidence based on location type
                confidence = 0.8  # Default
                location_type = result.get('geometry', {}).get('location_type', '')
                if location_type == 'ROOFTOP':
                    confidence = 0.95
                elif location_type == 'RANGE_INTERPOLATED':
                    confidence = 0.85
                
                self.logger.debug(f"Google Maps success: {address}")
                return GeocodingResult(
                    address=address,
                    provider=GeocodingProvider.GOOGLE_MAPS,
                    confidence=confidence,
                    coordinates=(lat, lng),
                    success=True
                )
            else:
                error_msg = data.get('error_message', 'No results found')
                self.logger.debug(f"Google Maps: {error_msg}")
                return GeocodingResult(
                    address="",
                    provider=GeocodingProvider.GOOGLE_MAPS,
                    confidence=0.0,
                    coordinates=(lat, lng),
                    success=False,
                    error_message=error_msg
                )
        
        except requests.RequestException as e:
            self.logger.error(f"Google Maps API error: {e}")
            # NetworkError accepts url and timeout, not provider/coordinates
            raise NetworkError(
                f"Google Maps API request failed: {e}",
                url=f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}"
            )
        except Exception as e:
            self.logger.error(f"Google Maps processing error: {e}")
            raise GeocodingError(
                f"Google Maps geocoding failed: {e}",
                provider=GeocodingProvider.GOOGLE_MAPS,
                coordinates=(lat, lng)
            )
    
    def reverse_geocode(self, lat: float, lng: float, preferred_provider: Optional[str] = None) -> GeocodingResult:
        """
        Reverse geocode coordinates to building address with provider fallback.
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            preferred_provider: Optional override for preferred provider.
                              If None, uses the service's configured preference.
            
        Returns:
            GeocodingResult with address and metadata
            
        Raises:
            RateLimitError: If session rate limit exceeded
            GeocodingError: If all providers fail
        """
        # Check rate limits
        if not self._check_rate_limit():
            self.logger.warning("Rate limit exceeded for geocoding request")
            raise RateLimitError(GeocodingProvider.AZURE_MAPS)  # Use first provider for error
        
        # Use instance preference if no override provided
        effective_preference = preferred_provider if preferred_provider is not None else self.preferred_provider
        
        self.logger.info(f"Reverse geocoding: {lat}, {lng} (preferred: {effective_preference})")
        
        # Determine provider order based on preference
        provider_order = self._get_provider_order(effective_preference)
        
        # Try each provider in order
        for provider in provider_order:
            try:
                if provider == GeocodingProvider.AZURE_MAPS:
                    result = self._geocode_azure_maps(lat, lng)
                elif provider == GeocodingProvider.GOOGLE_MAPS:
                    result = self._geocode_google_maps(lat, lng)
                else:
                    continue
                
                # Update session usage
                self._update_session_usage(provider, result.success)
                
                # Return if successful
                if result.success and result.address:
                    self.logger.info(f"Geocoding successful via {provider.value}: {result.address}")
                    return result
                else:
                    self.logger.debug(f"Provider {provider.value} returned no address, trying next")
                    continue
            
            except (NetworkError, GeocodingError) as e:
                self.logger.warning(f"Provider {provider.value} failed: {e}")
                self._update_session_usage(provider, False)
                continue
        
        # All providers failed - return failure result
        self.logger.error(f"All geocoding providers failed for coordinates: {lat}, {lng}")
        return GeocodingResult(
            address=f"Address unavailable - {lat:.6f}, {lng:.6f}",
            provider=self.providers[0] if self.providers else GeocodingProvider.AZURE_MAPS,
            confidence=0.0,
            coordinates=(lat, lng),
            success=False,
            error_message="All geocoding providers failed"
        )
    
    def forward_geocode_unified(self, query: str, preferred_provider: str = "auto") -> List[GeocodingResult]:
        """
        Convert address to coordinates with provider fallback.
        
        Args:
            query: Address or place query string
            preferred_provider: 'auto', 'azure', or 'google'
            
        Returns:
            List of geocoding results (may be empty if no results found)
        """
        self.logger.info(f"Forward geocoding query: {query[:50]}... (preferred: {preferred_provider})")
        
        # Determine provider order based on preference
        provider_order = self._get_provider_order(preferred_provider)
        
        for provider in provider_order:
            try:
                if provider == GeocodingProvider.AZURE_MAPS:
                    results = self._forward_geocode_azure_maps(query)
                elif provider == GeocodingProvider.GOOGLE_MAPS:
                    results = self._forward_geocode_google_maps(query)
                else:
                    continue
                
                if results:
                    self.logger.info(f"Forward geocoding successful via {provider.value}: {len(results)} result(s)")
                    return results
                    
            except RateLimitError:
                self.logger.warning(f"Rate limit exceeded for {provider.value}, trying next provider")
                continue
            except Exception as e:
                self.logger.warning(f"Forward geocoding failed for {provider.value}: {e}")
                continue
        
        # No results found from any provider
        self.logger.warning(f"No forward geocoding results found for query: {query}")
        return []
    
    def _forward_geocode_azure_maps(self, query: str) -> List[GeocodingResult]:
        """Forward geocoding using Azure Maps Search API."""
        if not self.azure_key:
            return []
        
        self._check_rate_limit()
        
        try:
            url = "https://atlas.microsoft.com/search/fuzzy/json"
            params = {
                'api-version': '1.0',
                'subscription-key': self.azure_key,
                'query': query,
                'limit': 5,
                'typeahead': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            self._track_request(GeocodingProvider.AZURE_MAPS, response.status_code == 200)
            
            if response.status_code == 429:
                raise RateLimitError(GeocodingProvider.AZURE_MAPS)
            elif not response.ok:
                self.logger.warning(f"Azure Maps forward geocoding failed: {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            for result in data.get('results', []):
                position = result.get('position', {})
                lat = position.get('lat')
                lng = position.get('lon')
                
                if lat is None or lng is None:
                    continue
                
                address = result.get('address', {}).get('freeformAddress', query)
                confidence = result.get('score', 0.5)
                
                results.append(GeocodingResult(
                    address=address,
                    provider=GeocodingProvider.AZURE_MAPS,
                    confidence=confidence,
                    coordinates=(lat, lng),
                    success=True
                ))
            
            return results
            
        except requests.Timeout:
            self.logger.warning("Azure Maps forward geocoding timeout")
            return []
        except Exception as e:
            self.logger.error(f"Azure Maps forward geocoding error: {e}")
            return []
    
    def _forward_geocode_google_maps(self, query: str) -> List[GeocodingResult]:
        """Forward geocoding using Google Maps Geocoding API."""
        if not self.google_key:
            return []
        
        self._check_rate_limit()
        
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': query,
                'key': self.google_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            self._track_request(GeocodingProvider.GOOGLE_MAPS, response.status_code == 200)
            
            if response.status_code == 429:
                raise RateLimitError(GeocodingProvider.GOOGLE_MAPS)
            elif not response.ok:
                self.logger.warning(f"Google Maps forward geocoding failed: {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            for result in data.get('results', []):
                location = result.get('geometry', {}).get('location', {})
                lat = location.get('lat')
                lng = location.get('lng')
                
                if lat is None or lng is None:
                    continue
                
                address = result.get('formatted_address', query)
                # Google doesn't provide confidence scores, estimate based on result type
                confidence = 0.9 if 'street_address' in result.get('types', []) else 0.7
                
                results.append(GeocodingResult(
                    address=address,
                    provider=GeocodingProvider.GOOGLE_MAPS,
                    confidence=confidence,
                    coordinates=(lat, lng),
                    success=True
                ))
            
            return results
            
        except requests.Timeout:
            self.logger.warning("Google Maps forward geocoding timeout")
            return []
        except Exception as e:
            self.logger.error(f"Google Maps forward geocoding error: {e}")
            return []
    
    def _get_provider_order(self, preferred_provider: str) -> List[GeocodingProvider]:
        """Get provider order based on preference."""
        if preferred_provider == "azure" and GeocodingProvider.AZURE_MAPS in self.providers:
            return [GeocodingProvider.AZURE_MAPS] + [p for p in self.providers if p != GeocodingProvider.AZURE_MAPS]
        elif preferred_provider == "google" and GeocodingProvider.GOOGLE_MAPS in self.providers:
            return [GeocodingProvider.GOOGLE_MAPS] + [p for p in self.providers if p != GeocodingProvider.GOOGLE_MAPS]
        else:
            return self.providers
    
    def get_session_usage(self) -> SessionApiUsage:
        """Get current session API usage statistics."""
        return self._get_session_usage()
    
    def reset_session_usage(self):
        """Reset session API usage counters."""
        if 'geocoding_usage' in session:
            del session['geocoding_usage']
        self.logger.info("Session geocoding usage counters reset")


# Factory function for easy integration
def create_geocoding_service(azure_key: Optional[str] = None, google_key: Optional[str] = None, 
                            preferred_provider: str = "auto") -> GeocodingService:
    """
    Factory function to create geocoding service with automatic environment fallback.
    
    Args:
        azure_key: Optional Azure Maps subscription key
        google_key: Optional Google Maps API key
        preferred_provider: 'auto', 'azure', or 'google' (default: 'auto')
        
    Returns:
        Configured GeocodingService instance
        
    Raises:
        ConfigurationError: If no API keys available
        
    Note:
        The preferred_provider is stored in the service instance and used automatically
        for all reverse_geocode() calls unless explicitly overridden.
    """
    return GeocodingService(
        azure_key=azure_key, 
        google_key=google_key,
        preferred_provider=preferred_provider
    )