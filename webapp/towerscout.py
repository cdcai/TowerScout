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

# import basic functionality
from ts_yolov5 import YOLOv5_Detector
from ts_en import EN_Classifier
import ts_imgutil
from ts_gmaps import GoogleMap
from ts_azure_maps import AzureMaps
from ts_zipcode import Zipcode_Provider
from ts_events import ExitEvents
import ts_maps
from flask import Flask, render_template, send_from_directory, request, session, Response, jsonify
from flask_session import Session
from waitress import serve
import json
import time
import os
import math
import secrets
from ts_validation import (
    TowerScoutValidator, ValidationError, rate_limiter,
    validate_detection_request, validate_zipcode_request
)
from ts_errors import (
    TowerScoutError, ConfigurationError, MapProviderError,
    NetworkError
)
from ts_logging import (
    get_main_logger, get_maps_logger, get_ml_logger, 
    get_api_logger
)
from ts_performance import PerformanceMetrics
import ts_config
import torch
from shutil import rmtree
import zipfile
import asyncio
from dotenv import load_dotenv
from ts_progress import DetectionProgressTracker
from ts_paths import (
    CSS_DIR,
    IMG_DIR,
    JS_DIR,
    SITE_DIR,
    get_base_dir,
    get_en_model_dir,
    get_flask_session_dir,
    get_map_cache_dir,
    get_model_params_dir,
    get_session_tmp_root,
    get_temp_dir,
    get_upload_dir,
    get_yolov5_model_dir,
)

# Initialize logging before startup diagnostics so first-run messages stay structured.
logger = get_main_logger()
api_logger = get_api_logger()
ml_logger = get_ml_logger()
maps_logger = get_maps_logger()
logger.info("TowerScout starting")

# Load environment variables from config/.env if available, otherwise legacy .env
script_dir = get_base_dir()
env_path = ts_config.ensure_env_file()

logger.info("TowerScout environment bootstrap starting")
logger.info("Current working directory: %s", os.getcwd())
logger.info("Script directory: %s", script_dir)
logger.info("Active env path: %s", env_path)
logger.info("Env file exists: %s", env_path.exists())

if env_path.exists():
    logger.info("Loading .env from %s", env_path)
    load_dotenv(env_path, override=False)
else:
    logger.info("No explicit env file found; using default load_dotenv() behavior")
    load_dotenv()

# Debug: Check if keys are loaded
google_key = os.getenv('GOOGLE_API_KEY', '')
azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
bing_key = os.getenv('BING_API_KEY', '')

logger.info("GOOGLE_API_KEY configured: %s", bool(google_key))
logger.info("AZURE_MAPS_SUBSCRIPTION_KEY configured: %s", bool(azure_key))
logger.info("BING_API_KEY configured: %s", bool(bing_key))

import tempfile
from ts_geocoding import create_geocoding_service, GeocodingError, RateLimitError
from ts_geocache import create_geocoding_cache

# Map proxy configuration
MAP_PROXY_CONFIG = {
    'google': {
        'tiles': {'rate_limit': (1000, 3600), 'cache_ttl': 86400},  # 1000/hour, 24hr cache
        'static': {'rate_limit': (500, 3600), 'cache_ttl': 43200}   # 500/hour, 12hr cache
    },
    'azure': {
        'search': {'rate_limit': (100, 3600), 'cache_ttl': 3600},   # 100/hour, 1hr cache  
        'tiles': {'rate_limit': (1000, 3600), 'cache_ttl': 86400}   # 1000/hour, 24hr cache
    }
}

# Create cache directory
MAP_CACHE_DIR = get_map_cache_dir()
UPLOAD_DIR = get_upload_dir()
MODEL_PARAMS_DIR = get_model_params_dir()
YOLO_MODEL_DIR = get_yolov5_model_dir()
EN_MODEL_DIR = get_en_model_dir()
from PIL import Image, ImageDraw
import torch
import threading
import gc
import datetime
import sys

dev = 0

MAX_TILES = 100000
MAX_TILES_SESSION = 100000

engines = {}

engine_default = None
engine_lock = threading.Lock()

exit_events = ExitEvents()
secondary_en = None
secondary_en_lock = threading.Lock()
LAZY_MODEL_INIT = os.getenv('TOWERSCOUT_LAZY_MODEL_INIT', '').strip().lower() in ('1', 'true', 'yes', 'on')
progress_tracker = DetectionProgressTracker()
SESSION_TMP_ROOT = get_session_tmp_root()
SESSION_ID_KEY = "ts_session_id"

# on-demand instantiate YOLOv5 model
def get_engine(e):
    if e is None:
        e = engine_default

    with engine_lock:
        # take all the other ones out of play
        for engine in engines:
            # print(engine)
            if engines[engine]['id'] != e:
                engines[engine]['engine'] = None
        gc.collect(generation=2)

        if engines[e]['engine'] is None:
            ml_logger.info(f"Loading model: {engines[e]['name']}")
            engines[e]['engine'] = YOLOv5_Detector(
                str(YOLO_MODEL_DIR / engines[e]['file']))

        return engines[e]['engine']


def find_model(m):
    for engine in engines:
        if m == engines[engine]['file']:
            return True
    return False


def get_custom_models():
    for f in os.listdir(YOLO_MODEL_DIR):
        if f.endswith(".pt") and not find_model(f):
            add_model(f)


def add_model(m):
    # remove ".pt"
    mid = m[:-3]

    engines[mid] = {
        'id': mid,
        'name': mid,
        'file': m,
        'engine': None,
        'ts': os.path.getmtime(YOLO_MODEL_DIR / m)
    }



# map providers
providers = {
    'google': {'id': 'google', 'name': 'Google Maps'},
    'bing': {'id': 'bing', 'name': 'Bing Maps'},
    'azure': {'id': 'azure', 'name': 'Azure Maps'},
}

# Load API keys from environment variables
def load_api_keys(allow_missing=False):
    """Load and validate API keys from environment variables."""
    google_key = os.getenv('GOOGLE_API_KEY', '')
    bing_key = os.getenv('BING_API_KEY', '')
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
    
    # Check for placeholder text and treat as missing
    placeholder_patterns = [
        'your_google_maps_api_key_here',
        'your_bing_maps_api_key_here', 
        'your_azure_maps_subscription_key_here',
        'your_google_api_key',
        'your_bing_maps_',
        'your_azure_maps_'
    ]
    
    # Validate Google API key
    if google_key and not any(placeholder in google_key.lower() for placeholder in placeholder_patterns):
        # Valid Google key
        pass
    else:
        logger.warning("GOOGLE_API_KEY not configured or contains placeholder text. Google Maps provider will be unavailable.")
        google_key = ""
    
    # Validate Bing API key  
    if bing_key and not any(placeholder in bing_key.lower() for placeholder in placeholder_patterns):
        # Valid Bing key
        pass
    else:
        logger.warning("BING_API_KEY not configured or contains placeholder text. Bing Maps provider will be unavailable.")
        bing_key = ""
        
    # Validate Azure API key
    if azure_key and not any(placeholder in azure_key.lower() for placeholder in placeholder_patterns):
        # Valid Azure key
        pass
    else:
        logger.warning("AZURE_MAPS_SUBSCRIPTION_KEY not configured or contains placeholder text. Azure Maps provider will be unavailable.")
        azure_key = ""
    
    setup_required = not google_key and not bing_key and not azure_key

    # At least one provider must be configured with a valid key unless setup mode is allowed
    if setup_required and not allow_missing:
        raise ConfigurationError(
            "At least one map provider API key is required",
            missing_config="GOOGLE_API_KEY or AZURE_MAPS_SUBSCRIPTION_KEY",
            user_message="Map provider API keys are required. Please configure Google Maps or Azure Maps."
        )
    
    return google_key, bing_key, azure_key, setup_required


def refresh_runtime_config():
    """Reload runtime environment variables and refresh global key state."""
    global google_api_key, bing_api_key, azure_api_key, needs_setup

    ts_config.reload_runtime_environment(env_path)
    google_api_key, bing_api_key, azure_api_key, needs_setup = load_api_keys(allow_missing=True)
    app.config['SETUP_REQUIRED'] = needs_setup
    return needs_setup

# Load API keys with degraded setup mode support
google_api_key, bing_api_key, azure_api_key, needs_setup = load_api_keys(allow_missing=True)
if needs_setup:
    logger.warning("Application booting in setup-required mode. Map and detection features will remain blocked until configuration is completed.")

# other global variables
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# prepare uploads directory
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
for existing_upload in UPLOAD_DIR.iterdir():
    if existing_upload.is_file():
        existing_upload.unlink()

ml_logger.info(f"Torch CUDA: {'available' if torch.cuda.is_available() else 'not available'}")


def get_secondary_classifier():
    global secondary_en
    with secondary_en_lock:
        if secondary_en is None:
            ml_logger.info("Loading EfficientNet secondary classifier")
            secondary_en = EN_Classifier()
    return secondary_en


def _get_session_run_id():
    session_id = session.get(SESSION_ID_KEY)
    if not session_id:
        session_id = f"session-{secrets.token_hex(16)}"
        session[SESSION_ID_KEY] = session_id
    return session_id


def _register_detection_run(
    session_id,
    provider,
    engine,
    tile_count,
    run_token=None,
    status='running',
    phase='preparing_tiles',
    title='Preparing tiles',
    detail='Starting detection request...',
    counts=None,
):
    return progress_tracker.start(
        session_id,
        run_token,
        provider=provider,
        engine=engine,
        tile_count=tile_count,
        status=status,
        phase=phase,
        title=title,
        detail=detail,
        counts=counts,
    )


def _update_detection_run(session_id, status=None, run_token=None, **fields):
    return progress_tracker.update(session_id, run_token=run_token, status=status, **fields)


def _mark_detection_run_cancel_requested(session_id):
    return progress_tracker.mark_cancel_requested(session_id)


def _finish_detection_run(session_id, status, run_token=None, **fields):
    return progress_tracker.finish(session_id, status, run_token=run_token, **fields)


def _get_detection_progress_state(session_id):
    return progress_tracker.get(session_id)


def _serialize_detection_progress_state(progress_state):
    public_state = dict(progress_state)
    public_state.pop('run_token', None)
    public_state.pop('expires_at', None)
    return public_state


def _cleanup_session_tmpdir():
    tmpdirname = session.get('tmpdirname')
    if tmpdirname:
        rmtree(tmpdirname, ignore_errors=True, onerror=None)
        api_logger.info("Cleaned up session temp dir %s", tmpdirname)
        del session['tmpdirname']


def _make_session_tmpdir():
    for _ in range(10):
        candidate = os.path.join(SESSION_TMP_ROOT, f"session-{secrets.token_hex(6)}")
        try:
            os.makedirs(candidate)
            return candidate
        except FileExistsError:
            continue

    raise RuntimeError("Unable to create writable session temp directory")


def _format_tile_filter_detail(candidate_tiles, retained_tiles):
    return (
        f"Retained {retained_tiles} of {candidate_tiles} candidate tile(s) "
        "after viewport and polygon filtering."
    )


def _format_download_detail(tile_count):
    return f"Downloading imagery for {tile_count} tile(s)."


def _format_model_detail(batches_completed, total_batches, tiles_processed, total_tiles):
    if total_batches <= 0 or total_tiles <= 0:
        return "Running model detection..."
    return (
        f"Processed {tiles_processed}/{total_tiles} tile(s) across "
        f"{batches_completed}/{total_batches} model batches."
    )


def _format_filtering_detail(raw_detections, inside_count=None, outside_count=None, retained_count=None):
    if inside_count is None or outside_count is None or retained_count is None:
        return f"Applying boundary and duplicate filtering to {raw_detections} raw detection(s)."
    return (
        f"Retained {retained_count} of {raw_detections} raw detection(s) "
        f"({inside_count} inside boundary, {outside_count} outside)."
    )


def _format_geocoding_detail(processed_count, total_count):
    return f"Resolved {processed_count}/{total_count} detection address(es)."


def _format_finalizing_detail(detection_count, tile_record_count):
    return (
        f"Preparing {detection_count} detection(s) and "
        f"{tile_record_count} tile record(s) for display."
    )


def _parse_detection_request(form_data):
    validated_data = validate_detection_request(form_data.to_dict())
    bounds_dict = validated_data['bounds']

    return {
        'bounds': f"{bounds_dict['lat1']},{bounds_dict['lng1']},{bounds_dict['lat2']},{bounds_dict['lng2']}",
        'engine': validated_data['engine'],
        'provider': validated_data['provider'],
        'polygons': validated_data['polygons'],
        'estimate': validated_data.get('estimate')
    }


def _create_map_provider(provider):
    api_logger.debug(
        "Initializing map provider '%s' (google=%s, azure=%s)",
        provider,
        bool(google_api_key),
        bool(azure_api_key),
    )

    if provider == "google" and google_api_key:
        api_logger.info("Google Maps provider initialized")
        return GoogleMap(google_api_key)
    if provider == "azure" and azure_api_key:
        api_logger.info("Azure Maps provider initialized")
        return AzureMaps(azure_api_key)

    api_logger.error("Map provider '%s' not available or not configured", provider)
    raise MapProviderError(
        f"Map provider '{provider}' not available or not configured",
        error_code="MAP_PROVIDER_UNAVAILABLE",
        user_message=f"The {provider} map service is not available. Please try a different provider."
    )


def _build_tiles_for_request(map_provider, bounds, polygons, crop_tiles):
    api_logger.debug(
        "Building tiles for bounds=%s crop_tiles=%s polygon_count=%s",
        bounds,
        crop_tiles,
        len(polygons),
    )

    tiles, nx, ny, meters, h, w = map_provider.make_tiles(bounds, crop_tiles=crop_tiles)
    candidate_tiles = len(tiles)
    api_logger.info("Created %s candidate tile(s) (%s x %s)", len(tiles), nx, ny)

    tiles = [t for t in tiles if ts_maps.check_tile_against_bounds(t, bounds)]
    viewport_tiles = len(tiles)
    tiles = [t for t in tiles if ts_imgutil.tileIntersectsPolygons(t, polygons)]
    for i, tile in enumerate(tiles):
        tile['id'] = i
    api_logger.debug("Retained %s tile(s) after viewport and polygon filtering", len(tiles))

    return tiles, nx, ny, meters, h, w, {
        'candidate_tiles': candidate_tiles,
        'viewport_tiles': viewport_tiles,
        'retained_tiles': len(tiles)
    }


def _get_geocoding_clustering_radius():
    clustering_radius = 50.0
    env_radius = os.getenv('GEOCODING_CLUSTERING_RADIUS', '')
    if env_radius:
        try:
            clustering_radius = float(env_radius)
        except ValueError:
            clustering_radius = 50.0
    return clustering_radius


def _detection_center(detection):
    return (
        (detection['y1'] + detection['y2']) / 2,
        (detection['x1'] + detection['x2']) / 2
    )


def _detection_iou(first, second):
    left = max(first['x1'], second['x1'])
    right = min(first['x2'], second['x2'])
    top = min(first['y1'], second['y1'])
    bottom = max(first['y2'], second['y2'])

    if right <= left or top <= bottom:
        return 0.0

    intersection = (right - left) * (top - bottom)
    first_area = max(0.0, first['x2'] - first['x1']) * max(0.0, first['y1'] - first['y2'])
    second_area = max(0.0, second['x2'] - second['x1']) * max(0.0, second['y1'] - second['y2'])
    union = first_area + second_area - intersection
    if union <= 0:
        return 0.0
    return intersection / union


def _detections_overlap(first, second):
    if first.get('class') != 0 or second.get('class') != 0:
        return False

    first_center_lat, first_center_lng = _detection_center(first)
    second_center_lat, second_center_lng = _detection_center(second)
    center_distance_m = ts_maps.get_distance(
        first_center_lng, first_center_lat,
        second_center_lng, second_center_lat
    )
    iou = _detection_iou(first, second)
    return iou >= 0.35 or center_distance_m <= 3.0


def _dedupe_detection_results(results):
    if len(results) <= 1:
        return results

    ordered_results = sorted(
        results,
        key=lambda detection: (
            0 if detection.get('inside') else 1,
            -float(detection.get('conf', 0.0)),
            -float(detection.get('secondary', 0.0)),
            detection.get('y1', 0.0),
            detection.get('x1', 0.0),
        )
    )

    deduped = []
    removed = 0
    for candidate in ordered_results:
        if any(_detections_overlap(candidate, kept) for kept in deduped):
            removed += 1
            continue
        deduped.append(candidate)

    if removed:
        api_logger.info("Removed %s duplicate detection(s) before geocoding", removed)

    return deduped


def _attach_detection_addresses(results, provider, perf_metrics=None, progress_callback=None):
    session['geocoding_limited'] = False
    if not results:
        return

    api_logger.info("Starting address lookup for %s detection(s)", len(results))
    if perf_metrics:
        perf_metrics.start_phase('geocoding')
    address_start_time = time.time()

    clustering_radius = _get_geocoding_clustering_radius()
    geocoding_service = create_geocoding_service(
        azure_key=azure_api_key,
        google_key=google_api_key,
        preferred_provider=provider
    )
    geocoding_cache = create_geocoding_cache(clustering_radius_meters=clustering_radius)
    geocoding_total = sum(1 for detection in results if detection.get('class') == 0)
    geocoding_processed = 0

    if progress_callback is not None:
        progress_callback(0, geocoding_total)

    for detection in results:
        if detection.get('class') != 0:
            detection['address'] = ""
            detection['address_confidence'] = 0.0
            detection['address_provider'] = "none"
            continue

        center_lat, center_lng = _detection_center(detection)

        try:
            cached_result = geocoding_cache.get(center_lat, center_lng, provider=provider)
            if cached_result:
                detection['address'] = cached_result.address
                detection['address_confidence'] = cached_result.confidence
                detection['address_provider'] = cached_result.provider.value
                geocoding_processed += 1
                if progress_callback is not None and (
                    geocoding_processed % 10 == 0 or geocoding_processed == geocoding_total
                ):
                    progress_callback(geocoding_processed, geocoding_total)
                continue

            geocoding_result = geocoding_service.reverse_geocode(center_lat, center_lng, provider)
            if geocoding_result.success and geocoding_result.address:
                detection['address'] = geocoding_result.address
                detection['address_confidence'] = geocoding_result.confidence
                detection['address_provider'] = geocoding_result.provider.value
                geocoding_cache.put(center_lat, center_lng, geocoding_result, provider=provider)
            else:
                detection['address'] = f"{center_lat:.6f}, {center_lng:.6f}"
                detection['address_confidence'] = 0.0
                detection['address_provider'] = "fallback"
                api_logger.warning(
                    "Geocoding returned no address for %.6f, %.6f: %s",
                    center_lat,
                    center_lng,
                    geocoding_result.error_message,
                )
        except RateLimitError as e:
            session['geocoding_limited'] = True
            detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
            detection['address_confidence'] = 0.0
            detection['address_provider'] = "rate_limited"
            api_logger.warning("Geocoding rate limited for %.6f, %.6f: %s", center_lat, center_lng, e)
        except GeocodingError as e:
            detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
            detection['address_confidence'] = 0.0
            detection['address_provider'] = "fallback"
            api_logger.warning("Geocoding failed for %.6f, %.6f: %s", center_lat, center_lng, e)
        except Exception as e:
            detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
            detection['address_confidence'] = 0.0
            detection['address_provider'] = "error"
            api_logger.error("Unexpected geocoding error for %.6f, %.6f: %s", center_lat, center_lng, e)

        geocoding_processed += 1
        if progress_callback is not None and (
            geocoding_processed % 10 == 0 or geocoding_processed == geocoding_total
        ):
            progress_callback(geocoding_processed, geocoding_total)

    try:
        usage = geocoding_service.get_session_usage()
        session['geocoding_usage'] = {
            'google_requests': usage.google_requests,
            'azure_requests': usage.azure_requests,
            'total_requests': usage.total_requests,
            'successful_requests': usage.successful_requests,
            'failed_requests': usage.failed_requests
        }
        if perf_metrics:
            perf_metrics.geocoding_api_calls = usage.total_requests
    except Exception as e:
        api_logger.warning("Could not store geocoding usage: %s", e)

    if perf_metrics:
        perf_metrics.end_phase('geocoding')
    address_time = time.time() - address_start_time
    api_logger.info("Address lookup completed in %.2f seconds", address_time)


def _run_detection_request():
    session_id = _get_session_run_id()
    run_token = f"{session_id}:{secrets.token_hex(8)}"
    api_logger.debug("Processing detection request for session %s", session_id)

    if 'tiles' not in session:
        session['tiles'] = 0

    if session['tiles'] > MAX_TILES_SESSION:
        return jsonify({'error': 'Tile limit for this session exceeded. Please close browser to continue.'}), 400

    start = time.time()
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    if not rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=60):
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    tmpdirname = None
    request_loop = None
    run_registered = False
    run_succeeded = False
    exit_event_allocated = False
    perf_metrics = None

    try:
        api_logger.debug(
            "Validating detection request with form keys=%s polygons_snippet=%s",
            list(request.form.keys()),
            request.form.get('polygons', '')[:200],
        )

        request_context = _parse_detection_request(request.form)
        bounds = request_context['bounds']
        engine = request_context['engine']
        provider = request_context['provider']
        polygons = request_context['polygons']

        _register_detection_run(
            session_id,
            provider,
            engine,
            0,
            run_token=run_token,
            status='running',
            phase='preparing_tiles',
            title='Preparing tiles',
            detail='Validating the detection request and building search tiles...',
        )
        run_registered = True
        exit_events.alloc(run_token)
        exit_event_allocated = True

        def cancelled_response(detail):
            api_logger.info("Detection cancelled for session %s: %s", session_id, detail)
            if run_registered:
                _finish_detection_run(
                    session_id,
                    'cancelled',
                    run_token=run_token,
                    phase='cancelled',
                    title='Detection cancelled',
                    detail=detail,
                    cancel_requested=True,
                )
            return Response("[]", mimetype='application/json')

        api_logger.info(
            "Incoming detection request session=%s provider=%s engine=%s polygon_count=%s bounds=%s",
            session_id,
            provider,
            engine,
            len(polygons),
            bounds,
        )

        crop_tiles = True
        perf_metrics = PerformanceMetrics(str(session_id))
        perf_metrics.detection_engine = engine
        perf_metrics.map_provider = provider
        perf_metrics.crop_tiles = crop_tiles

        if exit_events.query(run_token):
            return cancelled_response('Detection was cancelled before tile preparation finished.')

        det = get_engine(engine)
        if exit_events.query(run_token):
            return cancelled_response('Detection was cancelled before model initialization finished.')

        map_provider = _create_map_provider(provider)
        tiles, _nx, _ny, _meters, _h, _w, tile_stats = _build_tiles_for_request(
            map_provider,
            bounds,
            polygons,
            crop_tiles
        )

        perf_metrics.tile_count = len(tiles)
        _update_detection_run(
            session_id,
            run_token=run_token,
            tile_count=len(tiles),
            status='running',
            phase='tiles_filtered',
            title='Filtering tiles',
            detail=_format_tile_filter_detail(
                tile_stats['candidate_tiles'],
                tile_stats['retained_tiles']
            ),
            counts=tile_stats,
        )
        perf_metrics.estimate_processing_time(len(tiles))
        session['last_detection_provider'] = provider
        api_logger.info(
            "Detection estimate for session %s: %s tile(s), ~%.1f seconds",
            session_id,
            len(tiles),
            perf_metrics.estimated_time_seconds,
        )

        if exit_events.query(run_token):
            return cancelled_response('Detection was cancelled after tile preparation.')

        if len(tiles) > MAX_TILES:
            api_logger.warning(
                "Detection request for session %s exceeds MAX_TILES with %s tile(s)",
                session_id,
                len(tiles),
            )
            _finish_detection_run(
                session_id,
                'error',
                run_token=run_token,
                phase='error',
                title='Detection blocked',
                detail='The requested search area exceeds the tile limit for a single run.',
                cancel_requested=False,
                counts=tile_stats,
                tile_count=len(tiles),
            )
            return Response("[]", mimetype='application/json')

        session['tiles'] += len(tiles)

        _cleanup_session_tmpdir()
        tmpdirname = _make_session_tmpdir()
        tmpfilename = os.path.basename(tmpdirname)
        api_logger.info("Creating session temp dir %s", tmpdirname)
        session['tmpdirname'] = tmpdirname

        if exit_events.query(run_token):
            return cancelled_response('Detection was cancelled before imagery download started.')

        _update_detection_run(
            session_id,
            run_token=run_token,
            phase='downloading_imagery',
            title='Downloading imagery',
            detail=_format_download_detail(len(tiles)),
            counts={
                'imagery_tiles_total': len(tiles),
                'imagery_tiles_downloaded': 0,
            },
        )
        request_loop = asyncio.new_event_loop()
        perf_metrics.start_phase('tile_download')
        try:
            meta = map_provider.get_sat_maps(tiles, request_loop, tmpdirname, tmpfilename)
        except MapProviderError as error:
            perf_metrics.end_phase('tile_download')
            successful_tiles = int(error.details.get('successful_tile_count', 0))
            failed_tiles = int(
                error.details.get(
                    'failed_tile_count',
                    max(1, len(tiles) - successful_tiles),
                )
            )
            maps_logger.error(
                "Imagery download failed for session %s after %s/%s tile(s): %s",
                session_id,
                successful_tiles,
                len(tiles),
                error,
            )
            _finish_detection_run(
                session_id,
                'error',
                run_token=run_token,
                phase='error',
                title='Imagery download failed',
                detail=(
                    f"Downloaded {successful_tiles}/{len(tiles)} tile(s) before the imagery phase failed. "
                    f"{error.message}"
                ),
                cancel_requested=False,
                counts={
                    'imagery_tiles_total': len(tiles),
                    'imagery_tiles_downloaded': successful_tiles,
                    'imagery_tiles_failed': failed_tiles,
                },
                tile_count=len(tiles),
            )
            return jsonify({'error': f'Imagery download failed: {error.message}'}), 502
        else:
            perf_metrics.end_phase('tile_download')
        session['metadata'] = meta
        api_logger.info("Retrieved imagery for %s tile(s)", len(tiles))
        perf_metrics.map_api_calls = len(tiles)

        if exit_events.query(run_token):
            return cancelled_response('Detection was cancelled during imagery download.')

        missing_tile_filenames = []
        for i, tile in enumerate(tiles):
            filename = os.path.join(tmpdirname, tmpfilename + str(i) + ".jpg")
            tile['filename'] = filename
            if not os.path.exists(filename):
                missing_tile_filenames.append(filename)

        if missing_tile_filenames:
            downloaded_tiles = len(tiles) - len(missing_tile_filenames)
            api_logger.error(
                "Imagery phase for session %s completed without %s expected file(s): %s",
                session_id,
                len(missing_tile_filenames),
                missing_tile_filenames[:5],
            )
            _finish_detection_run(
                session_id,
                'error',
                run_token=run_token,
                phase='error',
                title='Imagery download failed',
                detail=(
                    f"Expected {len(tiles)} downloaded tile file(s) but only found "
                    f"{downloaded_tiles} on disk."
                ),
                cancel_requested=False,
                counts={
                    'imagery_tiles_total': len(tiles),
                    'imagery_tiles_downloaded': downloaded_tiles,
                    'imagery_tiles_failed': len(missing_tile_filenames),
                },
                tile_count=len(tiles),
            )
            return jsonify({
                'error': (
                    "Imagery download failed: required tile files were missing after the "
                    "download phase completed."
                )
            }), 502

        batch_size = max(1, getattr(det, 'batch_size', 1))
        model_batches_total = math.ceil(len(tiles) / batch_size) if len(tiles) > 0 else 0

        def update_model_progress(
            batches_completed,
            batches_total,
            tiles_processed,
            tiles_total,
        ):
            _update_detection_run(
                session_id,
                run_token=run_token,
                phase='running_model',
                title='Running model detection',
                detail=_format_model_detail(
                    batches_completed,
                    batches_total,
                    tiles_processed,
                    tiles_total,
                ),
                counts={
                    'imagery_tiles_total': len(tiles),
                    'imagery_tiles_downloaded': len(tiles),
                    'model_batches_completed': batches_completed,
                    'model_batches_total': batches_total,
                    'model_tiles_processed': tiles_processed,
                    'model_tiles_total': tiles_total,
                },
            )

        update_model_progress(0, model_batches_total, 0, len(tiles))

        perf_metrics.start_phase('model_detection')
        model_start_time = time.time()
        results_raw = det.detect(
            tiles,
            exit_events,
            run_token,
            crop_tiles=crop_tiles,
            secondary=get_secondary_classifier(),
            perf_metrics=perf_metrics,
            progress_callback=update_model_progress,
        )
        perf_metrics.actual_model_time_seconds = time.time() - model_start_time
        perf_metrics.end_phase('model_detection')
        perf_metrics.update_memory_usage()

        if exit_events.query(run_token):
            return cancelled_response('Detection was cancelled during model inference.')

        for tile in tiles:
            if meta:
                filename = os.path.join(tmpdirname, tmpfilename + str(tile['id']) + ".meta.txt")
                with open(filename) as file_handle:
                    tile['metadata'] = map_provider.get_date(file_handle.read())
            else:
                tile['metadata'] = ""

        session['detections'] = make_persistable_tile_results(tiles)

        results = []
        raw_detection_count = 0
        api_logger.info(
            "Starting detection post-processing for %s tile result(s)",
            len(results_raw),
        )
        for result, tile in zip(results_raw, tiles):
            tile_detection_count = len(result)
            raw_detection_count += tile_detection_count

            if tile_detection_count > 0:
                api_logger.debug(
                    "Tile %s produced %s detection(s)",
                    tile.get('id', '?'),
                    tile_detection_count,
                )

            for i, obj in enumerate(result):
                obj['x1'] = tile['lng'] - 0.5 * tile['w'] + obj['x1'] * tile['w']
                obj['x2'] = tile['lng'] - 0.5 * tile['w'] + obj['x2'] * tile['w']
                obj['y1'] = tile['lat'] + 0.5 * tile['h'] - obj['y1'] * tile['h']
                obj['y2'] = tile['lat'] + 0.5 * tile['h'] - obj['y2'] * tile['h']
                obj['tile'] = tile['id']
                obj['id_in_tile'] = i
                obj['selected'] = obj.get('secondary', 0.0) >= 0.35

            results += result

        api_logger.info(
            "Detection complete: %s detection(s) across %s tile(s)",
            len(results),
            len(results_raw),
        )
        perf_metrics.detection_count = len(results)
        if results:
            total_confidence = sum(result.get('conf', 0) for result in results)
            perf_metrics.avg_confidence = total_confidence / len(results)

        _update_detection_run(
            session_id,
            run_token=run_token,
            phase='filtering_results',
            title='Filtering detections',
            detail=_format_filtering_detail(raw_detection_count),
            counts={'raw_detections': raw_detection_count},
        )

        inside_count = 0
        outside_count = 0
        for result in results:
            result['inside'] = ts_imgutil.resultIntersectsPolygons(
                result['x1'],
                result['y1'],
                result['x2'],
                result['y2'],
                polygons
            ) and ts_maps.check_bounds(result['x1'], result['y1'], result['x2'], result['y2'], bounds)
            if result['inside']:
                inside_count += 1
            else:
                outside_count += 1

        api_logger.info(
            "Boundary filtering complete: inside=%s outside=%s",
            inside_count,
            outside_count,
        )
        results = _dedupe_detection_results(results)
        retained_detection_count = len(results)
        _update_detection_run(
            session_id,
            run_token=run_token,
            phase='filtering_results',
            title='Filtering detections',
            detail=_format_filtering_detail(
                raw_detection_count,
                inside_count=inside_count,
                outside_count=outside_count,
                retained_count=retained_detection_count,
            ),
            counts={
                'raw_detections': raw_detection_count,
                'inside_detections': inside_count,
                'outside_detections': outside_count,
                'retained_detections': retained_detection_count,
                'duplicate_detections_removed': max(0, raw_detection_count - retained_detection_count),
            },
        )

        geocoding_total = sum(1 for detection in results if detection.get('class') == 0)

        def update_geocoding_progress(processed_count, total_count):
            _update_detection_run(
                session_id,
                run_token=run_token,
                phase='geocoding',
                title='Reverse geocoding detections',
                detail=_format_geocoding_detail(processed_count, total_count),
                counts={
                    'geocoding_processed': processed_count,
                    'geocoding_total': total_count,
                },
            )

        try:
            update_geocoding_progress(0, geocoding_total)
            _attach_detection_addresses(
                results,
                provider,
                perf_metrics=perf_metrics,
                progress_callback=update_geocoding_progress,
            )
        except Exception as error:
            api_logger.warning("Address lookup initialization failed: %s", error)
            for detection in results:
                if detection.get('class') == 0:
                    center_lat, center_lng = _detection_center(detection)
                    detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                    detection['address_confidence'] = 0.0
                    detection['address_provider'] = "error"
                else:
                    detection['address'] = ""
                    detection['address_confidence'] = 0.0
                    detection['address_provider'] = "none"
            update_geocoding_progress(geocoding_total, geocoding_total)

        tile_results = []
        for tile in tiles:
            tile_results.append({
                'x1': tile['lng'] - 0.5 * tile['w'],
                'y1': tile['lat'] + 0.5 * tile['h'],
                'x2': tile['lng'] + 0.5 * tile['w'],
                'y2': tile['lat'] - 0.5 * tile['h'],
                'class': 1,
                'class_name': 'tile',
                'conf': 1,
                'metadata': tile['metadata'],
                'url': tile['url'],
                'id': tile.get('id', -1),
                'selected': True
            })

        selected_count = sum(1 for entry in results if entry.get('selected'))
        _update_detection_run(
            session_id,
            run_token=run_token,
            phase='finalizing',
            title='Finalizing results',
            detail=_format_finalizing_detail(len(results), len(tile_results)),
            counts={
                'retained_detections': len(results),
                'selected_detections': selected_count,
                'tile_records': len(tile_results),
            },
        )
        api_logger.info(
            "Detection request complete: %s detection(s), %s selected, elapsed %.2f seconds",
            len(results),
            selected_count,
            time.time() - start,
        )

        perf_metrics.detections_selected = selected_count
        perf_metrics.finalize()

        from ts_performance import get_performance_logger
        get_performance_logger().log_metrics(perf_metrics)

        results_json = json.dumps(tile_results + results)
        session['results'] = results_json
        _finish_detection_run(
            session_id,
            'completed',
            run_token=run_token,
            phase='complete',
            title='Detection complete',
            detail=(
                f"Returned {len(results)} detection(s) across "
                f"{len(tiles)} processed tile(s)."
            ),
            cancel_requested=False,
            counts={
                'retained_detections': len(results),
                'selected_detections': selected_count,
                'tile_records': len(tile_results),
            },
            tile_count=len(tiles),
        )
        run_succeeded = True
        return Response(results_json, mimetype='application/json')
    except ValidationError as error:
        api_logger.error("Validation error: %s", error.message)
        if run_registered:
            _finish_detection_run(
                session_id,
                'error',
                run_token=run_token,
                phase='error',
                title='Detection failed',
                detail=f'Validation error: {error.message}',
                cancel_requested=False,
            )
        return jsonify({'error': f'Validation error: {error.message}'}), 400
    except Exception as error:
        api_logger.error("Detection pipeline failed: %s", error, exc_info=True)
        if run_registered:
            _finish_detection_run(
                session_id,
                'error',
                run_token=run_token,
                phase='error',
                title='Detection failed',
                detail=f'Detection pipeline error: {str(error)}',
                cancel_requested=False,
            )
        return jsonify({'error': f'Detection pipeline error: {str(error)}'}), 500
    finally:
        if request_loop is not None:
            try:
                request_loop.close()
            except Exception as loop_error:
                api_logger.warning("Failed to close request event loop: %s", loop_error)
        if exit_event_allocated:
            exit_events.free(run_token)
        if not run_succeeded and session.get('tmpdirname') == tmpdirname:
            _cleanup_session_tmpdir()


# EfficientNet secondary classifier
if not LAZY_MODEL_INIT:
    secondary_en = EN_Classifier()
else:
    ml_logger.info("Secondary classifier lazy initialization enabled")


# variable for zipcode provider
zipcode_lock = threading.Lock()
zipcode_provider = None


def start_zipcodes():
    global zipcode_provider
    with zipcode_lock:
        logger.info("Loading zipcode data, this may take up to 10 seconds...")
        zipcode_provider = Zipcode_Provider()


# Flask boilerplate stuff
app = Flask(__name__)


def _get_max_request_body_size() -> int:
    configured_value = os.getenv('TOWERSCOUT_MAX_REQUEST_BODY_BYTES', '').strip()
    if not configured_value:
        return TowerScoutValidator.MAX_FILE_SIZE

    try:
        max_bytes = int(configured_value)
    except ValueError:
        logger.warning(
            "Invalid TOWERSCOUT_MAX_REQUEST_BODY_BYTES=%s; using default %s",
            configured_value,
            TowerScoutValidator.MAX_FILE_SIZE,
        )
        return TowerScoutValidator.MAX_FILE_SIZE

    if max_bytes <= 0:
        logger.warning(
            "TOWERSCOUT_MAX_REQUEST_BODY_BYTES must be positive; using default %s",
            TowerScoutValidator.MAX_FILE_SIZE,
        )
        return TowerScoutValidator.MAX_FILE_SIZE

    return max_bytes


MAX_REQUEST_BODY_SIZE = _get_max_request_body_size()
TowerScoutValidator.MAX_FILE_SIZE = MAX_REQUEST_BODY_SIZE
MODEL_UPLOAD_ENABLED = os.getenv('TOWERSCOUT_ENABLE_MODEL_UPLOAD', '').strip().lower() in {'1', 'true', 'yes', 'on'}

# Configure Flask from environment variables
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
if not app.config['SECRET_KEY']:
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    logger.warning("FLASK_SECRET_KEY not configured. Using a temporary in-memory secret for setup-required mode.")

app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = MAX_REQUEST_BODY_SIZE
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
app.config['SETUP_REQUIRED'] = needs_setup

# Configure server-side session
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
SESSION_FILE_DIR = str(get_flask_session_dir())
app.config.from_object(__name__)
Session(app)

# Flask Error Handlers
@app.errorhandler(TowerScoutError)
def handle_towerscout_error(error):
    """Handle all TowerScout custom exceptions with structured responses."""
    api_logger.error(f"TowerScout error: {error.message}", exc_info=True)
    response = jsonify(error.to_dict())
    if isinstance(error, ValidationError):
        response.status_code = 400
    elif isinstance(error, NetworkError):
        response.status_code = 502
    elif isinstance(error, ConfigurationError):
        response.status_code = 400
    else:
        response.status_code = 500
    return response

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle validation errors with 400 status code."""
    api_logger.warning(f"Validation error: {error.message}")
    if hasattr(error, 'to_dict'):
        response = jsonify(error.to_dict())
    else:
        # Handle legacy ValidationError format
        response = jsonify({
            "error": True,
            "type": "ValidationError",
            "message": str(error),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
    response.status_code = 400
    return response

@app.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors with structured response."""
    api_logger.error(f"Internal server error: {error}", exc_info=True)
    response = jsonify({
        "error": True,
        "type": "InternalServerError",
        "message": "An internal error occurred. Please try again or contact support.",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    response.status_code = 500
    return response

@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors with structured response."""
    api_logger.warning(f"404 error: {request.url}")
    response = jsonify({
        "error": True,
        "type": "NotFoundError", 
        "message": "The requested resource was not found.",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    response.status_code = 404
    return response

@app.before_request
def log_request_info():
    """Log incoming request information."""
    api_logger.debug(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log outgoing response information."""
    api_logger.debug(f"Response: {response.status_code} for {request.url}")
    return response

# route for js code


@app.route('/site/')
def send_site_index():
    return send_site('index.html')


@app.route('/site/<path:path>')
def send_site(path):
    # print("site page requested:",path)
    return send_from_directory(str(SITE_DIR), path)

# route for images


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(str(JS_DIR), path)

# route for images
@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory(str(IMG_DIR), path)

# route for custom images
@app.route('/uploads/<path:path>')
def send_upload(path):
    return send_from_directory(str(UPLOAD_DIR), path)

# route for custom images
@app.route('/rm/uploads/<path:path>')
def remove_upload(path):
    os.remove(UPLOAD_DIR / path)
    logger.debug("Upload file deleted")
    return "ok"

# route for js code
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(str(CSS_DIR), path)

# main page route


@app.route('/')
def map_func():

    #for h in request.headers:
    #    print(h)

    #if request.headers.getlist("X-Real-Ip"):
    #    ip = request.headers.getlist("X-Real-Ip")[0]
    #else:
    #    ip = request.remote_addr

    #print("from:", ip)
    #allowed = {"47.215.225.26", "67.188.108.149", "24.126.148.202" } #, "127.0.0.1"}
    # access checks

    #if ip in allowed:
    #    pass
    #elif request.args.get("pw") == "CDC":
    #    pass
    #else:
    #    return send_from_directory('templates', "unauthorized.html")

    if dev == 1:
        session['tiles'] = 0

    session['needs_setup'] = needs_setup

    # init default engine
    # get_engine(None)

    # check for compatible browser
    offset = datetime.timezone(datetime.timedelta(hours=-5))  # Atlanta / CDC
    api_logger.info(f"Main page loaded at {datetime.datetime.now(offset)} EST")
    api_logger.debug(f"Browser: {request.user_agent.string}")
    # if not request.user_agent.browser in ['chrome','firefox']:
    #     return render_template('incompatible.html')

    # clean out any temp dirs
    if "tmpdirname" in session:
        rmtree(session['tmpdirname'], ignore_errors=True, onerror=None)
        del session['tmpdirname']

    # now render the map.html template, inserting the keys and available providers
    available_providers = []
    if google_api_key:
        available_providers.append('google')
    if bing_api_key:
        available_providers.append('bing')
    if azure_api_key:
        available_providers.append('azure')
    
    return render_template('towerscout.html',
                           available_providers=available_providers,
                           needs_setup=needs_setup,
                           model_upload_enabled=MODEL_UPLOAD_ENABLED,
                           dev=dev)


# cache control
# todo: ratchet this up after development


@app.after_request
def add_header(response):
    response.cache_control.max_age = 1
    return response

# retrieve available engine choices


@app.route('/getengines')
def get_engines():
    api_logger.debug("Engines API endpoint requested")
    sorted_engines = sorted(engines.items(),key=lambda x:-x[1]['ts'])
    result = json.dumps([{'id': k, 'name': v['name']} for (k, v) in sorted_engines ])
    return result

# retrieve available map providers

@app.route('/debug-azure-maps')
def debug_azure_maps():
    """Debug page for Azure Maps initialization issues"""
    api_logger.debug("Azure Maps debug page requested")
    return send_from_directory(str(script_dir), 'debug_azure_maps.html')

@app.route('/getazurekey')
def get_azure_key():
    """Provide Azure Maps subscription key for frontend authentication"""
    api_logger.info(f"Azure Maps key API endpoint requested - Key available: {bool(azure_api_key)}")
    
    if not azure_api_key:
        api_logger.error("Azure Maps API key not available for frontend")
        response = jsonify({
            "error": True,
            "message": "Azure Maps API key not configured"
        })
        response.status_code = 400
        return response
    
    # Log key info for debugging (first 15 chars only)
    key_preview = azure_api_key[:15] + "..." if len(azure_api_key) > 15 else azure_api_key
    api_logger.info(f"Returning Azure subscription key to frontend (starts with: {key_preview})")
    
    return jsonify({
        "subscriptionKey": azure_api_key
    })

@app.route('/getgooglekey')
def get_google_key():
    """Provide Google Maps API key for frontend authentication"""
    api_logger.info(f"Google Maps key API endpoint requested - Key available: {bool(google_api_key)}")
    
    if not google_api_key:
        api_logger.error("Google Maps API key not available for frontend")
        response = jsonify({
            "error": True,
            "message": "Google Maps API key not configured"
        })
        response.status_code = 400
        return response
    
    # Log key info for debugging (first 15 chars only)
    key_preview = google_api_key[:15] + "..." if len(google_api_key) > 15 else google_api_key
    api_logger.info(f"Returning Google API key to frontend (starts with: {key_preview})")
    
    return jsonify({
        "apiKey": google_api_key
    })

@app.route('/getproviders')
def get_providers():
    api_logger.debug("Map providers API endpoint requested")
    
    # Return providers with Azure first (default provider from .env)
    available_providers = []
    
    # Check .env DEFAULT_MAP_PROVIDER setting and prioritize it
    default_provider = os.getenv('DEFAULT_MAP_PROVIDER', 'azure').lower()
    
    if default_provider == 'azure' and azure_api_key:
        available_providers.append({'id': 'azure', 'name': 'Azure Maps'})
        if google_api_key:
            available_providers.append({'id': 'google', 'name': 'Google Maps'})
    elif default_provider == 'google' and google_api_key:
        available_providers.append({'id': 'google', 'name': 'Google Maps'})
        if azure_api_key:
            available_providers.append({'id': 'azure', 'name': 'Azure Maps'})
    else:
        # Fallback order: Azure first, then Google
        if azure_api_key:
            available_providers.append({'id': 'azure', 'name': 'Azure Maps'})
        if google_api_key:
            available_providers.append({'id': 'google', 'name': 'Google Maps'})
    
    result = json.dumps(available_providers)
    return result


def _get_client_ip():
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))


def _mask_key_preview(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}{'*' * max(len(key) - 8, 4)}{key[-4:]}"


@app.route('/api/config/validate-key', methods=['POST'])
def validate_api_key_endpoint():
    """Validate a Google or Azure API key with a minimal provider request."""
    client_ip = _get_client_ip()
    if not rate_limiter.is_allowed(f"config-validate:{client_ip}", max_requests=10, window_seconds=300):
        return jsonify({'error': 'Rate limit exceeded. Please wait before trying again.'}), 429

    data = request.get_json(silent=True) or {}
    provider = TowerScoutValidator.validate_provider(data.get('provider'))
    key = TowerScoutValidator.sanitize_string(data.get('key', ''), max_length=512)

    result = ts_config.validate_api_key(provider, key)
    return jsonify(result)


@app.route('/api/config/save-keys', methods=['POST'])
def save_api_keys():
    """Validate and persist API key configuration without restarting the app."""
    client_ip = _get_client_ip()
    if not rate_limiter.is_allowed(f"config-save:{client_ip}", max_requests=5, window_seconds=300):
        return jsonify({'error': 'Rate limit exceeded. Please wait before trying again.'}), 429

    data = request.get_json(silent=True) or {}
    google_input = TowerScoutValidator.sanitize_string(str(data.get('google_api_key', '')).strip(), max_length=512)
    azure_input = TowerScoutValidator.sanitize_string(str(data.get('azure_maps_subscription_key', '')).strip(), max_length=512)
    default_provider_input = str(data.get('default_map_provider') or os.getenv('DEFAULT_MAP_PROVIDER', 'azure')).strip().lower()
    default_provider = TowerScoutValidator.validate_provider(default_provider_input)

    merged_google = google_input or os.getenv('GOOGLE_API_KEY', '')
    merged_azure = azure_input or os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')

    validation_results = {}
    if merged_google and not ts_config.is_placeholder(merged_google):
        validation_results['google'] = ts_config.validate_api_key('google', merged_google)
        if not validation_results['google']['valid']:
            return jsonify(validation_results['google']), 400

    if merged_azure and not ts_config.is_placeholder(merged_azure):
        validation_results['azure'] = ts_config.validate_api_key('azure', merged_azure)
        if not validation_results['azure']['valid']:
            return jsonify(validation_results['azure']), 400

    if not validation_results:
        return jsonify({
            'success': False,
            'message': 'At least one valid API key is required to save configuration.'
        }), 400

    updates = {
        'GOOGLE_API_KEY': merged_google,
        'AZURE_MAPS_SUBSCRIPTION_KEY': merged_azure,
        'DEFAULT_MAP_PROVIDER': default_provider,
    }

    ts_config.update_env_file(updates)
    refresh_runtime_config()
    session['needs_setup'] = needs_setup

    return jsonify({
        'success': True,
        'message': 'Configuration updated successfully.',
        'needs_setup': needs_setup,
        'default_map_provider': os.getenv('DEFAULT_MAP_PROVIDER', 'azure'),
    })


@app.route('/api/config/status', methods=['GET'])
def get_config_status():
    """Return current configuration status for setup and settings flows."""
    status = ts_config.get_env_status()
    status['google']['preview'] = _mask_key_preview(os.getenv('GOOGLE_API_KEY', ''))
    status['azure']['preview'] = _mask_key_preview(os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', ''))
    status['needs_setup'] = needs_setup
    return jsonify(status)


@app.route('/api/config/reset-session', methods=['POST'])
def reset_session():
    """Clear Flask session state and temporary files used by the current session."""
    tmpdirname = session.get('tmpdirname')
    if tmpdirname:
        rmtree(tmpdirname, ignore_errors=True, onerror=None)

    session.clear()
    session['needs_setup'] = needs_setup

    return jsonify({
        'success': True,
        'message': 'Session data and temporary files cleared.'
    })


@app.route('/api/config/performance', methods=['GET'])
def get_performance_stats():
    """Return recent performance summary derived from existing performance logs."""
    return jsonify(ts_config.get_recent_performance_stats())

# Forward geocoding API for address search
@app.route('/api/geocode/forward', methods=['POST'])
def forward_geocode():
    """Convert address to coordinates using available providers"""
    try:
        # Rate limiting check
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        if not rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=600):  # 10 minutes
            return jsonify({'error': 'Rate limit exceeded. Please wait before trying again.'}), 429
            
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
            
        query = TowerScoutValidator.validate_search_query(data['query'])
        preferred_provider = str(data.get('provider', 'auto')).strip().lower() or 'auto'
        if preferred_provider not in {'auto', 'azure', 'google'}:
            preferred_provider = 'auto'
        
        # Import geocoding service
        from ts_geocoding import GeocodingService
        
        # Initialize geocoding with available API keys
        geocoding = GeocodingService(
            azure_key=azure_api_key,
            google_key=google_api_key,
            preferred_provider=preferred_provider
        )
        
        # Perform forward geocoding with provider preference
        results = geocoding.forward_geocode_unified(query, preferred_provider)
        
        if not results:
            return jsonify({'error': 'No results found for query'}), 404
            
        # Return standardized geocoding results
        return jsonify({
            'success': True,
            'results': [result.to_dict() for result in results],
            'provider_used': results[0].provider if results else None
        })
        
    except ValidationError as e:
        api_logger.warning(f"Geocoding validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        api_logger.error(f"Geocoding error: {e}")
        return jsonify({'error': 'Internal geocoding error'}), 500

@app.route('/api/geocode/reverse', methods=['POST'])
def reverse_geocode():
    """Convert coordinates to address using available providers"""
    try:
        # Rate limiting check
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        if not rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=600):  # 10 minutes
            return jsonify({'error': 'Rate limit exceeded. Please wait before trying again.'}), 429
            
        data = request.get_json()
        if not data or 'lat' not in data or 'lng' not in data:
            return jsonify({'error': 'Missing lat/lng parameters'}), 400
            
        lat = float(data['lat'])
        lng = float(data['lng'])
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        preferred_provider = data.get('provider', 'auto')
        
        # Import geocoding service
        from ts_geocoding import GeocodingService, GeocodingError
        
        # Initialize geocoding with available API keys
        geocoding = GeocodingService(
            azure_key=azure_api_key,
            google_key=google_api_key
        )
        
        # Check cache first
        from ts_geocache import GeocodingCache
        cache = GeocodingCache()
        cached_result = cache.get(lat, lng, provider=preferred_provider)
        
        if cached_result:
            api_logger.info(f"Cache hit for reverse geocode: {lat}, {lng}")
            return jsonify({
                'success': True,
                'address': cached_result.address,
                'provider': cached_result.provider.value,
                'confidence': cached_result.confidence,
                'cached': True
            })
        
        # Perform reverse geocoding
        try:
            result = geocoding.reverse_geocode(lat, lng, preferred_provider)

            if result.success and result.address:
                cache.put(lat, lng, result, provider=preferred_provider)
                return jsonify({
                    'success': True,
                    'address': result.address,
                    'provider': result.provider.value,
                    'confidence': result.confidence,
                    'cached': False
                })

            return jsonify({
                'success': False,
                'address': f"{lat:.6f}, {lng:.6f}",
                'provider': result.provider.value,
                'confidence': result.confidence,
                'cached': False,
                'error': result.error_message or 'No address found'
            })
        except GeocodingError as e:
            api_logger.warning(f"Geocoding failed for {lat}, {lng}: {e}")
            # Return coordinates as fallback
            return jsonify({
                'success': False,
                'address': f"{lat:.6f}, {lng:.6f}",
                'provider': 'fallback',
                'confidence': 0.0,
                'error': str(e)
            })
        
    except ValueError as e:
        api_logger.warning(f"Invalid coordinate values: {e}")
        return jsonify({'error': 'Invalid coordinate format'}), 400
    except Exception as e:
        api_logger.error(f"Reverse geocoding error: {e}")
        return jsonify({'error': 'Internal geocoding error'}), 500

# Unified map proxy endpoints
@app.route('/api/maps/<provider>/<service>', methods=['GET'])
def map_proxy(provider, service):
    """Unified proxy for all map services to hide API keys from client"""
    try:
        # Validate provider and service
        if provider not in MAP_PROXY_CONFIG:
            return jsonify({'error': f'Unknown provider: {provider}'}), 400
        if service not in MAP_PROXY_CONFIG[provider]:
            return jsonify({'error': f'Unknown service {service} for provider {provider}'}), 400
            
        config = MAP_PROXY_CONFIG[provider][service]
        
        # Rate limiting check with service-specific limits
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
        max_requests, window_seconds = config['rate_limit']
        if not rate_limiter.is_allowed(client_ip, max_requests=max_requests, window_seconds=window_seconds):
            return jsonify({'error': f'Rate limit exceeded for {provider}/{service}. Please wait before trying again.'}), 429
            
        # Validate and sanitize request parameters
        params = {}
        for key, value in request.args.items():
            if key in ['z', 'x', 'y', 'zoom', 'width', 'height', 'format', 'limit']:  # Numeric params
                try:
                    params[key] = int(value) if key in ['z', 'x', 'y', 'zoom', 'width', 'height', 'limit'] else value
                except ValueError:
                    return jsonify({'error': f'Invalid numeric parameter: {key}'}), 400
            elif key in ['center', 'size', 'maptype', 'style', 'query', 'api-version', 'tilesetId', 'countrySet', 'lat', 'lon']:  # String params
                if len(value) > 1000:  # Prevent excessively long parameters
                    return jsonify({'error': f'Parameter {key} too long'}), 400
                params[key] = str(value)
            else:
                return jsonify({'error': f'Unauthorized parameter: {key}'}), 400
                
        # Generate cache key
        cache_key = f"{provider}_{service}_{hash(str(sorted(params.items())))}"
        cache_file = os.path.join(MAP_CACHE_DIR, f"{cache_key}.cache")
        
        # Check cache
        if os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < config['cache_ttl']:
                maps_logger.debug(f"Cache hit for {provider}/{service}")
                with open(cache_file, 'rb') as f:
                    cached_data = f.read()
                return Response(cached_data, headers={'Content-Type': _get_content_type(service)})
                
        # Route to appropriate provider handler
        if provider == 'google':
            response_data = _handle_google_proxy(service, params)
        elif provider == 'azure':
            response_data = _handle_azure_proxy(service, params)
        else:
            return jsonify({'error': f'Provider {provider} not implemented'}), 500
            
        # Cache successful responses
        if response_data:
            try:
                with open(cache_file, 'wb') as f:
                    f.write(response_data)
                maps_logger.debug(f"Cached response for {provider}/{service}")
            except Exception as cache_error:
                maps_logger.warning(f"Failed to cache response: {cache_error}")
                
        return Response(response_data, headers={'Content-Type': _get_content_type(service)})
        
    except ValidationError as e:
        api_logger.warning(f"Map proxy validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        api_logger.error(f"Map proxy error for {provider}/{service}: {e}")
        return jsonify({'error': f'Internal map proxy error for {provider}/{service}'}), 500


def _get_content_type(service):
    """Get appropriate content type for service response"""
    if service in ['tiles', 'static']:
        return 'image/png'
    elif service == 'search':
        return 'application/json'
    else:
        return 'application/octet-stream'


def _handle_google_proxy(service, params):
    """Handle Google Maps API proxying"""
    import requests
    
    if not google_api_key:
        raise Exception("Google API key not configured")
        
    # Log proxy request
    maps_logger.info(f"Google Maps proxy request: service={service}, params={len(params)} parameters")
        
    if service == 'tiles':
        # Google Maps tile service
        url = f"https://maps.googleapis.com/maps/api/staticmap"
        params['key'] = google_api_key
        maps_logger.debug(f"Google tiles request: {url} with {len(params)} params")
    elif service == 'static':
        # Google static maps
        url = f"https://maps.googleapis.com/maps/api/staticmap"
        params['key'] = google_api_key
        maps_logger.debug(f"Google static request: {url} with {len(params)} params")
    else:
        raise Exception(f"Unknown Google service: {service}")
        
    try:
        response = requests.get(url, params=params, timeout=30)
        maps_logger.info(f"Google API response: status={response.status_code}, size={len(response.content)} bytes")
        
        if response.status_code != 200:
            maps_logger.error(f"Google API error: {response.status_code} - {response.text[:200]}...")
            raise Exception(f"Google API returned status {response.status_code}: {response.text}")
        
        return response.content
    except requests.RequestException as e:
        maps_logger.error(f"Google API network error: {e}")
        raise Exception(f"Google API network error: {e}")


def _handle_azure_proxy(service, params):
    """Handle Azure Maps API proxying with secure authentication and comprehensive error handling"""
    import requests
    
    if not azure_api_key:
        raise Exception("Azure Maps API key not configured")
        
    # Log proxy request
    maps_logger.info(f"Azure Maps proxy request: service={service}, params={len(params)} parameters")
        
    if service == 'search':
        # Azure Maps Search API - Use address search for better geocoding results
        url = f"https://atlas.microsoft.com/search/address/json"
        
        # Build Azure Maps Search API parameters
        search_params = {
            'subscription-key': azure_api_key,
            'api-version': '1.0',
            'query': params.get('query', ''),
            'limit': min(int(params.get('limit', 5)), 20),  # Cap at 20 results for performance
            'countrySet': params.get('countrySet', 'US')  # Default to US
        }
        
        # Add optional geospatial bias if provided
        if 'lat' in params and 'lon' in params:
            try:
                lat = float(params['lat'])
                lon = float(params['lon']) 
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    search_params['lat'] = lat
                    search_params['lon'] = lon
                else:
                    maps_logger.warning(f"Invalid coordinates provided: lat={lat}, lon={lon}")
            except (ValueError, TypeError):
                maps_logger.warning(f"Invalid coordinate format: lat={params.get('lat')}, lon={params.get('lon')}")
        
        maps_logger.debug(f"Azure search request: {url} with query='{search_params['query']}', limit={search_params['limit']}")
        
    elif service == 'tiles':
        # Azure Maps Raster Tile Service for satellite imagery
        url = f"https://atlas.microsoft.com/map/tile"
        
        # Build Azure Maps tile parameters
        search_params = {
            'subscription-key': azure_api_key,
            'api-version': '2.0',
            'tilesetId': params.get('tilesetId', 'microsoft.imagery'),  # Satellite imagery
            'zoom': max(1, min(int(params.get('zoom', 19)), 22)),  # Clamp zoom level
            'x': int(params.get('x', 0)),
            'y': int(params.get('y', 0))
        }
        
        maps_logger.debug(f"Azure tiles request: {url} for tile z={search_params['zoom']}, x={search_params['x']}, y={search_params['y']}")
        
    else:
        raise Exception(f"Unknown Azure service: {service}")
        
    try:
        # Make API request with timeout and proper error handling
        response = requests.get(url, params=search_params, timeout=30)
        maps_logger.info(f"Azure API response: status={response.status_code}, size={len(response.content)} bytes")
        
        # Handle specific Azure API error codes
        if response.status_code == 401:
            maps_logger.error("Azure API authentication failed - check subscription key validity")
            raise Exception("Azure Maps authentication failed: Invalid or expired subscription key")
        elif response.status_code == 403:
            maps_logger.error("Azure API forbidden - check subscription key permissions")
            raise Exception("Azure Maps access denied: Subscription key lacks required permissions for this service")
        elif response.status_code == 429:
            maps_logger.error("Azure API rate limit exceeded")
            raise Exception("Azure Maps rate limit exceeded: Please wait before making more requests")
        elif response.status_code == 404 and service == 'tiles':
            maps_logger.warning(f"Azure tile not found: zoom={search_params.get('zoom')}, x={search_params.get('x')}, y={search_params.get('y')}")
            raise Exception("Requested map tile not available at this zoom level or location")
        elif response.status_code != 200:
            error_text = response.text[:200] if response.text else "Unknown error"
            maps_logger.error(f"Azure API error {response.status_code}: {error_text}...")
            raise Exception(f"Azure API returned status {response.status_code}: {error_text}")
        
        # Validate response content
        if len(response.content) == 0:
            maps_logger.warning(f"Azure API returned empty response for {service}")
            raise Exception("Azure API returned empty response")
            
        return response.content
        
    except requests.Timeout:
        maps_logger.error("Azure API request timeout")
        raise Exception("Azure Maps request timeout: Service temporarily unavailable")
    except requests.ConnectionError as e:
        maps_logger.error(f"Azure API connection error: {e}")
        raise Exception("Azure Maps connection failed: Please check internet connectivity")
    except requests.RequestException as e:
        maps_logger.error(f"Azure API network error: {e}")
        raise Exception(f"Azure Maps network error: {e}")

# zipcode boundary lookup


@app.route('/getzipcode')
def get_zipcode():
    global zipcode_provider
    
    # Input validation
    try:
        validated_data = validate_zipcode_request(request.args.to_dict())
        zipcode = validated_data['zipcode']
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception:
        return jsonify({'error': 'Invalid zipcode format'}), 400
        
    api_logger.debug(f"Zipcode requested: {zipcode}")
    with zipcode_lock:
        if zipcode_provider is None:
            logger.info("Loading zipcode data, this may take up to 10 seconds...")
            zipcode_provider = Zipcode_Provider()
        api_logger.debug("Looking up zipcode...")
        return zipcode_provider.zipcode_polygon(zipcode)


@app.route('/api/detection/estimate', methods=['POST'])
def estimate_detection_tiles():
    session_id = _get_session_run_id()
    api_logger.debug("Estimating tiles for session %s", session_id)

    if 'tiles' not in session:
        session['tiles'] = 0

    if session['tiles'] > MAX_TILES_SESSION:
        return jsonify({
            'tileCount': -1,
            'estimatedSeconds': 0.0
        })

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    if not rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=60):
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    try:
        api_logger.debug("Validating estimate request with form keys=%s", list(request.form.keys()))
        request_context = _parse_detection_request(request.form)
        bounds = request_context['bounds']
        engine = request_context['engine']
        provider = request_context['provider']
        polygons = request_context['polygons']
        crop_tiles = True

        api_logger.info(
            "Incoming estimate request session=%s provider=%s engine=%s polygon_count=%s bounds=%s",
            session_id,
            provider,
            engine,
            len(polygons),
            bounds,
        )

        perf_metrics = PerformanceMetrics(str(session_id))
        perf_metrics.detection_engine = engine
        perf_metrics.map_provider = provider
        perf_metrics.crop_tiles = crop_tiles

        map_provider = _create_map_provider(provider)
        tiles, _nx, _ny, _meters, _h, _w, _tile_stats = _build_tiles_for_request(
            map_provider,
            bounds,
            polygons,
            crop_tiles
        )

        perf_metrics.tile_count = len(tiles)
        perf_metrics.estimate_processing_time(len(tiles))
        session['last_detection_provider'] = provider

        api_logger.info(
            "Estimate complete for session %s: %s tile(s), ~%.1f seconds",
            session_id,
            len(tiles),
            perf_metrics.estimated_time_seconds,
        )
        return jsonify({
            'tileCount': len(tiles),
            'estimatedSeconds': round(perf_metrics.estimated_time_seconds, 2)
        })
    except ValidationError as e:
        api_logger.error("Validation error: %s", e.message)
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception as e:
        api_logger.error("Tile estimate failed: %s", e, exc_info=True)
        return jsonify({'error': f'Tile estimate error: {str(e)}'}), 500


@app.route('/api/detection/progress', methods=['GET'])
def get_detection_progress():
    session_id = _get_session_run_id()
    progress_state = _serialize_detection_progress_state(
        _get_detection_progress_state(session_id)
    )
    response = jsonify(progress_state)
    response.headers['Cache-Control'] = 'no-store'
    return response

# abort route

@app.route('/abort', methods=['GET', 'POST'])
def abort():
    session_id = _get_session_run_id()
    api_logger.info(f"Aborting session {session_id}")
    run_state = _mark_detection_run_cancel_requested(session_id)
    if run_state is not None and run_state.get('run_token'):
        exit_events.signal(run_state['run_token'])
    return "ok"

# detection route

@app.route('/getobjects', methods=['POST'])
def get_objects():
    return _run_detection_request()



def cleanup_temp_directory():
    # Cleanup the tempdir at the end of the session or application
    if "tmpdir_obj" in session:
        tmpdir = session['tmpdir_obj']
        api_logger.info("Cleaning up tmp dir %s", tmpdir.name)
        tmpdir.cleanup()
        del session['tmpdir_obj']
        del session['tmpdirname']


def allowed_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# detection route for provided images
@app.route('/api-usage', methods=['GET'])
def get_api_usage():
    """Return current session's API usage statistics for frontend display."""
    try:
        usage_data = {
            'geocoding_usage': session.get('geocoding_usage', {
                'google_requests': 0,
                'azure_requests': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0
            }),
            'geocoding_limited': session.get('geocoding_limited', False)
        }
        return jsonify(usage_data)
    except Exception as e:
        logger = get_api_logger()
        logger.error(f"Failed to get API usage: {e}")
        return jsonify({'error': 'Failed to retrieve API usage'}), 500


@app.route('/getobjectscustom', methods=['POST'])
def get_objects_custom():
    start = time.time()
    session_id = _get_session_run_id()
    
    # Rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    if not rate_limiter.is_allowed(client_ip, max_requests=10, window_seconds=60):
        return jsonify({'error': 'Rate limit exceeded for image uploads'}), 429
    
    # Input validation
    try:
        engine = TowerScoutValidator.validate_engine(request.form.get('engine'))
        
        if 'image' not in request.files:
            raise ValidationError("No image file provided")
            
        file = TowerScoutValidator.validate_image_file(request.files['image'])
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception:
        return jsonify({'error': 'Invalid request data'}), 400

    api_logger.info(
        "Incoming custom image detection request session=%s engine=%s file=%s",
        session_id,
        engine,
        file.filename,
    )

    # get the proper detector
    det = get_engine(engine)

    # empty results
    results = []

    # filename = secure_filename(file.filename)
    filename = file.filename
    upload_path = UPLOAD_DIR / filename
    file.save(str(upload_path))
    api_logger.info("Uploaded custom image to %s", upload_path)
    results = det.detect([{'filename': str(upload_path)}], exit_events, session_id, crop_tiles=False)

    # draw result bounding boxes on image
    objects = 0
    with Image.open(upload_path) as im:
        for result in results:
            for object in result:
                drawResult(object, im)
                objects += 1
        im.save(upload_path, quality=95)
    api_logger.info("Finished drawing %s custom detection result(s)", objects)

    # all done
    api_logger.info(
        "Custom image detection complete: %s object(s), elapsed %.2f seconds",
        objects,
        time.time() - start,
    )

    results = json.dumps(results)
    session['results'] = results
    cleanup_temp_directory()
    return results


#
# pillow helper function to draw
#
def drawResult(r, im):
    api_logger.debug("Drawing custom detection result bounding box")
    draw = ImageDraw.Draw(im)
    draw.rectangle([
        im.size[0]*r['x1'],
        im.size[1]*r['y1'],
        im.size[0]*r['x2'],
        im.size[1]*r['y2']
    ],
        outline="red")


# upload a new model
@ app.route('/uploadmodel', methods=['POST'])
def upload_model():
    api_logger.info("Model upload requested")

    if not MODEL_UPLOAD_ENABLED:
        api_logger.warning("Model upload rejected because TOWERSCOUT_ENABLE_MODEL_UPLOAD is not enabled")
        return jsonify({
            'error': 'Model upload is disabled for this release. Install trusted model files through the configured model volume or enable the local-admin upload override.'
        }), 403
    
    # Rate limiting (stricter for model uploads)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    if not rate_limiter.is_allowed(client_ip, max_requests=5, window_seconds=300):
        return jsonify({'error': 'Rate limit exceeded for model uploads'}), 429
    
    # Input validation
    try:
        if 'model' not in request.files:
            raise ValidationError("No model file provided")
            
        file = TowerScoutValidator.validate_model_file(request.files['model'])
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception:
        return jsonify({'error': 'Invalid request data'}), 400

    if file.filename == '':
        api_logger.warning("Model upload request did not include a selected filename")
        return None

    if not file or not file.filename.endswith(".pt"):
        api_logger.warning(
            "Model upload request had invalid file or extension filename=%s",
            file.filename,
        )
        return None

    # filename = secure_filename(file.filename)
    filename = file.filename
    target_dir = EN_MODEL_DIR if filename.startswith("b5") else YOLO_MODEL_DIR
    file.save(str(target_dir / filename))
    api_logger.info("Uploaded model file to %s", target_dir / filename)

    add_model(filename)

    ml_logger.info("Installed uploaded model %s", file.filename)

    return "ok"


# download results as dataset for formal training /testing
@ app.route('/getdataset', methods=['POST'])
def send_dataset():
    api_logger.info("Dataset export requested")

    # Validate JSON fields
    try:
        include = TowerScoutValidator.validate_json_field(request.form.get("include"), "include")
        additions = TowerScoutValidator.validate_json_field(request.form.get("additions"), "additions")
        api_logger.debug(
            "Dataset export payload include_count=%s additions_count=%s addition_tile_ids=%s",
            len(include),
            len(additions),
            [a.get('tile') for a in additions],
        )
    except ValidationError as e:
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    tiles = session['detections']
    meta = session['metadata']

    # print(" raw inclusions:", request.form.get("include"))
    # print(" inclusions:", include)
    # print(" last result:", json.dumps(tiles))

    # filter to keep only "included" (i.e. selected and meeting threshold) detections
    keep_detections = set([])
    keep_detection_ids = set([])
    keep_detection_refs = set([])
    for inclusion in include:
        try:
            matched_tile = _find_tile_by_session_index(tiles, inclusion.get('tile'))
            if matched_tile is None:
                raise KeyError(f"tile {inclusion.get('tile')} not found in session")

            keep_detections.add(
                matched_tile['detections'][inclusion['detection']])

            detection_ref = _normalize_detection_ref(
                inclusion.get('tile'),
                inclusion.get('detection')
            )
            if detection_ref is not None:
                keep_detection_refs.add(detection_ref)
            # if the absolute tile id was also included,
            if 'id' in inclusion:
                keep_detection_ids.add(inclusion['id'])
        except:
            api_logger.warning("Skipping invalid dataset inclusion %s", inclusion)
    api_logger.info("Writing dataset labels for export")

    # write files and records which ones had detections
    filenames = []
    api_logger.debug(
        "Preparing dataset labels tile_count=%s manual_additions=%s",
        len(tiles),
        len(additions),
    )
    
    for i, tile in enumerate(tiles):
        # Use tile's actual ID (stored as 'index') for matching with additions
        tile_id = tile.get('index', i)  # Fallback to enumeration index if 'index' not present
        api_logger.debug(
            "Writing labels for session_tile=%s session_index=%s resolved_tile_id=%s",
            i,
            tile.get('index', 'MISSING'),
            tile_id,
        )
        filenames += write_labels(tile_id, tile,
                                  keep_detections, additions, not meta)

    # write a contents file so we can load this again some time
    write_contents_file(
        session["tmpdirname"],
        tiles,
        keep_detection_refs,
        keep_detection_ids,
        additions,
        meta
    )

    api_logger.info("Zipping dataset export archive")
    zipdir(session['tmpdirname'], filenames)
    api_logger.info("Dataset export archive ready")
    return send_from_directory(str(get_temp_dir()), "dataset.zip")


# adapted from
# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python

def zipdir(path, filenames):
    # TASK-033 Phase 3: Ensure temp directory exists and use proper paths
    temp_dir = get_temp_dir()
    zip_path = temp_dir / 'dataset.zip'
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    
    # TASK-036: Add README.txt to dataset export
    readme_path = os.path.join(os.path.dirname(__file__), 'DATASET_README.txt')
    if os.path.exists(readme_path):
        zipf.write(readme_path, 'README.txt')
        api_logger.info("Added README.txt to dataset export archive")
    else:
        api_logger.warning("DATASET_README.txt not found; skipping README in dataset export")
    
    for root, dirs, files in os.walk(path):
        for file in files:
            api_logger.debug("Compressing dataset export file %s", file)
            # select the right folder
            if file.endswith("contents.txt"):
                folder = "."
            elif file.endswith(".meta.txt"):
                continue
            elif file.endswith(".zip"):
                continue
            elif os.path.join(root, file) in filenames:
                if file.endswith(".jpg"):
                    folder = "train/images"
                elif file.endswith(".xml"):
                    folder = "train/labels-xml"
                else:
                    folder = "train/labels"
            else:
                folder = "empty"
            zipf.write(os.path.join(root, file), os.path.relpath(
                os.path.join(root, folder, file), os.path.join(path, '..')))
    zipf.close()


def _normalize_detection_ref(tile_id, detection_id):
    """Build a stable lookup key for ML detections across export and restore."""
    try:
        return (int(tile_id), int(detection_id))
    except (TypeError, ValueError):
        return None


def _find_tile_by_session_index(tiles, tile_id):
    """Resolve a persisted tile identifier back to the current session tile record."""
    tile_ref = _normalize_detection_ref(tile_id, 0)
    if tile_ref is None:
        return None

    normalized_tile_id = tile_ref[0]
    for fallback_index, tile in enumerate(tiles):
        if int(tile.get('index', fallback_index)) == normalized_tile_id:
            return tile

    return None


# get a portion of the tiles in serializable form to attach to the session
def make_persistable_tile_results(tiles):
    return [{
        'filename': tile['filename'],
        'labelfilename': tile['filename'][0:-4]+".txt",
        'detections':tile['detections'],
        'metadata':tile['metadata'],
        'url':tile['url'],
        'index':tile['id'],
    } for tile in tiles]


# write out the detections as label files (to download the dataset)
# returns the names of img and label if detections were present, otherwise empty list
def write_labels(tile_id, tile, keep, additions, double_res):
    empty = True
    # print(" attempting to write file ", tile['labelfilename'], "...")

    with open(tile['labelfilename'], "w", encoding="utf-8") as f:
        api_logger.debug("Writing dataset label file %s", f.name)
        manual_towers_written = 0
        for detection in tile['detections']:
            if detection in keep:
                # print("", detection)
                f.write(detection)
                empty = False
        for a in additions:
            api_logger.debug(
                "Checking manual addition for tile_id=%s addition_tile=%s match=%s",
                tile_id,
                a.get('tile'),
                a.get('tile') == tile_id,
            )
            if a['tile'] == tile_id:
                f.write(" ".join(["0", str(a['centerx']), str(
                    a['centery']), str(a['w']), str(a['h'])])+"\n")
                empty = False
                manual_towers_written += 1
        if manual_towers_written > 0:
            api_logger.info(
                "Wrote %s manual tower(s) to tile_id=%s",
                manual_towers_written,
                tile_id,
            )

    # write xml labels for augmentation pipeline
    name = tile['labelfilename'][:-3]+"xml"
    size = 1280 if double_res else 640

    with open(name, "w", encoding="utf-8") as f:
        api_logger.debug("Writing dataset XML label file %s", f.name)
        xml = "<annotation>\n"
        xml += "<size>\n"
        xml += "  <width>"+str(size)+"</width>\n"
        xml += "  <height>"+str(size)+"</height>\n"
        xml += "  <depth>3</depth>\n"
        xml += "</size>\n"
        f.write(xml)
        for detection in tile['detections']:
            if detection in keep:
                # print("", detection)
                xml = xml_from_label(detection, size)
                f.write(xml)
                empty = False
        for a in additions:
            if a['tile'] == tile_id:
                label = " ".join(["0", str(a['centerx']), str(
                    a['centery']), str(a['w']), str(a['h'])])
                xml = xml_from_label(label, size)
                f.write(xml)
                empty = False
        xml = "</annotation>\n"
        f.write(xml)

    return [] if empty else [tile['filename'], tile['labelfilename'], tile['labelfilename'][:-3]+"xml"]


# convert YOLOv5-style object label to roboflow XML:
def xml_from_label(label, size):
    x = [float(x) for x in label.split(" ")]
    xmin = int((x[1]-0.5*x[3])*size)
    xmax = int((x[1]+0.5*x[3])*size)
    ymin = int((x[2]-0.5*x[4])*size)
    ymax = int((x[2]+0.5*x[4])*size)

   
    xml = "<object>\n"
    xml += "  <bndbox>\n"
    xml += "    <xmin>"+str(xmin)+"</xmin>\n"
    xml += "    <xmax>"+str(xmax)+"</xmax>\n"
    xml += "    <ymin>"+str(ymin)+"</ymin>\n"
    xml += "    <ymax>"+str(ymax)+"</ymax>\n"
    xml += "  </bndbox>\n"
    xml += "</object>\n"

    return xml


def write_contents_file(tmpdirname, tiles, keep_refs, keep_ids, additions, meta):
    with open(tmpdirname+"/contents.txt", "w", encoding="utf-8") as f:
        f.write("[")
        f.write(json.dumps(tiles))
        f.write(",")
        # if we got information about which ids were still selected, filter the result before recording
        if len(keep_refs) > 0 or len(keep_ids) > 0:
            if len(keep_refs) > 0:
                api_logger.debug(
                    "Filtering dataset contents for %s stable selections",
                    len(keep_refs),
                )
            else:
                api_logger.debug(
                    "Filtering dataset contents for %s legacy selections",
                    len(keep_ids),
                )
            results = json.loads(session['results'])
            tile_count = 0

            # first, write write current results that are checked (i.e. in keep_ids)
            for i, result in enumerate(results):
                if result['class_name'] != 'tile':
                    result_ref = _normalize_detection_ref(
                        result.get('tile'),
                        result.get('id_in_tile')
                    )
                    if len(keep_refs) > 0 and result_ref is not None:
                        result['selected'] = result_ref in keep_refs
                        api_logger.debug(
                            "Stable detection ref %s %s",
                            result_ref,
                            "included" if result_ref in keep_refs else "not included",
                        )
                    else:
                        result['selected'] = (i-tile_count in keep_ids)
                        api_logger.debug(
                            "Legacy detection index %s %s",
                            i - tile_count,
                            "included" if (i - tile_count) in keep_ids else "not included",
                        )
                else:
                    tile_count += 1

            # store the filtered results back in session
            session['results'] = json.dumps(results)
        
        # now, process additions, and add them to the session results
        # TASK-033 Phase 3: Convert additions back to full detection objects with lat/long
        api_logger.debug(
            "Preparing dataset contents with manual additions count=%s",
            len(additions),
        )
        if len(additions) > 0:
            # Convert each addition from normalized tile coordinates to lat/long
            # Input: {"tile": 0, "centerx": 0.91, "centery": 0.66, "w": 0.034, "h": 0.037}
            # Output: {"x1": lat, "y1": lng, "x2": lat, "y2": lng, "conf": 1.0, "class": 0, 
            #          "class_name": "ct", "secondary": 1.0, "tile": 0, "id_in_tile": -1, 
            #          "selected": true, "inside": true}
            
            manual_provider = session.get('last_detection_provider', 'auto')

            # Initialize geocoding service and cache for manual tower address lookup
            geocoding_service = create_geocoding_service(
                azure_key=azure_api_key,
                google_key=google_api_key,
                preferred_provider=manual_provider
            )
            geocoding_cache = create_geocoding_cache(clustering_radius_meters=50.0)
            
            results = json.loads(session['results'])
            
            for addition in additions:
                tile_id = addition['tile']
                # Find the corresponding tile to get its geographic bounds
                tile = None
                for t in tiles:
                    if t.get('index', -1) == tile_id:
                        tile = t
                        break
                
                if tile is None:
                    api_logger.warning("Could not find tile %s for manual addition", tile_id)
                    continue
                
                # Get tile geographic bounds from results (tiles are at start of results array)
                tile_result = None
                for r in results:
                    if r.get('class_name') == 'tile' and r.get('id') == tile_id:
                        tile_result = r
                        break
                
                if tile_result is None:
                    api_logger.warning(
                        "Could not find tile result %s for manual addition",
                        tile_id,
                    )
                    continue
                
                # Convert normalized coordinates to lat/lng
                # Tile bounds: x1=lng_west, y1=lat_north, x2=lng_east, y2=lat_south
                tile_x1 = tile_result['x1']  # west longitude
                tile_y1 = tile_result['y1']  # north latitude
                tile_x2 = tile_result['x2']  # east longitude
                tile_y2 = tile_result['y2']  # south latitude
                
                tile_width = tile_x2 - tile_x1
                tile_height = tile_y1 - tile_y2  # Note: y1 > y2 (north > south)
                
                # Calculate detection bounds in lat/lng
                center_lng = tile_x1 + (addition['centerx'] * tile_width)
                center_lat = tile_y1 - (addition['centery'] * tile_height)  # Subtract because y increases downward
                
                half_width_lng = (addition['w'] * tile_width) / 2
                half_height_lat = (addition['h'] * tile_height) / 2
                
                detection_x1 = center_lng - half_width_lng  # west
                detection_y1 = center_lat + half_height_lat  # north
                detection_x2 = center_lng + half_width_lng  # east
                detection_y2 = center_lat - half_height_lat  # south
                
                # TASK-033 Phase 3: Reverse geocode manual tower location (with caching for performance)
                try:
                    # Try cache first for performance
                    cached_result = geocoding_cache.get(center_lat, center_lng, provider=manual_provider)
                    if cached_result:
                        manual_address = cached_result.address
                        manual_addr_conf = cached_result.confidence
                        manual_addr_provider = cached_result.provider.value
                        api_logger.debug(
                            "Manual tower address resolved from cache tile=%s",
                            tile_id,
                        )
                    else:
                        # Geocode and cache result
                        geocoding_result = geocoding_service.reverse_geocode(center_lat, center_lng, manual_provider)
                        if geocoding_result.success and geocoding_result.address:
                            manual_address = geocoding_result.address
                            manual_addr_conf = geocoding_result.confidence
                            manual_addr_provider = geocoding_result.provider.value
                            
                            # Cache the result for future restorations
                            geocoding_cache.put(center_lat, center_lng, geocoding_result, provider=manual_provider)
                            api_logger.debug(
                                "Manual tower reverse geocoded tile=%s provider=%s",
                                tile_id,
                                manual_addr_provider,
                            )
                        else:
                            manual_address = ""
                            manual_addr_conf = 0.0
                            manual_addr_provider = "manual"
                            api_logger.warning(
                                "Manual tower geocoding returned no address tile=%s error=%s",
                                tile_id,
                                geocoding_result.error_message,
                            )
                except RateLimitError as e:
                    api_logger.warning("Geocoding rate limited for manual tower tile=%s: %s", tile_id, e)
                    manual_address = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                    manual_addr_conf = 0.0
                    manual_addr_provider = "rate_limited"
                except GeocodingError as e:
                    api_logger.warning("Reverse geocoding failed for manual tower tile=%s: %s", tile_id, e)
                    manual_address = ""
                    manual_addr_conf = 0.0
                    manual_addr_provider = "manual"
                except Exception as geocode_error:
                    api_logger.error(
                        "Unexpected geocoding error for manual tower tile=%s: %s",
                        tile_id,
                        geocode_error,
                        exc_info=True,
                    )
                    manual_address = ""
                    manual_addr_conf = 0.0
                    manual_addr_provider = "manual"
                
                # Create detection object (TASK-033 Phase 3: Include all required fields)
                detection = {
                    "x1": detection_x1,
                    "y1": detection_y1,
                    "x2": detection_x2,
                    "y2": detection_y2,
                    "conf": 1.0,
                    "class": 0,
                    "class_name": "ct",
                    "secondary": 1.0,
                    "tile": tile_id,
                    "id_in_tile": -1,  # Mark as manual addition
                    "selected": True,
                    "inside": True,
                    "address": manual_address,
                    "address_confidence": manual_addr_conf,
                    "address_provider": manual_addr_provider
                }
                
                results.append(detection)
                api_logger.info(
                    "Added manual tower to results tile=%s lat=%.6f lng=%.6f",
                    tile_id,
                    center_lat,
                    center_lng,
                )
            
            # Update session results with additions
            session['results'] = json.dumps(results)

        # write the whole "current result set", modified selections, additions and all
        f.write(session['results'])
        f.write(","+("false" if meta else "true"))
        f.write("]")


#
#
# upload dataset for further editing:
#

@app.route('/uploaddataset', methods=['POST'])
def upload_dataset():
    api_logger.info("Dataset upload requested")
    
    # Rate limiting (more lenient for local development/testing)
    # TASK-033 Phase 3: Increased limit for manual verification testing
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    if not rate_limiter.is_allowed(client_ip, max_requests=10, window_seconds=60):
        return jsonify({'error': 'Rate limit exceeded for dataset uploads'}), 429
    
    # Input validation
    try:
        if 'dataset' not in request.files:
            raise ValidationError("No dataset file provided")
            
        file = TowerScoutValidator.validate_dataset_file(request.files['dataset'])
    except ValidationError as e:
        api_logger.warning("Dataset upload validation failed: %s", e.message)
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception as e:
        api_logger.error("Unexpected dataset upload validation error: %s", e, exc_info=True)
        return jsonify({'error': 'Invalid request data'}), 400

    # ISSUE-001 FIX: Wrap entire processing in try-except for better error handling
    try:
        # make a temp dir as usual
        # first, clean out the old tempdir
        if "tmpdirname" in session:
            rmtree(session['tmpdirname'], ignore_errors=True, onerror=None)
            api_logger.info("Cleaned up existing dataset temp dir %s", session['tmpdirname'])
            del session['tmpdirname']

        # make a new tempdir name and attach to session
        tmpdirname = _make_session_tmpdir()
        api_logger.info("Creating dataset temp dir %s", tmpdirname)
        session['tmpdirname'] = tmpdirname

        # TASK-033 Phase 3: Use os.path.join and os.path.basename for cross-platform compatibility
        filename = os.path.join(tmpdirname, file.filename)
        file.save(filename)
        new_stem = os.path.basename(tmpdirname)

        # unzip dataset.zip
        # - "empty" tiles and labels right into "."
        # - "train" combine "images" and "labels" folders into "."
        # content.txt in "."
        with zipfile.ZipFile(filename) as zipf:
            # read previous results and tiles from content.txt and add to session
            # print(" zip contents:")
            filenames = zipf.namelist()
            
            # TASK-036: Skip root-level files (README.txt, contents.txt) when finding old_stem
            # Only use files in subfolders to extract the dataset prefix
            subfolder_files = [f for f in filenames if "/" in f and not f.endswith("/")]
            if not subfolder_files:
                api_logger.warning("Dataset ZIP did not contain any subfolder files")
                return jsonify({"error": "Invalid dataset structure: no subfolder files found"}), 400
            
            old_stem = subfolder_files[0][:subfolder_files[0].index("/")]
            files = adapt_filenames(filenames, old_stem, new_stem)
            # print(files)
            for f_zip, f_new in zip(zipf.namelist(), files):
                api_logger.debug("Restoring dataset archive member %s to %s", f_zip, f_new)
                if not f_zip.endswith(".xml"):
                    with zipf.open(f_zip) as f:
                        with open(tmpdirname+"/"+f_new, "wb") as f_target:
                            api_logger.debug("Writing restored dataset file %s", tmpdirname+"/"+f_new)
                            f_target.write(f.read())

        # process contents file
        api_logger.info("Parsing restored contents.txt in %s", tmpdirname)
        contents_file = os.path.join(tmpdirname, "contents.txt")
        
        if not os.path.exists(contents_file):
            api_logger.warning("contents.txt not found in restored dataset")
            return jsonify({"error": "Invalid dataset: contents.txt missing"}), 400
        
        with open(contents_file) as f:
            results = json.loads(f.read())
        
        # Validate results structure
        if not isinstance(results, list) or len(results) < 3:
            api_logger.warning(
                "Invalid contents.txt structure type=%s len=%s",
                type(results),
                len(results) if isinstance(results, list) else 'N/A',
            )
            return jsonify({"error": "Invalid dataset format: contents.txt structure invalid"}), 400

        session['detections'] = adapt_tiles(
            results[0], tmpdirname, old_stem, new_stem)
        session['results'] = json.dumps(results[1])
        session['metadata'] = results[2]
        # print("Results:", results[1])
        # return previous results
        api_logger.info("Dataset restore completed successfully")

        # TASK-033 Phase 3: Return JSON response, not plain text string
        # Frontend expects parsed JSON array, not a JSON string
        return jsonify(results[1])
    
    except zipfile.BadZipFile as e:
        api_logger.warning("Invalid dataset ZIP file: %s", e)
        return jsonify({'error': 'Invalid ZIP file format'}), 400
    except json.JSONDecodeError as e:
        api_logger.warning("Invalid JSON in dataset contents.txt: %s", e)
        return jsonify({'error': 'Invalid dataset: corrupted contents.txt'}), 400
    except KeyError as e:
        api_logger.warning("Missing required field in restored dataset: %s", e)
        return jsonify({'error': f'Invalid dataset: missing field {str(e)}'}), 400
    except Exception as e:
        api_logger.error("Unexpected error during dataset upload: %s", e, exc_info=True)
        return jsonify({'error': f'Failed to process dataset: {str(e)}'}), 500

# carefully unravel the zip structure we created in the dataset, and make it all flat


def adapt_filenames(filenames, old_stem, new_stem):
    # print("f[0]", filenames[0])
    # print("old_dir",old_dir)
    results = []
    for f in filenames:
        # TASK-036: Handle root-level files (README.txt, contents.txt)
        # These don't have the old_stem prefix
        if "/" not in f:
            # Root-level file - keep as-is
            results.append(f)
            continue
        
        f = f[len(old_stem)+1:]  # strip old dir name
        # print("stripped:",f)
        if f.startswith("empty/"):
            f = f[len("empty/"):]
        elif f.startswith("train/images/"):
            f = f[len("train/images/"):]
        elif f.startswith("train/labels/"):
            f = f[len("train/labels/"):]

        # print("check: f:", f, "old:", old_dir, "new:", new_dir)
        if f.startswith(old_stem):
            f = new_stem+f[len(old_stem):]

        results.append(f)

    return results


def adapt_tiles(tiles, tmpdirname, old_stem, new_stem):
    for t in tiles:
        # print("before", t['filename'], t['labelfilename'])
        # TASK-033 Phase 3: Use os.path.basename for cross-platform compatibility
        name = os.path.basename(t['filename'])
        # TASK-033 Phase 3: Use os.path.join for cross-platform compatibility
        t['filename'] = os.path.join(tmpdirname, new_stem + name[len(old_stem):])
        t['labelfilename'] = os.path.join(tmpdirname, new_stem + name[len(old_stem):][0:-4] + ".txt")
        # print("after", t['filename'], t['labelfilename'])
    return tiles


if __name__ == '__main__':
    # API keys are now loaded from environment variables at module level
    # app.run(debug = True)
    # app.secret_key = 'super secret key'
    # app.config['SESSION_TYPE'] = 'filesystem'
    get_custom_models()
    engine_default = sorted(engines.items(),key=lambda x:-x[1]['ts'])[0][0]


    if len(sys.argv) <= 1 or sys.argv[1] != 'dev':
        start_zipcodes()
        get_engine(engine_default)
    else:
        dev = 1

    logger.info("Starting Waitress server on http://localhost:5000/")
    serve(app, host='0.0.0.0', port=5000, max_request_body_size=MAX_REQUEST_BODY_SIZE)
