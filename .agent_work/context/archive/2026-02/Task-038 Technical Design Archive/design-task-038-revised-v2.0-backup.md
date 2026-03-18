# Technical Design: TASK-038 Frontend Code Quality & Refactoring (REVISED)

**Task**: TASK-038  
**Type**: B (Technical Debt & Code Quality)  
**Status**: DESIGN PHASE - REVISION 2  
**Created**: February 18, 2026  
**Revised**: February 18, 2026 (post-review)  
**Estimated Effort**: 38 hours (revised from 30 hours)  
**Design Version**: 2.0

---

## Revision History

**v2.0 (February 18, 2026)** - Major revisions based on expert review:
- Added `globals.js` for complete window API exposure (NEW)
- Added `store.js` for shared mutable state (NEW)
- Reordered stages: Boundaries now Stage 2 (before Providers)
- Fixed API endpoint constant: `/providers` → `/getproviders`
- Added 9-hour buffer to timeline (23h → 30h implementation)
- Clarified module loading strategy (script-compatible transition)
- Documented all 18+ inline handler dependencies
- Specified "logic changes" vs "structural changes" clearly

**v1.0 (February 18, 2026)** - Initial design

---

## Executive Summary

### Objective
Transform monolithic 5,272-line frontend file into modular, maintainable architecture organized in **24 files** across **7 logical directories**, while maintaining **100% backward compatibility** with inline HTML event handlers and script-global assumptions.

### Critical Success Factors
1. **Zero Functionality Regression**: All user workflows must work identically
2. **Inline Handler Compatibility**: 18+ template functions must remain accessible
3. **Script-Compatible Transition**: No ES6 module breaking changes in Sprint 02
4. **Incremental Validation**: Each stage must be independently testable
5. **Safe Rollback**: Git checkpoints allow reverting any stage

### Strategic Value
- **Maintenance**: Faster feature development, easier navigation
- **Testing**: Isolated modules enable comprehensive unit testing
- **Extensibility**: Clear abstractions for new providers (Mapbox, Leaflet)
- **Performance**: Smaller bundle sizes, lazy loading potential
- **Quality**: Eliminate duplicate code, standardize patterns

### Risk Assessment
- **Overall Risk**: MEDIUM-HIGH (revised from MEDIUM due to compatibility complexity)
- **Highest Risk**: Inline handler compatibility and global state migration
- **Mitigation**: New compatibility layer (`globals.js`), staged rollout, comprehensive testing

---

## Review Findings & Resolutions

### Finding 1: ES Module Migration Under-Scoped ✅ RESOLVED
**Issue**: Design assumed direct ES6 modules would work, but many references rely on script-global resolution via window shims.

**Resolution**:
- Added `globals.js` - explicit window API exposure contract
- Added `store.js` - centralized mutable state management
- Clarified migration strategy: script-compatible transition first, ES6 modules later (Sprint 03+)
- Stage 5 now includes comprehensive global exposure setup

### Finding 2: Inline Handler Compatibility Incomplete ✅ RESOLVED
**Issue**: Design showed partial window exposure but missed many template dependencies.

**Resolution**: Documented complete global exposure requirements:

**Required Window Globals** (18+ functions):
```javascript
// Workflow functions (from templates)
window.cancelRequest         // towerscout.html line 71
window.circleBoundary        // towerscout.html line 87
window.drawnBoundary         // towerscout.html line 90
window.clearBoundaries       // towerscout.html line 93
window.about                 // towerscout.html line 103
window.getObjects           // towerscout.html line 146-147

// Download functions (from templates)
window.download_csv          // towerscout.html line 196
window.download_kml          // towerscout.html line 196
window.download_dataset      // towerscout.html line 198

// Class static methods (from templates)
window.Detection.prev        // towerscout.html line 159
window.Detection.next        // towerscout.html line 162
window.Tile.prev            // towerscout.html line 171
window.Tile.next            // towerscout.html line 174

// Array access (dynamically generated HTML)
window.Detection_detections  // towerscout.js line 3370, 3402
window.Detection.showDetection  // towerscout.js line 3372, 3404

// Map instance (from templates)
window.currentMap.addShapes  // towerscout.html line 189
window.currentMap.clearShapes  // towerscout.html line 191
window.currentMap.clearAll   // towerscout.html line 192

// Backend integration
window.getBackendProviders   // towerscout.js line 5152, 5196
window.executeSearch         // towerscout.js line 772
```

### Finding 3: Stage Ordering Contradiction ✅ RESOLVED
**Issue**: Stage 2 (Providers) said "import boundaries from Stage 3" - impossible chronologically.

**Resolution**: Reordered stages:
- **OLD**: Stage 1 (Managers) → Stage 2 (Providers) → Stage 3 (Boundaries)
- **NEW**: Stage 1 (Managers) → Stage 2 (Boundaries) → Stage 3 (Providers)

Now TSMap in Stage 3 can safely import boundaries that already exist from Stage 2.

### Finding 4: Endpoint Constant Mismatch ✅ RESOLVED
**Issue**: Design used `PROVIDERS: '/providers'` but backend route is `/getproviders`.

**Resolution**: Fixed in config.js specification:
```javascript
export const API_ENDPOINTS = {
  GET_OBJECTS: '/getobjects',
  GET_GOOGLE_KEY: '/getgooglekey',
  GET_AZURE_KEY: '/getazurekey',
  API_USAGE: '/api-usage',
  PROVIDERS: '/getproviders'  // ← CORRECTED
};
```

### Finding 5: Document Baseline Verified ✅ CONFIRMED
**Issue**: Reviewer questioned 5,272 line count.

**Resolution**: Verified with `wc -l webapp/js/towerscout.js` → **5,272 lines** is correct.

### Finding 6: "No Logic Changes" Clarified ✅ RESOLVED
**Issue**: Design claimed "no logic changes" but added new methods like `toGeoJSON()`.

**Resolution**: Clarified terminology:
- **Structural changes**: File organization, imports/exports, code movement
- **API additions**: New optional methods that don't affect existing behavior
- **Logic changes**: Modifications to existing algorithms or workflows

**Commitment**: Zero logic changes to **critical paths**:
- Detection workflow
- Provider switching
- Boundary rendering
- Coordinate transformations
- ML pipeline integration

---

## Current State Analysis

### File Structure
```
webapp/js/
├── towerscout.js (5,272 lines - monolithic)
├── jquery-3.5.1.min.js (dependency)
└── azure_maps_debug.js (utility)
```

### Code Organization (towerscout.js)

**Lines 1-27**: Configuration and license  
**Lines 28-36**: Global state variables (7+ globals)  
**Lines 39-308**: ProviderStateManager class  
**Lines 311-372**: TimerManager class  
**Lines 375-471**: EventListenerManager class  
**Lines 474-666**: TowerScoutErrorHandler class  
**Lines 667-856**: DOM initialization and search functions  
**Lines 857-959**: About screen functionality  
**Lines 967-1062**: Google Maps initialization  
**Lines 1063-1178**: TSMap base class  
**Lines 1180-2512**: AzureMap class (~1,332 lines)  
**Lines 2515-2975**: GoogleMap class (~460 lines)  
**Lines 2976-3049**: Boundary base class  
**Lines 3050-3160**: PolygonBoundary, SimpleBoundary, CircleBoundary classes  
**Lines 3161-3229**: PlaceRect class  
**Lines 3230-3299**: Tile class  
**Lines 3300-3595**: Detection class  
**Lines 3596-4500**: Detection workflow functions  
**Lines 4501-4800**: Download and export functions  
**Lines 4801-5272**: Initialization and utility functions

### Global Dependencies (Must Preserve)

**Window-Level Globals** (18+ required for inline handlers):
- Functions: `cancelRequest`, `circleBoundary`, `drawnBoundary`, `clearBoundaries`, `about`, `getObjects`
- Downloads: `download_csv`, `download_kml`, `download_dataset`
- Classes: `De Detection`, `Tile`
- Arrays: `Detection_detections`, `Tile_tiles`
- State: `currentMap`
- Backend: `getBackendProviders`, `executeSearch`

**Inline Event Handlers** (in templates/towerscout.html):
- 18 onclick attributes calling global functions
- Dynamically generated onclick in Detection list HTML

**Script Loading Assumptions**:
- Sequential script loading (not module imports)
- Immediate global availability after script execution
- No async/await module loading

---

## Proposed Architecture (REVISED)

### Module Structure

```
webapp/js/
├── towerscout.js                    (Main initialization, ~400 lines)
├── config.js                        (Configuration constants, ~100 lines)
├── store.js                         (Shared mutable state, ~50 lines) ← NEW
├── globals.js                       (Window API exposure, ~100 lines) ← NEW
│
├── managers/
│   ├── ProviderStateManager.js      (~300 lines)
│   ├── TimerManager.js              (~70 lines)
│   ├── EventListenerManager.js      (~100 lines)
│   └── ErrorHandler.js              (~200 lines)
│
├── utils/                           ← MOVED TO STAGE 2 (partial)
│   ├── geometry.js                  (~100 lines) ← Stage 2
│   ├── validation.js                (~150 lines) ← Stage 2
│   └── search.js                    (~200 lines) ← Stage 5 (deferred)
│
├── boundaries/                      ← NOW STAGE 2 (moved up)
│   ├── Boundary.js                  (~80 lines)
│   ├── PolygonBoundary.js           (~60 lines)
│   ├── CircleBoundary.js            (~90 lines)
│   └── SimpleBoundary.js            (~30 lines)
│
├── providers/                       ← NOW STAGE 3 (moved down)
│   ├── TSMap.js                     (~150 lines)
│   ├── AzureMap.js                  (~1,400 lines)
│   ├── GoogleMap.js                 (~500 lines)
│
├── detection/
│   ├── PlaceRect.js                 (~100 lines)
│   ├── Tile.js                      (~120 lines)
│   └── Detection.js                 (~400 lines)
│
└── ui/
    ├── about.js                     (~120 lines)
    ├── progress.js                  (~150 lines)
    └── downloads.js                 (~300 lines)
```

**Total Files**: 24 (vs. original 22, vs. current 1)  
**New Additions**: `store.js`, `globals.js`

### Dependency Graph (REVISED)

```
Level 1 (No dependencies):
└── config.js
└── store.js (NEW - shared state container)

Level 2 (Config + Store dependencies):
├── utils/geometry.js
├── utils/validation.js
└── managers/TimerManager.js

Level 3 (Utils + Manager dependencies):
├── managers/EventListenerManager.js (→ TimerManager)
├── managers/ErrorHandler.js (→ TimerManager, validation)
└── boundaries/Boundary.js (→ geometry)

Level 4 (Foundation classes):
├── boundaries/PolygonBoundary.js (→ Boundary)
├── boundaries/CircleBoundary.js (→ PolygonBoundary, geometry)
├── boundaries/SimpleBoundary.js (→ PolygonBoundary)
└── detection/PlaceRect.js (→ config, store)

Level 5 (Provider foundation):
└── providers/TSMap.js (→ Boundary classes) ← NOW WORKS (boundaries exist)

Level 6 (Provider implementations):
├── managers/ProviderStateManager.js (→ all managers, ErrorHandler, store)
├── providers/AzureMap.js (→ TSMap, all boundaries, ErrorHandler, store)
└── providers/GoogleMap.js (→ TSMap, all boundaries, ErrorHandler, store)

Level 7 (Detection classes):
├── detection/Tile.js (→ PlaceRect, store)
└── detection/Detection.js (→ PlaceRect, config, store, Tile)

Level 8 (UI components):
├── ui/about.js (→ managers, config, store)
├── ui/progress.js (→ managers, config, store)
├── ui/downloads.js (→ Detection, Tile, config)
└── utils/search.js (→ providers, validation, ErrorHandler, store)

Level 9 (Integration):
├── globals.js (→ ALL modules, exposes to window) ← NEW
└── towerscout.js (→ ALL modules, calls globals.exposeGlobals())
```

**Key Change**: Boundaries (Level 3-4) now come before Providers (Level 5-6), eliminating circular dependency risk.

---

## NEW Module Specifications

### 1. store.js (NEW)
**Purpose**: Centralized mutable application state, replacing scattered globals

**Location**: `webapp/js/store.js`  
**Estimated Size**: ~50 lines  
**Dependencies**: None  
**Risk**: LOW

**Exports**:
```javascript
// store.js - Shared mutable application state
export const AppState = {
  // Provider state
  currentProvider: null,
  googleMap: null,
  azureMap: null,
  
  // Detection state
  detections: [],           // Replaces Detection_detections
  tiles: [],                // Replaces Tile_tiles
  minConfidence: 0.15,      // Replaces Detection_minConfidence
  currentDetection: null,   // Replaces Detection_current
  detectionsAugmented: 0,   // Replaces Detection_detectionsAugmented
  
  // UI state
  currentElement: null,
  currentAddrElement: null,
  isInitializing: true,
  
  // Engines
  engines: {},
  
  // Backend provider cache
  backendProviders: null
};

// Convenience getters/setters
export function getCurrentMap() {
  return AppState[AppState.currentProvider + 'Map'];
}

export function setCurrentProvider(provider) {
  AppState.currentProvider = provider;
}

// Reset functions (for testing/cleanup)
export function resetDetectionState() {
  AppState.detections = [];
  AppState.tiles = [];
  AppState.currentDetection = null;
  AppState.detectionsAugmented = 0;
}
```

**Migration Strategy**:
- Stage 1: Create store.js, populate with current global values
- Stage 2-4: Gradually migrate modules to use AppState instead of globals
- Stage 5: Expose AppState properties to window for inline handler compatibility

**Benefits**:
- Single source of truth for app state
- Easier to debug (one object to inspect)
- Testable (can reset state between tests)
- Prepare for future state management (Redux, MobX)

---

### 2. globals.js (NEW)
**Purpose**: Explicit window API exposure for inline handler compatibility

**Location**: `webapp/js/globals.js`  
**Estimated Size**: ~100 lines  
**Dependencies**: ALL application modules  
**Risk**: CRITICAL (must be comprehensive)

**Exports**:
```javascript
// globals.js - Complete window API for template compatibility
// This module bridges modular code with legacy inline event handlers

export function exposeGlobals(app) {
  console.log('🔗 Exposing global API for template compatibility...');
  
  // ===== WORKFLOW FUNCTIONS =====
  // Used by inline onclick handlers in towerscout.html
  
  window.cancelRequest = app.cancelRequest;
  window.circleBoundary = app.circleBoundary;
  window.drawnBoundary = app.drawnBoundary;
  window.clearBoundaries = app.clearBoundaries;
  window.about = app.about;
  window.getObjects = app.getObjects;
  
  // ===== DOWNLOAD FUNCTIONS =====
  // Used by download buttons in towerscout.html
  
  window.download_csv = app.download_csv;
  window.download_kml = app.download_kml;
  window.download_dataset = app.download_dataset;
  
  // ===== CLASSES WITH STATIC METHODS =====
  // Used by navigation buttons in towerscout.html
  
  window.Detection = {
    prev: app.Detection.prev.bind(app.Detection),
    next: app.Detection.next.bind(app.Detection),
    showDetection: app.Detection.showDetection.bind(app.Detection),
    sort: app.Detection.sort.bind(app.Detection),
    generateList: app.Detection.generateList.bind(app.Detection),
    resetAll: app.Detection.resetAll.bind(app.Detection)
  };
  
  window.Tile = {
    prev: app.Tile.prev.bind(app.Tile),
    next: app.Tile.next.bind(app.Tile),
    number: app.Tile.number.bind(app.Tile),
    resetAll: app.Tile.resetAll.bind(app.Tile),
    getTileIds: app.Tile.getTileIds.bind(app.Tile)
  };
  
  // ===== MUTABLE STATE ARRAYS =====
  // Used by dynamically generated onclick handlers
  // These MUST be kept in sync with AppState
  
  Object.defineProperty(window, 'Detection_detections', {
    get: () => app.AppState.detections,
    set: (value) => { app.AppState.detections = value; }
  });
  
  Object.defineProperty(window, 'Tile_tiles', {
    get: () => app.AppState.tiles,
    set: (value) => { app.AppState.tiles = value; }
  });
  
  // ===== MAP INSTANCE =====
  // Used by map manipulation buttons in towerscout.html
  
  Object.defineProperty(window, 'currentMap', {
    get: () => app.providerManager.getCurrentMap(),
    set: (value) => {
      console.warn('⚠️ Direct currentMap assignment deprecated, use providerManager.switchProvider()');
    }
  });
  
  // ===== BACKEND INTEGRATION =====
  // Used by provider initialization
  
  window.getBackendProviders = app.getBackendProviders;
  window.executeSearch = app.handleGlobalSearch;
  
  // ===== MANAGERS (optional, for debugging) =====
  
  window.providerManager = app.providerManager;
  window.timerManager = app.timerManager;
  window.eventManager = app.eventManager;
  
  // ===== UI FUNCTIONS =====
  
  window.adjustConfidence = app.adjustConfidence;
  window.changeReviewMode = app.changeReviewMode;
  
  console.log('✅ Global API exposed successfully');
  console.log('📊 Exposed functions:', Object.keys(window).filter(k => k.startsWith('cancel') || k.startsWith('circle') || k.startsWith('drawn') || k.startsWith('download')));
}

// Validation function - call after exposure to verify
export function validateGlobalAPI() {
  const required = [
    'cancelRequest', 'circleBoundary', 'drawnBoundary', 'clearBoundaries',
    'about', 'getObjects', 'download_csv', 'download_kml', 'download_dataset',
    'Detection', 'Tile', 'Detection_detections', 'Tile_tiles',
    'currentMap', 'getBackendProviders', 'executeSearch'
  ];
  
  const missing = required.filter(fn => typeof window[fn] === 'undefined');
  
  if (missing.length > 0) {
    console.error('❌ Missing global API functions:', missing);
    return false;
  }
  
  console.log('✅ All required global API functions present');
  return true;
}
```

**Usage Pattern** (in towerscout.js):
```javascript
// At end of initialization
import { exposeGlobals, validateGlobalAPI } from './globals.js';

// Collect all app modules into single object
const TowerScoutApp = {
  // Managers
  providerManager,
  timerManager,
  eventManager,
  
  // State
  AppState,
  
  // Classes
  Detection,
  Tile,
  
  // Functions
  cancelRequest,
  circleBoundary,
  drawnBoundary,
  clearBoundaries,
  about,
  getObjects,
  download_csv,
  download_kml,
  download_dataset,
  adjustConfidence,
  changeReviewMode,
  handleGlobalSearch,
  getBackendProviders
};

// Expose to window for inline handlers
exposeGlobals(TowerScoutApp);

// Validate exposure
if (!validateGlobalAPI()) {
  console.error('❌ Global API validation failed - inline handlers may not work');
}
```

**Why This Matters**:
- Inline handlers in templates require window-level functions
- Dynamically generated HTML uses `Detection_detections[id]` syntax
- Without this, ALL onclick handlers would break
- Provides clear contract of what must remain globally accessible

---

## REVISED Module Specifications

### config.js (UPDATED)
**Change**: Fixed endpoint constant

```javascript
export const API_ENDPOINTS = {
  GET_OBJECTS: '/getobjects',
  GET_GOOGLE_KEY: '/getgooglekey',
  GET_AZURE_KEY: '/getazurekey',
  API_USAGE: '/api-usage',
  PROVIDERS: '/getproviders'  // ← CORRECTED from '/providers'
};
```

### detection/Detection.js (UPDATED)
**Change**: Use AppState instead of global arrays

**Old Pattern**:
```javascript
let Detection_detections = [];
let Detection_current = null;
```

**New Pattern**:
```javascript
import { AppState } from '../store.js';

class Detection extends PlaceRect {
  constructor(...) {
    // ...
    this.id = AppState.detections.length;
    AppState.detections.push(this);
  }
  
  static resetAll() {
    for (let det of AppState.detections) {
      det.select(false);
    }
    AppState.detections = [];
    AppState.detectionsAugmented = 0;
    // ...
  }
}

// Still export for globals.js exposure
export { Detection };
export const Detection_detections = AppState.detections; // Alias for compatibility
```

### providers/TSMap.js (UPDATED)
**Change**: Can now safely import boundaries (they exist in Stage 2)

```javascript
import { Boundary } from '../boundaries/Boundary.js';
import { PolygonBoundary } from '../boundaries/PolygonBoundary.js';
import { CircleBoundary } from '../boundaries/CircleBoundary.js';
import { SimpleBoundary } from '../boundaries/SimpleBoundary.js';

class TSMap {
  // ... existing methods ...
  
  // CONSOLIDATED: Move implementation from subclasses (Stage 2)
  getBoundariesStr() {
    let result = [];
    for (let b of this.boundaries) {
      result.push(b.toString());
    }
    return "[" + result.join(",") + "]";
  }
}
```

**Risk**: NONE - boundaries extracted first in Stage 2

---

## REVISED Migration Strategy

### 5-Stage Incremental Approach (REORDERED)

---

### **STAGE 1: Extract Managers + State** (8 hours, was 6 hours)

**Goal**: Extract managers and create state/globals infrastructure

**Files to Create**:
1. `config.js` (~1 hour)
2. `store.js` (~1 hour) ← NEW
3. `managers/TimerManager.js` (~1 hour)
4. `managers/EventListenerManager.js` (~1 hour)
5. `managers/ErrorHandler.js` (~2 hours)
6. `managers/ProviderStateManager.js` (~1.5 hours)
7. `globals.js` (stub, ~0.5 hour) ← NEW (complete in Stage 5)

**New Steps**:
1. Create `store.js` FIRST
   - Define AppState object with all global state
   - Export state and helper functions
   - Document migration path for each global

2. Create `globals.js` stub
   - Define exposeGlobals signature
   - Create validation function
   - Add TODO comments for each required exposure

3. Update all managers to use AppState where applicable
   - ProviderStateManager uses AppState.currentProvider
   - ErrorHandler uses AppState for error tracking

**Validation** (Updated):
- [ ] AppState accessible from all modules
- [ ] globals.js stub validates required functions list
- [ ] All managers instantiate without errors
- [ ] Provider switching still works
- [ ] No console errors on page load

**Buffer**: +2 hours for state migration complexity

---

### **STAGE 2: Extract Boundaries + Utilities** (4 hours, was 3 hours)

**Goal**: Create boundary class hierarchy and geometry utilities BEFORE providers need them

**Files to Create**:
1. `utils/geometry.js` (~1 hour)
2. `utils/validation.js` (~1 hour)
3. `boundaries/Boundary.js` (~0.5 hour)
4. `boundaries/PolygonBoundary.js` (~0.5 hour)
5. `boundaries/CircleBoundary.js` (~0.5 hour)
6. `boundaries/SimpleBoundary.js` (~0.5 hour)

**Key Change**: This is now Stage 2 (was Stage 3), so providers in Stage 3 can import boundaries

**Validation** (Updated):
- [ ] All boundary types instantiate correctly
- [ ] CircleBoundary generates correct point count
- [ ] Geometry utilities work (Haversine distance calculation)
- [ ] Validation prevents invalid coordinates
- [ ] No circular dependencies (verify with madge if available)

**Buffer**: +1 hour for geometry edge cases

---

### **STAGE 3: Extract Providers** (6 hours, was 5 hours)

**Goal**: Isolate map provider implementations (now dependencies are ready)

**Files to Create**:
1. `providers/TSMap.js` (~1.5 hours)
2. `providers/AzureMap.js` (~2.5 hours)
3. `providers/GoogleMap.js` (~2 hours)

**Key Change**: Boundaries now exist (Stage 2), so TSMap can import them without issue

**Steps** (Updated):
1. Extract `TSMap.js` FIRST
   - Import ALL boundary classes from Stage 2 ✅
   - **IMPLEMENT `getBoundariesStr()`** in base class
   - No "import from future stage" issues

2. Extract `AzureMap.js`
   - Import TSMap, boundaries (both exist now)
   - **REMOVE** `getBoundariesStr()` override
   - Use AppState for current provider tracking

3. Extract `GoogleMap.js`
   - Same pattern as AzureMap
   - **REMOVE** `getBoundariesStr()` override

**Validation** (Updated):
- [ ] TSMap successfully imports all boundaries
- [ ] Only ONE implementation of getBoundariesStr() exists (in TSMap)
- [ ] No duplicate method warnings
- [ ] Both providers render correctly
- [ ] Provider switching works
- [ ] AppState.currentProvider updates correctly

**Buffer**: +1 hour for state integration

---

### **STAGE 4: Extract Detections** (5 hours, was 4 hours)

**Goal**: Isolate detection result management, integrate with AppState

**Files to Create**:
1. `detection/PlaceRect.js` (~1 hour)
2. `detection/Tile.js` (~2 hours)
3. `detection/Detection.js` (~2 hours)

**Key Change**: Use AppState instead of global arrays

**Steps** (Updated):
1. Extract `PlaceRect.js`
   - Import AppState for currentMap access
   - Use AppState.currentProvider for provider checks

2. Extract `Tile.js`
   - Use `AppState.tiles` instead of `Tile_tiles` global
   - Export alias for backward compatibility:
     ```javascript
     export const Tile_tiles = AppState.tiles;
     ```

3. Extract `Detection.js`
   - Use `AppState.detections` instead of `Detection_detections`
   - Use `AppState.currentDetection` instead of `Detection_current`
   - Export aliases for inline handler compatibility

**Validation** (Updated):
- [ ] AppState.detections populated correctly
- [ ] AppState.tiles tracked properly
- [ ] Detections render on map
- [ ] List generation works
- [ ] Highlighting functional
- [ ] Tile navigation works
- [ ] No global array references outside AppState

**Buffer**: +1 hour for array migration complexity

---

### **STAGE 5: Extract UI + Search + Complete Globals** (7 hours, was 5 hours)

**Goal**: Complete modularization, finalize global exposure, consolidate duplicates

**Files to Create/Complete**:
1. `ui/about.js` (~0.5 hour)
2. `ui/progress.js` (~1.5 hours)
3. `ui/downloads.js` (~1.5 hours)
4. `utils/search.js` (~1 hour) - DEFERRED to this stage (provider-coupled)
5. `globals.js` (complete implementation, ~2 hours) ← CRITICAL
6. Update `towerscout.js` (integrate all, ~0.5 hour)

**Critical Steps**:

**5.1 Complete globals.js** (~2 hours)
- Implement ALL 18+ function exposures
- Implement AppState property getters for arrays
- Implement currentMap property getter
- Add validation function
- Test each exposure individually

**5.2 Extract UI modules** (~3.5 hours)
- Extract about.js (use timerManager, eventManager)
- Extract progress.js (detection progress tracking)
- Extract downloads.js (CSV, KML, YOLO exports)
- All UI modules import AppState as needed

**5.3 Extract search.js** (~1 hour) - DEFERRED from Stage 2
- Extract provider-aware search coordination
- Import both AzureMap and GoogleMap (now available)
- Use AppState.currentProvider

**5.4 Integrate in towerscout.js** (~0.5 hour)
- Import ALL modules
- Create TowerScoutApp object with all exports
- Call `exposeGlobals(TowerScoutApp)`
- Call `validateGlobalAPI()`

**5.5 Consolidate Duplicates**
- ✅ `getBoundariesStr()` already consolidated (Stage 3)
- Consolidate repeated null checks
- Move remaining magic numbers to CONFIG
- Standardize all error handling (remove legacy fatalError)

**Validation** (COMPREHENSIVE):
- [ ] All 18+ window functions defined
- [ ] `validateGlobalAPI()` returns true
- [ ] Template onclick handlers work
- [ ] Dynamically generated onclick handlers work
- [ ] Detection_detections[id] array access works
- [ ] currentMap.addShapes() works from template
- [ ] About screen functional
- [ ] Progress overlay displays
- [ ] All exports generate correctly
- [ ] Search works on both providers
- [ ] NO duplicate code patterns
- [ ] ALL error handling uses ErrorHandler
- [ ] ALL magic numbers in CONFIG

**Buffer**: +2 hours for global exposure complexity and validation

---

## Module Loading Strategy (DETAILED)

### Phase 1: Script-Compatible Transition (Sprint 02 - THIS DESIGN)

**Approach**: Use traditional `<script>` tags in sequence, NO ES6 module loading

**Template Update** (towerscout.html):
```html
<head>
  <!-- ... existing CSS ... -->
  
  <!-- TowerScout Core (load order matters) -->
  <script src="{{ url_for('static', filename='js/config.js') }}"></script>
  <script src="{{ url_for('static', filename='js/store.js') }}"></script>
  
  <!-- Utilities (no dependencies except config/store) -->
  <script src="{{ url_for('static', filename='js/utils/geometry.js') }}"></script>
  <script src="{{ url_for('static', filename='js/utils/validation.js') }}"></script>
  
  <!-- Managers (depend on config/store/utils) -->
  <script src="{{ url_for('static', filename='js/managers/TimerManager.js') }}"></script>
  <script src="{{ url_for('static', filename='js/managers/EventListenerManager.js') }}"></script>
  <script src="{{ url_for('static', filename='js/managers/ErrorHandler.js') }}"></script>
  
  <!-- Boundaries (depend on utils) -->
  <script src="{{ url_for('static', filename='js/boundaries/Boundary.js') }}"></script>
  <script src="{{ url_for('static', filename='js/boundaries/PolygonBoundary.js') }}"></script>
  <script src="{{ url_for('static', filename='js/boundaries/CircleBoundary.js') }}"></script>
  <script src="{{ url_for('static', filename='js/boundaries/SimpleBoundary.js') }}"></script>
  
  <!-- Providers (depend on boundaries/managers) -->
  <script src="{{ url_for('static', filename='js/providers/TSMap.js') }}"></script>
  <script src="{{ url_for('static', filename='js/managers/ProviderStateManager.js') }}"></script>
  <script src="{{ url_for('static', filename='js/providers/AzureMap.js') }}"></script>
  <script src="{{ url_for('static', filename='js/providers/GoogleMap.js') }}"></script>
  
  <!-- Detection (depend on providers/store) -->
  <script src="{{ url_for('static', filename='js/detection/PlaceRect.js') }}"></script>
  <script src="{{ url_for('static', filename='js/detection/Tile.js') }}"></script>
  <script src="{{ url_for('static', filename='js/detection/Detection.js') }}"></script>
  
  <!-- UI (depend on detection/managers) -->
  <script src="{{ url_for('static', filename='js/ui/about.js') }}"></script>
  <script src="{{ url_for('static', filename='js/ui/progress.js') }}"></script>
  <script src="{{ url_for('static', filename='js/ui/downloads.js') }}"></script>
  <script src="{{ url_for('static', filename='js/utils/search.js') }}"></script>
  
  <!-- Main Application (depends on ALL above) -->
  <script src="{{ url_for('static', filename='js/towerscout.js') }}"></script>
  
  <!-- Global API Exposure (MUST be last) -->
  <script src="{{ url_for('static', filename='js/globals.js') }}"></script>
  <script>
    // Expose global API for inline handlers
    if (typeof TowerScoutApp !== 'undefined' && typeof exposeGlobals === 'function') {
      exposeGlobals(TowerScoutApp);
      validateGlobalAPI();
    } else {
      console.error('❌ TowerScoutApp or exposeGlobals not available');
    }
  </script>
  
  <!-- External APIs (Google Maps, Azure Maps) -->
  <script async defer
    src="https://maps.googleapis.com/maps/api/js?key={{ google_api_key }}&libraries=drawing,places&callback=initGoogleMap">
  </script>
  <link rel="stylesheet" href="https://atlas.microsoft.com/sdk/javascript/mapcontrol/2/atlas.min.css" type="text/css" />
  <script src="https://atlas.microsoft.com/sdk/javascript/mapcontrol/2/atlas.min.js"></script>
  <script src="https://atlas.microsoft.com/sdk/javascript/drawing/0/atlas-drawing.min.js"></script>
  <script src ="https://atlas.microsoft.com/sdk/javascript/service/2/atlas-service.min.js"></script>
</head>
```

**Module File Pattern** (for script compatibility):
```javascript
// config.js - NO import/export, direct global assignment
(function(window) {
  'use strict';
  
  window.CONFIG = {
    RETRY_DELAY_MS: 2000,
    // ... all config
  };
  
  window.API_ENDPOINTS = {
    PROVIDERS: '/getproviders',  // ← CORRECTED
    // ... all endpoints
  };
  
})(window);
```

**Why This Approach**:
- ✅ No ES6 module loading complexity
- ✅ Inline handlers work immediately
- ✅ Sequential loading guarantees dependencies
- ✅ Backward compatible with all browsers
- ✅ Can transition to ES6 later without changing logic

**Drawbacks** (acceptable for Sprint 02):
- ⚠️ Global namespace pollution (mitigated by globals.js)
- ⚠️ Load order must be perfect (documented in template)
- ⚠️ No tree-shaking or code splitting
- ⚠️ Larger initial bundle size

### Phase 2: ES6 Module Transition (Sprint 03+ - FUTURE)

**After** Sprint 02 refactoring is stable and validated:

1. Convert all files to ES6 module format:
   ```javascript
   // config.js
   export const CONFIG = { /* ... */ };
   export const API_ENDPOINTS = { /* ... */ };
   ```

2. Update HTML to use single module entry:
   ```html
   <script type="module" src="{{ url_for('static', filename='js/towerscout.js') }}"></script>
   ```

3. Add build process (webpack/rollup) for production bundling

4. Keep globals.js for inline handler compatibility (still needed)

**Benefits** (future):
- Tree-shaking (remove unused code)
- Code splitting (lazy load providers)
- Proper dependency management
- Better IDE support

---

## Updated Timeline with Buffer

| Stage | Description | Base | Buffer | Total | Risk |
|-------|-------------|------|--------|-------|------|
| 1 | Managers + Store + Globals stub | 6h | +2h | **8h** | LOW-MED |
| 2 | Boundaries + Utils (geometry, validation) | 3h | +1h | **4h** | LOW |
| 3 | Providers (dependencies ready) | 5h | +1h | **6h** | MEDIUM |
| 4 | Detections (with AppState) | 4h | +1h | **5h** | MEDIUM |
| 5 | UI + Search + Complete Globals | 5h | +2h | **7h** | MEDIUM-HIGH |
| **Implementation Subtotal** | | **23h** | **+7h** | **30h** | |
| Testing | Comprehensive validation | 3h | +1h | **4h** | |
| Documentation | Updates | 2h | - | **2h** | |
| Integration | HTML templates, compatibility | 1h | +1h | **2h** | |
| **GRAND TOTAL** | | **29h** | **+9h** | **38h** | |

**Sprint Fit**: 38 hours / 14 days = **2.7 hours/day**
- Week 1 (7 days): 19 hours = 2.7 hours/day
- Week 2 (7 days): 19 hours = 2.7 hours/day

**Realistic**: Yes, with disciplined daily progress

**Buffer Allocation**:
- Stage 1: +2h (state migration, globals stub complexity)
- Stage 2: +1h (geometry edge cases)
- Stage 3: +1h (AppState integration)
- Stage 4: +1h (array migration)
- Stage 5: +2h (complete global exposure, validation)
- Testing: +1h (comprehensive regression testing)
- Integration: +1h (HTML template debugging)

**Total Buffer**: 9 hours (~24% of base estimate) - industry standard for refactoring

---

## Success Criteria (UPDATED)

### Code Quality Metrics
- [ ] **File Count**: 24 files in 7 directories (vs. 1 monolithic)
- [ ] **Main File Size**: towerscout.js <400 lines (vs. 5,272 lines)
- [ ] **Module Size**: Average ~250 lines per module
- [ ] **Code Duplication**: ZERO (getBoundariesStr consolidated)
- [ ] **Error Handling**: 100% using TowerScoutErrorHandler
- [ ] **Magic Numbers**: 100% in CONFIG object
- [ ] **Global State**: Centralized in AppState
- [ ] **Dependencies**: Clear dependency graph, zero circular

### Functionality Metrics
- [ ] **Zero Regressions**: All user workflows unchanged
- [ ] **Inline Handlers**: All 18+ functions work from templates
- [ ] **Dynamic HTML**: Detection list onclick handlers work
- [ ] **Provider Parity**: Google Maps and Azure Maps identical
- [ ] **Performance**: No degradation (page load, detection)
- [ ] **Memory**: No new leaks (validated with Chrome DevTools)

### Compatibility Metrics (NEW)
- [ ] **Window API**: validateGlobalAPI() returns true
- [ ] **Template Functions**: All onclick handlers functional
- [ ] **Array Access**: Detection_detections[id] works
- [ ] **Map Instance**: currentMap.addShapes() works
- [ ] **Backend Integration**: getBackendProviders() works
- [ ] **Search**: executeSearch works from template

### Documentation Metrics
- [ ] **JSDoc Coverage**: All exported functions documented
- [ ] **Global Contract**: All window exposures documented
- [ ] **Migration Guide**: State migration paths clear
- [ ] **Decision Records**: Architectural choices documented

---

## Risk Mitigation (UPDATED)

### CRITICAL Risk: Inline Handler Compatibility

**Risk**: Inline onclick handlers break when functions not window-accessible

**Likelihood**: HIGH (without mitigation)  
**Impact**: CRITICAL (complete UI failure)

**Mitigation**:
1. ✅ Created comprehensive globals.js with ALL required exposures
2. ✅ Added validateGlobalAPI() to verify completeness
3. ✅ Staged rollout (manual test each function after Stage 5)
4. ✅ Rollback plan (revert Stage 5 if validation fails)

**Validation Steps**:
```javascript
// Test each inline handler manually
document.querySelector('[onclick*="cancelRequest"]').click();
document.querySelector('[onclick*="circleBoundary"]').click();
document.querySelector('[onclick*="Detection.prev"]').click();
// ... test all 18+ handlers
```

### HIGH Risk: State Migration Errors

**Risk**: AppState not properly synced with window-exposed arrays

**Likelihood**: MEDIUM  
**Impact**: HIGH (data inconsistency)

**Mitigation**:
1. ✅ Use Object.defineProperty for bidirectional sync
2. ✅ AppState as single source of truth
3. ✅ Comprehensive logging during migration
4. ✅ Test array mutations from both module and window contexts

**Validation**:
```javascript
// Test bidirectional sync
console.log(AppState.detections.length);
console.log(window.Detection_detections.length); // Should match

AppState.detections.push(newDetection);
console.log(window.Detection_detections.length); // Should update

window.Detection_detections.pop();
console.log(AppState.detections.length); // Should update
```

### MEDIUM Risk: Stage Ordering Dependencies

**Risk**: Extract module before its dependencies exist

**Likelihood**: LOW (mitigated by reordering)  
**Impact**: MEDIUM (blocking compilation errors)

**Mitigation**:
1. ✅ Reordered stages (boundaries before providers)
2. ✅ Clear dependency graph (Level 1-9)
3. ✅ Validation after each stage
4. ✅ Can use madge for circular dependency detection

### LOW-MEDIUM Risk: Endpoint Constant Errors

**Risk**: Use wrong endpoint paths in API calls

**Likelihood**: LOW (fixed in design)  
**Impact**: MEDIUM (API calls fail)

**Mitigation**:
1. ✅ Corrected in design: `/providers` → `/getproviders`
2. ✅ Centralized in API_ENDPOINTS constant
3. ✅ Test backend integration after Stage 1
4. ✅ Add validation for 404 errors

---

## Appendix A: Complete Global Exposure Contract

**This is the definitive list of ALL window-level globals required for backward compatibility:**

### Functions (16 total)

| Function | Source Location | Used By | Template Line |
|----------|----------------|---------|---------------|
| cancelRequest | towerscout.js | About overlay | towerscout.html:71 |
| circleBoundary | towerscout.js | Circle tool button | towerscout.html:87 |
| drawnBoundary | towerscout.js | Polygon tool button | towerscout.html:90 |
| clearBoundaries | towerscout.js | Clear button | towerscout.html:93 |
| about | ui/about.js | About link | towerscout.html:103 |
| getObjects | towerscout.js | Find/Estimate buttons | towerscout.html:146-147 |
| download_csv | ui/downloads.js | Download button | towerscout.html:196 |
| download_kml | ui/downloads.js | Download button | towerscout.html:196 |
| download_dataset | ui/downloads.js | Download button | towerscout.html:198 |
| adjustConfidence | towerscout.js | Confidence slider | (event listener) |
| changeReviewMode | towerscout.js | Review checkbox | (event listener) |
| executeSearch | utils/search.js | Search input | towerscout.js:772 |
| getBackendProviders | towerscout.js | Provider init | towerscout.js:5152, 5196 |
| initGoogleMap | towerscout.js | Google Maps callback | googleapi script |
| validateMapIntegrity | towerscout.js | Resize handler | (internal) |
| syncWithBackendProviders | towerscout.js | Provider setup | (internal) |

### Classes with Static Methods (2 total)

| Class | Methods | Used By | Template Line |
|-------|---------|---------|---------------|
| Detection | prev(), next(), showDetection() | Navigation buttons | towerscout.html:159, 162 |
| Tile | prev(), next(), number() | Tile navigation | towerscout.html:171, 174 |

### Arrays (2 total)

| Array | Type | Used By | JavaScript Line |
|-------|------|---------|-----------------|
| Detection_detections | Array<Detection> | Dynamic onclick | towerscout.js:3370, 3402 |
| Tile_tiles | Array<Tile> | Tile navigation | (internal references) |

### Properties (1 total)

| Property | Type | Used By | Template Line |
|----------|------|---------|---------------|
| currentMap | TSMap instance | Map buttons | towerscout.html:189, 191, 192 |

**Total Required Window Globals**: 21 items

---

## Appendix B: Validation Test Matrix (UPDATED)

### Stage 1 Validation

```javascript
// Test AppState
console.assert(typeof AppState === 'object', 'AppState exists');
console.assert(typeof AppState.detections === 'object', 'AppState.detections is array');
console.assert(typeof AppState.currentProvider === 'string' || AppState.currentProvider === null, 'AppState.currentProvider valid');

// Test CONFIG
console.assert(CONFIG.RETRY_DELAY_MS === 2000, 'CONFIG loaded');
console.assert(API_ENDPOINTS.PROVIDERS === '/getproviders', 'Endpoint corrected');

// Test Managers
console.assert(typeof timerManager === 'object', 'timerManager exists');
console.assert(typeof eventManager === 'object', 'eventManager exists');
console.assert(typeof TowerScoutErrorHandler === 'function', 'ErrorHandler exists');
console.assert(typeof providerManager === 'object', 'providerManager exists');

// Test globals.js stub
console.assert(typeof exposeGlobals === 'function', 'exposeGlobals defined');
console.assert(typeof validateGlobalAPI === 'function', 'validateGlobalAPI defined');
```

### Stage 2 Validation

```javascript
// Test Boundaries
console.assert(typeof Boundary === 'function', 'Boundary class exists');
console.assert(typeof PolygonBoundary === 'function', 'PolygonBoundary exists');
console.assert(typeof CircleBoundary === 'function', 'CircleBoundary exists');
console.assert(typeof SimpleBoundary === 'function', 'SimpleBoundary exists');

// Test boundary creation
const circle = new CircleBoundary([0, 0], 1000);
console.assert(circle.points.length === 65, 'Circle has correct points (64 + closing)');

// Test geometry utilities
console.assert(typeof rad === 'function', 'rad() exists');
console.assert(typeof getDistance === 'function', 'getDistance() exists');
const dist = getDistance([0, 0], [0, 0.001]);
console.assert(dist > 0 && dist < 200, 'getDistance calculates correctly');
```

### Stage 3 Validation

```javascript
// Test Providers
console.assert(typeof TSMap === 'function', 'TSMap class exists');
console.assert(typeof AzureMap === 'function', 'AzureMap exists');
console.assert(typeof GoogleMap === 'function', 'GoogleMap exists');

// Test getBoundariesStr consolidation
const tsmap = new TSMap();
console.assert(typeof tsmap.getBoundariesStr === 'function', 'TSMap has getBoundariesStr');

// Verify NO duplicates
const azureProto = AzureMap.prototype;
const googleProto = GoogleMap.prototype;
console.assert(!azureProto.hasOwnProperty('getBoundariesStr'), 'AzureMap does NOT override getBoundariesStr');
console.assert(!googleProto.hasOwnProperty('getBoundariesStr'), 'GoogleMap does NOT override getBoundariesStr');

// Test provider initialization
// (requires DOM and API keys, manual testing)
```

### Stage 4 Validation

```javascript
// Test Detection classes
console.assert(typeof PlaceRect === 'function', 'PlaceRect exists');
console.assert(typeof Tile === 'function', 'Tile exists');
console.assert(typeof Detection === 'function', 'Detection exists');

// Test AppState integration
console.assert(Array.isArray(AppState.detections), 'AppState.detections is array');
console.assert(Array.isArray(AppState.tiles), 'AppState.tiles is array');

// Test array aliases
console.assert(Detection_detections === AppState.detections, 'Detection_detections aliases AppState');
console.assert(Tile_tiles === AppState.tiles, 'Tile_tiles aliases AppState');

// Test detection creation (requires map context, manual)
```

### Stage 5 Validation (COMPREHENSIVE)

```javascript
// Test UI modules
console.assert(typeof about === 'function', 'about() exists');
console.assert(typeof download_csv === 'function', 'download_csv() exists');
console.assert(typeof download_kml === 'function', 'download_kml() exists');
console.assert(typeof download_dataset === 'function', 'download_dataset() exists');

// Test globals exposure
const result = validateGlobalAPI();
console.assert(result === true, 'All required globals exposed');

// Test each window global individually
console.assert(typeof window.cancelRequest === 'function', 'window.cancelRequest exposed');
console.assert(typeof window.circleBoundary === 'function', 'window.circleBoundary exposed');
console.assert(typeof window.drawnBoundary === 'function', 'window.drawnBoundary exposed');
console.assert(typeof window.clearBoundaries === 'function', 'window.clearBoundaries exposed');
console.assert(typeof window.about === 'function', 'window.about exposed');
console.assert(typeof window.getObjects === 'function', 'window.getObjects exposed');
console.assert(typeof window.download_csv === 'function', 'window.download_csv exposed');
console.assert(typeof window.download_kml === 'function', 'window.download_kml exposed');
console.assert(typeof window.download_dataset === 'function', 'window.download_dataset exposed');

// Test class static methods
console.assert(typeof window.Detection === 'object', 'window.Detection exposed');
console.assert(typeof window.Detection.prev === 'function', 'window.Detection.prev exposed');
console.assert(typeof window.Detection.next === 'function', 'window.Detection.next exposed');
console.assert(typeof window.Tile === 'object', 'window.Tile exposed');
console.assert(typeof window.Tile.prev === 'function', 'window.Tile.prev exposed');
console.assert(typeof window.Tile.next === 'function', 'window.Tile.next exposed');

// Test arrays
console.assert(window.Detection_detections === AppState.detections, 'window.Detection_detections exposed');
console.assert(window.Tile_tiles === AppState.tiles, 'window.Tile_tiles exposed');

// Test currentMap property
console.assert(typeof window.currentMap === 'object' || window.currentMap === null, 'window.currentMap exposed');

// Test backend integration
console.assert(typeof window.getBackendProviders === 'function', 'window.getBackendProviders exposed');
console.assert(typeof window.executeSearch === 'function', 'window.executeSearch exposed');
```

### Manual Inline Handler Tests

```html
<!-- Test inline handlers by clicking buttons in Chrome DevTools -->
<script>
// Test each onclick handler
document.querySelector('button[onclick*="cancelRequest"]')?.click();
document.querySelector('button[onclick*="circleBoundary"]')?.click();
document.querySelector('button[onclick*="drawnBoundary"]')?.click();
document.querySelector('button[onclick*="clearBoundaries"]')?.click();
document.querySelector('a[onclick*="about"]')?.click();
document.querySelector('button[onclick*="getObjects"]')?.click();
document.querySelector('button[onclick*="Detection.prev"]')?.click();
document.querySelector('button[onclick*="Detection.next"]')?.click();
document.querySelector('button[onclick*="Tile.prev"]')?.click();
document.querySelector('button[onclick*="Tile.next"]')?.click();
document.querySelector('button[onclick*="currentMap.addShapes"]')?.click();
document.querySelector('button[onclick*="download_csv"]')?.click();

console.log('✅ All inline handlers clicked without errors');
</script>
```

---

## Approval & Sign-Off (REVISED)

### Design Review Checklist v2.0
- [x] Module structure logical and maintainable
- [x] Dependency graph acyclic and ordered correctly
- [x] Migration strategy safe and incremental
- [x] Testing strategy comprehensive
- [x] Rollback plan defined
- [x] Timeline realistic with buffer
- [x] Risk mitigation adequate
- [x] Success criteria measurable
- [x] **NEW**: Complete global exposure contract documented
- [x] **NEW**: Script-compatible transition strategy defined
- [x] **NEW**: AppState centralized state management
- [x] **NEW**: Stage ordering corrected (boundaries before providers)
- [x] **NEW**: API endpoint constants corrected
- [x] **NEW**: Inline handler compatibility ensured

### Approval Required Before Implementation
**Reviewer**: User / Project Stakeholder  
**Date Submitted**: February 18, 2026 (Revision 2)  
**Status**: ⏳ PENDING APPROVAL

**Changes from v1.0**:
- Added globals.js module (100 lines)
- Added store.js module (50 lines)
- Reordered stages (boundaries Stage 2, providers Stage 3)
- Fixed API endpoint constant
- Added 9 hours buffer (38 hours total)
- Clarified script-compatible transition strategy
- Documented complete window exposure contract (21 items)

**Approval Signature**: ___________________________  
**Date**: ___________________________

**Recommendation**: Approve with understanding that Stage 5 validation is critical for inline handler compatibility. If Stage 5 validation fails, revert to v1.0 approach or defer to Sprint 03 for ES6 module investigation.

---

## End of Revised Design Document

**Next Steps After Approval**:
1. ✅ Create task file: `TASK-038-frontend-refactoring.md`
2. ✅ Update `current-tasks.md` status to IN_PROGRESS
3. ✅ Create feature branch: `git checkout -b task-038-stage-1`
4. ✅ Begin Stage 1 implementation (Managers + Store + Globals stub)
5. ✅ Validate Stage 1 before proceeding to Stage 2

**Estimated Start Date**: February 19, 2026 (pending approval)  
**Estimated Completion Date**: March 5, 2026 (38 hours / 14 days = 2.7 hours/day)
