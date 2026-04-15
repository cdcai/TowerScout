# TowerScout Developer Architecture Guide

**Version**: 1.0 (March 2026)  
**Audience**: Developers contributing to TowerScout  
**Scope**: Frontend architecture, state management, build system, and testing procedures

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Frontend Module Structure](#frontend-module-structure)
3. [State Management with ProviderStateManager](#state-management-with-providerstatemanager)
4. [Build System](#build-system)
5. [Testing Procedures](#testing-procedures)
6. [Migration Patterns](#migration-patterns)
7. [Contributing Guidelines](#contributing-guidelines)

---

## Architecture Overview

### Current Architecture (Sprint 02 - March 2026)

TowerScout follows a **modular, event-driven architecture** with centralized state management:

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (User Interface)                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend JavaScript (27 Modular Files)                      │
│  ├─ State Management (ProviderStateManager)                 │
│  ├─ Lifecycle Managers (Timer, Event, Error)                │
│  ├─ Map Providers (Google Maps, Azure Maps)                 │
│  ├─ Boundaries (Circle, Polygon, Rectangle)                 │
│  ├─ Detection Display & Confidence Filtering                │
│  └─ UI Modules (Search, Controls, Results)                  │
├─────────────────────────────────────────────────────────────┤
│  Flask Backend (Python)                                      │
│  ├─ Route Handlers (towerscout.py)                          │
│  ├─ Map Providers (ts_maps.py, ts_gmaps.py, ts_azure_maps.py)│
│  ├─ ML Models (ts_yolov5.py, ts_en.py)                     │
│  ├─ Geocoding & Caching (ts_geocoding.py, ts_geocache.py)  │
│  ├─ Error Handling (ts_errors.py)                           │
│  ├─ Logging (ts_logging.py)                                 │
│  └─ Validation (ts_validation.py)                           │
├─────────────────────────────────────────────────────────────┤
│  External Services                                           │
│  ├─ Google Maps API (satellite imagery, geocoding)          │
│  ├─ Azure Maps API (satellite imagery, geocoding)           │
│  ├─ YOLOv5 Model (cooling tower detection)                  │
│  └─ EfficientNet Model (secondary classification)           │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Principles

1. **Modular Frontend**: 5,272-line monolith refactored into 27 focused modules
2. **Centralized State**: ProviderStateManager prevents race conditions and improves testability
3. **Provider Abstraction**: Map provider interface enables multi-provider support
4. **Lifecycle Management**: Automatic cleanup of timers, event listeners, and resources
5. **Progressive Migration**: Deprecation warnings guide migration from legacy patterns

---

## Frontend Module Structure

### Directory Organization

```
webapp/js/
├── src/                          # Source modules (27 files)
│   ├── config.js                 # Configuration constants
│   ├── store.js                  # ProviderStateManager (state management)
│   ├── globals.js                # Global utilities
│   ├── managers/                 # Lifecycle managers (4 files)
│   │   ├── timerManager.js       # Timer tracking and cleanup
│   │   ├── eventListenerManager.js  # Event listener tracking
│   │   ├── errorHandler.js       # Centralized error handling
│   │   └── modalManager.js       # Modal dialog management
│   ├── boundaries/               # Boundary implementations (3 files)
│   │   ├── circleBoundary.js     # Circle drawing and rendering
│   │   ├── polygonBoundary.js    # Polygon drawing and rendering
│   │   └── rectangleBoundary.js  # Rectangle drawing and rendering
│   ├── providers/                # Map provider abstractions (3 files)
│   │   ├── providerMap.js        # Abstract base class
│   │   ├── googleMaps.js         # Google Maps implementation
│   │   └── azureMaps.js          # Azure Maps implementation
│   ├── detection/                # Detection display modules (3 files)
│   │   ├── detectionDisplay.js   # Detection rendering and management
│   │   ├── confidence.js         # Confidence threshold filtering
│   │   └── highlighting.js       # Bidirectional marker ↔ list highlighting
│   ├── ui/                       # UI interaction modules (5 files)
│   │   ├── search.js             # Location search and detection trigger
│   │   ├── controls.js           # Map controls (zoom, pan, clear)
│   │   ├── results.js            # Results list display and interaction
│   │   ├── export.js             # Export functionality (CSV, KML)
│   │   └── progress.js           # Progress indicators and cancellation
│   ├── utils/                    # Utility functions (2 files)
│   │   ├── coordinates.js        # Coordinate transformations
│   │   └── validation.js         # Client-side validation helpers
│   └── towerscout.js             # Main initialization (loaded last)
├── towerscout.js                 # Generated bundle (319.0 KB)
└── jquery-3.5.1.min.js          # jQuery dependency
```

### Module Loading Order

**Critical**: Modules must be loaded in dependency order:

1. **config.js** - Constants used by other modules
2. **store.js** - ProviderStateManager (state management)
3. **globals.js** - Global utilities
4. **managers/** - Lifecycle managers (timer, event, error)
5. **boundaries/** - Boundary implementations
6. **providers/** - Map provider abstractions
7. **detection/** - Detection display modules
8. **ui/** - UI interaction modules
9. **utils/** - Utility functions
10. **towerscout.js** - Main initialization (last)

**IIFE Pattern**: Each module wrapped in Immediately Invoked Function Expression:

```javascript
// Example module structure
(function() {
    'use strict';
    
    // Module-scoped variables
    let privateVar = 'not accessible outside';
    
    // Expose to global scope only what's needed
    window.MyModule = {
        publicFunction: function() {
            // Implementation
        }
    };
})();
```

---

## State Management with ProviderStateManager

### Purpose and Design

**ProviderStateManager** (in `webapp/js/src/store.js`) is the centralized state management system that prevents race conditions and improves maintainability.

**Core Responsibilities**:
1. Track current map provider and instances
2. Prevent race conditions during asynchronous initialization
3. Protect detection array from concurrent mutations
4. Manage progress timer lifecycle
5. Provide deprecation guidance for legacy patterns

### Key API Methods

#### Provider State Management

```javascript
// Set the current active provider
providerManager.setCurrentProvider('azure');  // or 'google'

// Get the current provider name
const provider = providerManager.getCurrentProvider();  // Returns: 'azure' or 'google'

// Register provider instances
providerManager.setGoogleMap(googleMapInstance);
providerManager.setAzureMap(azureMapInstance);

// Retrieve provider instances
const googleMap = providerManager.getGoogleMap();
const azureMap = providerManager.getAzureMap();
```

#### Initialization Tracking

```javascript
// Mark provider initialization phases
providerManager.providerInitializing('azure', 'loading_sdk');
providerManager.providerInitializing('azure', 'creating_map');
providerManager.providerReady('azure');

// Check initialization status
const isReady = providerManager.isProviderReady('azure');
const phase = providerManager.getProviderPhase('azure');
```

**Initialization Phases**:
- `loading_sdk` - Loading provider JavaScript SDK
- `creating_map` - Creating map instance
- `ready` - Fully initialized and usable

#### Detection State (Mutex-Protected)

```javascript
// Get detections (returns read-only copy)
const detections = providerManager.getDetections();

// Clear all detections (thread-safe)
providerManager.clearDetections();

// Add single detection (mutex-protected)
providerManager.addDetection({
    id: 'detection_123',
    lat: 40.7128,
    lng: -74.0060,
    confidence: 0.95,
    address: '123 Main St, New York, NY'
});

// Sort detections (mutex-protected)
providerManager.sortDetections((a, b) => 
    a.address.localeCompare(b.address)
);
```

**Mutex Pattern**: All detection mutations use async/await mutex to prevent race conditions:

```javascript
// Internal implementation (simplified)
class ProviderStateManager {
    constructor() {
        this._detections = [];
        this._detectionsMutex = Promise.resolve();
    }
    
    async addDetection(detection) {
        this._detectionsMutex = this._detectionsMutex.then(async () => {
            this._detections.push(detection);
        });
        await this._detectionsMutex;
    }
}
```

#### Progress Timer Management

```javascript
// Start progress timer
const timerId = setTimeout(() => {
    // Update progress
}, 1000);
providerManager.startProgressTimer(timerId);

// Stop progress timer (automatic cleanup)
providerManager.stopProgressTimer();

// Check if progress active
if (providerManager.isProgressActive()) {
    // Progress in progress
}
```

### Property Descriptors (Deprecation System)

**Purpose**: Guide migration from legacy global variables to ProviderStateManager API.

**Implementation**:

```javascript
// Property descriptors with migration warnings
Object.defineProperty(window, 'googleMap', {
    get: function() {
        console.warn('[DEPRECATED] Direct access to window.googleMap is deprecated. Use providerManager.getGoogleMap() instead.');
        return providerManager.getGoogleMap();
    },
    set: function(value) {
        console.warn('[DEPRECATED] Direct assignment to window.googleMap is deprecated. Use providerManager.setGoogleMap(value) instead.');
        providerManager.setGoogleMap(value);
    }
});
```

**Expected Warnings**: ~150+ deprecation warnings during typical session as legacy code gradually migrates.

### Usage Examples

#### Provider Switching

```javascript
function switchToAzureProvider() {
    // Check initialization status
    if (!providerManager.isProviderReady('azure')) {
        console.warn('Azure Maps not ready yet');
        return;
    }
    
    // Hide current provider
    const currentProvider = providerManager.getCurrentProvider();
    document.getElementById(`${currentProvider}Map`).style.display = 'none';
    
    // Show Azure Maps
    document.getElementById('azureMap').style.display = 'block';
    providerManager.setCurrentProvider('azure');
    
    // Resize map for proper rendering
    const azureMap = providerManager.getAzureMap();
    azureMap.map.resize();
}
```

#### Detection Display

```javascript
async function displayDetectionResults(results) {
    // Clear previous detections (mutex-protected)
    providerManager.clearDetections();
    
    // Get current provider instance
    const provider = providerManager.getCurrentProvider();
    const mapInstance = provider === 'google' 
        ? providerManager.getGoogleMap() 
        : providerManager.getAzureMap();
    
    // Add new detections (thread-safe)
    for (const detection of results) {
        providerManager.addDetection(detection);
        mapInstance.addDetection(detection);
    }
    
    // Sort detections by address (mutex-protected)
    providerManager.sortDetections((a, b) => 
        a.address.localeCompare(b.address)
    );
    
    // Update UI
    updateDetectionList();
}
```

---

## Build System

### Concatenation-Based Build

**Purpose**: Simple, fast, dependency-free build process for modular JavaScript.

**Build Script**: `webapp/build.js`

```javascript
const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'js', 'src');
const outputFile = path.join(__dirname, 'js', 'towerscout.js');

// Define source files in dependency order
const sourceFiles = [
    'config.js',
    'store.js',
    'globals.js',
    'managers/timerManager.js',
    'managers/eventListenerManager.js',
    'managers/errorHandler.js',
    'managers/modalManager.js',
    'boundaries/circleBoundary.js',
    'boundaries/polygonBoundary.js',
    'boundaries/rectangleBoundary.js',
    'providers/providerMap.js',
    'providers/googleMaps.js',
    'providers/azureMaps.js',
    'detection/detectionDisplay.js',
    'detection/confidence.js',
    'detection/highlighting.js',
    'ui/search.js',
    'ui/controls.js',
    'ui/results.js',
    'ui/export.js',
    'ui/progress.js',
    'utils/coordinates.js',
    'utils/validation.js',
    'towerscout.js'  // Main initialization (last)
];

// Read and concatenate files
let bundle = '';
for (const file of sourceFiles) {
    const content = fs.readFileSync(path.join(srcDir, file), 'utf8');
    bundle += `\n// ===== ${file} =====\n${content}\n`;
}

// Write bundle
fs.writeFileSync(outputFile, bundle);

// Log statistics
const sizeKB = (fs.statSync(outputFile).size / 1024).toFixed(1);
console.log(`✅ Build complete: ${sourceFiles.length} modules → ${sizeKB} KB`);
```

### Build Commands

```bash
# Manual build
cd webapp
node build.js

# Expected output:
# ✅ Build complete: 27 modules → 319.0 KB

# Verify build
ls -lh js/towerscout.js
```

### Pre-commit Hook

**Location**: `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Automatically rebuild bundle when source files change

# Check if any src files staged
if git diff --cached --name-only | grep 'webapp/js/src/'; then
    echo "🔨 Rebuilding frontend bundle..."
    cd webapp
    node build.js
    
    if [ $? -eq 0 ]; then
        git add js/towerscout.js
        echo "✅ Bundle rebuilt and staged"
    else
        echo "❌ Build failed - commit aborted"
        exit 1
    fi
fi
```

**Setup**:

```bash
# Make hook executable
chmod +x .git/hooks/pre-commit
```

### Build Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Build Time | <2 seconds | Concatenation-based, no complex transforms |
| Bundle Size | 319.0 KB | Unminified, human-readable |
| Source Files | 27 modules | Across 7 directories |
| Dependencies | Node.js | No webpack, rollup, or babel |

---

## Testing Procedures

### Manual Testing Methodology (4-Stage User Journey)

Established in TASK-042, validated to achieve zero JavaScript errors throughout workflow.

#### Stage 0: Initialization

**Objective**: Verify TowerScout initializes correctly with both providers.

**Steps**:
1. Open browser (Chrome recommended)
2. Navigate to http://127.0.0.1:5000
3. Open browser console (F12)
4. Verify initialization message: `"✅ TowerScout initialized successfully"`
5. Check for JavaScript errors (should be zero)
6. Verify both provider buttons visible: "Google Maps" and "Azure Maps"

**Success Criteria**:
- ✅ Console shows initialization success
- ✅ Zero JavaScript errors
- ✅ Both providers available
- ✅ Map displays with proper controls

#### Stage 1: Location Search

**Objective**: Verify search functionality and boundary creation.

**Test Cases**:

1. **Address Search**:
   ```
   Search: "New York City Hall"
   Expected: Map pans to location, geocoding result displays
   ```

2. **Zipcode Search**:
   ```
   Search: "10007" (with quotes)
   Expected: Zipcode boundary polygon appears, tile estimation displays
   ```

3. **Manual Polygon Drawing**:
   ```
   Action: Click polygon tool, add vertices, double-click to close
   Expected: Polygon renders correctly, clear button removes polygon
   ```

**Success Criteria**:
- ✅ Address geocoding works
- ✅ Zipcode boundaries display
- ✅ Manual polygon drawing functional
- ✅ Clear button removes boundaries

#### Stage 2: Detection Execution

**Objective**: Verify detection workflow and progress tracking.

**Steps**:
1. Draw boundary (circle or polygon)
2. Click "Get Detections" button
3. Observe progress indicator
4. Verify tile estimation matches actual count
5. Monitor console logs for processing updates
6. Wait for detection completion
7. Test cancel button (optional)

**Console Logging Validation**:
```
[Detection] Starting detection for 24 tiles
[Detection] Tile 1/24 complete
[Detection] Tile 2/24 complete
...
[Detection] Detection complete: 158 results
[Geocoding] Geocoding 158 detections
[Geocoding] Geocoding complete: 158 addresses
```

**Success Criteria**:
- ✅ Progress indicator appears
- ✅ Tile count accurate
- ✅ Console logs show processing
- ✅ Detections appear on map
- ✅ Cancel button stops processing

**Performance Expectations**:
- 24 tiles: ~70 seconds (~158 detections)
- 57 tiles: ~160 seconds (~430 detections)
- <100 tiles: ~30 seconds (mission-critical target)

#### Stage 3: Result Review

**Objective**: Verify results display and interaction features.

**Test Cases**:

1. **Detection Display**:
   ```
   Expected: Detections render on map with addresses in right panel
   ```

2. **Interactive Highlighting**:
   ```
   Action: Click detection in list
   Expected: Map marker highlights, map pans to location
   
   Action: Click map marker
   Expected: List item highlights, list scrolls to item
   ```

3. **Confidence Filtering**:
   ```
   Action: Move confidence slider
   Expected: Detections filter dynamically, map updates in real-time
   ```

4. **False Positive Deselection**:
   ```
   Action: Uncheck detection checkbox
   Expected: Detection marked as false positive, excluded from export
   ```

5. **Export Functionality**:
   ```
   Action: Click "Export CSV" button
   Expected: CSV file downloads with detection data
   
   Action: Click "Export KML" button
   Expected: KML file downloads for Google Earth
   ```

**Success Criteria**:
- ✅ Detections display on map with addresses
- ✅ Bidirectional highlighting works (marker ↔ list)
- ✅ Confidence slider filters dynamically
- ✅ Checkbox deselection functional
- ✅ Export buttons create correct files

### Automated Testing

**Unit Tests** (`tests/unit/`):
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_validation.py -v

# Run with coverage
pytest tests/unit/ --cov=webapp --cov-report=html
```

**Integration Tests** (`tests/integration/`):
```bash
# Run integration tests (require API keys)
pytest tests/integration/ -v

# Skip Azure Maps tests if no key
pytest tests/integration/ -v -k "not azure"
```

**Frontend Tests** (`tests/frontend/`):
```bash
# Open test harness in browser
open tests/frontend/test_stage_0_manual.html

# Run console validation
# Execute tests/frontend/test_stage_0_console.js in browser console
```

### Memory Leak Testing (20-Cycle Stress Test)

**Procedure**:
1. Open browser console and navigate to Memory tab
2. Take initial heap snapshot (baseline)
3. Execute detection workflow (search → detect → clear results)
4. Repeat 20 times
5. Take final heap snapshot
6. Compare memory usage

**Validated Results** (TASK-041):
- Baseline: 28.6 MB
- After 20 cycles: 28.4 MB
- Change: -0.7% (memory DECREASED!)

**Expected Behavior**:
- Memory should remain stable or decrease slightly
- No continuous upward trend (indicates leaks)
- Sawtooth pattern acceptable (garbage collection)

---

## Migration Patterns

### From Global Variables to ProviderStateManager

**Decision Record**: `.agent_work/decisions/015-global-variable-migration-patterns.md`

#### Pattern 1: Provider Instance Access

**Before** (Deprecated):
```javascript
// Direct global access
const map = currentProvider === 'google' ? googleMap : azureMap;
```

**After** (Recommended):
```javascript
// ProviderStateManager API
const provider = providerManager.getCurrentProvider();
const map = provider === 'google' 
    ? providerManager.getGoogleMap() 
    : providerManager.getAzureMap();
```

#### Pattern 2: Detection Array Mutations

**Before** (Deprecated):
```javascript
// Direct array mutation (not thread-safe)
Detection_detections.push(newDetection);
```

**After** (Recommended):
```javascript
// Mutex-protected mutation
providerManager.addDetection(newDetection);
```

#### Pattern 3: Provider Switching

**Before** (Deprecated):
```javascript
// Direct state mutation
currentProvider = 'azure';
azureMap = initializeAzureMap();
```

**After** (Recommended):
```javascript
// Centralized state management
providerManager.providerInitializing('azure', 'loading_sdk');
const azureMap = await initializeAzureMap();
providerManager.setAzureMap(azureMap);
providerManager.providerReady('azure');
providerManager.setCurrentProvider('azure');
```

#### Pattern 4: Progress Timer Management

**Before** (Deprecated):
```javascript
// Manual timer tracking (prone to orphaned timers)
let progressTimer = setInterval(() => {
    updateProgress();
}, 1000);

// Cleanup often missed in error cases
clearInterval(progressTimer);
```

**After** (Recommended):
```javascript
// Automatic lifecycle management
const timerId = setInterval(() => {
    updateProgress();
}, 1000);
providerManager.startProgressTimer(timerId);

// Cleanup handled automatically
providerManager.stopProgressTimer();
```

### Clear-and-Rebuild Pattern (TASK-045)

**Problem**: Stale boundaries accumulate across detection runs.

**Anti-pattern**:
```javascript
// Incremental additions without clearing
function addBoundaries(newBoundaries) {
    for (const boundary of newBoundaries) {
        map.addBoundary(boundary);  // Accumulates!
    }
}
```

**Solution**:
```javascript
// Clear-and-rebuild pattern
function updateBoundaries(newBoundaries) {
    // Step 1: Clear all existing shapes
    map.clearBoundaries();
    
    // Step 2: Rebuild from authoritative data source
    for (const boundary of newBoundaries) {
        map.addBoundary(boundary);
    }
}
```

**Application in Detection Workflow**:
```javascript
async function getObjects() {
    // TASK-045: Pre-detection boundary clearing
    if (hasNewShapes()) {
        const currentMap = getCurrentMapInstance();
        currentMap.resetBoundaries();  // Clear stale boundaries
        
        // Synchronize to other provider
        const otherProvider = providerManager.getCurrentProvider() === 'google' 
            ? providerManager.getAzureMap() 
            : providerManager.getGoogleMap();
        otherProvider.resetBoundaries();
    }
    
    // Calculate bounds only from current boundaries
    const bounds = currentMap.getBoundaryBoundsUrl();
    
    // Send detection request
    const response = await fetch('/getobjects', {
        method: 'POST',
        body: JSON.stringify({ bounds, ... })
    });
}
```

---

## Contributing Guidelines

### Code Style

**JavaScript**:
- 4-space indentation
- Single quotes for strings
- Semicolons required
- Descriptive variable names
- Use `const` and `let`, never `var`

**Example**:
```javascript
function calculateTileBounds(lat, lng, zoom) {
    const tileSize = 256;
    const worldSize = tileSize * Math.pow(2, zoom);
    
    // Calculate tile coordinates
    const tileX = Math.floor((lng + 180) / 360 * worldSize / tileSize);
    const tileY = Math.floor((1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * worldSize / tileSize);
    
    return { x: tileX, y: tileY, zoom: zoom };
}
```

**Python**:
- PEP 8 compliance
- Type hints where appropriate
- Docstrings for public functions
- Black formatting (88 character line length)

### Git Workflow

**Branch Naming**:
- `feature/ui-improvement-<description>` - UI/UX enhancements
- `fix/bug-<description>` - Bug fixes
- `refactor/code-quality-<component>` - Code improvements
- `docs/update-<section>` - Documentation updates

**Commit Messages**:
```
<type>(<scope>): <description>

[optional body explaining what and why]

[optional footer with issue references]
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `security`

**Example Commits**:
```
feat(ui): add progress indicator for detection processing

Implements real-time progress tracking with cancellation capability.
Referenced in TASK-042 testing validation.

Refs: TASK-042
```

```
fix(boundaries): prevent boundary accumulation in independent detection runs

Implements clear-and-rebuild pattern to remove stale boundaries
before each detection run. Validated with 3 consecutive independent tests.

Fixes: TASK-045
```

### Pull Request Process

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/my-enhancement
   ```

2. **Make Changes**:
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**:
   ```bash
   # Run unit tests
   pytest tests/unit/ -v
   
   # Run frontend build
   cd webapp && node build.js
   
   # Manual 4-stage validation
   python towerscout.py dev
   # Execute manual testing procedure
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat(detection): add new feature"
   ```

5. **Push and Create PR**:
   ```bash
   git push origin feature/my-enhancement
   ```

6. **PR Description** (Template):
   ```markdown
   ## Summary
   [Brief description of changes]
   
   ## Changes Made
   - [Change 1]
   - [Change 2]
   
   ## Testing
   - [x] Unit tests pass
   - [x] 4-stage manual validation complete
   - [x] Zero JavaScript errors
   - [x] Memory leak test passed
   
   ## Screenshots (if UI changes)
   [Add screenshots]
   
   ## Related Issues
   Refs: TASK-XXX
   ```

### Testing Requirements

**For All Changes**:
- [ ] Unit tests pass: `pytest tests/unit/ -v`
- [ ] Code formatted: `black webapp/`
- [ ] Linting passes: `flake8 webapp/`
- [ ] Frontend builds: `node build.js`

**For Backend Changes**:
- [ ] Integration tests pass: `pytest tests/integration/ -v`
- [ ] Type hints added where appropriate
- [ ] Docstrings added for public functions

**For Frontend Changes**:
- [ ] 4-stage manual validation complete
- [ ] Zero JavaScript errors in console
- [ ] Cross-provider testing (Google Maps and Azure Maps)
- [ ] Memory leak test passed (if state management changes)

**For State Management Changes**:
- [ ] 20-cycle stress test passed
- [ ] No memory leaks detected
- [ ] Mutex protection verified for concurrent operations
- [ ] Deprecation warnings guide migration appropriately

### Documentation Requirements

**Update When**:
- Adding new features → Update AGENTS.md/towerscout-domain.md
- Changing architecture → Update AGENTS.md/architecture.md
- Modifying state management → Update this guide
- Adding API endpoints → Update AGENTS.md/dev-workflow.md
- Resolving issues → Update .agent_work/context/guides/TowerScout_Development_Setup_Guide.txt troubleshooting

---

## Additional Resources

### Documentation

- **Project Overview**: [AGENTS.md/towerscout-domain.md](../../../AGENTS.md/towerscout-domain.md)
- **Architecture Patterns**: [AGENTS.md/architecture.md](../../../AGENTS.md/architecture.md)
- **Development Workflows**: [AGENTS.md/dev-workflow.md](../../../AGENTS.md/dev-workflow.md)
- **Security Practices**: [AGENTS.md/security.md](../../../AGENTS.md/security.md)
- **Setup Guide**: [TowerScout_Development_Setup_Guide.txt](TowerScout_Development_Setup_Guide.txt)

### Decision Records

- **Global Variable Migration**: [.agent_work/decisions/015-global-variable-migration-patterns.md](../../decisions/015-global-variable-migration-patterns.md)
- **Azure Maps Integration**: [.agent_work/decisions/006-azure-maps-migration.md](../../decisions/006-azure-maps-migration.md)
- **Error Handling**: [.agent_work/decisions/009-error-handling-infrastructure.md](../../decisions/009-error-handling-infrastructure.md)

### Task Documentation

- **Frontend Modularization**: [.agent_work/tasks/completed/TASK-038-frontend-refactoring.md](../../tasks/completed/TASK-038-frontend-refactoring.md)
- **State Management**: [.agent_work/tasks/completed/TASK-041-deep-dive-priority-2.md](../../tasks/completed/TASK-041-deep-dive-priority-2.md)
- **Manual Testing**: [.agent_work/tasks/completed/TASK-042-testing-action-log.md](../../tasks/completed/TASK-042-testing-action-log.md)
- **Global Variable Deprecation**: [.agent_work/tasks/completed/TASK-043-global-variable-deprecation.md](../../tasks/completed/TASK-043-global-variable-deprecation.md)
- **Boundary Bug Fix**: [.agent_work/tasks/completed/TASK-045-boundary-accumulation-bug.md](../../tasks/completed/TASK-045-boundary-accumulation-bug.md)

---

**This guide is actively maintained. Last updated: March 2026 (Sprint 02 completion)**
