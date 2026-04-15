# TowerScout AI Coding Guide

TowerScout is a Flask web application for detecting cooling towers from satellite imagery using YOLOv5 and EfficientNet models. Originally a graduate school project, it's been used in 12+ Legionnaires' disease outbreak investigations across 8 states and is being improved for public accessibility.

## Architecture Overview

**Core Components:**
- `webapp/towerscout.py` - Main Flask app with session-based processing
- `webapp/ts_yolov5.py` - YOLOv5 detector wrapper (batch_size=16, lazy-loaded)
- `webapp/ts_en.py` - EfficientNet secondary classifier (threshold=0.5, lazy-loaded)
- `webapp/ts_maps.py` - Abstract map provider interface
- `webapp/ts_gmaps.py` & `webapp/ts_azure_maps.py` - Google Maps and Azure Maps implementations
- `webapp/ts_events.py` - Event handling and progress tracking system
- `webapp/ts_imgutil.py` - Image processing utilities and coordinate transforms
- `webapp/ts_zipcode.py` - Geographic boundary validation using Census TIGER data
- `webapp/ts_geocoding.py` - Address and location geocoding services
- `webapp/ts_geocache.py` - Caching layer for geocoding and map data
- `webapp/ts_errors.py` - Centralized error handling and custom exceptions
- `webapp/ts_logging.py` - Structured logging system for debugging and monitoring
- `webapp/ts_validation.py` - Input validation and data sanitization utilities
- `Model/` - Jupyter notebooks for training and evaluation
- `SyntheticData/` - Dataset augmentation tools
- `TowerScoutSite/` - Static marketing site

**Data Flow:**
1. User draws polygon or searches by address/zipcode → validated against zipcode boundaries
2. Backend tiles area into 640x640px chunks via `ts_imgutil.make_tiles()`
3. Tile intersection check with `tileIntersectsPolygons()`
4. Downloads satellite imagery asynchronously via map APIs
5. YOLOv5 detection in GPU batches (16 images/batch, semaphore-controlled)
6. EfficientNet classifier filters results (threshold=0.5)
7. Coordinate transformation back to lat/lng with confidence scores
8. Results stored in session for frontend display and dataset export

## Legacy Feature Requirements (Production-Critical)

**Core Detection Workflow:**
- Machine learning-based cooling tower detection with confidence scores
- Multi-provider satellite imagery (Google Maps, Azure Maps) with quality comparison
- Interactive confidence threshold filtering and result toggling
- Automatic address geocoding for detected towers

**Search and Navigation:**
- Location-based searches (city, neighborhood, zipcode with quotes)
- Custom polygon drawing tool for complex search areas
- Circular radius search around specific coordinates
- Tile estimation for processing time prediction (<100 tiles ≈ 30 seconds)
- Map controls (pan, zoom, drag) with provider switching

**Result Review and Editing:**
- Interactive map overlay with clickable tower markers
- Right-panel details (address, confidence, imagery date)
- Bidirectional highlighting (address ↔ map marker)
- False positive deselection via checkboxes
- Manual tower addition using polygon tool
- Tile-by-tile and tower-by-tower review modes

**Export and Data Management:**
- Multi-format export (CSV with source indicator, KML for Google Earth)
- **CSV Format (Sprint 03)**: Added "source" column to distinguish ML vs Manual detections
  - `idInTile === -1` → Manual tower (user-drawn)
  - `idInTile >= 0` → ML detection (YOLOv5 + EfficientNet)
  - Supports outbreak investigation provenance tracking
- YOLO format dataset export for ML training
- Manual dataset addition via map selection
- Session persistence for iterative labeling workflows

**Outbreak Investigation Workflow (Mission-Critical):**
- Rapid area definition with tile estimation
- Real-time detection progress with cancellation capability
- Systematic review modes for accuracy verification
- Export integration for epidemiological tracking
- **Performance Target:** <100 tiles processed in ~30 seconds
- **Accuracy Target:** Manual review capability to ensure detection completeness

**Label Mode (Registry Support):**
- Display all towers in full tiles (including outside search boundaries)
- Tile navigation for comprehensive labeling
- Support for building registries and ML training data collection

**Critical Constraint:** All legacy features must remain operational during any improvements or refactoring. These features support active disease outbreak investigations across multiple states.

## Security Status (RESOLVED)

**✅ PREVIOUS VULNERABILITY:** API keys were stored in plain text (`apikey.txt`) and committed to repository
- **Impact:** Previously exposed Google/Azure API keys, potential billing fraud
- **Resolution:** Migrated to environment variables with `.env` files and `.gitignore`
- **Current State:** Secure environment variable configuration implemented

## Industry Best Practice Gaps

**Implemented Improvements:**
- ✅ Comprehensive error handling via `ts_errors.py` and `ts_validation.py`
- ✅ Structured logging system implemented in `ts_logging.py`
- ✅ Unit testing framework established with comprehensive test suite
- ✅ Enhanced geocoding capabilities via `ts_geocoding.py` and `ts_geocache.py`
- ✅ Frontend modular architecture (TASK-038) - 27 JavaScript modules with 412.8 KB bundle
- ✅ Google Maps API quarterly version migration with PlaceAutocompleteElement
- ✅ Context-aware drawing notifications for search boundaries vs manual towers
- ✅ CSV export with ML/Manual source indicator column

**Remaining Architecture Improvements:**
- Reduce tight coupling between components for better testability
- Improve global state management for concurrent requests
- Further separate business logic from Flask routes

## Improvement Goals & Context

**Current State:** Student prototype requiring technical setup (manual downloads, CLI commands, API key files)
**Target:** User-friendly, locally-deployable tool with Docker containerization and multi-provider API support

**Improvement Priorities (Corrected):**

**Security (CRITICAL):**
1. ✅ Remove `apikey.txt` from repository history 
2. ✅ Implement environment variable configuration
3. Add input validation and rate limiting  
4. Use secure session configuration for local deployment

**Code Quality:**
1. ✅ Add comprehensive error handling and logging
2. ✅ Unit testing framework with comprehensive test coverage and development dependencies
3. ✅ Code formatting (black) and linting (flake8) tools available
4. Separate business logic from Flask routes

**Architecture:**
1. Implement dependency injection for testability
2. Add configuration management system
3. Create proper service layer abstractions
4. Add diagnostic endpoints for troubleshooting

**Performance:**
- Current GPU detection works but lacks CPU optimization
- Apply torch.quantization for CPU deployment
- Implement proper async/await patterns (currently mixed sync/async)

## Key Patterns

**Session Management:**
- Flask default sessions (signed cookies, not filesystem)
- Temporary directories in `uploads/` for image processing
- Results stored as `session['results']` and `session['detections']`
- Tile limits: `MAX_TILES=100000`, `MAX_TILES_SESSION=100000`

**Model Loading (Corrected):**
- Both YOLOv5 and EfficientNet are lazy-loaded via `get_engine()` functions
- Thread locks prevent concurrent loading: `self.lock = threading.Lock()`
- GPU memory managed with semaphores: `self.semaphore = threading.Semaphore(1)` (not 8)
- Batch size: 16 images (not 8 as previously documented)
- **Optimization Opportunity:** Apply torch.quantization for CPU deployment

**Map Provider Architecture:**
- Abstract `Map` base class in `ts_maps.py` enables provider selection
- **Current:** Google Maps (primary), Azure Maps (available as alternative)
- API keys stored in environment variables (completed security migration)

**Google Maps API Migration (Sprint 03 - TASK-039):**
- **Quarterly Version**: Using `v=quarterly` for automatic minor version updates
- **Search Implementation**: Replaced deprecated `SearchBox` with `PlaceAutocompleteElement` Web Component
  - Single global instance prevents duplicate Web Components
  - Automatic bounds biasing based on current map viewport
  - Seamless provider switching without re-initialization
- **Drawing Implementation**: Custom polygon drawing replaces deprecated `DrawingManager`
  - **Left-click**: Add polygon points with visual markers
  - **Right-click outside**: Complete polygon (alternative to double-click)
  - **Visual preview**: Live polyline preview while drawing
  - **Editable**: Completed polygons are editable and draggable
  - **Purple styling**: Matches manual tower identification workflow (#800080)
- **Deprecation Strategy**: 
  - `google.maps.Marker` deprecation warning acknowledged (12+ months notice from Google)
  - Migration to `AdvancedMarkerElement` planned for future sprint
  - Custom drawing avoids reliance on deprecated DrawingManager

**Azure Maps Integration:**
- **Drawing Tools**: Native `atlas.drawing.DrawingManager` with toolbar UI
  - Polygon and rectangle drawing tools
  - Edit geometry mode for post-draw modifications
  - Double-click completion (Azure Maps standard)
- **Search**: Native Azure Maps Search service with subscription key authentication
- **Styling**: Satellite imagery with fallback to road maps

**Async Image Processing:**
```python
# Pattern: Batch async downloads then sync GPU processing
urls = [self.get_url(tile) for tile in tiles]
loop.run_until_complete(gather_urls(urls, dir, fname, self.has_metadata))
results_raw = det.detect(tiles, exit_events, id(session))
```

**Coordinate Systems:**
```python
# Critical transformation pipeline:
1. User polygon (lat/lng) → Web Mercator projection
2. Tile generation with geographic bounds checking
3. YOLO detection (normalized 0-1 coordinates)
4. Coordinate transformation back to lat/lng via ts_imgutil
```

**Event System:**
- `ts_events.py` manages progress tracking and user cancellation
- Events stored per session for real-time UI updates
- Thread-safe event handling for concurrent processing

**JavaScript Architecture**
- **Frontend Architecture (Sprint 03 - TASK-038 Refactoring):**
  - Modular structure: 27 JavaScript files organized by responsibility
  - Build system: `webapp/build.js` concatenates modules → `webapp/js/towerscout.js` (412.8 KB)
  - Module loading order enforced for dependency management
  - Source files in `webapp/js/src/` organized by functional areas
  
- **Module Organization:**
  - **`src/config.js`** - Application configuration constants
  - **`src/store.js`** - Centralized state management
  - **`src/managers/`** - State managers and service coordinators
    - `ProviderStateManager.js` - Map provider switching and state synchronization
    - `TimerManager.js` - setTimeout/setInterval lifecycle management
    - `EventListenerManager.js` - DOM event listener tracking and cleanup
    - `ErrorHandler.js` - Client-side error handling and user notifications
  - **`src/providers/`** - Map provider implementations
    - `TSMap_base.js` - Abstract base class for all providers
    - `GoogleMap.js` - Google Maps API integration with custom drawing
    - `AzureMap.js` - Azure Maps API integration with native drawing tools
    - `providerInit.js` - Provider initialization and setup logic
  - **`src/boundaries/`** - Search boundary management
    - `PolygonBoundary.js` - Custom polygon drawing and management
    - `CircleBoundary.js` - Radius-based search boundaries
    - `ZipcodeBoundary.js` - ZIP code boundary validation
  - **`src/detection/`** - Detection result management
    - `Detection.js` - Detection object class with map overlays
    - `DetectionList.js` - Detection list rendering and filtering
    - `Tile.js` - Tile coordinate management
  - **`src/ui/`** - User interface components
    - `search.js` - Search and detection workflow
    - `export.js` - CSV, KML, and dataset export functionality
    - `navigation.js` - Map navigation and UI controls
  - **`src/utils/`** - Utility functions
    - `coordinates.js` - Coordinate transformations
    - `imagery.js` - Image processing helpers
    - `apiHelpers.js` - Backend API communication
  - **`src/globals.js`** - Global variable declarations and compatibility layer
  - **`src/towerscout.js`** - Main application initialization and workflow orchestration

- **State Management Classes:**
  - `ProviderStateManager` - Handles map provider switching and prevents race conditions
  - `TimerManager` - Manages setTimeout/setInterval lifecycle and cleanup
  - `EventListenerManager` - Tracks and manages DOM event listeners
  - `TowerScoutErrorHandler` - Client-side error handling and user feedback

- **Core UI Functions:**
  - Map initialization and provider switching (Google Maps ↔ Azure Maps)
  - Interactive polygon drawing with context-aware notifications
  - Real-time detection progress tracking and cancellation
  - Results display with confidence filtering and manual editing
  - Data export workflows (CSV with ML/Manual source, KML, YOLO format)

- **Search Capabilities:**
  - Address/zipcode geocoding with auto-complete (PlaceAutocompleteElement for Google, native search for Azure)
  - Polygon-based area selection with tile estimation
  - Circular radius search around points of interest
  - Provider-aware search optimization

- **Drawing Mode Features (Sprint 03):**
  - **Persistent notifications** during drawing (no auto-dismiss until complete)
  - **Provider-specific instructions**: "Right-click outside" (Google) vs "Double-click" (Azure)
  - **Context-aware completion messages**: Different messages for search boundaries vs manual tower additions
  - **Custom Shape button workflow**: Consumes drawn polygons as search boundaries
  - **Visual differentiation**: Purple polygons (drawing mode) → Blue/green lines (search boundaries)

## Development Workflows

**Current Local Development Setup:**
```bash
# Standard local development approach
cd webapp
python towerscout.py dev
```

**Local Deployment Docker Strategy:**
```dockerfile
# Use specific Python version, security-focused base
FROM python:3.12-slim

# Don't run as root
RUN useradd --create-home --shell /bin/bash app
USER app

# Environment-based configuration
ENV FLASK_ENV=development
ENV GOOGLE_API_KEY=""
ENV AZURE_MAPS_KEY=""
```

**Dependencies Critical Notes:**
- `fiona==1.9.6` pinned due to GDAL compatibility issues
- `torch` without CUDA in requirements.txt (CPU fallback missing)
- Core: `torch`, `torchvision`, `flask`, `waitress`
- CV: `opencv-python`, `Pillow`, `efficientnet_pytorch`, `rasterio`
- GIS: `geopandas`, `Shapely`, `fiona==1.9.6`
- Async: `aiohttp`, `aiofiles`

**Asset Management:**
- YOLOv5 weights: Download `newest.pt` from Google Drive → `model_params/yolov5/`
- EfficientNet weights: Download from Google Drive → `model_params/EN/`
- US Shapefile: Census TIGER data → `data/` directory
- **Docker Strategy:** Embed models in container (~1.2GB) for one-command local deployment

**API Key Security:**
- **Previous:** Plain text in `apikey.txt` (security risk - resolved)
- **Current:** Environment variables (`GOOGLE_API_KEY`, `AZURE_MAPS_KEY`) 
- **Future Enhancement:** `MAPBOX_TOKEN` when Mapbox provider added
- Use `.gitignore` for sensitive files, pre-commit hooks to detect secrets

**Performance Optimization:**
- Hardware detection for GPU/CPU/Apple Silicon MPS capabilities
- Platform-specific batch size optimization (AMD64: 8-16, ARM64: 4-8, CPU: 4)
- Memory monitoring and management for 8GB RAM constraints
- Implement proper async patterns for I/O operations (currently mixed sync/async)
- Monitor GPU memory with CUDA device properties
- Use vectorized numpy operations for imagery processing

**Debugging Detection Issues:**
- Check `session['tiles']` for tile count limits
- Use tile debugging mode (returns tile boundaries as pseudo-results)
- Check polygon intersection with `ts_imgutil.tileIntersectsPolygons()`
- Test cross-provider imagery compatibility (Google vs Azure)
- **Hardware Testing:** Hardware compatibility testing (GPU/CPU/MPS detection)
- **Configuration Testing:** API key validation and network connectivity testing

## Critical Implementation Details

**Map Provider Security (Current Implementation):**
```python
# SECURE PATTERN (IMPLEMENTED):
class GoogleMap(Map):
    def __init__(self, api_key):
        self.key = api_key
        self.has_metadata = False
        # API key validation handled at application level

# USAGE PATTERN:
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("Google API key not configured")
google_map = GoogleMap(api_key)
```

**Missing Validation:**
- No input sanitization on polygon coordinates
- No rate limiting on API endpoints
- File upload validation missing

**Map Provider Evolution:**
- **Legacy:** Google Maps + Bing Maps via `apikey.txt` (SECURITY RISK - RESOLVED)
- **Current:** Google Maps + Azure Maps via environment variables
- **Target:** Multi-provider support with environment variables
- Abstract base class `Map` in `ts_maps.py` defines interface
- Each provider implements `get_url()` and `make_tiles()` methods
- **Key Challenge:** Normalize imagery outputs for consistent CV model performance
- Metadata support varies by provider (`has_metadata` flag)

**Thread Safety Issues:**
- Global model instances with threading locks (improvement needed)
- Session data shared across threads without proper synchronization
- Event system lacks proper cleanup mechanisms

**GPU Memory Management:**
- Batch size auto-calculated based on available CUDA memory
- Model instances cleared between requests to prevent OOM
- Thread locks prevent concurrent model loading
- Semaphore limits concurrent GPU operations
- **CPU Support:** Essential for diverse local hardware environments

**UI/UX Modernization:**
- **Current:** Bootstrap template, basic forms
- **Target:** In-app API key management, provider selection dropdown
- Error handling and fallbacks for failed API calls
- User guides with screenshots for non-technical users

**Dataset Export:**
- Users can export labeled datasets as ZIP files
- Generates both YOLO format (.txt) and XML format labels
- Maintains session state for iterative labeling workflows
- Supports dataset upload/restore via `contents.txt` manifest

**Deployment Strategy:**
- **Current Strategy:** Docker containerization for local deployment
- Base: Python 3.12-slim, optional NVIDIA CUDA runtime
- Volume mounts for models, data, and configuration
- Environment-based configuration for API keys

## File Structure Conventions

- `ts_*.py` - TowerScout module prefix for all backend components
- `model_params/` - Model weights storage (excluded from git)
- `uploads/` - Temporary user files (auto-cleaned)
- `flask_session/` - Session storage directory
- `templates/` - Jinja2 templates for web interface
- Jupyter notebooks use descriptive names ending in purpose (e.g., `_train.ipynb`, `_eval.ipynb`)

## Integration Guidelines

### Request Classification

**Type A (Quick Fixes):**
- Bug fixes, typos, small configuration changes
- Use abbreviated workflow focusing on implementation
- Document with streamlined action logs
- Skip formal requirements.md/design.md creation
- Examples: Fix import errors, update dependencies, correct documentation

**Type B (Feature Development):**
- New functionality, UI enhancements, API endpoints
- Full spec-driven approach with all 6 phases per [workflow guidelines](instructions/spec-driven-approach.instructions.md)
- Follow multi-file task management and context organization protocols
- Comprehensive testing and validation required
- Examples: Add new map providers, create new detection algorithms, implement advanced UI features

**Type C (Architecture Changes):**
- Security fixes, performance optimization, major refactoring
- Enhanced documentation requirements
- Create decision records for all architectural choices
- Full impact analysis and migration planning
- Examples: API key security fix, model optimization, major refactoring

### User Interaction Protocol

**Confirmation Points:**
- Always confirm before IMPLEMENT phase for Type B/C requests
- Ask for approval when Confidence Score < 85% for any request type
- Provide progress updates during operations exceeding 30 seconds
- Request clarification when requirements are ambiguous

**Autonomous Execution:**
- Type A requests can proceed without confirmation if Confidence Score > 85%
- Continue through VALIDATE and REFLECT phases without interruption
- Auto-create technical debt issues and decision records

**Communication Style:**
- Use clear phase indicators: "🔍 ANALYZING", "🏗️ DESIGNING", "⚡ IMPLEMENTING", etc.
- Provide estimated completion times for multi-step operations
- Summarize key decisions and trade-offs made

### TowerScout Workspace Integration

**Follow [Spec-Driven Approach](instructions/spec-driven-approach.instructions.md) for:**
- Task management protocols (current-tasks.md, task-backlog.md, completed-tasks.md)
- File organization and context documentation structure
- Maintenance schedules and archival strategies

**TowerScout-Specific Constraints:**
- **ML Model Protection**: Never modify core detection logic in `ts_yolov5.py` or `ts_en.py`
- **Legacy Feature Preservation**: All production-critical features must remain operational
- **Performance Requirements**: Support <100 tiles in ~30 seconds, 8GB RAM constraints
- **Context Priorities**: Prioritize outbreak investigation workflow documentation

**Project Structure Reference:**
```
.agent_work/
├── [Follow spec-driven multi-file task organization]
├── context/
│   ├── guides/          # Azure setup, deployment guides
│   ├── analysis/        # Provider independence, performance analysis
│   └── status/          # Progress tracking, commit readiness
└── decisions/           # TowerScout-specific architectural decisions
```

**Version Control Integration:**
- Create feature branches for Type B/C requests
- Use descriptive commit messages following conventional commits format
- Tag decision points and milestones for complex changes

## Git Workflow Integration (TowerScout-Optimized)

### **Branch Strategy - Solo Development with Paper Trail**

**Primary Workflow:**
```bash
main → feature/improvement branch → main (via PR)
```

**Branch Naming Convention:**
- `feature/ui-improvement-<description>` - UI/UX enhancements
- `fix/security-<issue>` - Security fixes (Type C - critical)
- `fix/bug-<description>` - Bug fixes (Type A)
- `docs/update-<section>` - Documentation updates
- `refactor/code-quality-<component>` - Code quality improvements

### **Commit Strategy - Frequent & Descriptive**

**Commit Message Format:**
```
<type>(<scope>): <description>

[optional body explaining what and why]

[optional footer with issue references]
```

**Types:**
- `feat:` - New UI/UX features
- `fix:` - Bug fixes
- `security:` - Security improvements
- `refactor:` - Code improvements without functionality change
- `docs:` - Documentation updates
- `style:` - CSS/UI styling changes
- `test:` - Adding tests

**Examples:**
```bash
feat(ui): add progress indicator for detection processing
fix(security): migrate API keys from plain text to environment variables
style(mobile): improve responsive design for polygon drawing
refactor(maps): abstract map provider interface for better testability
```

### **ML Model Protection Strategy**

**Protected Paths** (avoid changes):
- `model_params/` - Pre-trained model weights
- `Model/` - Training notebooks and evaluation scripts
- Core detection logic in `ts_yolov5.py` and `ts_en.py`

**Safe Improvement Areas:**
- `webapp/towerscout.py` - Flask routes and session management
- `templates/` - HTML templates and user interface
- `css/`, `js/` - Frontend styling and interactions
- `ts_maps.py`, `ts_gmaps.py`, `ts_azure_maps.py` - Map provider interfaces
- Configuration and deployment scripts

### **Commit Frequency Guidelines**

**High Frequency (Every Change):**
- Each UI component modification
- Each security fix iteration
- Configuration file updates
- Documentation improvements

**Medium Frequency (Per Feature):**
- Complete user workflow improvements
- API endpoint modifications
- Error handling enhancements

**Checkpoint Commits:**
- Before starting risky refactoring
- After successful validation phases
- At decision points documented in decision records

### **Paper Trail Documentation**

**Required for Each PR:**
1. **Executive Summary** - What changed and why
2. **Impact Assessment** - User experience improvements
3. **ML Model Safety** - Confirmation no detection logic modified
4. **Testing Evidence** - Screenshots, validation results
5. **Decision Records** - Links to architectural choices made

**Automated Paper Trail:**
- Commit messages provide granular change history
- PR descriptions provide feature-level summaries
- Decision records provide architectural rationale
- Issue references provide requirement traceability

## Coding Guidelines for Improvements

**Security First:**
- Never suggest hardcoded secrets or API keys
- Always implement proper error handling
- Use environment variables for configuration
- Validate all user inputs

**Developer Guidelines:**
- Follow coding standards and best practices
- Ensure code readability and maintainability
- Conduct thorough code reviews
- Use meaningful variable and function names. Ensure consistency and clarity.
- Maintain comprehensive inline documentation for complex logic.
- Ensure proper authentication and authorization for all endpoints.
- Before creating new classes and functions, evaluate existing ones for reuse.
- Always be skeptical of whether your developed solutions have been implemented properly and securely.
- Continuously review and refactor code to improve security and performance.
- Pay close attention to potential instances of ophaned code, unused dependencies, and infinite recursion issues.
- Ensure solutions comprehensively address all identified requirements and edge cases without creating additional complexity or unforeseen consequences.

**Quality Standards:**
- Add logging for all operations (use Python `logging` module)
- Implement proper exception handling with specific exception types
- Write testable code with dependency injection
- Follow PEP 8 style guidelines

**TowerScout-Specific:**
- Preserve CV model accuracy when optimizing
- Maintain coordinate system precision for geographic accuracy
- Test cross-platform compatibility (Windows/Linux/macOS) for local deployment
- Ensure CPU fallback works without GPU hardware (critical for diverse user hardware)
- Implement user-friendly error messages for non-technical users
- Support hardware detection and platform-specific optimization

**Performance Considerations:**
- Monitor GPU memory usage and implement proper cleanup
- Use vectorized operations for image processing
- Implement proper async patterns for I/O operations
- Cache model weights to avoid repeated loading
- **Hardware Detection:** Platform-specific batch sizing and optimization
- **Memory Management:** Constraint handling for 8GB systems
- **CPU Processing:** Progress indicators and optimization for CPU-only processing

## Development Priorities

**Completed Infrastructure:**
- ✅ Security: API keys migrated to environment variables
- ✅ Error Handling: Comprehensive error handling system implemented
- ✅ Logging: Structured logging system with `ts_logging.py`
- ✅ Testing: Unit test framework with integration and mocking capabilities
- ✅ Geocoding: Enhanced address lookup and caching system
- ✅ Frontend Refactoring (TASK-038): Modular 27-file architecture with build system
- ✅ Google Maps API Migration (TASK-039): Quarterly version with modern Web Components
- ✅ Drawing Mode UX: Context-aware notifications and persistent instructions
- ✅ CSV Export Enhancement: ML/Manual source tracking for outbreak investigations

**Sprint 03 Completions (March 16-17, 2026):**
- ✅ **ISSUE-001 (Dataset Upload)**: Backend error handling + frontend validation
  - Comprehensive try-except blocks for zipfile/JSON errors
  - HTTP status checking before JSON parsing
  - User-friendly error notifications
- ✅ **ISSUE-002 (Drawing Tools Visibility)**: Provider switching restoration
  - `restore()` method for Google/Azure Maps
  - Global variable synchronization for legacy code compatibility
  - HTML template fix for Custom Shape button workflow
- ✅ **Context-Aware Notifications**: Differentiate search area vs manual tower workflows
  - Persistent drawing instructions (no auto-dismiss)
  - Provider-specific completion methods (right-click vs double-click)
  - Automatic context detection based on detection state
- ✅ **Deprecation Warnings Cleanup**: Remove property descriptor triggers
  - Fixed initialization code to use local variables
  - Use providerManager API for state management
  - Clean console output without warnings

**Current Focus Areas:**
1. **User Experience**: Streamline local deployment with Docker containerization
2. **Documentation**: Update setup guides for non-technical users
3. **Performance**: Optimize CPU-only deployment scenarios
4. **Multi-Architecture**: Support ARM64/Apple Silicon deployment
5. **Provider Management**: Enhance map provider selection and fallback capabilities

## Sprint 03 Summary (March 16-17, 2026)

**Objective:** Complete Google Maps API migration and resolve Phase 5 integration testing issues

**Bundle Evolution:** 404.9 KB → 412.8 KB (+7.9 KB for all enhancements)

**Key Accomplishments:**
1. **Phase 5 Integration Testing**
   - 13 test scenarios executed (10 PASS, 2 PARTIAL, 1 FAIL initially)
   - Fixed 2 critical issues (ISSUE-001, ISSUE-002)
   - All scenarios passing after fixes

2. **Drawing Mode UX Enhancements**
   - Time investment: ~4-5 hours
   - Persistent notifications during polygon drawing
   - Context-aware completion messages
   - Custom Shape button consumes polygons as search boundaries
   - Provider-specific instructions (Google: right-click, Azure: double-click)

3. **Code Quality Improvements**
   - Fixed context detection timing bug (order of operations)
   - Removed deprecation warnings from initialization code
   - Enhanced error handling for dataset uploads
   - Improved provider switching reliability

4. **Export Enhancement**
   - Added "source" column to CSV exports
   - Enables ML vs Manual detection tracking
   - Supports outbreak investigation provenance requirements

**Technical Debt Addressed:**
- Google Maps DrawingManager deprecation (replaced with custom implementation)
- Global variable management (migrated to ProviderStateManager API)
- Property descriptor warnings (fixed initialization patterns)

**Testing & Validation:**
- ✅ Dataset upload/restore workflows
- ✅ Google Maps drawing tools after provider switch
- ✅ Context-aware notifications (both providers)
- ✅ CSV export with source column
- ✅ Large dataset performance (ISSUE-003 noted, not blocking)
