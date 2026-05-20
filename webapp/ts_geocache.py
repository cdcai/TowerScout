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
TowerScout Geocoding Cache System

Caching system for geocoding results with spatial clustering and multi-backend support.
Supports Redis (primary) and file-based (fallback) caching with configurable clustering
radius to reduce API calls for nearby detections.

Author: TowerScout Development Team
Date: January 2026
"""

import json
import os
import time
import hashlib
import math
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from ts_geocoding import GeocodingResult, GeocodingProvider
from ts_logging import get_api_logger
from ts_errors import ConfigurationError
from ts_paths import get_geocoding_cache_dir


@dataclass
class CacheEntry:
    """Cache entry for geocoding results."""
    address: str
    provider: str  # Store as string for JSON serialization
    confidence: float
    lat: float
    lng: float
    timestamp: float
    hit_count: int = 1

    @staticmethod
    def is_unavailable_address(address: Optional[str]) -> bool:
        """Identify fallback placeholder addresses that should not be reused."""
        normalized = (address or "").strip()
        lowered = normalized.lower()
        return lowered.startswith("address unavailable") or lowered.startswith("coordinates:")
    
    @classmethod
    def from_geocoding_result(cls, result: GeocodingResult) -> 'CacheEntry':
        """Create cache entry from geocoding result."""
        return cls(
            address=result.address,
            provider=result.provider.value,
            confidence=result.confidence,
            lat=result.coordinates[0],
            lng=result.coordinates[1],
            timestamp=time.time()
        )
    
    def to_geocoding_result(self) -> GeocodingResult:
        """Convert cache entry back to geocoding result."""
        is_unavailable = self.is_unavailable_address(self.address)
        return GeocodingResult(
            address=self.address,
            provider=GeocodingProvider(self.provider),
            confidence=self.confidence,
            coordinates=(self.lat, self.lng),
            success=bool(self.address and not is_unavailable),
            error_message="Cached fallback address" if is_unavailable else None
        )
    
    def is_expired(self, max_age_seconds: int = 86400) -> bool:
        """Check if cache entry has expired (default: 24 hours)."""
        return (time.time() - self.timestamp) > max_age_seconds


class GeocodingCache:
    """
    Multi-backend geocoding cache with spatial clustering.
    
    Provides intelligent caching of geocoding results with configurable spatial
    clustering to group nearby detections and reduce API calls.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, redis_url: Optional[str] = None,
                 clustering_radius_meters: float = 50.0, max_cache_age_hours: int = 24):
        """
        Initialize geocoding cache with backend configuration.
        
        Args:
            cache_dir: Directory for file-based cache (default: webapp/cache/geocoding)
            redis_url: Redis connection URL (optional, file fallback if None)
            clustering_radius_meters: Spatial clustering radius in meters
            max_cache_age_hours: Maximum age for cache entries in hours
        """
        self.logger = get_api_logger()
        self.clustering_radius = clustering_radius_meters
        self.max_cache_age = max_cache_age_hours * 3600  # Convert to seconds
        
        # Setup file-based cache directory
        if cache_dir is None:
            cache_dir = get_geocoding_cache_dir()

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'geocoding_cache.json'
        
        # Try to initialize Redis if URL provided
        self.redis_client = None
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
                # Test connection
                self.redis_client.ping()
                self.logger.info(f"Redis geocoding cache enabled: {redis_url}")
            except ImportError:
                self.logger.warning("Redis not installed, using file-based cache only")
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}, falling back to file cache")
                self.redis_client = None
        
        # Load existing cache from file
        self.file_cache = self._load_file_cache()
        
        self.logger.info(f"Geocoding cache initialized with clustering radius {clustering_radius_meters}m")
        self.logger.info(f"Cache backend: {'Redis + File' if self.redis_client else 'File only'}")
    
    def _load_file_cache(self) -> Dict[str, CacheEntry]:
        """Load cache entries from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cache = {}
                    
                    # Convert JSON back to CacheEntry objects
                    for key, entry_data in data.items():
                        try:
                            cache[key] = CacheEntry(**entry_data)
                        except Exception as e:
                            self.logger.warning(f"Skipping invalid cache entry {key}: {e}")
                    
                    self.logger.info(f"Loaded {len(cache)} entries from file cache")
                    return cache
        except Exception as e:
            self.logger.error(f"Failed to load file cache: {e}")
        
        return {}
    
    def _save_file_cache(self):
        """Save cache entries to file."""
        try:
            # Convert CacheEntry objects to JSON-serializable dict
            data = {key: asdict(entry) for key, entry in self.file_cache.items()}
            
            # Write to temporary file first, then rename for atomicity
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename - use replace() for Windows compatibility
            # replace() overwrites existing file on both Unix and Windows
            temp_file.replace(self.cache_file)
            self.logger.debug(f"Saved {len(self.file_cache)} entries to file cache")
            
        except Exception as e:
            self.logger.error(f"Failed to save file cache: {e}")
    
    def _normalize_provider_key(self, provider: Optional[Union[str, GeocodingProvider]]) -> str:
        """Normalize provider input for cache isolation."""
        if isinstance(provider, GeocodingProvider):
            return provider.value
        if isinstance(provider, str) and provider.strip():
            provider_key = provider.strip().lower()
            aliases = {
                "azure": GeocodingProvider.AZURE_MAPS.value,
                "azure_maps": GeocodingProvider.AZURE_MAPS.value,
                "azuremaps": GeocodingProvider.AZURE_MAPS.value,
                "google": GeocodingProvider.GOOGLE_MAPS.value,
                "google_maps": GeocodingProvider.GOOGLE_MAPS.value,
                "googlemaps": GeocodingProvider.GOOGLE_MAPS.value,
            }
            return aliases.get(provider_key, provider_key)
        return "auto"

    def _provider_key_aliases(self, provider: Optional[Union[str, GeocodingProvider]]) -> List[str]:
        """Return canonical and legacy provider keys for cache lookup compatibility."""
        provider_key = self._normalize_provider_key(provider)
        aliases = [provider_key]

        legacy_aliases = {
            GeocodingProvider.AZURE_MAPS.value: ["azure"],
            GeocodingProvider.GOOGLE_MAPS.value: ["google"],
        }
        for alias in legacy_aliases.get(provider_key, []):
            if alias not in aliases:
                aliases.append(alias)

        return aliases

    def _cluster_coordinates(self, lat: float, lng: float, radius: Optional[float] = None) -> Tuple[float, float]:
        """Return the internal cache-grid coordinates for a lat/lng pair."""
        if radius is None:
            radius = self.clustering_radius

        if radius > 0:
            grid_size = radius / 111000
            return (
                round(lat / grid_size) * grid_size,
                round(lng / grid_size) * grid_size,
            )

        return lat, lng

    def _cache_key_for_cluster(self, cluster_lat: float, cluster_lng: float, provider_key: str) -> str:
        key_string = f"geocode:{provider_key}:{cluster_lat:.8f},{cluster_lng:.8f}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _generate_cache_key(self, lat: float, lng: float,
                            provider: Optional[Union[str, GeocodingProvider]] = None,
                            radius: Optional[float] = None) -> str:
        """
        Generate cache key for coordinates with optional clustering.
        
        Args:
            lat: Latitude
            lng: Longitude
            provider: Provider dimension for cache isolation
            radius: Clustering radius override (uses instance default if None)
            
        Returns:
            Cache key string
        """
        if radius is None:
            radius = self.clustering_radius
        
        # Round coordinates to clustering precision
        if radius > 0:
            # Calculate grid size based on clustering radius
            # Approximate: 1 degree is about 111 km, so grid_size = radius / 111000
            grid_size = radius / 111000
            cluster_lat = round(lat / grid_size) * grid_size
            cluster_lng = round(lng / grid_size) * grid_size
        else:
            # No clustering - use exact coordinates
            cluster_lat = lat
            cluster_lng = lng
        
        provider_key = self._normalize_provider_key(provider)

        # Create hash for cache key
        key_string = f"geocode:{provider_key}:{cluster_lat:.8f},{cluster_lng:.8f}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate Haversine distance between two points in meters.
        
        Args:
            lat1, lng1: First point coordinates
            lat2, lng2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        # Haversine formula
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _candidate_cache_keys(self, lat: float, lng: float,
                              provider: Optional[Union[str, GeocodingProvider]] = None) -> List[str]:
        """Return provider-scoped base and neighboring cache bucket keys."""
        provider_keys = self._provider_key_aliases(provider)
        if self.clustering_radius <= 0:
            keys = []
            seen = set()
            for provider_key in provider_keys:
                cache_key = self._cache_key_for_cluster(lat, lng, provider_key)
                if cache_key not in seen:
                    seen.add(cache_key)
                    keys.append(cache_key)
            return keys

        grid_size = self.clustering_radius / 111000
        base_lat, base_lng = self._cluster_coordinates(lat, lng)
        keys = []
        seen = set()

        for provider_key in provider_keys:
            for lat_offset in (-1, 0, 1):
                for lng_offset in (-1, 0, 1):
                    cache_key = self._cache_key_for_cluster(
                        base_lat + (lat_offset * grid_size),
                        base_lng + (lng_offset * grid_size),
                        provider_key,
                    )
                    if cache_key not in seen:
                        seen.add(cache_key)
                        keys.append(cache_key)

        return keys

    def _entry_score(self, entry: CacheEntry, lat: float, lng: float) -> Optional[Tuple[float, float, float]]:
        """Return deterministic cache-hit ordering fields, or None if unusable."""
        if entry.is_expired(self.max_cache_age) or entry.is_unavailable_address(entry.address):
            return None

        distance = self._calculate_distance(lat, lng, entry.lat, entry.lng)
        if self.clustering_radius > 0 and distance > self.clustering_radius:
            return None

        return distance, -entry.confidence, -entry.timestamp

    def get(self, lat: float, lng: float,
            provider: Optional[Union[str, GeocodingProvider]] = None) -> Optional[GeocodingResult]:
        """
        Get cached geocoding result for coordinates, checking neighboring buckets.

        When clustering is enabled, the nearest valid result inside the radius wins,
        then higher confidence, then newest timestamp.
        """
        provider_key = self._normalize_provider_key(provider)
        cache_keys = self._candidate_cache_keys(lat, lng, provider=provider_key)
        candidates = []

        if self.redis_client:
            try:
                for cache_key in cache_keys:
                    redis_key = f"towerscout:geocoding:{cache_key}"
                    cached_data = self.redis_client.get(redis_key)
                    if not cached_data:
                        continue

                    entry_data = json.loads(cached_data.decode())
                    entry = CacheEntry(**entry_data)
                    score = self._entry_score(entry, lat, lng)
                    if score is None:
                        self.redis_client.delete(redis_key)
                        continue

                    candidates.append((score, "redis", cache_key, entry))
            except Exception as e:
                self.logger.warning(f"Redis cache lookup failed: {e}")

        file_cache_changed = False
        for cache_key in cache_keys:
            entry = self.file_cache.get(cache_key)
            if entry is None:
                continue

            score = self._entry_score(entry, lat, lng)
            if score is None:
                del self.file_cache[cache_key]
                file_cache_changed = True
                continue

            candidates.append((score, "file", cache_key, entry))

        if file_cache_changed:
            self._save_file_cache()

        if not candidates:
            self.logger.debug(f"Cache miss for {lat}, {lng} ({provider_key})")
            return None

        score, source, cache_key, entry = min(candidates, key=lambda item: item[0])
        entry.hit_count += 1

        if source == "redis" and self.redis_client:
            try:
                self.redis_client.set(
                    f"towerscout:geocoding:{cache_key}",
                    json.dumps(asdict(entry)),
                    ex=self.max_cache_age
                )
            except Exception as e:
                self.logger.warning(f"Redis cache hit update failed: {e}")

        distance = score[0]
        self.logger.debug(
            f"{source.capitalize()} cache hit for {lat}, {lng} ({provider_key}, distance: {distance:.1f}m)"
        )
        return entry.to_geocoding_result()
    
    def put(self, lat: float, lng: float, result: GeocodingResult,
            provider: Optional[Union[str, GeocodingProvider]] = None):
        """
        Store geocoding result in cache.
        
        Args:
            lat: Original latitude coordinate
            lng: Original longitude coordinate  
            result: GeocodingResult to cache
            provider: Preferred provider for this cache entry
        """
        if (not result.success) or CacheEntry.is_unavailable_address(result.address):
            self.logger.debug(
                f"Skipping cache store for unsuccessful geocode at {lat}, {lng}"
            )
            return

        provider_key = self._normalize_provider_key(provider or result.provider)
        cache_key = self._generate_cache_key(lat, lng, provider=provider_key)
        entry = CacheEntry.from_geocoding_result(result)
        
        # Store original coordinates in cache entry
        entry.lat = lat
        entry.lng = lng
        
        # Store in Redis if available
        if self.redis_client:
            try:
                self.redis_client.set(
                    f"towerscout:geocoding:{cache_key}",
                    json.dumps(asdict(entry)),
                    ex=self.max_cache_age
                )
                self.logger.debug(f"Stored in Redis cache: {lat}, {lng} ({provider_key})")
            except Exception as e:
                self.logger.warning(f"Redis cache store failed: {e}")
        
        # Store in file cache
        self.file_cache[cache_key] = entry
        self._save_file_cache()
        
        self.logger.debug(
            f"Stored in file cache: {lat}, {lng} ({provider_key}) -> {result.address[:50]}"
        )
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            "file_cache_entries": len(self.file_cache),
            "redis_enabled": self.redis_client is not None,
            "clustering_radius_meters": self.clustering_radius,
            "max_cache_age_hours": self.max_cache_age / 3600,
            "total_hit_count": sum(entry.hit_count for entry in self.file_cache.values())
        }
        
        # Add Redis stats if available
        if self.redis_client:
            try:
                redis_keys = self.redis_client.keys("towerscout:geocoding:*")
                stats["redis_cache_entries"] = len(redis_keys)
            except Exception as e:
                self.logger.warning(f"Failed to get Redis stats: {e}")
                stats["redis_cache_entries"] = "unknown"
        
        return stats
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        removed_count = 0
        
        # Clean file cache
        expired_keys = []
        for key, entry in self.file_cache.items():
            if entry.is_expired(self.max_cache_age):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.file_cache[key]
            removed_count += 1
        
        if expired_keys:
            self._save_file_cache()
        
        # Clean Redis cache (entries should auto-expire, but clean manually if needed)
        if self.redis_client:
            try:
                redis_keys = self.redis_client.keys("towerscout:geocoding:*")
                for key in redis_keys:
                    ttl = self.redis_client.ttl(key)
                    if ttl == -1:  # Key exists but has no expiration
                        self.redis_client.delete(key)
                        removed_count += 1
            except Exception as e:
                self.logger.warning(f"Redis cleanup failed: {e}")
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    def clear_cache(self):
        """Clear all cache entries."""
        # Clear file cache
        self.file_cache.clear()
        self._save_file_cache()
        
        # Clear Redis cache
        if self.redis_client:
            try:
                redis_keys = self.redis_client.keys("towerscout:geocoding:*")
                if redis_keys:
                    self.redis_client.delete(*redis_keys)
                self.logger.info(f"Cleared {len(redis_keys)} Redis cache entries")
            except Exception as e:
                self.logger.warning(f"Redis cache clear failed: {e}")
        
        self.logger.info("Geocoding cache cleared")


# Factory function for easy integration
def create_geocoding_cache(clustering_radius_meters: float = 50.0, 
                         redis_url: Optional[str] = None) -> GeocodingCache:
    """
    Factory function to create geocoding cache with defaults.
    
    Args:
        clustering_radius_meters: Spatial clustering radius (default: 50m)
        redis_url: Optional Redis URL for enhanced caching
        
    Returns:
        Configured GeocodingCache instance
    """
    return GeocodingCache(
        clustering_radius_meters=clustering_radius_meters,
        redis_url=redis_url
    )
