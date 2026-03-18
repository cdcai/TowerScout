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

print("🚀 TowerScout starting...")

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
from ts_validation import (
    TowerScoutValidator, ValidationError, rate_limiter,
    validate_detection_request, validate_zipcode_request
)
from ts_errors import (
    TowerScoutError, ConfigurationError, ModelLoadError, MapProviderError,
    ProcessingError, SessionError, NetworkError, ResourceError, create_error_response
)
from ts_logging import (
    TowerScoutLogger, get_main_logger, get_maps_logger, get_ml_logger, 
    get_api_logger, log_startup_info, log_shutdown_info
)
from ts_performance import track_performance, PerformanceMetrics
import torch
import os
from shutil import rmtree
import zipfile
import ssl
import asyncio
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
script_dir = Path(__file__).parent
env_path = script_dir / '.env'

print("=" * 60)
print("TOWERSCOUT ENVIRONMENT DEBUG")
print("=" * 60)
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {script_dir}")
print(f".env file path: {env_path}")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    print(f"Loading .env from: {env_path}")
    load_dotenv(env_path)
else:
    print("Using default load_dotenv() behavior")
    load_dotenv()

# Debug: Check if keys are loaded
google_key = os.getenv('GOOGLE_API_KEY', '')
azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
bing_key = os.getenv('BING_API_KEY', '')

print(f"\nEnvironment Variables Status:")
print(f"GOOGLE_API_KEY: {'✓ Loaded' if google_key else '✗ Missing'}")
if google_key:
    print(f"  - Starts with: {google_key[:15]}...")
    print(f"  - Length: {len(google_key)} characters")

print(f"AZURE_MAPS_SUBSCRIPTION_KEY: {'✓ Loaded' if azure_key else '✗ Missing'}")
if azure_key:
    print(f"  - Starts with: {azure_key[:15]}...")
    print(f"  - Length: {len(azure_key)} characters")

print(f"BING_API_KEY: {'✓ Loaded' if bing_key else '✗ Missing'}")
if bing_key:
    print(f"  - Starts with: {bing_key[:15]}...")
    print(f"  - Length: {len(bing_key)} characters")

print("=" * 60)

import tempfile
from ts_geocoding import create_geocoding_service, GeocodingError, RateLimitError
from ts_geocache import create_geocoding_cache

# Initialize logging system early
logger = get_main_logger()
api_logger = get_api_logger()
ml_logger = get_ml_logger()
maps_logger = get_maps_logger()

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
MAP_CACHE_DIR = os.path.join(os.getcwd(), 'cache', 'maps')
os.makedirs(MAP_CACHE_DIR, exist_ok=True)
from PIL import Image, ImageDraw
import torch
import threading
import gc
import datetime
import sys
from functools import reduce 

dev = 0

MAX_TILES = 100000
MAX_TILES_SESSION = 100000

engines = {}

engine_default = None
engine_lock = threading.Lock()

exit_events = ExitEvents()

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
                'model_params/yolov5/'+engines[e]['file'])

        return engines[e]['engine']


def find_model(m):
    for engine in engines:
        if m == engines[engine]['file']:
            return True
    return False


def get_custom_models():
    for f in os.listdir("./model_params/yolov5"):
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
        'ts': os.path.getmtime("./model_params/yolov5/"+m)
    }



# map providers
providers = {
    'google': {'id': 'google', 'name': 'Google Maps'},
    'bing': {'id': 'bing', 'name': 'Bing Maps'},
    'azure': {'id': 'azure', 'name': 'Azure Maps'},
}

# Load API keys from environment variables
def load_api_keys():
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
    
    # At least one provider must be configured with a valid key
    if not google_key and not bing_key and not azure_key:
        raise ConfigurationError(
            "At least one map provider API key is required",
            missing_config="GOOGLE_API_KEY or AZURE_MAPS_SUBSCRIPTION_KEY",
            user_message="Map provider API keys are required. Please configure Google Maps or Azure Maps."
        )
    
    return google_key, bing_key, azure_key

# Load API keys with proper error handling
try:
    google_api_key, bing_api_key, azure_api_key = load_api_keys()
except ConfigurationError as e:
    logger.error(f"Configuration Error: {e.message}")
    logger.info("To fix this:")
    logger.info("1. Copy .env.example to .env")
    logger.info("2. Edit .env and add your Google Maps API key")
    logger.info("3. Restart the application")
    exit(1)

# other global variables
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# prepare uploads directory
if not os.path.isdir("./uploads"):
    os.mkdir("./uploads")
for f in os.listdir("./uploads"):
    os.remove(os.path.join("./uploads", f))

ml_logger.info(f"Torch CUDA: {'available' if torch.cuda.is_available() else 'not available'}")
ssl._create_default_https_context = ssl._create_unverified_context


# EfficientNet secondary classifier
secondary_en = EN_Classifier()


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

# Configure Flask from environment variables
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise EnvironmentError(
        "FLASK_SECRET_KEY environment variable is required for secure sessions. "
        "Please copy .env.example to .env and configure your secret key."
    )

app.config['UPLOAD_FOLDER'] = "uploads"
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# Configure server-side session
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
app.config.from_object(__name__)
Session(app)

# Flask Error Handlers
@app.errorhandler(TowerScoutError)
def handle_towerscout_error(error):
    """Handle all TowerScout custom exceptions with structured responses."""
    api_logger.error(f"TowerScout error: {error.message}", exc_info=True)
    response = jsonify(error.to_dict())
    response.status_code = 400 if isinstance(error, ValidationError) else 500
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
    return send_from_directory('../TowerScoutSite', path)

# route for images


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

# route for images
@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

# route for custom images
@app.route('/uploads/<path:path>')
def send_upload(path):
    return send_from_directory('uploads', path)

# route for custom images
@app.route('/rm/uploads/<path:path>')
def remove_upload(path):
    os.remove('uploads/'+path)
    logger.debug("Upload file deleted")
    return "ok"

# route for js code
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

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
    return send_from_directory('.', 'debug_azure_maps.html')

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
        preferred_provider = data.get('provider', 'auto')
        
        # Import geocoding service
        from ts_geocoding import GeocodingService
        
        # Initialize geocoding with available API keys
        geocoding = GeocodingService(
            azure_key=azure_api_key,
            google_key=google_api_key
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
        cached_result = cache.get(lat, lng)
        
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
            
            # Cache the result
            cache.put(lat, lng, result)
            
            return jsonify({
                'success': True,
                'address': result.address,
                'provider': result.provider.value,
                'confidence': result.confidence,
                'cached': False
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
    except Exception as e:
        return jsonify({'error': 'Invalid zipcode format'}), 400
        
    api_logger.debug(f"Zipcode requested: {zipcode}")
    with zipcode_lock:
        if zipcode_provider is None:
            logger.info("Loading zipcode data, this may take up to 10 seconds...")
            zipcode_provider = Zipcode_Provider()
        api_logger.debug("Looking up zipcode...")
        return zipcode_provider.zipcode_polygon(zipcode)

# abort route

@app.route('/abort', methods=['get'])
def abort():
    api_logger.info(f"Aborting session {id(session)}")
    exit_events.signal(id(session))
    return "ok"

# detection route

@app.route('/getobjects', methods=['POST'])
def get_objects():
    api_logger.debug(f"Processing session {id(session)}")

    # check whether this session is over its limit
    if 'tiles' not in session:
        session['tiles'] = 0

    # print("tiles queried in session:", session['tiles'])
    if session['tiles'] > MAX_TILES_SESSION:
        return "-1"

    # start time
    start = time.time()
    
    # Rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    if not rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=60):
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    
    # Input validation
    try:
        print("\n🔍 DIAGNOSTIC: Validating detection request...")
        print(f"   Form data keys: {list(request.form.keys())}")
        print(f"   Polygons data (first 200 chars): {request.form.get('polygons', '')[:200]}...")
        
        validated_data = validate_detection_request(request.form.to_dict())
        bounds_dict = validated_data['bounds']
        bounds = f"{bounds_dict['lat1']},{bounds_dict['lng1']},{bounds_dict['lat2']},{bounds_dict['lng2']}"
        engine = validated_data['engine']
        provider = validated_data['provider']
        polygons = validated_data['polygons']
        estimate = validated_data.get('estimate')
        
        print("✅ Validation passed")
    except ValidationError as e:
        print(f"❌ ValidationError: {e.message}")
        api_logger.error(f"Validation error: {e.message}")
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception as e:
        print(f"❌ Unexpected validation error: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        api_logger.error(f"Invalid request data: {str(e)}", exc_info=True)
        return jsonify({'error': f'Invalid request data: {str(e)}'}), 400
    
    print("incoming detection request:")
    print(" bounds:", bounds)
    print(" engine:", engine)
    print(" map provider:", provider)
    print(" polygons count:", len(polygons))
    
    # cropping
    crop_tiles = True
    
    # Initialize performance tracking for this detection workflow
    # NOTE: Do NOT store in session - PerformanceMetrics contains threading locks that can't be pickled
    perf_metrics = PerformanceMetrics(str(id(session)))
    perf_metrics.detection_engine = engine
    perf_metrics.map_provider = provider
    perf_metrics.crop_tiles = crop_tiles
    
    # Note: polygons are already validated Shapely Polygon objects

    # get the proper detector
    det = get_engine(engine)

    # empty results
    results = []

    # create a map provider object
    map = None
    try:
        print(f"\n🗺️  DIAGNOSTIC: Initializing map provider '{provider}'...")
        print(f"   Google API key available: {bool(google_api_key)}")
        print(f"   Azure API key available: {bool(azure_api_key)}")
        
        if provider == "google" and google_api_key:
            map = GoogleMap(google_api_key)
            print("✅ Google Maps initialized")
        elif provider == "azure" and azure_api_key:
            map = AzureMaps(azure_api_key)
            print("✅ Azure Maps initialized")
        
        if map is None:
            print(f"❌ Map provider '{provider}' not available or not configured")
            raise MapProviderError(
                f"Map provider '{provider}' not available or not configured",
                error_code="MAP_PROVIDER_UNAVAILABLE",
                user_message=f"The {provider} map service is not available. Please try a different provider."
            )
            
    except MapProviderError:
        raise
    except Exception as e:
        print(f"❌ Map provider initialization failed: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        api_logger.error(f"Failed to create map provider '{provider}': {e}", exc_info=True)
        return jsonify({'error': f'Map provider error: {str(e)}'}), 500

    # divide the map into 640x640 parts
    try:
        print(f"\n🔲 DIAGNOSTIC: Making tiles from bounds...")
        print(f"   Bounds: {bounds}")
        print(f"   Crop tiles: {crop_tiles}")
        
        tiles, nx, ny, meters, h, w = map.make_tiles(bounds, crop_tiles=crop_tiles)
        print(f"✅ Created {len(tiles)} tiles ({nx} x {ny})")
    except Exception as e:
        print(f"❌ Tile creation failed: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'Tile creation error: {str(e)}'}), 500
    # print(f" {len(tiles)} tiles, {nx} x {ny}, {meters} x {meters} m")
    # print(" Tile centers:")
    # for c in tiles:
    #   print("  ",c)

    tiles = [t for t in tiles if ts_maps.check_tile_against_bounds(t, bounds)]
    tiles = [t for t in tiles if ts_imgutil.tileIntersectsPolygons(t, polygons)]
    print(f"🔍 DEBUG: Setting IDs for {len(tiles)} tiles")  # Debug logging
    for i, tile in enumerate(tiles):
        tile['id'] = i
        print(f"  Tile {i}: keys = {tile.keys()}")  # Show what keys exist
    print(" tiles left after viewport and polygon filter:", len(tiles))
    
    # Update performance metrics with tile count and estimate processing time
    perf_metrics.tile_count = len(tiles)
    perf_metrics.estimate_processing_time(len(tiles))
    print(f"📊 Performance estimate: {len(tiles)} tiles, ~{perf_metrics.estimated_time_seconds:.1f} seconds")

    if estimate == "yes":
        # reset abort flag
        exit_events.alloc(id(session))  # todo: might leak some of these
        print(" returning number of tiles")
        print()
        # + ("" if len(tiles) > MAX_TILES else " (exceeds limit)")
        return str(len(tiles))

    if len(tiles) > MAX_TILES:
        print(" ---> request contains too many tiles")
        exit_events.free(id(session))
        return "[]"
    else:
        # tally the new request
        session['tiles'] += len(tiles)

    # main processing:
    # first, clean out the old tempdir
    if "tmpdirname" in session:
        rmtree(session['tmpdirname'], ignore_errors=True, onerror=None)
        print("cleaned up tmp dir", session['tmpdirname'])
        del session['tmpdirname']

    # make a new tempdir name and attach to session
    # TASK-033 Phase 3: Use mkdtemp() instead of TemporaryDirectory() to prevent automatic cleanup
    # TemporaryDirectory() auto-deletes when garbage collected, breaking dataset export
    tmpdirname = tempfile.mkdtemp()
    tmpfilename = os.path.basename(tmpdirname)
    print("creating tmp dir", tmpdirname)
    session['tmpdirname'] = tmpdirname
    print("created tmp dir", tmpdirname)

    # retrieve tiles and metadata if available
    perf_metrics.start_phase('tile_download')
    meta = map.get_sat_maps(tiles, loop, tmpdirname, tmpfilename)
    perf_metrics.end_phase('tile_download')
    session['metadata'] = meta
    print(" asynchronously retrieved", len(tiles), "files")
    
    # Update API call count for map tiles (1 call per tile)
    perf_metrics.map_api_calls = len(tiles)

    # check for abort
    if exit_events.query(id(session)):
        print(" client aborted request.")
        exit_events.free(id(session))
        return "[]"

    # augment tiles with retrieved filenames
    for i, tile in enumerate(tiles):
        # TASK-033 Phase 3: Use os.path.join for cross-platform compatibility
        tile['filename'] = os.path.join(tmpdirname, tmpfilename + str(i) + ".jpg")

    # detect all towers
    perf_metrics.start_phase('model_detection')
    model_start_time = time.time()
    results_raw = det.detect(tiles, exit_events, id(session), crop_tiles=crop_tiles, secondary=secondary_en, perf_metrics=perf_metrics)
    perf_metrics.actual_model_time_seconds = time.time() - model_start_time
    perf_metrics.end_phase('model_detection')
    perf_metrics.update_memory_usage()  # Capture memory after model inference
    # abort if signaled
    if exit_events.query(id(session)):
        print(" client aborted request.")
        exit_events.free(id(session))
        return "[]"

    # read metadata if present
    for tile in tiles:
        if meta:
            filename = tmpdirname+"/"+tmpfilename+str(tile['id'])+".meta.txt"
            with open(filename) as f:
                tile['metadata'] = map.get_date(f.read())
                # print(" metadata: "+tile['metadata'])
                f.close
        else:
            tile['metadata'] = ""

    # record some results in session for later saving if desired
    session['detections'] = make_persistable_tile_results(tiles)

    # post-process the results
    results = []
    detection_count = 0
    print(f"\n📊 DETECTION SUMMARY - Starting post-processing for {len(results_raw)} tiles")
    
    for result, tile in zip(results_raw, tiles):
        tile_detection_count = len(result)
        detection_count += tile_detection_count
        
        if tile_detection_count > 0:
            print(f"\n🎯 Tile {tile.get('id', '?')}: {tile_detection_count} detections")
        
        # adjust xyxy normalized results to lat, long pairs
        for i, object in enumerate(result):
            # Add diagnostic logging BEFORE transformation
            print(f"\n🔍 Detection {i+1}/{tile_detection_count} transformation debug:")
            print(f"  Tile: lng={tile['lng']:.6f}, lat={tile['lat']:.6f}, w={tile['w']:.6f}, h={tile['h']:.6f}")
            print(f"  YOLO normalized: x1={object['x1']:.6f}, y1={object['y1']:.6f}, x2={object['x2']:.6f}, y2={object['y2']:.6f}")
            print(f"  YOLO box size: width={(object['x2']-object['x1']):.6f}, height={(object['y2']-object['y1']):.6f}")
            print(f"  YOLO confidence: {object.get('conf', 0):.3f}, Class: {object.get('class', '?')}")
            
            # Track if this went through EfficientNet (secondary classifier)
            secondary_conf = object.get('secondary', None)
            if secondary_conf is not None:
                print(f"  EfficientNet: {secondary_conf:.3f} (YOLO was in intermediate range 0.25-0.65)")
            elif object.get('conf', 0) < 0.25:
                print(f"  EfficientNet: SKIPPED (YOLO < 0.25, auto-rejected)")
            else:
                print(f"  EfficientNet: SKIPPED (YOLO >= 0.65, auto-accepted)")
            
            # object['conf'] *= map.checkCutOffs(object) # used to do this before we started cropping
            object['x1'] = tile['lng'] - 0.5*tile['w'] + object['x1']*tile['w']
            object['x2'] = tile['lng'] - 0.5*tile['w'] + object['x2']*tile['w']
            object['y1'] = tile['lat'] + 0.5*tile['h'] - object['y1']*tile['h']
            object['y2'] = tile['lat'] + 0.5*tile['h'] - object['y2']*tile['h']
            
            # Add diagnostic logging AFTER transformation
            width_deg = abs(object['x2'] - object['x1'])
            height_deg = abs(object['y1'] - object['y2'])
            width_meters = width_deg * 111320 * math.cos(math.radians(object['y1']))
            height_meters = height_deg * 110540
            print(f"  Geographic: x1={object['x1']:.6f}, y1={object['y1']:.6f}, x2={object['x2']:.6f}, y2={object['y2']:.6f}")
            print(f"  Final box size: {width_meters:.1f}m x {height_meters:.1f}m")
            
            # Detection size analysis  
            if width_meters < 4 or height_meters < 4:
                print(f"  WARNING: Extremely small detection (< 4m) - likely false positive or image resolution issue!")
            elif width_meters < 10 or height_meters < 10:
                print(f"  Small detection (< 10m) - may be individual tower component rather than full structure")
            elif width_meters > 50 or height_meters > 50:
                print(f"  Large detection (> 50m) - verify not detecting entire building")
            else:
                print(f"  Detection size in expected range (10-50m for cooling tower)")
            
            object['tile'] = tile['id']
            object['id_in_tile'] = i
            object['selected'] = object['secondary'] >= 0.35

            # print(" output:",str(object))
        results += result

    # Print detection summary
    print(f"\n📊 DETECTION COMPLETE:")
    print(f"   Total detections: {len(results)}")
    print(f"   Tiles processed: {len(results_raw)}")
    print(f"   Average detections per tile: {len(results)/len(results_raw):.2f}" if len(results_raw) > 0 else "   No tiles processed")
    
    # Update performance metrics with detection counts
    perf_metrics.detection_count = len(results)
    
    # Calculate average confidence
    if results:
        total_confidence = sum(r.get('conf', 0) for r in results)
        perf_metrics.avg_confidence = total_confidence / len(results)

    # mark results out of bounds or polygon
    inside_count = 0
    outside_count = 0
    for o in results:
        o['inside'] = ts_imgutil.resultIntersectsPolygons(o['x1'], o['y1'], o['x2'], o['y2'], polygons) and \
            ts_maps.check_bounds(o['x1'], o['y1'], o['x2'], o['y2'], bounds)
        if o['inside']:
            inside_count += 1
        else:
            outside_count += 1
    
    print(f"\n📍 BOUNDARY FILTERING:")
    print(f"   Inside boundary: {inside_count}")
    print(f"   Outside boundary: {outside_count}")
    print(f"   Total detections: {inside_count + outside_count}")

    # sort the results by lat, long, conf
    results.sort(key=lambda x: x['y1']*2*180+2*x['x1']+x['conf'])

    # coaslesce neighboring (in list) towers that are closer than 1 m for x1, y1
    
    if len(results) > 1:
        i = 0
        while i < len(results)-1:
            if ts_maps.get_distance(results[i]['x1'], results[i]['y1'],
                                    results[i+1]['x1'], results[i+1]['y1']) < 1:
                print(" removing 1 duplicate result")
                results.remove(results[i+1])
            else:
                i += 1
    
    # Add server-side address lookup for detections
    session['geocoding_limited'] = False
    if results:  # Only geocode if we have detections
        print(f" starting address lookup for {len(results)} detections")
        perf_metrics.start_phase('geocoding')
        address_start_time = time.time()
        
        try:
            # Use dedicated geocoding clustering radius (do not reuse search radius)
            clustering_radius = 50.0
            env_radius = os.getenv('GEOCODING_CLUSTERING_RADIUS', '')
            if env_radius:
                try:
                    clustering_radius = float(env_radius)
                except ValueError:
                    clustering_radius = 50.0  # Fallback to default

            # Initialize geocoding service and cache with provider preference
            # Use the same provider selected for map imagery to ensure consistency
            geocoding_service = create_geocoding_service(
                azure_key=azure_api_key,
                google_key=google_api_key,
                preferred_provider=provider
            )
            geocoding_cache = create_geocoding_cache(clustering_radius_meters=clustering_radius)
            
            # Add address to each detection
            for detection in results:
                if detection.get('class') == 0:  # Only geocode actual detections, not tiles
                    # Calculate center coordinates for geocoding
                    center_lat = (detection['y1'] + detection['y2']) / 2
                    center_lng = (detection['x1'] + detection['x2']) / 2
                    
                    try:
                        # Try cache first
                        cached_result = geocoding_cache.get(center_lat, center_lng)
                        if cached_result:
                            detection['address'] = cached_result.address
                            detection['address_confidence'] = cached_result.confidence
                            detection['address_provider'] = cached_result.provider.value
                        else:
                            # Geocode and cache result (uses service's configured preference)
                            geocoding_result = geocoding_service.reverse_geocode(center_lat, center_lng)
                            detection['address'] = geocoding_result.address
                            detection['address_confidence'] = geocoding_result.confidence
                            detection['address_provider'] = geocoding_result.provider.value
                            
                            # Cache the result
                            geocoding_cache.put(center_lat, center_lng, geocoding_result)
                            
                    except RateLimitError as e:
                        session['geocoding_limited'] = True
                        # Graceful fallback to coordinates
                        detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                        detection['address_confidence'] = 0.0
                        detection['address_provider'] = "rate_limited"
                        print(f" geocoding rate limited for {center_lat}, {center_lng}: {e}")
                    except GeocodingError as e:
                        # Graceful fallback to coordinates
                        detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                        detection['address_confidence'] = 0.0
                        detection['address_provider'] = "fallback"
                        print(f" geocoding failed for {center_lat}, {center_lng}: {e}")
                    except Exception as e:
                        # Unexpected error - use coordinates as fallback
                        detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                        detection['address_confidence'] = 0.0
                        detection['address_provider'] = "error"
                        print(f" unexpected geocoding error for {center_lat}, {center_lng}: {e}")
                else:
                    # For tile results (debugging), don't add address
                    detection['address'] = ""
                    detection['address_confidence'] = 0.0
                    detection['address_provider'] = "none"
            
            # Store geocoding usage in session for frontend display
            try:
                usage = geocoding_service.get_session_usage()
                session['geocoding_usage'] = {
                    'google_requests': usage.google_requests,
                    'azure_requests': usage.azure_requests,
                    'total_requests': usage.total_requests,
                    'successful_requests': usage.successful_requests,
                    'failed_requests': usage.failed_requests
                }
                # Update performance metrics with geocoding API calls
                perf_metrics.geocoding_api_calls = usage.total_requests
            except Exception as e:
                print(f" warning: could not store geocoding usage: {e}")
            
            address_time = time.time() - address_start_time
            perf_metrics.end_phase('geocoding')
            print(f" address lookup completed in {address_time:.2f} seconds")
            
        except Exception as e:
            print(f" address lookup initialization failed: {e}")
            # Add fallback address fields to all detections
            for detection in results:
                if detection.get('class') == 0:
                    center_lat = (detection['y1'] + detection['y2']) / 2
                    center_lng = (detection['x1'] + detection['x2']) / 2
                    detection['address'] = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                    detection['address_confidence'] = 0.0
                    detection['address_provider'] = "error"
                else:
                    detection['address'] = ""
                    detection['address_confidence'] = 0.0
                    detection['address_provider'] = "none"

    # Send tile metadata for JavaScript consumption (needed for metadata lookup)
    # These tiles are NOT rendered as detection rectangles (opacity=0, class=1)
    # JavaScript needs tile data for metadata, URLs, and coordinate references
    tile_results = []
    for tile in tiles:
        print(f"🔍 DEBUG: Processing tile, keys: {tile.keys()}")  # Debug logging
        tile_results.append({
            'x1': tile['lng'] - 0.5*tile['w'],
            'y1': tile['lat'] + 0.5*tile['h'],
            'x2': tile['lng'] + 0.5*tile['w'],
            'y2': tile['lat'] - 0.5*tile['h'],
            'class': 1,  # Class 1 = Tile (not detection)
            'class_name': 'tile',
            'conf': 1,
            'metadata': tile['metadata'],
            'url': tile['url'],
            'id': tile.get('id', -1),  # TASK-033 Phase 3: Use .get() with fallback
            'selected': True
        })

    # all done
    selected = str(reduce(lambda a,e: a+(e['selected']),results, 0))
    print(" request complete," + str(len(results)) +" detections (" + selected +" selected), elapsed time: ", (time.time()-start))
    
    # Update performance metrics with selected count and finalize
    perf_metrics.detections_selected = int(selected)
    perf_metrics.finalize()
    
    # Log performance metrics
    from ts_performance import get_performance_logger
    get_performance_logger().log_metrics(perf_metrics)
    
    results = tile_results+results  # Prepend tiles for metadata lookup
    print()

    exit_events.free(id(session))
    results = json.dumps(results)
    session['results'] = results
    
    return results

def cleanup_temp_directory():
    # Cleanup the tempdir at the end of the session or application
    if "tmpdir_obj" in session:
        tmpdir = session['tmpdir_obj']
        print("Cleaning up tmp dir", tmpdir.name)
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
    except Exception as e:
        return jsonify({'error': 'Invalid request data'}), 400
        
    print("incoming custom image detection request:")
    print(" engine:", engine)
    print(" file:", file.filename)

    # get the proper detector
    det = get_engine(engine)

    # empty results
    results = []

    # filename = secure_filename(file.filename)
    filename = file.filename
    file.save("uploads/" + filename)
    print(" uploaded file ")
    results = det.detect([{'filename':"uploads/"+filename}],exit_events, id(session), crop_tiles=False)

    # draw result bounding boxes on image
    objects = 0
    with Image.open("uploads/" + filename) as im:
        for result in results:
            for object in result:
                drawResult(object, im)
                objects += 1
        im.save("uploads/" + filename, quality=95)
    print(" done drawing results.")

    # all done
    print(" custom request complete,", objects,
          " objects, elapsed time: ", (time.time()-start))

    results = json.dumps(results)
    session['results'] = results
    cleanup_temp_directory()
    return results


#
# pillow helper function to draw
#
def drawResult(r, im):
    print(" drawing ...")
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
    print("uploading model:")
    
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
    except Exception as e:
        return jsonify({'error': 'Invalid request data'}), 400

    if file.filename == '':
        print(' --- no selected model file')
        return None

    if not file or not file.filename.endswith(".pt"):
        print(" --- invalid file or extension:", file.filename)
        return None

    # filename = secure_filename(file.filename)
    filename = file.filename
    file.save("model_params/"+("EN" if filename.startswith("b5") else "yolov5")+"/" + filename)
    print(" uploaded file!")

    add_model(filename)

    print(" installed model", file.filename)

    return "ok"


# download results as dataset for formal training /testing
@ app.route('/getdataset', methods=['POST'])
def send_dataset():
    print("Dataset requested")

    # Validate JSON fields
    try:
        include = TowerScoutValidator.validate_json_field(request.form.get("include"), "include")
        additions = TowerScoutValidator.validate_json_field(request.form.get("additions"), "additions")
        
        # TASK-033 Phase 3: Debug logging for manual tower export
        print(f"\n🔍 DATASET EXPORT DEBUG:")
        print(f"   Include (ML detections): {len(include)} items")
        print(f"   Additions (manual towers): {len(additions)} items")
        if additions:
            print(f"   First addition: {additions[0]}")
            print(f"   Addition tile IDs: {[a['tile'] for a in additions]}")
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
    for inclusion in include:
        try:
            keep_detections.add(
                tiles[inclusion['tile']]['detections'][inclusion['detection']])
            # if the absolute tile id was also included,
            if 'id' in inclusion:
                keep_detection_ids.add(inclusion['id'])
        except:
            print(" invalid inclusion:", inclusion)
    print(" writing labels ...")

    # write files and records which ones had detections
    filenames = []
    print(f"\n🔍 WRITE LABELS DEBUG:")
    print(f"   Processing {len(tiles)} tiles from session")
    print(f"   Additions to match: {len(additions)} manual towers")
    
    for i, tile in enumerate(tiles):
        # Use tile's actual ID (stored as 'index') for matching with additions
        tile_id = tile.get('index', i)  # Fallback to enumeration index if 'index' not present
        print(f"   Tile {i}: session index={tile.get('index', 'MISSING')}, using tile_id={tile_id}")
        filenames += write_labels(tile_id, tile,
                                  keep_detections, additions, not meta)

    # write a contents file so we can load this again some time
    write_contents_file(session["tmpdirname"], tiles, keep_detection_ids, additions, meta)

    print(" zipping data ...")
    zipdir(session['tmpdirname'], filenames)
    print(" done.")
    print()
    return send_from_directory('temp', "dataset.zip")


# adapted from
# https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python

def zipdir(path, filenames):
    # TASK-033 Phase 3: Ensure temp directory exists and use proper paths
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    zip_path = os.path.join(temp_dir, 'dataset.zip')
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    
    # TASK-036: Add README.txt to dataset export
    readme_path = os.path.join(os.path.dirname(__file__), 'DATASET_README.txt')
    if os.path.exists(readme_path):
        zipf.write(readme_path, 'README.txt')
        print(" added README.txt to dataset")
    else:
        print(" WARNING: DATASET_README.txt not found, skipping README in export")
    
    for root, dirs, files in os.walk(path):
        for file in files:
            print(" compressing file", file)
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

    with open(tile['labelfilename'], "w") as f:
        print(" writing file ", f.name, "...")
        manual_towers_written = 0
        for detection in tile['detections']:
            if detection in keep:
                # print("", detection)
                f.write(detection)
                empty = False
        for a in additions:
            print(f"     Checking addition: tile={a['tile']} vs tile_id={tile_id}, match={a['tile'] == tile_id}")
            if a['tile'] == tile_id:
                f.write(" ".join(["0", str(a['centerx']), str(
                    a['centery']), str(a['w']), str(a['h'])])+"\n")
                empty = False
                manual_towers_written += 1
        if manual_towers_written > 0:
            print(f"     ✅ Wrote {manual_towers_written} manual tower(s) to this tile")

    # write xml labels for augmentation pipeline
    name = tile['labelfilename'][:-3]+"xml"
    size = 1280 if double_res else 640

    with open(name, "w") as f:
        print(" writing file ", f.name, "...")
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


def write_contents_file(tmpdirname, tiles, keep_ids, additions, meta):
    with open(tmpdirname+"/contents.txt", "w") as f:
        f.write("[")
        f.write(json.dumps(tiles))
        f.write(",")
        # if we got information about which ids were still selected, filter the result before recording
        if len(keep_ids) > 0:
            print(" filtering results for", len(keep_ids), "selections")
            results = json.loads(session['results'])
            tile_count = 0

            # first, write write current results that are checked (i.e. in keep_ids)
            for i, result in enumerate(results):
                if result['class_name'] != 'tile':
                    result['selected'] = (i-tile_count in keep_ids)
                    print("", i-tile_count, "included" if (i-tile_count)
                          in keep_ids else "not included")
                else:
                    tile_count += 1

            # store the filtered results back in session
            session['results'] = json.dumps(results)
        
        # now, process additions, and add them to the session results
        # TASK-033 Phase 3: Convert additions back to full detection objects with lat/long
        print("Session results before additions: ", session['results'])
        print("JSON version of additions:", json.dumps(additions))
        if len(additions) > 0:
            # Convert each addition from normalized tile coordinates to lat/long
            # Input: {"tile": 0, "centerx": 0.91, "centery": 0.66, "w": 0.034, "h": 0.037}
            # Output: {"x1": lat, "y1": lng, "x2": lat, "y2": lng, "conf": 1.0, "class": 0, 
            #          "class_name": "ct", "secondary": 1.0, "tile": 0, "id_in_tile": -1, 
            #          "selected": true, "inside": true}
            
            # Initialize geocoding service and cache for manual tower address lookup
            geocoding_service = create_geocoding_service(
                azure_key=azure_api_key,
                google_key=google_api_key,
                preferred_provider='google'  # Use consistent provider
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
                    print(f"  Warning: Could not find tile {tile_id} for addition")
                    continue
                
                # Get tile geographic bounds from results (tiles are at start of results array)
                tile_result = None
                for r in results:
                    if r.get('class_name') == 'tile' and r.get('id') == tile_id:
                        tile_result = r
                        break
                
                if tile_result is None:
                    print(f"  Warning: Could not find tile result {tile_id} for addition")
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
                    cached_result = geocoding_cache.get(center_lat, center_lng)
                    if cached_result:
                        manual_address = cached_result.address
                        manual_addr_conf = cached_result.confidence
                        manual_addr_provider = cached_result.provider.value
                        print(f"  ✅ Manual tower address from cache: {manual_address[:50]}...")
                    else:
                        # Geocode and cache result
                        geocoding_result = geocoding_service.reverse_geocode(center_lat, center_lng)
                        manual_address = geocoding_result.address
                        manual_addr_conf = geocoding_result.confidence
                        manual_addr_provider = geocoding_result.provider.value
                        
                        # Cache the result for future restorations
                        geocoding_cache.put(center_lat, center_lng, geocoding_result)
                        print(f"  ✅ Manual tower geocoded: {manual_address[:50]}...")
                except RateLimitError as e:
                    print(f"  ⚠️ Geocoding rate limited for manual tower: {e}")
                    manual_address = f"Address unavailable - {center_lat:.6f}, {center_lng:.6f}"
                    manual_addr_conf = 0.0
                    manual_addr_provider = "rate_limited"
                except GeocodingError as e:
                    print(f"  ⚠️ Reverse geocoding failed for manual tower: {e}")
                    manual_address = ""
                    manual_addr_conf = 0.0
                    manual_addr_provider = "manual"
                except Exception as geocode_error:
                    print(f"  ⚠️ Unexpected geocoding error for manual tower: {geocode_error}")
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
                print(f"  Added manual tower to results: tile={tile_id}, lat={center_lat:.6f}, lng={center_lng:.6f}")
            
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
    print("Dataset upload")
    
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
        print(f" ERROR: Validation failed: {e.message}")
        return jsonify({'error': f'Validation error: {e.message}'}), 400
    except Exception as e:
        print(f" ERROR: Unexpected validation error: {str(e)}")
        return jsonify({'error': 'Invalid request data'}), 400

    # ISSUE-001 FIX: Wrap entire processing in try-except for better error handling
    try:
        # make a temp dir as usual
        # first, clean out the old tempdir
        if "tmpdirname" in session:
            rmtree(session['tmpdirname'], ignore_errors=True, onerror=None)
            print(" cleaned up tmp dir", session['tmpdirname'])
            del session['tmpdirname']

        # make a new tempdir name and attach to session
        tmpdirname = tempfile.mkdtemp()
        print(" creating tmp dir", tmpdirname)
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
                print(" ERROR: No subfolder files found in dataset ZIP")
                return jsonify({"error": "Invalid dataset structure: no subfolder files found"}), 400
            
            old_stem = subfolder_files[0][:subfolder_files[0].index("/")]
            files = adapt_filenames(filenames, old_stem, new_stem)
            # print(files)
            for f_zip, f_new in zip(zipf.namelist(), files):
                print(" processing",f_zip,"to:",f_new)
                if not f_zip.endswith(".xml"):
                    with zipf.open(f_zip) as f:
                        with open(tmpdirname+"/"+f_new, "wb") as f_target:
                            print(" writing", tmpdirname+"/"+f_new)
                            f_target.write(f.read())

        # process contents file
        print("parsing contents.txt in", tmpdirname)
        contents_file = os.path.join(tmpdirname, "contents.txt")
        
        if not os.path.exists(contents_file):
            print(" ERROR: contents.txt not found in dataset")
            return jsonify({"error": "Invalid dataset: contents.txt missing"}), 400
        
        with open(contents_file) as f:
            results = json.loads(f.read())
        
        # Validate results structure
        if not isinstance(results, list) or len(results) < 3:
            print(f" ERROR: Invalid contents.txt structure: {type(results)}, len={len(results) if isinstance(results, list) else 'N/A'}")
            return jsonify({"error": "Invalid dataset format: contents.txt structure invalid"}), 400

        session['detections'] = adapt_tiles(
            results[0], tmpdirname, old_stem, new_stem)
        session['results'] = json.dumps(results[1])
        session['metadata'] = results[2]
        # print("Results:", results[1])
        # return previous results
        print(" dataset restored.")

        # TASK-033 Phase 3: Return JSON response, not plain text string
        # Frontend expects parsed JSON array, not a JSON string
        return jsonify(results[1])
    
    except zipfile.BadZipFile as e:
        print(f" ERROR: Invalid ZIP file: {str(e)}")
        return jsonify({'error': 'Invalid ZIP file format'}), 400
    except json.JSONDecodeError as e:
        print(f" ERROR: Invalid JSON in contents.txt: {str(e)}")
        return jsonify({'error': 'Invalid dataset: corrupted contents.txt'}), 400
    except KeyError as e:
        print(f" ERROR: Missing required field in dataset: {str(e)}")
        return jsonify({'error': f'Invalid dataset: missing field {str(e)}'}), 400
    except Exception as e:
        print(f" ERROR: Unexpected error during dataset upload: {str(e)}")
        import traceback
        traceback.print_exc()
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

    serve(app, host='0.0.0.0', port=5000)
    print("Web app running at http://localhost:5000/")
