# TowerScout Domain Guide

TowerScout is a Flask web application for detecting cooling towers from satellite imagery using YOLOv5 and EfficientNet models. Originally a graduate school project, it has been used in 12+ Legionnaires' disease outbreak investigations across 8 states and is being improved for public accessibility.

## Architecture Overview

**Core Components:**
- `webapp/towerscout.py` - Main Flask app with session-based processing
- `webapp/ts_yolov5.py` - YOLOv5 detector wrapper (batch_size=16, lazy-loaded)
- `webapp/ts_en.py` - EfficientNet secondary classifier (threshold=0.5, lazy-loaded)
- `webapp/ts_maps.py` - Abstract map provider interface
- `webapp/ts_gmaps.py` and `webapp/ts_azure_maps.py` - Google Maps and Azure Maps implementations
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
1. User draws polygon or searches by address/zipcode and validated against zipcode boundaries
2. Backend tiles area into 640x640px chunks via `ts_imgutil.make_tiles()`
3. Tile intersection check with `tileIntersectsPolygons()`
4. Downloads satellite imagery asynchronously via map APIs
5. YOLOv5 detection in GPU batches (16 images/batch, semaphore-controlled)
6. EfficientNet classifier filters results (threshold=0.5)
7. Coordinate transformation back to lat/lng with confidence scores
8. Results stored in session for frontend display and dataset export

## Frontend Architecture (Sprint 03 - Completed March 18, 2026)

**Modular Structure** - Refactored from 5,272-line monolithic file to 27 modular files:

```
webapp/js/src/
├── config.js              # Application configuration constants
├── store.js               # Centralized state management (ProviderStateManager)
├── globals.js             # Global scope utilities and DOM references
├── towerscout.js          # Main initialization and coordination (4,848 lines)
├── managers/              # Lifecycle and state managers (4 files)
│   ├── providerStateManager.js  # State management with race condition prevention
│   ├── timerManager.js          # Timer lifecycle and cleanup tracking
│   ├── eventListenerManager.js  # DOM event listener tracking
│   └── errorHandler.js          # Centralized error handling
├── boundaries/            # Boundary type implementations (3 files)
│   ├── circleBoundary.js        # Circle drawing and management
│   ├── polygonBoundary.js       # Freehand polygon drawing
│   └── rectangleBoundary.js     # Rectangle boundary tool
├── providers/             # Map provider abstractions (4 files)
│   ├── providerInit.js          # Provider initialization logic
│   ├── googleMaps.js            # Google Maps SDK integration
│   ├── azureMaps.js             # Azure Maps SDK integration
│   └── providerMap.js           # Abstract provider interface
├── detection/             # Detection workflow modules (5 files)
│   ├── Detection.js             # Detection state and filtering
│   ├── detectionDisplay.js      # Rendering detections on map
│   ├── detectionList.js         # Results panel management
│   ├── detectionExport.js       # CSV/KML/YOLO export formats
│   └── confidence.js            # Confidence threshold filtering
├── ui/                    # User interface modules (3 files)
│   ├── navigation.js            # Map navigation and zoom controls
│   ├── search.js                # Location search and detection requests
│   └── highlighting.js          # Bidirectional list↔map highlighting
└── utils/                 # Shared utilities (3 files)
    ├── coordinates.js           # Coordinate system transformations
    ├── geometry.js              # Geometric calculations
    └── api.js                   # API request utilities
```

**Build System**:
- Concatenation-based (no webpack/rollup overhead)
- Pre-commit hooks automatically rebuild bundle on source changes
- Build command: `node build.js` (< 2 seconds)
- Output: Single `towerscout.js` bundle (412.8 KB - includes Sprint 03 enhancements)
- Source files maintained in `webapp/js/src/` for development

**Key Architectural Patterns**:
- **ProviderStateManager**: Centralized state preventing race conditions
- **Property Descriptors**: Deprecation warnings guide migration from globals
- **IIFE Modules**: Backward compatibility with inline HTML event handlers
- **Mutex Protection**: Thread-safe state mutations for detection arrays
- **Lifecycle Management**: Automatic timer and event listener cleanup

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
- Tile estimation for processing time prediction (<100 tiles, approx. 30 seconds)
- Map controls (pan, zoom, drag) with provider switching

**Result Review and Editing:**
- Interactive map overlay with clickable tower markers
- Right-panel details (address, confidence, imagery date)
- Bidirectional highlighting (address and map marker)
- False positive deselection via checkboxes
- Manual tower addition using polygon tool
- Tile-by-tile and tower-by-tower review modes

**Export and Data Management:**
- Multi-format export (Excel/CSV for tracking, KML for Google Earth)
- YOLO format dataset export for ML training
- Manual dataset addition via map selection
- Session persistence for iterative labeling workflows

**Outbreak Investigation Workflow (Mission-Critical):**
- Rapid area definition with tile estimation
- Real-time detection progress with cancellation capability
- Systematic review modes for accuracy verification
- Export integration for epidemiological tracking
- **Performance Target:** <100 tiles processed in approx. 30 seconds
- **Accuracy Target:** Manual review capability to ensure detection completeness

**Label Mode (Registry Support):**
- Display all towers in full tiles (including outside search boundaries)
- Tile navigation for comprehensive labeling
- Support for building registries and ML training data collection

**Critical Constraint:** All legacy features must remain operational during any improvements or refactoring. These features support active disease outbreak investigations across multiple states.

## Industry Best Practice Gaps

**Implemented Improvements:**
- ✅ Comprehensive error handling via `ts_errors.py` and `ts_validation.py` - Sprint 01
- ✅ Structured logging system implemented in `ts_logging.py` - Sprint 01
- ✅ Unit testing framework established with comprehensive test suite - Sprint 01
- ✅ Enhanced geocoding capabilities via `ts_geocoding.py` and `ts_geocache.py` - Sprint 01
- ✅ Frontend modularization complete (TASK-038, Sprint 02) - 27-file modular architecture
- ✅ Race condition fixes (TASK-043, Sprint 02) - ProviderStateManager pattern established
- ✅ Boundary accumulation bug resolved (TASK-045, Sprint 02) - Independent detection runs
- ✅ Google Maps API migration (TASK-039, Sprint 03) - Quarterly version with modern Web Components
- ✅ Manual tower addition restored (TASK-033, Sprint 03) - Drawing tools and export
- ✅ Export system enhanced (TASK-036, Sprint 03) - ML/Manual source tracking
- ✅ Drawing mode UX (Sprint 03) - Context-aware notifications and persistent instructions
- ✅ Integration testing framework (Sprint 03) - 13-scenario validation methodology

**Architecture Status (Sprint 03 - Completed March 18, 2026)**:
- ✅ **Frontend Modularization**: 5,272-line monolithic `towerscout.js` refactored into 27 modular files across 7 directories
- ✅ **State Management**: ProviderStateManager pattern with property descriptors and deprecation warnings
- ✅ **Memory Management**: Stress testing shows 0.7% memory decrease (exceptional performance)
- ✅ **Race Conditions**: 3 critical race conditions resolved (provider switching, detection mutations, progress timers)
- ✅ **Global Variable Deprecation**: Phase 1 & 2 complete, 97% deprecation warnings reduced
- ✅ **Google Maps API**: Quarterly version migration complete, zero legacy API usage
- ✅ **Drawing Tools**: Custom implementations replace all deprecated Google Maps components

**Remaining Architecture Improvements:**
- Setup wizard for user-friendly configuration (TASK-046, Sprint 04)
- Reduce tight coupling between components for better testability (Sprint 05-06)
- Further separate business logic from Flask routes (Sprint 05-06)
- Large dataset performance optimization (ISSUE-003 investigation, Sprint 04)

## Sprint Status

**Current Sprint**: Sprint 04 (March 19 - April 4, 2026)  
**Previous Sprint**: Sprint 03 ✅ COMPLETED March 18, 2026 (8 days, 6 days ahead of schedule)

### Sprint 03 Achievements (Completed March 18, 2026)

**Major Completions**:
- ✅ **Google Maps API Migration** (TASK-039 Phases 5-6): Quarterly version with PlaceAutocompleteElement Web Component
- ✅ **Manual Tower Addition** (TASK-033): Full feature restoration with drawing tools
- ✅ **Export System Enhancement** (TASK-036): CSV export with ML/Manual source column for outbreak investigations
- ✅ **Drawing Mode UX**: Context-aware notifications (search boundaries vs manual towers)
- ✅ **Integration Testing**: 13 scenarios validated, all passing
- ✅ **Issue Resolutions**: ISSUE-001 (dataset upload errors), ISSUE-002 (provider switching detection visibility)
- ✅ **Global Variable Deprecation**: Phase 1 & 2 complete, 97% deprecation warnings reduced
- ✅ **Deprecation Warnings Cleanup**: Property descriptor timing fixes, clean console output

**Bundle Evolution**: 372.6 KB → 412.8 KB (+40.2 KB for all Sprint 03 enhancements)

**Sprint Metrics**:
- Tasks Completed: 8 of 8 (100%)
- Sprint Effort: 56 hours actual (planned: 44-71 hours)
- Sprint Velocity: 7.0 hours/day
- Critical Issues Resolved: 2 of 2

**Technical Highlights**:
- PlaceAutocompleteElement replaces deprecated SearchBox (single global instance, automatic bounds biasing)
- Custom polygon drawing replaces deprecated DrawingManager (left-click add points, right-click complete)
- Context-aware notifications: persistent instructions during drawing, workflow-specific completion messages
- Dataset upload error handling: comprehensive try-except blocks, HTTP validation, user-friendly errors
- Provider switching fixes: restore() method, global variable synchronization, HTML template corrections

### Sprint 04 Current Focus (March 19 - April 4, 2026)

**Primary Objective**: Setup Wizard and Settings Screen (TASK-046)
- First-launch wizard for API key configuration
- In-app settings modal (no manual .env editing)
- Docker-compatible configuration persistence
- Performance metrics display
- Estimated: 40-50 hours (5-7 days with testing)

**Secondary Objectives**:
- ISSUE-003 investigation: Large dataset performance (500+ detections)
- UI polish and formatting improvements
- Console logging simplification for end users
- Legacy code cleanup from refactoring

**Sprint Capacity**: 65-75 hours (16 days)

---

## Improvement Goals and Context

**Current State:** Student prototype requiring technical setup (manual downloads, CLI commands, ~~API key files~~ - **RESOLVED**)  
**Target:** User-friendly, locally-deployable tool with Docker containerization and multi-provider API support

**Improvement Priorities (Updated Sprint 04 - March 18, 2026):**

**Security (CRITICAL):**
1. ✅ Remove `apikey.txt` from repository history - COMPLETED Sprint 01
2. ✅ Implement environment variable configuration - COMPLETED Sprint 01 (`.env` files, `GOOGLE_API_KEY`, `AZURE_MAPS_KEY`)
3. ✅ Input validation implementation - COMPLETED Sprint 01 (`ts_validation.py` with comprehensive testing)
4. ✅ Secure session configuration for local deployment - COMPLETED Sprint 01
5. ⏳ Rate limiting on API endpoints - PLANNED Sprint 05

**Code Quality:**
1. ✅ Add comprehensive error handling and logging - COMPLETED Sprint 01 (`ts_errors.py`, `ts_logging.py`)
2. ✅ Unit testing framework with comprehensive test coverage - COMPLETED Sprint 01 (23/23 tests passing)
3. ✅ Code formatting (black) and linting (flake8) tools - AVAILABLE Sprint 01
4. ✅ Frontend modularization - COMPLETED Sprint 02 (TASK-038, 27-file architecture)
5. ⏳ Separate business logic from Flask routes - PLANNED Sprint 05-06

**Architecture:**
1. ✅ State management consolidation - COMPLETED Sprint 02 (ProviderStateManager pattern, TASK-041/TASK-043)
2. ✅ Setup wizard and settings screen - IN PROGRESS Sprint 04 (TASK-046)
3. ⏳ Implement dependency injection for testability - PLANNED Sprint 05-06
4. ⏳ Add configuration management system - PLANNED Sprint 04-05
5. ⏳ Create proper service layer abstractions - PLANNED Sprint 06
6. ⏳ Add diagnostic endpoints for troubleshooting - PLANNED Sprint 05

**Performance:**
- ✅ GPU detection works with excellent performance - COMPLETED Sprint 01 (16 images/batch, semaphore-controlled)
- ✅ Memory management exceptional - COMPLETED Sprint 02 (0.7% decrease in stress testing - TASK-041)
- ✅ Async patterns for I/O operations - COMPLETED Sprint 01 (aiohttp, aiofiles)
- ✅ GPU memory management - COMPLETED Sprint 01 (batch sizing, cleanup)
- ⏳ CPU optimization with torch.quantization - PLANNED Sprint 05
- ⏳ Large dataset performance investigation - IN PROGRESS Sprint 04 (ISSUE-003)

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
1. User polygon (lat/lng) to Web Mercator projection
2. Tile generation with geographic bounds checking
3. YOLO detection (normalized 0-1 coordinates)
4. Coordinate transformation back to lat/lng via ts_imgutil
```

**Event System:**
- `ts_events.py` manages progress tracking and user cancellation
- Events stored per session for real-time UI updates
- Thread-safe event handling for concurrent processing

**JavaScript Architecture**
- **Frontend Architecture (Sprint 03 - Completed March 18, 2026):**
  - **Modular Build System**: 27 source modules compiled into single bundle via `build.js`
  - **Bundle**: `js/towerscout.js` (412.8 KB - includes Sprint 03 enhancements) - auto-built via pre-commit hooks
  - **Source Structure** (4,848 lines across 7 directories):
    - `js/src/` - Root modules (app initialization, main entry point)
    - `js/src/managers/` - State management (Provider, Timer, EventListener, Error)
    - `js/src/boundaries/` - Search area tools (Circle, Polygon, Zipcode)
    - `js/src/providers/` - Map provider implementations (Google, Azure, switching)
    - `js/src/detection/` - Detection workflow (PlaceRect, Detection, Tile, List, Review)
    - `js/src/ui/` - User interface (search, export, navigation)
    - `js/src/utils/` - Utilities (coordinates, imagery metadata, API helpers)
  - `js/jquery-3.5.1.min.js` - jQuery dependency for DOM manipulation
- **State Management Classes:**
  - `ProviderStateManager` - Handles map provider switching and prevents race conditions
  - `TimerManager` - Manages setTimeout/setInterval lifecycle and cleanup
  - `EventListenerManager` - Tracks and manages DOM event listeners
  - `TowerScoutErrorHandler` - Client-side error handling and user feedback
- **Core UI Functions:**
  - Map initialization and provider switching (Google Maps and Azure Maps)
  - Interactive polygon drawing and search area definition
  - Real-time detection progress tracking and cancellation
  - Results display with confidence filtering and manual editing
  - Data export workflows (CSV, KML, YOLO format)
- **Search Capabilities:**
  - Address/zipcode geocoding with auto-complete
  - Polygon-based area selection with tile estimation
  - Circular radius search around points of interest
  - Provider-aware search optimization
- **Architecture Benefits** (from TASK-038 refactoring):
  - 100% backward compatibility (zero template changes, all inline handlers preserved)
  - Easier feature development with isolated modules
  - Better testability with dependency injection patterns
  - Foundation for future TypeScript migration
  - Automatic bundle rebuilds via Git pre-commit hooks

## Critical Implementation Details

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

## File Structure Conventions

- `ts_*.py` - TowerScout module prefix for all backend components
- `model_params/` - Model weights storage (excluded from git)
- `uploads/` - Temporary user files (auto-cleaned)
- `flask_session/` - Session storage directory
- `templates/` - Jinja2 templates for web interface
- Jupyter notebooks use descriptive names ending in purpose (e.g., `_train.ipynb`, `_eval.ipynb`)

## Development Priorities

**Completed Infrastructure:**
- Security: API keys migrated to environment variables
- Error Handling: Comprehensive error handling system implemented
- Logging: Structured logging system with `ts_logging.py`
- Testing: Unit test framework with integration and mocking capabilities
- Geocoding: Enhanced address lookup and caching system

**Current Focus Areas:**
1. **User Experience**: Setup Wizard (TASK-046, Sprint 04) - Eliminate manual .env editing
2. **Documentation**: Update setup guides for non-technical users
3. **Performance**: Large dataset optimization investigation (ISSUE-003, Sprint 04)
4. **Multi-Architecture**: Support ARM64/Apple Silicon deployment
5. **Provider Management**: Enhance map provider selection and fallback capabilities

---

## 📚 Deep Dive Resources

For detailed information on specific topics, refer to these comprehensive documentation resources:

### Sprint Planning & History
- [Active Sprint Tasks](../.agent_work/current-tasks.md) - Sprint 04 objectives and task details
- [Historical Completions](../.agent_work/completed-tasks.md) - Sprint 01-03 completed work
- [Sprint 03 Retrospective](../.agent_work/context/status/SPRINT-03-RETROSPECTIVE.md) - Recent sprint learnings and metrics
- [Sprint 04 Plan](../.agent_work/context/status/SPRINT-04-PLAN.md) - Current sprint detailed planning
- [Q1 2026 Sprint Metrics](../.agent_work/context/status/SPRINT-METRICS-2026-Q1.md) - Velocity tracking and trends

### Architecture & Design
- [Developer Architecture Guide](../.agent_work/context/guides/Developer-Architecture-Guide.md) - Comprehensive architecture reference
- [Frontend Code Review](../.agent_work/context/analysis/FRONTEND-CODE-REVIEW.md) - Deep dive into JavaScript architecture
- [Global Variable Migration Patterns](../.agent_work/decisions/015-global-variable-migration-patterns.md) - ProviderStateManager migration guide
- [Provider Lock Decision](../.agent_work/decisions/014-provider-lock-after-detection.md) - Provider switching design rationale
- [Memory Leak Solution Design](../.agent_work/context/analysis/MEMORY-LEAK-SOLUTION-DESIGN.md) - TASK-041 lifecycle management patterns

### User Workflows & Testing
- [Legacy Features Guide](../.agent_work/context/guides/legacy-features.md) - Production-critical feature documentation
- [User Journey Guide](../.agent_work/context/guides/USER-JOURNEY-GUIDE.md) - 4-stage testing methodology
- [Phase 5 Integration Testing Guide](../.agent_work/context/status/PHASE-5-INTEGRATION-TESTING-GUIDE.md) - Comprehensive testing procedures
- [Phase 5 Test Results](../.agent_work/context/status/PHASE-5-TEST-RESULTS.md) - Sprint 03 validation outcomes

### Performance & Optimization
- [Performance Implementation Summary](../.agent_work/context/guides/PERFORMANCE_IMPLEMENTATION_SUMMARY.md) - Optimization strategies and benchmarks
- [Azure Maps ML Pipeline Analysis](../.agent_work/context/analysis/AZURE-MAPS-ML-PIPELINE-ANALYSIS.md) - Provider performance comparison
- [Mapping Workflow Deep Dive](../.agent_work/context/analysis/MAPPING-WORKFLOW-DEEP-DIVE.md) - Detection pipeline analysis

### Security & Deployment
- [Security-First Approach](../.agent_work/decisions/003-security-first-approach.md) - Security design principles
- [API Key Security Architecture](../.agent_work/decisions/012-api-key-security-architecture.md) - Environment variable implementation
- [Local Deployment Strategy](../.agent_work/context/guides/LOCAL_DEPLOYMENT_STRATEGY.md) - Docker containerization approach
- [Migration Guide](../.agent_work/context/guides/MIGRATION_GUIDE.md) - Security migration procedures
