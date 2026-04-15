# TowerScout Architecture Patterns

This document provides detailed architectural patterns and implementation guidelines for TowerScout's frontend and backend systems.

---

## State Management Architecture

### ProviderStateManager Pattern

**Purpose**: Centralized state management preventing race conditions and improving maintainability.

**Location**: `webapp/js/src/store.js` (exported as `providerManager`)

**Core Responsibilities**:
1. **Provider State**: Track current map provider and instances
2. **Initialization State**: Prevent race conditions during multi-provider initialization
3. **Detection State**: Mutex-protected detection array mutations
4. **Progress Timers**: Lifecycle management with automatic cleanup
5. **Deprecation Guidance**: Property descriptors with migration warnings

**Key Methods**:

```javascript
// Provider State Management
providerManager.setCurrentProvider(name)  // Set active provider
providerManager.getCurrentProvider()       // Get active provider name
providerManager.setGoogleMap(instance)     // Register Google Maps instance
providerManager.setAzureMap(instance)      // Register Azure Maps instance
providerManager.getGoogleMap()             // Retrieve Google Maps instance
providerManager.getAzureMap()              // Retrieve Azure Maps instance

// Initialization Tracking
providerManager.providerInitializing(name, phase)  // Mark phase start
providerManager.providerReady(name)                // Mark provider fully ready
providerManager.isProviderReady(name)              // Check readiness
providerManager.getProviderPhase(name)             // Get current init phase

// Detection State (Mutex-Protected)
providerManager.getDetections()            // Get detection array (read-only copy)
providerManager.clearDetections()          // Clear all detections safely
providerManager.addDetection(detection)    // Add single detection (thread-safe)
providerManager.sortDetections(compareFn)  // Sort detections (mutex-protected)

// Progress Timer Management
providerManager.startProgressTimer(timerId)   // Register progress timer
providerManager.stopProgressTimer()           // Stop and cleanup timer
providerManager.isProgressActive()            // Check if timer running

// Property Descriptors (Deprecation Warnings)
window.googleMap = ...  // Triggers warning: "Use providerManager.setGoogleMap()"
window.azureMap = ...   // Triggers warning: "Use providerManager.setAzureMap()"
Detection_detections.push(...)  // Triggers warning: "Use providerManager.addDetection()"
```

**Implementation Pattern**:

```javascript
// CORRECT: Using ProviderStateManager
function switchToAzure() {
    providerManager.setCurrentProvider('azure');
    const azureMap = providerManager.getAzureMap();
    // ... use azureMap safely
}

// INCORRECT: Direct global access (deprecated)
function switchToAzure() {
    // This triggers deprecation warning in console
    currentProvider = 'azure';  // ⚠️ Warning logged
    azureMap = ...;             // ⚠️ Warning logged
}
```

**Benefits**:
- ✅ Race condition prevention during provider initialization
- ✅ Thread-safe detection array mutations
- ✅ Automatic timer cleanup (no orphaned setInterval instances)
- ✅ Progressive migration via deprecation warnings
- ✅ Centralized state for easier debugging

**Migration Guide**:
See `.agent_work/decisions/015-global-variable-migration-patterns.md` for detailed migration patterns from global variables to ProviderStateManager.

**Sprint 03 Deprecation Warnings Cleanup**:
- Property descriptor initialization timing fixes (order of operations)
- Removed deprecation warnings from startup/initialization code
- Clean console output without triggering migration warnings during setup
- Warnings only appear for actual deprecated usage patterns

---

## Lifecycle Managers

### TimerManager

**Purpose**: Track all setTimeout/setInterval instances for proper cleanup.

**Location**: `webapp/js/src/managers/timerManager.js`

**Key Responsibilities**:
- Register timer IDs with descriptive names
- Automatic cleanup on page unload
- Prevent orphaned timers causing memory leaks
- Integration with ProviderStateManager for progress timers

**Usage Pattern**:

```javascript
// Start a timer with tracking
const timerId = setTimeout(() => {
    // Timer logic
}, 1000);
timerManager.registerTimer(timerId, 'myFeatureTimer');

// Cleanup automatically handled on page unload
// Or manual cleanup:
timerManager.clearTimer(timerId);
```

**Console Logging**:
```
⏱️ Progress timer started with TimerManager (ID: 39)
🛑 Progress timer stopped (ID: 39)
```

---

### EventListenerManager

**Purpose**: Track DOM event listeners for proper cleanup and debugging.

**Location**: `webapp/js/src/managers/eventListenerManager.js`

**Key Responsibilities**:
- Register all addEventListener calls
- Automatic removal on page unload
- Prevent memory leaks from orphaned listeners
- Debugging aid for event-related issues

**Usage Pattern**:

```javascript
// Register event listener with tracking
document.getElementById('myButton').addEventListener('click', handler);
eventListenerManager.register(document.getElementById('myButton'), 'click', handler);

// Cleanup automatically handled or manual:
eventListenerManager.removeListener(element, 'click', handler);
```

---

### TowerScoutErrorHandler

**Purpose**: Centralized error handling with user-friendly notifications.

**Location**: `webapp/js/src/managers/errorHandler.js`

**Key Responsibilities**:
- Catch unhandled errors and promise rejections
- Log detailed error context to console
- Display user-friendly error notifications
- Sanitize error messages (never expose sensitive data)

**Error Levels**:
- `error`: Critical failures requiring user attention
- `warning`: Non-critical issues with degraded functionality
- `info`: Informational messages for user guidance

**Usage Pattern**:

```javascript
try {
    // Risky operation
    await performDetection();
} catch (error) {
    TowerScoutErrorHandler.handleError(error, 'Detection failed');
    // User sees: "Detection failed. Please try again."
    // Console logs: Full error stack trace with context
}
```

---

## Boundary System Architecture

### Boundary Type Implementations

**Abstract Pattern**: Each boundary type implements:
- Drawing interaction (mouse/touch events)
- Rendering on map (provider-agnostic)
- Boundary data serialization for backend
- Cleanup and state management

**Implementations**:

#### CircleBoundary (`webapp/js/src/boundaries/circleBoundary.js`)
- **Interaction**: Click to set center, drag to set radius
- **Rendering**: Native circle shapes on both Google Maps and Azure Maps
- **Data Format**: `{ center: [lng, lat], radius: number, isCircle: true }`
- **Clearing Logic**: TASK-045 fix - clears stale circles before new detection, prevents boundary accumulation

#### PolygonBoundary (`webapp/js/src/boundaries/polygonBoundary.js`)
- **Interaction**: Click to add vertices, double-click to close
- **Rendering**: Polyline path with semi-transparent fill
- **Data Format**: `{ coordinates: [[lng, lat], ...], isCircle: false }`
- **Auto-close**: Closes polygon when last point near first point

#### RectangleBoundary (`webapp/js/src/boundaries/rectangleBoundary.js`)
- **Interaction**: Click-and-drag rectangle selection
- **Rendering**: Rectangle bounds with blue outline
- **Data Format**: `{ bounds: { north, south, east, west } }`
- **Snap-to-Square**: Optional constraint for perfect squares

**Provider Synchronization**:
All boundary operations maintain synchronization across providers:
1. User draws boundary on current provider
2. Boundary added to both `googleMap.boundaries` and `azureMap.boundaries`
3. Provider switch preserves all boundaries
4. Clearing operations affect both providers (TASK-045 fix - prevents accumulation bug)

**Sprint 03 Enhancements**:
- Context-aware drawing notifications (search boundaries vs manual towers)
- Persistent instructions during polygon drawing (no auto-dismiss)
- Provider-specific completion methods (right-click for Google, double-click for Azure)
- Automatic workflow detection based on detection state

---

## Map Provider Abstraction

### Provider Interface Pattern

**Abstract Class**: `webapp/js/src/providers/providerMap.js`

**Required Methods**:
```javascript
class ProviderMap {
    initialize()              // Setup SDK and initialize map
    setCenter(lat, lng)       // Pan to coordinates
    getCenter()               // Get current center
    setZoom(level)            // Set zoom level
    getZoom()                 // Get current zoom
    addBoundary(boundary)     // Render boundary shape
    removeBoundary(id)        // Remove boundary by ID
    clearBoundaries()         // Remove all boundaries
    addDetection(detection)   // Render detection rectangle
    removeDetection(id)       // Remove detection by ID
    clearDetections()         // Remove all detections
    fitBounds(bounds)         // Pan/zoom to fit bounds
}
```

**Implementations**:

#### GoogleMaps (`webapp/js/src/providers/googleMaps.js`)
- Uses Google Maps JavaScript API v3
- Native `google.maps.Circle`, `google.maps.Polygon` classes
- Detection rendering via `google.maps.Rectangle`
- Bidirectional highlighting via `mouseover`/`mouseout` events

#### AzureMaps (`webapp/js/src/providers/azureMaps.js`)
- Uses Azure Maps Web SDK v2
- DataSource pattern for shape management
- Detection rendering via `atlas.Shape` with styling
- **TASK-040 Fix**: Transparency and visual consistency with Google Maps
- **TASK-045 Fix**: Boundary clearing for independent detection runs

**Provider Switching**:
```javascript
// User clicks provider switch button
function switchProvider(newProvider) {
    const oldProvider = providerManager.getCurrentProvider();
    
    // Hide old provider map
    document.getElementById(`${oldProvider}Map`).style.display = 'none';
    
    // Show new provider map
    document.getElementById(`${newProvider}Map`).style.display = 'block';
    
    // Update state
    providerManager.setCurrentProvider(newProvider);
    
    // Synchronize boundaries (already in both providers)
    // No data transfer needed - boundaries maintained in both
    
    // Resize map for proper rendering
    if (newProvider === 'azure') {
        providerManager.getAzureMap().map.resize();
    }
}
```

---

## Detection System Architecture

### Detection State Flow

**1. Detection Request Initiation** (`webapp/js/src/ui/search.js`):
```javascript
async function getObjects() {
    // TASK-045: Pre-detection boundary clearing
    if (hasNewShapes()) {
        const currentMap = providerManager.getCurrentProvider() === 'google' 
            ? providerManager.getGoogleMap() 
            : providerManager.getAzureMap();
        
        currentMap.resetBoundaries();  // Clear stale boundaries
        const syncedProvider = providerManager.getCurrentProvider() === 'google' 
            ? providerManager.getAzureMap() 
            : providerManager.getGoogleMap();
        syncedProvider.resetBoundaries();  // Clear from both providers
    }
    
    // Calculate bounds from current boundaries only
    const bounds = currentMap.getBoundaryBoundsUrl();
    
    // Send detection request to backend
    const response = await fetch('/getobjects', {
        method: 'POST',
        body: JSON.stringify({ bounds, polygons, ... })
    });
}
```

**2. Backend Processing** (`webapp/towerscout.py`):
```python
@app.route('/getobjects', methods=['POST'])
def get_objects():
    # Tile generation from bounds
    tiles = map.make_tiles(bounds, crop_tiles=True)
    
    # YOLOv5 detection
    results_raw = detector.detect(tiles, exit_events, session_id)
    
    # EfficientNet classification
    results_filtered = classifier.classify(results_raw, threshold=0.5)
    
    # Geocoding
    results_with_addresses = geocoder.batch_geocode(results_filtered)
    
    return jsonify(results_with_addresses)
```

**3. Result Display** (`webapp/js/src/detection/detectionDisplay.js`):
```javascript
function displayDetections(results) {
    // Clear previous detections (mutex-protected)
    providerManager.clearDetections();
    
    // Add new detections (thread-safe)
    for (const detection of results) {
        providerManager.addDetection(detection);
        
        // Render on map
        currentMap.addDetection(detection);
    }
    
    // Sort by address (mutex-protected)
    providerManager.sortDetections((a, b) => 
        a.address.localeCompare(b.address)
    );
    
    // Update results list UI
    updateDetectionList();
}
```

**4. Confidence Filtering** (`webapp/js/src/detection/confidence.js`):
```javascript
function updateConfidenceThreshold(newThreshold) {
    const detections = providerManager.getDetections();
    
    for (const detection of detections) {
        const shouldShow = detection.confidence >= newThreshold;
        
        // Update visibility on map
        currentMap.setDetectionVisibility(detection.id, shouldShow);
        
        // Update visibility in results list
        updateListItemVisibility(detection.id, shouldShow);
    }
}
```

---

## Build System Architecture

### Concatenation-Based Build

**Purpose**: Simple, fast, dependency-free build process for modular JavaScript.

**Build Script**: `webapp/build.js`

**Process**:
1. Read all source files from `webapp/js/src/` in dependency order
2. Wrap each file in IIFE for scope isolation
3. Concatenate in correct order
4. Write to `webapp/js/towerscout.js`
5. Log bundle size and module count

**Dependency Order**:
```javascript
const sourceFiles = [
    'src/config.js',           // Configuration constants
    'src/store.js',            // ProviderStateManager
    'src/globals.js',          // Global utilities
    'src/managers/*.js',       // Lifecycle managers
    'src/boundaries/*.js',     // Boundary implementations
    'src/providers/*.js',      // Map providers
    'src/detection/*.js',      // Detection modules
    'src/ui/*.js',             // UI modules
    'src/utils/*.js',          // Utilities
    'src/towerscout.js'        // Main initialization (last)
];
```

**Pre-commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
# Automatically rebuild bundle when source files change

# Check if any src files staged
if git diff --cached --name-only | grep 'webapp/js/src/'; then
    cd webapp
    node build.js
    git add js/towerscout.js
fi
```

**Benefits**:
- ✅ No webpack/rollup dependencies
- ✅ Fast build times (< 2 seconds)
- ✅ Simple debugging (source maps not needed, clear IIFE boundaries)
- ✅ Automatic via pre-commit hooks
- ✅ Backward compatible with inline HTML handlers

---

## Memory Management Patterns

### TASK-041 Memory Management Achievements

**Stress Test Results** (20-cycle detection workflow):
- **Before**: 28.6 MB baseline memory
- **After**: 28.4 MB final memory
- **Change**: -0.7% (memory DECREASED!)

**Key Patterns**:

#### 1. Clear-and-Rebuild Pattern
```javascript
// CORRECT: Clear all shapes, rebuild from fresh data
function updateBoundaries(newBoundaries) {
    // Clear all existing shapes
    currentMap.clearBoundaries();
    
    // Rebuild from authoritative data source
    for (const boundary of newBoundaries) {
        currentMap.addBoundary(boundary);
    }
}

// INCORRECT: Incremental additions without clearing
function updateBoundaries(newBoundaries) {
    // Old boundaries remain, causing accumulation
    for (const boundary of newBoundaries) {
        currentMap.addBoundary(boundary);  // ❌ Accumulates
    }
}
```

#### 2. Property-Based Filtering
```javascript
// CORRECT: Identify shapes by properties, not references
function clearCircles() {
    const allShapes = dataSource.getShapes();
    const circleShapes = allShapes.filter(shape => 
        shape.getProperties().isCircle === true
    );
    dataSource.remove(circleShapes);
}

// INCORRECT: Reference tracking (unreliable)
let circleReferences = [];  // Can become stale
```

#### 3. Lifecycle Cleanup
```javascript
// Automatic cleanup on page unload
window.addEventListener('beforeunload', () => {
    timerManager.clearAll();
    eventListenerManager.removeAll();
    providerManager.clearDetections();
    // ... other cleanup
});
```

---

## Testing Patterns

### Manual Testing Methodology (TASK-042)

**4-Stage User Journey Validation**:

#### Stage 0: Initialization
```javascript
// Validation Steps:
1. Open browser console (F12)
2. Verify: "✅ TowerScout initialized successfully"
3. Check: No JavaScript errors
4. Confirm: Both providers available in UI
5. Test: Provider switching works (map updates, no errors)
```

#### Stage 1: Location Search
```javascript
// Test Cases:
1. Address search: "New York City Hall"
   - Verify: Map pans to location
   - Verify: Geocoding result displays

2. Zipcode search: "10007" (with quotes)
   - Verify: Boundary polygon appears
   - Verify: Tile estimation displays

3. Manual polygon drawing:
   - Verify: Vertices render correctly
   - Verify: Double-click closes polygon
   - Verify: Clear button removes polygon
```

#### Stage 2: Detection Execution
```javascript
// Test Workflow:
1. Draw boundary (circle or polygon)
2. Click "Get Detections" button
3. Verify: Progress indicator appears
4. Verify: Tile estimation matches actual count
5. Monitor: Console logs show processing
6. Verify: Detections appear on map after completion
7. Test: Cancel button stops detection mid-process
```

#### Stage 3: Result Review
```javascript
// Verification Points:
1. Detections display on map with addresses
2. Right panel shows detection list
3. Click list item → map marker highlights
4. Click map marker → list item scrolls into view
5. Confidence slider filters detections dynamically
6. Checkbox unselects false positives
7. Export buttons create CSV/KML files correctly
```

**Console Logging Validation**:
- Zero JavaScript errors throughout workflow
- State transitions logged clearly
- Deprecation warnings guide migration (~150+ instances expected)
- Boundary clearing logs visible (TASK-045 fix)

**Performance Benchmarks**:
- Monitor network tab for API request timing
- Check memory tab for leak detection
- Verify responsive UI during detection processing

---

## Security Patterns

### API Key Management

**CORRECT Pattern**:
```python
# Backend: Load from environment variables
import os

google_key = os.getenv('GOOGLE_API_KEY')
azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')

if not google_key:
    raise ConfigurationError("Google API key not configured")
```

**Configuration**:
```bash
# .env file (never committed to git)
GOOGLE_API_KEY=your_key_here
AZURE_MAPS_SUBSCRIPTION_KEY=your_key_here
DEFAULT_MAP_PROVIDER=azure
```

**Frontend**:
```javascript
// API keys NEVER exposed to frontend
// Backend proxy pattern for all map API calls
const response = await fetch('/api/maps/tile', {
    method: 'POST',
    body: JSON.stringify({ tileCoords })
});
// Backend adds API key to third-party requests
```

### Input Validation

**Pattern**: Validate all user inputs before processing

```python
# Backend validation (ts_validation.py)
from webapp.ts_validation import validate_detection_request

@app.route('/getobjects', methods=['POST'])
def get_objects():
    data = request.get_json()
    
    # Comprehensive validation
    validated = validate_detection_request(data)
    
    # Sanitized data safe to process
    tiles = map.make_tiles(validated['bounds'])
```

---

## Common Patterns Reference

### Async/Await Error Handling
```javascript
async function performAsyncOperation() {
    try {
        const result = await fetch('/api/endpoint');
        const data = await result.json();
        return data;
    } catch (error) {
        TowerScoutErrorHandler.handleError(error, 'Operation failed');
        throw error;  // Re-throw for caller to handle
    }
}
```

### Mutex-Protected State Mutations
```javascript
class MutexStore {
    constructor() {
        this.data = [];
        this.mutex = Promise.resolve();
    }
    
    async modify(callback) {
        this.mutex = this.mutex.then(async () => {
            await callback(this.data);
        });
        await this.mutex;
    }
}
```

### Provider-Agnostic Operations
```javascript
function getCurrentMapInstance() {
    const provider = providerManager.getCurrentProvider();
    return provider === 'google' 
        ? providerManager.getGoogleMap() 
        : providerManager.getAzureMap();
}

// Use in code:
const map = getCurrentMapInstance();
map.setCenter(lat, lng);  // Works for both providers
```

---

## Google Maps API Migration Patterns (Sprint 03 - TASK-039)

### PlaceAutocompleteElement Web Component Pattern

**Purpose**: Replace deprecated SearchBox with modern Web Component.

**Implementation** (`webapp/js/src/providers/googleMaps.js`):
```javascript
// Single global instance (prevents duplicate Web Components)
let globalPlaceAutocomplete = null;

function initializePlaceAutocomplete() {
    if (globalPlaceAutocomplete) {
        return globalPlaceAutocomplete;  // Reuse existing instance
    }
    
    // Create Web Component
    const autocompleteElement = document.createElement('gmp-place-autocomplete');
    autocompleteElement.id = 'place-autocomplete';
    
    // Automatic bounds biasing based on current map viewport
    const map = providerManager.getGoogleMap().map;
    autocompleteElement.addEventListener('gmp-placeselect', async (event) => {
        const place = event.place;
        if (place.geometry) {
            map.fitBounds(place.geometry.viewport);
        }
    });
    
    globalPlaceAutocomplete = autocompleteElement;
    return autocompleteElement;
}
```

**Benefits**:
- Single instance prevents Web Component registration conflicts
- Automatic bounds biasing improves search relevance
- Seamless provider switching without re-initialization
- Future-proof against SearchBox deprecation (April 2026)

### Custom Polygon Drawing Pattern

**Purpose**: Replace deprecated DrawingManager with custom implementation.

**User Interaction**:
- **Left-click**: Add polygon vertex with visual marker
- **Right-click outside polygon**: Complete and close polygon (alternative to double-click)
- **Visual preview**: Live polyline preview while drawing
- **Editable**: Completed polygons are editable and draggable
- **Purple styling**: Matches manual tower identification workflow (#800080)

**Implementation Pattern**:
```javascript
class CustomPolygonDrawing {
    constructor(map) {
        this.map = map;
        this.vertices = [];
        this.markers = [];
        this.tempPolyline = null;
        this.isDrawing = false;
        
        // Context-aware notifications (Sprint 03 UX enhancement)
        this.showPersistentNotification();  // No auto-dismiss during drawing
    }
    
    handleLeftClick(latLng) {
        this.vertices.push(latLng);
        this.addMarker(latLng);
        this.updatePreviewPolyline();
    }
    
    handleRightClick(latLng) {
        if (!this.isPointInsidePolygon(latLng, this.vertices)) {
            this.completePolygon();  // Only close if outside
        }
    }
    
    completePolygon() {
        const polygon = new google.maps.Polygon({
            paths: this.vertices,
            strokeColor: '#800080',
            fillColor: '#800080',
            editable: true,
            draggable: true
        });
        
        this.cleanup();  // Remove markers and preview
        this.showCompletionMessage();  // Context-aware completion notification
    }
}
```

**Migration Benefits**:
- Avoids DrawingManager deprecation (12+ months notice from Google)
- Custom right-click completion improves UX
- Full control over styling and behavior
- Provider-specific interaction patterns

---

## Related Documentation

- [towerscout-domain.md](./towerscout-domain.md) - Project overview and architecture
- [dev-workflow.md](./dev-workflow.md) - Development setup and workflows
- [security.md](./security.md) - Security practices and guidelines
- [spec-driven-workflow.md](./spec-driven-workflow.md) - Task management and workflows

---

## 📚 Architecture Deep Dive Resources

### State Management & Patterns
- [Global Variable Migration Patterns](../.agent_work/decisions/015-global-variable-migration-patterns.md) - ProviderStateManager migration guide  - Comprehensive examples for converting legacy globals to managed state
- [Provider Lock Decision](../.agent_work/decisions/014-provider-lock-after-detection.md) - Provider switching design rationale and constraints
- [Memory Leak Solution Design](../.agent_work/context/analysis/MEMORY-LEAK-SOLUTION-DESIGN.md) - TASK-041 lifecycle management patterns and stress test results

### Provider Integration
- [Azure Maps Migration](../.agent_work/decisions/006-azure-maps-migration.md) - Azure Maps integration architecture
- [Provider Independence Reality](../.agent_work/context/analysis/PROVIDER-INDEPENDENCE-REALITY.md) - Multi-provider design trade-offs
- [Azure Maps ML Pipeline Analysis](../.agent_work/context/analysis/AZURE-MAPS-ML-PIPELINE-ANALYSIS.md) - Provider performance comparison

### Frontend Architecture
- [Developer Architecture Guide](../.agent_work/context/guides/Developer-Architecture-Guide.md) - Comprehensive frontend architecture reference
- [Frontend Code Review](../.agent_work/context/analysis/FRONTEND-CODE-REVIEW.md) - Deep dive into JavaScript architecture and refactoring
- [Mapping Workflow Deep Dive](../.agent_work/context/analysis/MAPPING-WORKFLOW-DEEP-DIVE.md) - Detection pipeline and data flow analysis

### Error Handling & Infrastructure
- [Error Handling Infrastructure](../.agent_work/decisions/009-error-handling-infrastructure.md) - Error handling patterns and TowerScoutErrorHandler design
- [Input Validation Architecture](../.agent_work/decisions/004-input-validation-architecture.md) - Validation strategy and sanitization patterns

### Task Documentation & Implementation Examples
- Task files in `.agent_work/tasks/completed/` provide real-world implementation examples:
  - `TASK-038-frontend-refactoring.md` - Frontend modularization execution
  - `TASK-041-memory-management.md` - State management improvements
  - `TASK-043-global-variable-deprecation.md` - Global variable migration process
  - `TASK-045-boundary-accumulation-bug.md` - Boundary clearing fix implementation
  - `TASK-039-google-maps-api-migration.md` - API migration with modern Web Components
