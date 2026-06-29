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
# the provider-independent part of maps
#

import time
import random
import tempfile
import os
import math
import asyncio
import aiohttp
import aiofiles
from ts_logging import get_maps_logger
from ts_errors import MapProviderError, NetworkError
from ts_provider_http import (
    PROVIDER_NETWORK_BLOCKED,
    PROVIDER_TIMEOUT,
    TLS_CA_UNTRUSTED,
    create_provider_ssl_context,
    provider_repair_command,
    provider_support_action,
    redact_provider_url,
)

# Initialize logger for this module
maps_logger = get_maps_logger()
TRUTHY_ENV_VALUES = {'1', 'true', 'yes', 'on'}


def _allow_insecure_tls():
    return os.getenv('TOWERSCOUT_ALLOW_INSECURE_TLS', '').strip().lower() in TRUTHY_ENV_VALUES


def _provider_name_from_url(url):
    if "maps.googleapis.com" in url:
        return "google"
    if "atlas.microsoft.com" in url:
        return "azure"
    return "unknown"


def _build_connector(provider):
    ssl_context = create_provider_ssl_context(provider)
    if ssl_context is False:
        maps_logger.warning(
            "Map downloads are running with TLS verification disabled because "
            "TOWERSCOUT_ALLOW_INSECURE_TLS is enabled."
        )
        return aiohttp.TCPConnector(limit=50, limit_per_host=16, ssl=False)
    return aiohttp.TCPConnector(limit=50, limit_per_host=16, ssl=ssl_context)


def _network_error(provider, category, message, url, cause=None, timeout=None):
    details = {
        "provider": provider,
        "category": category,
    }
    support_action = provider_support_action(category, provider)
    if support_action:
        details["support_action"] = support_action
        details["repair_command"] = provider_repair_command(provider)
    return NetworkError(
        message,
        url=redact_provider_url(url),
        cause=cause,
        timeout=timeout,
        details=details,
    )


class Map:

    def __init__(self):
        self.has_metadata = False

    def get_sat_maps(self, tiles, loop, dir, fname):
        try:
            maps_logger.info(f"Starting satellite map download for {len(tiles)} tiles")
            urls = []
            
            for tile in tiles:
                # ask provider for this specific url
                url = self.get_url(tile)
                urls.append(url)
                tile['url'] = url
                tile['provider_url_redacted'] = redact_provider_url(url)
                maps_logger.debug(
                    "Generated provider URL for tile %s: %s",
                    tile.get('id', '?'),
                    tile['provider_url_redacted'],
                )
                if self.has_metadata:
                    urls.append(self.get_meta_url(tile))
            
            # execute download
            loop.run_until_complete(gather_urls(urls, dir, fname, self.has_metadata))
            maps_logger.info(f"Satellite map download completed for {len(tiles)} tiles")
            return self.has_metadata
            
        except Exception as e:
            maps_logger.error(f"Satellite map download failed: {e}")
            raise MapProviderError(
                f"Failed to download satellite maps: {str(e)}",
                provider=self.__class__.__name__,
                cause=e
            )

    #
    # adapted from https://stackoverflow.com/users/6099211/anton-ovsyannikov
    # correct for both bing and GMaps
    #

    def get_static_map_wh(self, lat=None, lng=None, zoom=19, sx=640, sy=640, crop_tiles=False):
        # lat, lng - center
        # sx, sy - map size in pixels

        sy_cropped = int(sy*0.96) if crop_tiles else sy # cut off bottom 4% if cropping requested

        # common factor based on latitude
        lat_factor = math.cos(lat*math.pi/180.)

        # determine degree size
        globe_size = 256 * 2 ** zoom  # total earth map size in pixels at current zoom
        d_lng = sx * 360. / globe_size  # degrees/pixel
        d_lat = sy_cropped * 360. * lat_factor / globe_size  # degrees/pixel
        d_lat_for_url = sy * 360. * lat_factor / globe_size  # degrees/pixel
 
        # determine size in meters
        ground_resolution = 156543.04 * lat_factor / (2 ** zoom)  # meters/pixel
        d_x = sx * ground_resolution
        d_y = sy_cropped * ground_resolution

        #print("d_lat", d_lat, "d_lng", d_lng)
        return (d_lat, d_lat_for_url, d_lng, d_y, d_x)

    #
    # make_map_list:
    #
    # takes a center and radius, or bounds
    # returns a list of centers for zoom 19 scale 2 images
    #

    def make_tiles(self, bounds, overlap_percent=5, crop_tiles=False):
        south, west, north, east = [float(x) for x in bounds.split(",")]

        # width and height of total map
        w = abs(west-east)
        h = abs(south-north)
        lng = (east+west)/2.0
        lat = (north+south)/2.0

        # width and height of a tile as degrees, also get the meters
        h_tile, h_for_url, w_tile, meters, meters_x = self.get_static_map_wh(
            lng=lng, lat=lat, crop_tiles=crop_tiles)
        maps_logger.debug(f"Tile dimensions: width={w_tile:.6f}, height={h_tile:.6f} degrees")

        # how many tiles horizontally and vertically?
        nx = math.ceil(w/w_tile/(1-overlap_percent/100.))
        ny = math.ceil(h/h_tile/(1-overlap_percent/100.))

        # now make a list of centerpoints of the tiles for the map
        tiles = []
        for row in range(ny):
            for col in range(nx):
                tiles.append({
                    'lat': north - (0.5+row) * h_tile * (1-overlap_percent/100.),
                    'lat_for_url':north - (0.5 * h_for_url + row * h_tile) * (1-overlap_percent/100.),
                    'lng': west + (col+0.5) * w_tile * (1-overlap_percent/100.),
                    'h':h_tile, 
                    'w': w_tile,
                    'id':len(tiles)
                })

        return tiles, nx, ny, meters, h_tile, w_tile


#
#  async file download helpers
#

async def gather_urls(urls, dir, fname, metadata):
    try:
        # change number to limit how many simultaneous calls
        semaphore = asyncio.Semaphore(16)
        
        maps_logger.info(f"Starting download of {len(urls)} map tiles")
        
        # Create session with proper error handling
        provider = _provider_name_from_url(urls[0]) if urls else "unknown"
        connector = _build_connector(provider)
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute total timeout
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            maps_logger.debug("Running with Semaphore limiter (16 concurrent)")
            await fetch_all(semaphore, session, urls, dir, fname, metadata)
            
        maps_logger.info(f"Completed download of {len(urls)} map tiles")
        
    except Exception as e:
        maps_logger.error(f"Map tile download failed: {e}")
        if isinstance(e, (MapProviderError, NetworkError)):
            raise
        else:
            raise MapProviderError(
                f"Map tile download system error: {str(e)}",
                provider="unknown",
                cause=e
            )


async def fetch(semaphore, session, url, dir, fname, i, max_retries=3):
    meta = False
    urlorig = url
    if url.endswith(" (meta)"):
        url = url[0:-7]
        meta = True
    provider = _provider_name_from_url(url)
    redacted_url = redact_provider_url(url)
    
    retry_count = 0
    while retry_count <= max_retries:
        try:
            async with semaphore:
                timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        # write the file
                        filename = os.path.join(dir, fname + str(i) + (".meta.txt" if meta else ".jpg"))
                        maps_logger.debug(f"Retrieving {filename}")
                        
                        try:
                            async with aiofiles.open(filename, mode='wb') as f:
                                await f.write(await response.read())
                            return  # Success, exit function
                        except Exception as e:
                            maps_logger.error(f"File write failed for {filename}: {e}")
                            raise NetworkError(
                                f"Failed to write downloaded file: {filename}",
                                url=redacted_url,
                                cause=e
                            )
                    
                    elif response.status == 429:
                        # Rate limited - exponential backoff
                        retry_after = int(response.headers.get('Retry-After', 2 ** retry_count))
                        maps_logger.warning("Rate limited (429) for %s, retrying after %ss", redacted_url, retry_after)
                        await asyncio.sleep(retry_after)
                        retry_count += 1
                        continue
                        
                    elif response.status in [500, 502, 503, 504]:
                        # Server errors - retry with backoff
                        backoff_time = 2 ** retry_count
                        maps_logger.warning("Server error %s for %s, retrying after %ss", response.status, redacted_url, backoff_time)
                        await asyncio.sleep(backoff_time)
                        retry_count += 1
                        continue
                        
                    else:
                        # Client error or other status - don't retry
                        maps_logger.error("HTTP %s for %s: %s", response.status, redacted_url, response.reason)
                        raise MapProviderError(
                            f"Map API returned status {response.status}: {response.reason}",
                            provider="unknown",
                            api_response_code=response.status
                        )
                        
        except asyncio.TimeoutError:
            maps_logger.warning("Timeout for %s, attempt %s/%s", redacted_url, retry_count + 1, max_retries + 1)
            retry_count += 1
            if retry_count <= max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                continue
            else:
                raise _network_error(
                    provider,
                    PROVIDER_TIMEOUT,
                    f"Request timeout after {max_retries + 1} attempts",
                    url=url,
                    timeout=30,
                )

        except aiohttp.ClientSSLError as e:
            maps_logger.warning(
                "TLS verification failed for %s, attempt %s/%s",
                redacted_url,
                retry_count + 1,
                max_retries + 1,
            )
            raise _network_error(
                provider,
                TLS_CA_UNTRUSTED,
                "TLS certificate validation failed during map tile download",
                url=url,
                cause=e,
                timeout=30,
            )

        except aiohttp.ClientError as e:
            maps_logger.warning(
                "Network error for %s, attempt %s/%s",
                redacted_url,
                retry_count + 1,
                max_retries + 1,
            )
            retry_count += 1
            if retry_count <= max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                continue
            else:
                raise _network_error(
                    provider,
                    PROVIDER_NETWORK_BLOCKED,
                    f"Network error after {max_retries + 1} attempts",
                    url=url,
                    cause=e,
                )
                
        except Exception as e:
            maps_logger.error("Unexpected error fetching %s: %s", redacted_url, e)
            raise MapProviderError(
                "Unexpected error during map tile download",
                provider="unknown",
                cause=e
            )
    
    # If we get here, all retries failed
    raise MapProviderError(
        f"Failed to download map tile after {max_retries + 1} attempts",
        provider="unknown",
        api_response_code=None
    )
            

async def fetch_all(semaphore, session, urls, dir, fname, metadata):
    try:
        tasks = []
        for (i, url) in enumerate(urls):
            task = fetch(semaphore, session, url, dir, fname, i//2 if metadata else i)
            tasks.append(task)
        
        # Gather all results so we can fail the imagery phase with accurate counts.
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_tiles = len(urls) // 2 if metadata else len(urls)
        failed_asset_count = 0
        failed_tile_ids = set()
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_asset_count += 1
                failed_tile_ids.add(i // 2 if metadata else i)
                maps_logger.error(f"Failed to download tile {i}: {result}")
        
        successful_tile_count = total_tiles - len(failed_tile_ids)
        if failed_tile_ids:
            failed_tile_count = len(failed_tile_ids)
            maps_logger.warning(
                "Imagery download failed for %s of %s tile(s).",
                failed_tile_count,
                total_tiles,
            )
            raise MapProviderError(
                f"Failed to download required imagery for {failed_tile_count} of {total_tiles} tile(s).",
                provider="unknown",
                details={
                    "successful_tile_count": successful_tile_count,
                    "failed_tile_count": failed_tile_count,
                    "failed_asset_count": failed_asset_count,
                    "total_tile_count": total_tiles,
                    "failed_tile_ids": sorted(failed_tile_ids),
                },
                user_message=(
                    "Required imagery tiles could not be downloaded. "
                    "Detection stopped before model inference started."
                ),
            )
        
        maps_logger.info(
            "Download completed: %s/%s tile(s) successful",
            successful_tile_count,
            total_tiles,
        )
        return results
        
    except Exception as e:
        if isinstance(e, MapProviderError):
            raise
        else:
            maps_logger.error(f"Batch download error: {e}")
            raise MapProviderError(
                f"Batch tile download failed: {str(e)}",
                provider="unknown",
                cause=e
            )


#
# radian conversion and Haversine distance
#

def rad(x):
    return x * math.pi / 180.


def get_distance(x1, y1, x2, y2):
    R = 6378137.
    # Earth’s mean radius in meters
    dLat = rad(abs(y2 - y1))
    dLong = rad(abs(x2-x1))
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(rad(y1)) * math.cos(rad(y2)) * \
        math.sin(dLong / 2) * math.sin(dLong / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d
    # returns the distance in meters

#
# bounds checking
#


def check_bounds(x1, y1, x2, y2, bounds):
    south, west, north, east = [float(x) for x in bounds.split(",")]
    return not (y1 < south or y2 > north or x2 < west or x1 > east)


def check_tile_against_bounds(t, bounds):
    south, west, north, east = [float(x) for x in bounds.split(",")]
    x1 = t['lng']-t['w']/2
    x2 = t['lng']+t['w']/2
    y1 = t['lat']+t['h']/2
    y2 = t['lat']-t['h']/2

    return not (y1 < south or y2 > north or x2 < west or x1 > east)
