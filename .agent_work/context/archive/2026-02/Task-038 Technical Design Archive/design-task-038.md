# Technical Design: TASK-038 Frontend Code Quality & Refactoring

**Task**: TASK-038  
**Type**: B (Technical Debt & Code Quality)  
**Status**: DESIGN PHASE  
**Created**: February 18, 2026  
**Estimated Effort**: 23 hours  
**Design Version**: 1.0

---

## Executive Summary

### Objective
Transform monolithic 5,272-line frontend file into modular, maintainable architecture organized in 12+ files across 6 logical directories. This refactoring establishes foundation for rapid future development while preserving all existing functionality.

### Strategic Value
- **Maintenance**: Easier navigation, faster feature development
- **Testing**: Isolated modules enable comprehensive unit testing
- **Extensibility**: Clear abstractions for adding new map providers
- **Performance**: Smaller bundle sizes, potential for lazy loading
- **Quality**: Eliminates duplicate code, standardizes error handling

### Scope
- **In Scope**: Module extraction, code consolidation, error handling standardization, configuration centralization
- **Out of Scope**: TypeScript migration, jQuery removal (deferred to Sprint 03), architectural rewrites
- **Non-Goals**: Changing functionality, adding features, modifying ML pipeline

### Risk Assessment
- **Overall Risk**: MEDIUM
- **Mitigation**: Incremental 5-stage approach with validation checkpoints
- **Dependencies**: TASK-041 foundation complete ✅, Sprint 01 bugs resolved ✅

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

### Key Issues Identified

**1. Code Duplication**
- `getBoundariesStr()` implemented 3 times (TSMap line 1167, AzureMap line 2504, GoogleMap line 2975)
- Repeated null checks for currentMap/provider
- Duplicate error handling patterns

**2. Error Handling Inconsistency**
- `TowerScoutErrorHandler.showUserNotification()` (modern, preferred)
- `fatalError()` (legacy, blocking)
- `console.error()` + return (no user feedback)

**3. Configuration Management**
- Magic numbers scattered throughout (timeout values, circle segments, opacity levels)
- CONFIG object exists but underutilized

**4. Global State**
- 7+ global variables create synchronization complexity
- Global arrays for detections/tiles

**5. Module Coupling**
- Tight coupling between UI and business logic
- Provider-specific code mixed with generic functionality

---

## Proposed Architecture

### Module Structure

```
webapp/js/
├── towerscout.js                    (Main initialization, ~500 lines)
├── config.js                        (Configuration constants, ~100 lines)
├── managers/
│   ├── ProviderStateManager.js      (~300 lines)
│   ├── TimerManager.js              (~70 lines)
│   ├── EventListenerManager.js      (~100 lines)
│   └── ErrorHandler.js              (~200 lines)
├── providers/
│   ├── TSMap.js                     (Base class, ~150 lines)
│   ├── AzureMap.js                  (~1,400 lines)
│   └── GoogleMap.js                 (~500 lines)
├── boundaries/
│   ├── Boundary.js                  (Base class, ~80 lines)
│   ├── PolygonBoundary.js           (~60 lines)
│   ├── CircleBoundary.js            (~90 lines)
│   └── SimpleBoundary.js            (~30 lines)
├── detection/
│   ├── PlaceRect.js                 (Base class, ~100 lines)
│   ├── Tile.js                      (~120 lines)
│   └── Detection.js                 (~400 lines)
├── ui/
│   ├── about.js                     (~120 lines)
│   ├── progress.js                  (~150 lines)
│   └── downloads.js                 (~300 lines)
└── utils/
    ├── geometry.js                  (~100 lines)
    ├── validation.js                (~150 lines)
    └── search.js                    (~200 lines)
```

### Dependency Graph

```
Level 1 (No dependencies):
└── config.js

Level 2 (Config-only dependencies):
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
├── detection/PlaceRect.js (→ config)
└── providers/TSMap.js (→ Boundary)

Level 5 (Provider implementations):
├── managers/ProviderStateManager.js (→ all managers, ErrorHandler)
├── providers/AzureMap.js (→ TSMap, all boundaries, ErrorHandler)
└── providers/GoogleMap.js (→ TSMap, all boundaries, ErrorHandler)

Level 6 (Detection classes):
├── detection/Tile.js (→ PlaceRect)
└── detection/Detection.js (→ PlaceRect, config)

Level 7 (UI components):
├── ui/about.js (→ managers, config)
├── ui/progress.js (→ managers, config)
├── ui/downloads.js (→ Detection, Tile, config)
└── utils/search.js (→ providers, validation, ErrorHandler)

Level 8 (Main application):
└── towerscout.js (→ ALL modules)
```

---

## Detailed Module Specifications

### 1. config.js
**Purpose**: Centralize all configuration constants, magic numbers, API endpoints

**Exports**:
```javascript
export const CONFIG = {
  // Timing
  RETRY_DELAY_MS: 2000,
  MAX_RETRIES: 3,
  DRAWING_TOOLS_RETRY_DELAY_MS: 500,
  DRAWING_TOOLS_MAX_RETRIES: 10,
  PROVIDER_SWITCH_DELAY_MS: 100,
  MAP_VALIDATION_DELAY_MS: 1000,
  ABOUT_SCREEN_DURATION_SEC: 6,
  PROGRESS_UPDATE_INTERVAL_MS: 100,
  SECS_PER_TILE_DEFAULT: 0.25,
  
  // UI Constants
  DEFAULT_CONFIDENCE: 0.15,
  CIRCLE_SEGMENTS: 64,
  DEFAULT_ZOOM: 19,
  MAX_ZOOM: 21,
  
  // Detection
  DETECTION_OPACITY_UNSELECTED: 0.15,
  DETECTION_OPACITY_SELECTED: 0.3,
  SECONDARY_THRESHOLD: 0.35,
  
  // Geocoding
  GEOCODING_RATE_LIMIT_THRESHOLD: 100,
  
  // Map Coordinates
  NYC_CENTER: [-74.00820558171071, 40.71083794970947]
};

export const API_ENDPOINTS = {
  GET_OBJECTS: '/getobjects',
  GET_GOOGLE_KEY: '/getgooglekey',
  GET_AZURE_KEY: '/getazurekey',
  API_USAGE: '/api-usage',
  PROVIDERS: '/providers'
};
```

**Source Lines**: Extract from lines 13-26, plus scattered magic numbers
**Estimated Size**: ~100 lines
**Dependencies**: None
**Risk**: LOW - Simple constant definitions

---

### 2. managers/TimerManager.js
**Purpose**: Centralized timer lifecycle management with automatic cleanup

**Source Lines**: 311-372
**Current Size**: ~70 lines
**Dependencies**: None
**Risk**: LOW - Well-defined, isolated class

**Exports**:
```javascript
export class TimerManager {
  constructor()
  setTimeout(callback, delay, description = '')
  setInterval(callback, interval, description = '')
  clearTimeout(timerId)
  clearInterval(intervalId)
  clearAll()
  getActiveTimersInfo()
}

export const timerManager = new TimerManager();
```

**Changes Needed**:
- Add module imports/exports
- Update internal references to use imported CONFIG
- No logic changes

---

### 3. managers/EventListenerManager.js
**Purpose**: Track and manage DOM event listeners with automatic cleanup

**Source Lines**: 375-471
**Current Size**: ~100 lines
**Dependencies**: `timerManager` (for cleanup timing)
**Risk**: LOW - Well-defined, isolated class

**Exports**:
```javascript
export class EventListenerManager {
  constructor()
  addEventListener(element, event, callback, options)
  removeEventListener(element, event, callback)
  clearElementListeners(element, event)
  clearAllListeners()
  getActiveListenersInfo()
}

export const eventManager = new EventListenerManager();
```

**Changes Needed**:
- Import `timerManager` from `./TimerManager.js`
- Add module exports
- No logic changes

---

### 4. managers/ErrorHandler.js
**Purpose**: Centralized error handling with user notifications and provider fallbacks

**Source Lines**: 474-666
**Current Size**: ~200 lines
**Dependencies**: `timerManager`, `config`, DOM validation utilities
**Risk**: MEDIUM - Critical for user experience

**Exports**:
```javascript
export class TowerScoutErrorHandler {
  static handleProviderError(provider, error)
  static handleAPIError(error, context = '')
  static showUserNotification(message, type = 'info', duration = 3000)
  static showFatalError(message)
  static clearAllNotifications()
}

export function validateDOMElement(elementId, required = true)
```

**Changes Needed**:
- Import `timerManager`, `CONFIG`
- Extract `validateDOMElement()` function (lines 666-679)
- Consolidate with legacy `fatalError()` function
- Add validation utilities

---

### 5. managers/ProviderStateManager.js
**Purpose**: Eliminate race conditions during provider switching, manage initialization state

**Source Lines**: 39-308
**Current Size**: ~300 lines
**Dependencies**: All other managers, `ErrorHandler`
**Risk**: HIGH - Critical for state consistency (but proven stable from TASK-041)

**Exports**:
```javascript
export class ProviderStateManager {
  constructor()
  async switchProvider(targetProvider, mapInstance = null)
  getCurrentProvider()
  getCurrentMap()
  isSwitching()
  markProviderReady(provider, component)
  isProviderReady(provider)
}

export const providerManager = new ProviderStateManager();
```

**Changes Needed**:
- Import all managers
- Import `TowerScoutErrorHandler`
- Reference `timerManager` for delays
- No logic changes (proven stable)

---

### 6. boundaries/Boundary.js
**Purpose**: Base class for all boundary types

**Source Lines**: 2976-3049
**Current Size**: ~80 lines
**Dependencies**: `utils/geometry.js` (for coordinate calculations)
**Risk**: LOW - Simple base class

**Exports**:
```javascript
export class Boundary {
  constructor(description)
  toString()
  toGeoJSON() // New method for standardization
}
```

**Changes Needed**:
- Extract base Boundary class
- Add GeoJSON conversion method
- Import geometry utilities

---

### 7. boundaries/PolygonBoundary.js
**Purpose**: Polygon boundary implementation

**Source Lines**: 3050-3109
**Current Size**: ~60 lines
**Dependencies**: `Boundary.js`
**Risk**: LOW - Simple subclass

**Exports**:
```javascript
export class PolygonBoundary extends Boundary {
  constructor(description, points)
  toString()
}
```

---

### 8. boundaries/CircleBoundary.js
**Purpose**: Circle boundary with geographic calculations

**Source Lines**: 3110-3160
**Current Size**: ~90 lines
**Dependencies**: `PolygonBoundary.js`, `utils/geometry.js`
**Risk**: LOW - Well-tested circle generation

**Exports**:
```javascript
export class CircleBoundary extends PolygonBoundary {
  constructor(center, radius)
  generateCircle(center, radiusMeters, segments = 64)
}
```

**Changes Needed**:
- Import `CONFIG.CIRCLE_SEGMENTS`
- Import geometry utilities
- No logic changes

---

### 9. boundaries/SimpleBoundary.js
**Purpose**: Rectangular boundary from bounds

**Source Lines**: 3120-3150 (within PolygonBoundary section)
**Current Size**: ~30 lines
**Dependencies**: `PolygonBoundary.js`
**Risk**: LOW - Simple subclass

**Exports**:
```javascript
export class SimpleBoundary extends PolygonBoundary {
  constructor(bounds)
}
```

---

### 10. providers/TSMap.js
**Purpose**: Abstract base class for all map providers

**Source Lines**: 1063-1178
**Current Size**: ~150 lines
**Dependencies**: Boundary classes
**Risk**: MEDIUM - Core abstraction

**Exports**:
```javascript
export class TSMap {
  getBounds()
  getBoundsUrl()
  getBoundaryBounds()
  getBoundaryBoundsUrl()
  cleanup()
  setCenter()
  getCenter()
  getCenterUrl()
  getZoom()
  setZoom(z)
  fitCenter()
  search(place)
  makeMapRect(o)
  updateMapRect(o)
  getBoundariesStr() // CONSOLIDATE: Move implementation from subclasses
}
```

**Changes Needed**:
- **CRITICAL**: Implement `getBoundariesStr()` in base class (remove from AzureMap/GoogleMap)
- Import all Boundary classes
- Add validation for abstract methods
- Add type hints in JSDoc

---

### 11. providers/AzureMap.js
**Purpose**: Azure Maps implementation

**Source Lines**: 1180-2512
**Current Size**: ~1,400 lines
**Dependencies**: `TSMap.js`, all Boundary classes, `ErrorHandler`
**Risk**: HIGH - Largest, most complex class

**Exports**:
```javascript
export class AzureMap extends TSMap {
  constructor()
  async initialize()
  async getSubscriptionKey()
  setupDrawingTools()
  addBoundary(boundary)
  retrieveDrawnBoundaries()
  clearBoundaries()
  clearCircles()
  clearPolygons()
  hasShapes()
  search(place)
  addSearchResultMarker(result)
  biasSearchBox()
  makeMapRect(o, listener)
  updateMapRect(o, show)
  cleanup()
  getBoundariesStr() // REMOVE: Move to TSMap base
}
```

**Changes Needed**:
- Import `TSMap`, boundaries, `ErrorHandler`
- Import `CONFIG`, `API_ENDPOINTS`
- **REMOVE** `getBoundariesStr()` method (use inherited from TSMap)
- Extract search functionality to `utils/search.js`
- No logic changes to core functionality

---

### 12. providers/GoogleMap.js
**Purpose**: Google Maps implementation

**Source Lines**: 2515-2975
**Current Size**: ~500 lines
**Dependencies**: `TSMap.js`, all Boundary classes, `ErrorHandler`
**Risk**: MEDIUM - Core provider functionality

**Exports**:
```javascript
export class GoogleMap extends TSMap {
  constructor()
  addBoundary(boundary)
  retrieveDrawnBoundaries()
  clearBoundaries()
  clearCircles()
  clearPolygons()
  hasShapes()
  drawCircle(center, radius)
  drawPolygon(boundary)
  cleanup()
  getBoundariesStr() // REMOVE: Move to TSMap base
}
```

**Changes Needed**:
- Import `TSMap`, boundaries, `ErrorHandler`
- Import `CONFIG`, `API_ENDPOINTS`
- **REMOVE** `getBoundariesStr()` method (use inherited from TSMap)
- Extract search box initialization
- No logic changes to core functionality

---

### 13. detection/PlaceRect.js
**Purpose**: Base class for rectangular map objects

**Source Lines**: 3161-3229
**Current Size**: ~100 lines
**Dependencies**: `config.js`, provider awareness
**Risk**: MEDIUM - Base class for Detection/Tile

**Exports**:
```javascript
export class PlaceRect {
  constructor(x1, y1, x2, y2, color, fillColor, opacity, classname, listener)
  centerInMap()
  getCenter()
  getCenterUrl()
  highlight(color)
  update(currentMapInstance)
}
```

**Changes Needed**:
- Import `CONFIG`
- Add null checks for provider safety
- No logic changes

---

### 14. detection/Tile.js
**Purpose**: Tile management for detection processing

**Source Lines**: 3230-3299
**Current Size**: ~120 lines
**Dependencies**: `PlaceRect.js`
**Risk**: LOW - Simple subclass

**Exports**:
```javascript
export class Tile extends PlaceRect {
  constructor(x1, y1, x2, y2, metadata, url)
  static resetAll()
  static getTileIds(x1, y1, x2, y2)
  static number()
  static prev()
  static next()
}

export let Tile_tiles = [];
```

**Changes Needed**:
- Import `PlaceRect`
- Move `Tile_tiles` array to module-level
- Add array exports for global access

---

### 15. detection/Detection.js
**Purpose**: Detection result management and UI generation

**Source Lines**: 3300-3595
**Current Size**: ~400 lines
**Dependencies**: `PlaceRect.js`, `config.js`, `Tile.js`
**Risk**: MEDIUM - Complex UI interactions

**Exports**:
```javascript
export class Detection extends PlaceRect {
  constructor(x1, y1, x2, y2, classname, conf, tile, idInTile, inside, selected, secondary, address, addressConfidence, addressProvider)
  static resetAll()
  static sort()
  static generateList()
  generateCheckBox()
  select(onoff)
  selectAddr(onoff)
  show(onoff)
  isShown()
  showAddr(onoff)
  static showDetection(id, center)
  highlight(center, scroll)
  resetHighlight()
}

export let Detection_detections = [];
export let Detection_minConfidence;
export let Detection_current = null;
```

**Changes Needed**:
- Import `PlaceRect`, `CONFIG`, `Tile`
- Move detection arrays to module-level
- Standardize DOM ID generation
- No logic changes to highlighting

---

### 16. ui/about.js
**Purpose**: About screen overlay functionality

**Source Lines**: 857-959
**Current Size**: ~120 lines
**Dependencies**: `timerManager`, `eventManager`, `config`
**Risk**: LOW - Simple overlay management

**Exports**:
```javascript
export function about(aboutTotal)
export function closeAbout()
export function aboutTimerFunc(aboutTotal)
export function aboutOpacity(secs, total)
```

**Changes Needed**:
- Import managers and CONFIG
- Extract global timer variables to module scope
- Use `timerManager` for all timers

---

### 17. ui/progress.js
**Purpose**: Detection progress tracking and display

**Source Lines**: Scattered throughout detection workflow
**Current Size**: ~150 lines (estimated after extraction)
**Dependencies**: `config`, `timerManager`
**Risk**: MEDIUM - Critical for UX during detection

**Exports**:
```javascript
export function initializeProgressTracking()
export function updateProgress(current, total)
export function showProgressOverlay(show)
export function estimateTileProcessingTime(tileCount)
```

**Changes Needed**:
- Extract from detection workflow functions
- Centralize progress calculation logic
- Use CONFIG for timing estimates

---

### 18. ui/downloads.js
**Purpose**: Export functionality (CSV, KML, YOLO format)

**Source Lines**: 4501-4800
**Current Size**: ~300 lines
**Dependencies**: `Detection.js`, `Tile.js`, `config`
**Risk**: MEDIUM - Complex export logic

**Exports**:
```javascript
export function download(filename, data)
export function exportCSV()
export function exportKML()
export function exportYOLO()
export function downloadDataset()
```

**Changes Needed**:
- Import Detection, Tile classes
- Import CONFIG for formatting
- Standardize export formats
- No logic changes

---

### 19. utils/geometry.js
**Purpose**: Geographic calculations and coordinate transformations

**Source Lines**: Scattered throughout (Haversine, circle generation, etc.)
**Current Size**: ~100 lines
**Dependencies**: None
**Risk**: LOW - Pure mathematical functions

**Exports**:
```javascript
export function rad(x)
export function getDistance(p1, p2)
export function degreesToMeters(degrees, latitude)
export function metersToDegrees(meters, latitude)
export function calculateBoundingBox(points)
```

**Changes Needed**:
- Extract from multiple locations
- Consolidate similar calculations
- Add JSDoc with examples
- Add unit tests

---

### 20. utils/validation.js
**Purpose**: Input validation and data sanitization

**Source Lines**: Scattered throughout
**Current Size**: ~150 lines (estimated after extraction)
**Dependencies**: `config`
**Risk**: MEDIUM - Security-critical

**Exports**:
```javascript
export function validateCoordinates(lng, lat)
export function validateBounds(bounds)
export function validateRadius(radius)
export function validateConfidence(confidence)
export function validateDOMElement(elementId, required)
export function sanitizeCoordinates(coords)
```

**Changes Needed**:
- Extract validation logic from various functions
- Add comprehensive bounds checking
- Add type validation
- Add sanitization for user inputs

---

### 21. utils/search.js
**Purpose**: Provider-agnostic search functionality

**Source Lines**: 760-856 (provider-aware search) + provider-specific search methods
**Current Size**: ~200 lines
**Dependencies**: `providers/AzureMap.js`, `providers/GoogleMap.js`, `validation`, `ErrorHandler`
**Risk**: MEDIUM - Complex provider coordination

**Exports**:
```javascript
export function initializeProviderAwareSearch()
export function handleGlobalSearch()
export async function performSearch(provider, query)
export function handleSearchResult(result, provider)
```

**Changes Needed**:
- Extract search coordination logic
- Consolidate provider-specific search handling
- Import validation utilities
- Use ErrorHandler for search failures

---

### 22. towerscout.js (Main Application)
**Purpose**: Application initialization, provider coordination, workflow orchestration

**Source Lines**: All remaining after extractions (~500-800 lines)
**Dependencies**: ALL modules
**Risk**: MEDIUM - Integration point

**Responsibilities**:
- Initialize all managers
- Set up provider instances
- Coordinate detection workflow
- Handle provider switching UI
- DOM event binding
- Application lifecycle management

**Key Functions Remaining**:
```javascript
// Initialization
DOMContentLoaded handler
initializeDOMReferences()
initGoogleMap()

// Provider management
async initializeDefaultProvider()
async syncWithBackendProviders()
function validateMapIntegrity()

// Detection workflow
function startDetection(estimate)
function circleBoundary()
function drawnBoundary()
function adjustConfidence()
function changeReviewMode()

// API integration
function afterAugment()
function updateApiUsageDisplay()
```

**Changes Needed**:
- Import ALL modules
- Replace global instances with imports
- Coordinate provider initialization
- Maintain backward compatibility for inline event handlers
- Add comprehensive error handling

---

## Migration Strategy

### 5-Stage Incremental Approach

Each stage is designed to be:
- **Independent**: Can be completed and validated separately
- **Reversible**: Git commits allow rollback if issues arise
- **Testable**: Clear success criteria for each stage

---

### **STAGE 1: Extract Managers** (6 hours)

**Goal**: Extract well-defined manager classes with minimal external dependencies

**Files to Create**:
1. `config.js` (~1 hour)
2. `managers/TimerManager.js` (~1 hour)
3. `managers/EventListenerManager.js` (~1 hour)
4. `managers/ErrorHandler.js` (~2 hours)
5. `managers/ProviderStateManager.js` (~1 hour)

**Steps**:
1. Create `webapp/js/config.js`
   - Copy CONFIG object from lines 13-26
   - Extract magic numbers from throughout file
   - Add API_ENDPOINTS object
   - Export as named exports

2. Create `webapp/js/managers/` directory

3. Extract `TimerManager.js`
   - Copy lines 311-372
   - Add imports: `import { CONFIG } from '../config.js'`
   - Add exports: `export class TimerManager` and `export const timerManager`
   - Update internal CONFIG references

4. Extract `EventListenerManager.js`
   - Copy lines 375-471  
   - Import `timerManager` from `./TimerManager.js`
   - Add exports

5. Extract `ErrorHandler.js`
   - Copy lines 474-666
   - Import `timerManager`, `CONFIG`
   - Extract `validateDOMElement` function (lines 666-679)
   - Consolidate legacy `fatalError()` function (lines ~4765)
   - Add exports

6. Extract `ProviderStateManager.js`
   - Copy lines 39-308
   - Import all other managers
   - Import `ErrorHandler`
   - Add exports

7. Update `towerscout.js`
   - Add imports at top:
     ```javascript
     import { CONFIG, API_ENDPOINTS } from './config.js';
     import { timerManager } from './managers/TimerManager.js';
     import { eventManager } from './managers/EventListenerManager.js';
     import { TowerScoutErrorHandler, validateDOMElement } from './managers/ErrorHandler.js';
     import { providerManager } from './managers/ProviderStateManager.js';
     ```
   - Remove original class definitions
   - Test all manager functionality

**Validation**:
- [ ] All managers instantiate without errors
- [ ] Provider switching still works
- [ ] Error notifications display correctly
- [ ] Timer cleanup executes properly
- [ ] Event listeners tracked correctly
- [ ] No console errors on page load
- [ ] Provider initialization completes successfully

**Rollback**: `git revert` to pre-Stage 1 commit

**Estimated Time**: 6 hours  
**Risk**: LOW (managers are well-isolated)

---

### **STAGE 2: Extract Providers** (5 hours)

**Goal**: Isolate map provider implementations

**Files to Create**:
1. `providers/TSMap.js` (~1.5 hours)
2. `providers/AzureMap.js` (~2 hours)
3. `providers/GoogleMap.js` (~1.5 hours)

**Steps**:
1. Create `webapp/js/providers/` directory

2. Extract `TSMap.js`
   - Copy lines 1063-1178
   - Add imports for Boundary classes (will be from Stage 3)
   - **IMPLEMENT `getBoundariesStr()`** in base class:
     ```javascript
     getBoundariesStr() {
       let result = [];
       for (let b of this.boundaries) {
         result.push(b.toString());
       }
       return "[" + result.join(",") + "]";
     }
     ```
   - Add comprehensive JSDoc
   - Export class

3. Extract `AzureMap.js`
   - Copy lines 1180-2512
   - Import `TSMap` from `./TSMap.js`
   - Import `TowerScoutErrorHandler` from `../managers/ErrorHandler.js`
   - Import `CONFIG`, `API_ENDPOINTS` from `../config.js`
   - **REMOVE** `getBoundariesStr()` method (line ~2504) - use inherited
   - Add exports

4. Extract `GoogleMap.js`
   - Copy lines 2515-2975
   - Import `TSMap` from `./TSMap.js`
   - Import `ErrorHandler`, `CONFIG`, `API_ENDPOINTS`
   - **REMOVE** `getBoundariesStr()` method (line ~2975) - use inherited
   - Add exports

5. Update `towerscout.js`
   - Add imports:
     ```javascript
     import { AzureMap } from './providers/AzureMap.js';
     import { GoogleMap } from './providers/GoogleMap.js';
     ```
   - Remove original class definitions
   - Test provider instantiation and switching

**Validation**:
- [ ] Both providers initialize successfully
- [ ] Provider switching works without errors
- [ ] Maps render correctly
- [ ] Boundary strings generate correctly from base class
- [ ] Search functionality works on both providers
- [ ] Drawing tools functional
- [ ] No duplicate getBoundariesStr() implementations
- [ ] Console shows no errors
- [ ] Memory cleanup executes properly

**Rollback**: `git revert` to pre-Stage 2 commit

**Estimated Time**: 5 hours  
**Risk**: MEDIUM (large classes, critical functionality)

---

### **STAGE 3: Extract Boundaries** (3 hours)

**Goal**: Create boundary class hierarchy

**Files to Create**:
1. `boundaries/Boundary.js` (~30 min)
2. `boundaries/PolygonBoundary.js` (~30 min)
3. `boundaries/CircleBoundary.js` (~1 hour)
4. `boundaries/SimpleBoundary.js` (~30 min)
5. `utils/geometry.js` (~30 min)

**Steps**:
1. Create `webapp/js/boundaries/` directory
2. Create `webapp/js/utils/` directory

3. Extract `utils/geometry.js` FIRST (dependency for boundaries)
   - Extract `rad()` function
   - Extract `getDistance()` function
   - Add geographic calculation utilities
   - Add exports

4. Extract `Boundary.js`
   - Copy lines 2976-3049 (base class)
   - Import geometry utilities
   - Add GeoJSON conversion method
   - Export class

5. Extract `PolygonBoundary.js`
   - Copy lines 3050-3109
   - Import `Boundary` from `./Boundary.js`
   - Export class

6. Extract `CircleBoundary.js`
   - Copy lines 3110-3160
   - Import `PolygonBoundary` from `./PolygonBoundary.js`
   - Import `CONFIG` for CIRCLE_SEGMENTS
   - Import geometry utilities
   - Export class

7. Extract `SimpleBoundary.js`
   - Copy lines 3120-3150
   - Import `PolygonBoundary`
   - Export class

8. Update `providers/TSMap.js`
   - Add imports:
     ```javascript
     import { Boundary } from '../boundaries/Boundary.js';
     import { PolygonBoundary } from '../boundaries/PolygonBoundary.js';
     import { CircleBoundary } from '../boundaries/CircleBoundary.js';
     import { SimpleBoundary } from '../boundaries/SimpleBoundary.js';
     ```

9. Update `providers/AzureMap.js` and `GoogleMap.js`
   - Import boundary classes
   - Test boundary creation and rendering

10. Update `towerscout.js`
    - Import boundary classes
    - Remove original class definitions
    - Test circle and polygon creation

**Validation**:
- [ ] All boundary types instantiate correctly
- [ ] Circles generate with correct number of segments
- [ ] Polygons render on both providers
- [ ] SimpleBoundary creates rectangles correctly
- [ ] Boundary string serialization works
- [ ] GeoJSON conversion functional
- [ ] No console errors
- [ ] Drawing tools create correct boundary types

**Rollback**: `git revert` to pre-Stage 3 commit

**Estimated Time**: 3 hours  
**Risk**: LOW (well-defined class hierarchy)

---

### **STAGE 4: Extract Detection Classes** (4 hours)

**Goal**: Isolate detection result management

**Files to Create**:
1. `detection/PlaceRect.js` (~1 hour)
2. `detection/Tile.js` (~1 hour)
3. `detection/Detection.js` (~2 hours)

**Steps**:
1. Create `webapp/js/detection/` directory

2. Extract `PlaceRect.js`
   - Copy lines 3161-3229
   - Import `CONFIG` from `../config.js`
   - Add provider null checks
   - Export class

3. Extract `Tile.js`
   - Copy lines 3230-3299
   - Import `PlaceRect` from `./PlaceRect.js`
   - Move `Tile_tiles` array to module level
   - Export class and array:
     ```javascript
     export let Tile_tiles = [];
     export class Tile extends PlaceRect { ... }
     ```

4. Extract `Detection.js`
   - Copy lines 3300-3595
   - Import `PlaceRect` from `./PlaceRect.js`
   - Import `CONFIG` from `../config.js`
   - Import `Tile_tiles` from `./Tile.js`
   - Move detection arrays to module level:
     ```javascript
     export let Detection_detections = [];
     export let Detection_detectionsAugmented = 0;
     export let Detection_minConfidence;
     export let Detection_current = null;
     ```
   - Export class and arrays

5. Update `towerscout.js`
   - Add imports:
     ```javascript
     import { PlaceRect } from './detection/PlaceRect.js';
     import { Tile, Tile_tiles } from './detection/Tile.js';
     import { Detection, Detection_detections, Detection_minConfidence, Detection_current } from './detection/Detection.js';
     ```
   - Remove original class definitions
   - Update array references throughout file
   - Test detection workflow

**Validation**:
- [ ] Detections render on map correctly
- [ ] Tiles track processing properly
- [ ] Detection list generates correctly
- [ ] Highlighting works (marker ↔ list)
- [ ] Confidence filtering functional
- [ ] Checkbox selection works
- [ ] Address grouping correct
- [ ] Tile navigation functional
- [ ] Both providers render detections identically
- [ ] No console errors

**Rollback**: `git revert` to pre-Stage 4 commit

**Estimated Time**: 4 hours  
**Risk**: MEDIUM (complex UI interactions, global array dependencies)

---

### **STAGE 5: Extract UI & Utilities, Consolidate Duplicates** (5 hours)

**Goal**: Complete modularization, eliminate duplicate code, standardize patterns

**Files to Create**:
1. `ui/about.js` (~30 min)
2. `ui/progress.js` (~1.5 hours)
3. `ui/downloads.js` (~1.5 hours)
4. `utils/validation.js` (~1 hour)
5. `utils/search.js` (~30 min)

**Steps**:
1. Create `webapp/js/ui/` directory (if not exists)

2. Extract `ui/about.js`
   - Copy lines 857-959
   - Import `timerManager`, `eventManager`, `CONFIG`
   - Move about timer variables to module scope
   - Export functions

3. Extract `ui/progress.js`
   - Extract progress-related functions from detection workflow
   - Import `CONFIG`, `timerManager`
   - Export progress tracking functions

4. Extract `ui/downloads.js`
   - Copy lines 4501-4800
   - Import `Detection`, `Tile`, `CONFIG`
   - Export download functions

5. Extract `utils/validation.js`
   - Extract validation functions from throughout file
   - Import `CONFIG` for validation thresholds
   - Export validation functions

6. Extract `utils/search.js`
   - Copy lines 760-856 (provider-aware search)
   - Import providers, validation, ErrorHandler
   - Export search functions

7. **CONSOLIDATE DUPLICATE CODE**:
   - ✅ `getBoundariesStr()` already consolidated in Stage 2 (TSMap base)
   - Consolidate repeated null checks into validation utilities
   - Standardize error handling patterns (remove all legacy `fatalError()` calls)
   - Move remaining magic numbers to CONFIG

8. **STANDARDIZE ERROR HANDLING**:
   - Search and replace all `fatalError()` calls with `TowerScoutErrorHandler.showFatalError()`
   - Remove legacy `fatalError()` function definition
   - Ensure all error paths use ErrorHandler

9. Update `towerscout.js`
   - Add all remaining imports
   - Remove all extracted functions
   - Verify initialization order
   - Test complete application workflow

**Validation**:
- [ ] About screen displays and dismisses correctly
- [ ] Progress tracking updates during detection
- [ ] All export formats work (CSV, KML, YOLO)
- [ ] Search functionality works on both providers
- [ ] Validation prevents invalid inputs
- [ ] No `getBoundariesStr()` duplication
- [ ] No legacy `fatalError()` calls remain
- [ ] All error handling uses ErrorHandler
- [ ] All magic numbers moved to CONFIG
- [ ] No console errors
- [ ] Complete user workflow functional (search → detect → review → export)

**Rollback**: `git revert` to pre-Stage 5 commit

**Estimated Time**: 5 hours  
**Risk**: MEDIUM (many small changes, comprehensive testing needed)

---

## HTML Integration & Module Support

### Challenge
Current HTML likely uses `<script>` tags without module support. ES6 modules require `type="module"` attribute.

### Solution (Choose One)

**Option 1: Direct ES6 Modules** (Recommended for development)
```html
<script type="module" src="js/towerscout.js"></script>
```
Pros: No build step, modern approach
Cons: Requires modern browsers, no bundling

**Option 2: Build Process with Bundler**
Use webpack/rollup to bundle modules for production:
```bash
npm install --save-dev webpack webpack-cli
npx webpack --config webpack.config.js
```
Pros: Production-ready, backward compatible
Cons: Requires build step, adds complexity

**Recommendation**: Start with Option 1 for refactoring, add Option 2 for production deployment in future sprint

### HTML Template Updates Required
```html
<!-- Update in templates/*.html -->
<script type="module" src="{{ url_for('static', filename='js/towerscout.js') }}"></script>
```

---

## Testing Strategy

### Per-Stage Validation

**Automated Checks** (run after each stage):
```javascript
// Stage validation script
function validateStage(stageNumber) {
  const checks = {
    1: validateManagers,
    2: validateProviders,
    3: validateBoundaries,
    4: validateDetections,
    5: validateComplete
  };
  
  return checks[stageNumber]();
}

function validateManagers() {
  return {
    timerManager: typeof timerManager !== 'undefined',
    eventManager: typeof eventManager !== 'undefined',
    errorHandler: typeof TowerScoutErrorHandler !== 'undefined',
    providerManager: typeof providerManager !== 'undefined'
  };
}

// ... similar for other stages
```

**Manual Testing Checklist** (after each stage):
- [ ] Page loads without console errors
- [ ] No undefined variable errors
- [ ] Previous functionality still works
- [ ] New modules accessible
- [ ] Import/export syntax correct
- [ ] File paths resolve correctly

### Comprehensive Testing (After All Stages)

**User Journey Validation** (from TASK-037):
1. **Stage 1: Search & Navigation**
   - Address search with autocomplete
   - Zipcode search
   - Provider switching (Google ↔ Azure)
   - Map navigation (pan, zoom, drag)

2. **Stage 2: Search Area Definition**
   - Polygon drawing tool
   - Circle radius creation
   - Boundary visualization
   - Tile estimation

3. **Stage 3: Detection Processing**
   - Start detection workflow
   - Progress tracking
   - Cancellation capability
   - Results rendering

4. **Stage 4: Result Review**
   - Interactive highlighting (marker ↔ list)
   - Smooth scrolling
   - Confidence filtering
   - Checkbox selection
   - Address grouping

5. **Stage 5: Export & Cleanup**
   - CSV export
   - KML export
   - YOLO dataset export
   - Session cleanup

### Performance Validation
- [ ] Page load time ≤ 3 seconds
- [ ] Provider switch time ≤ 2 seconds
- [ ] Module loading time acceptable
- [ ] Memory usage stable (use Chrome DevTools Memory Profiler)
- [ ] No memory leaks during provider switching (validated in TASK-041)

### Cross-Browser Testing
- [ ] Chrome/Edge (primary)
- [ ] Firefox
- [ ] Safari (if available)

---

## Rollback Plan

### Git Strategy
```bash
# Before each stage
git checkout -b task-038-stage-N
git commit -m "TASK-038 Stage N: [description]"

# If stage fails validation
git checkout main
git branch -D task-038-stage-N

# If stage succeeds
git checkout main
git merge task-038-stage-N
git push origin main
git tag task-038-stage-N-complete
```

### Emergency Rollback
If critical bug discovered after multiple stages:
```bash
# Identify last known good commit
git log --oneline

# Revert to specific commit
git revert <commit-hash>

# Or reset completely (destructive)
git reset --hard <commit-hash>
```

### Staged Rollback
If only specific module has issues:
1. Identify problematic module
2. Revert just that file's changes
3. Restore original code from towerscout.js
4. Continue with other modules

**Safety Net**: Keep original `towerscout.js` as `towerscout.BACKUP.js` until full validation complete

---

## Success Criteria

### Code Quality Metrics
- [ ] **File Size**: Main `towerscout.js` reduced from 5,272 to <800 lines
- [ ] **Module Count**: 22 files organized in 6 directories
- [ ] **Code Duplication**: Zero duplicate `getBoundariesStr()` implementations
- [ ] **Error Handling**: 100% using TowerScoutErrorHandler (no legacy `fatalError()`)
- [ ] **Magic Numbers**: 100% moved to CONFIG object
- [ ] **Dependencies**: Clear dependency graph with no circular dependencies

### Functionality Metrics
- [ ] **Zero Regressions**: All existing functionality preserved
- [ ] **All User Journeys**: Stages 1-5 complete successfully
- [ ] **Provider Parity**: Google Maps and Azure Maps feature-identical
- [ ] **Performance**: No degradation from baseline (page load, detection workflow)
- [ ] **Memory**: No new leaks introduced (validated with Chrome DevTools)

### Documentation Metrics
- [ ] **JSDoc Coverage**: All exported functions/classes documented
- [ ] **README Update**: Module structure documented
- [ ] **Migration Guide**: Document for future developers
- [ ] **Decision Records**: Architectural choices documented in `.agent_work/decisions/`

### Validation Metrics
- [ ] **Stage 1**: All managers functional (100% validation checks pass)
- [ ] **Stage 2**: Both providers working (100% user journey Stage 1-2)
- [ ] **Stage 3**: All boundary types renderıng (100% boundary tests)
- [ ] **Stage 4**: Detection workflow complete (100% user journey Stage 3-4)
- [ ] **Stage 5**: All utilities functional (100% complete user journey)

---

## Risk Mitigation

### High-Risk Areas

**1. Provider State Management (ProviderStateManager)**
- **Risk**: Race conditions, initialization timing issues
- **Mitigation**: Already battle-tested in TASK-041, no logic changes
- **Validation**: Use same tests from TASK-041

**2. Detection Array References**
- **Risk**: Global array access patterns break when moved to modules
- **Mitigation**: Export arrays from modules, update all references carefully
- **Validation**: Search codebase for all `Detection_detections` references before extraction

**3. HTML Template Integration**
- **Risk**: Module loading breaks inline event handlers
- **Mitigation**: Define global functions that wrap module exports
- **Example**:
  ```javascript
  // In towerscout.js (make available globally for inline handlers)
  window.Detection = { showDetection: Detection.showDetection };
  ```

**4. Circular Dependencies**
- **Risk**: Modules import each other circularly
- **Mitigation**: Follow dependency graph strictly (Level 1 → Level 8)
- **Validation**: Use `madge` tool to detect circular dependencies
  ```bash
  npm install -g madge
  madge --circular webapp/js/
  ```

### Medium-Risk Areas

**1. Error Handler Consolidation**
- **Risk**: Legacy `fatalError()` calls scattered throughout
- **Mitigation**: Global search and replace, comprehensive testing
- **Validation**: `grep -r "fatalError" webapp/js/` should return 0 results after Stage 5

**2. Configuration Management**
- **Risk**: Missing magic number extraction
- **Mitigation**: Code review for hard-coded values
- **Validation**: ESLint rule to detect magic numbers

**3. Import Path Resolution**
- **Risk**: Relative paths break when files move
- **Mitigation**: Test all imports after each file movement
- **Validation**: Browser console should show no 404 errors

### Low-Risk Areas

**1. Boundary Classes**
- **Risk**: Simple class hierarchy, minimal dependencies
- **Mitigation**: Direct extraction with minimal changes

**2. Utility Functions**
- **Risk**: Pure functions, no side effects
- **Mitigation**: Unit tests for validation

---

## Timeline Estimate

### By Stage (Conservative Estimates)

| Stage | Description | Estimated Time | Risk Level |
|-------|-------------|----------------|------------|
| 1 | Extract Managers | 6 hours | LOW |
| 2 | Extract Providers | 5 hours | MEDIUM |
| 3 | Extract Boundaries | 3 hours | LOW |
| 4 | Extract Detections | 4 hours | MEDIUM |
| 5 | Extract UI/Utils, Consolidate | 5 hours | MEDIUM |
| **Total** | **Implementation** | **23 hours** | **MEDIUM** |

### Additional Time Allocation

| Activity | Estimated Time |
|----------|----------------|
| HTML template updates | 1 hour |
| Module loading setup | 1 hour |
| Comprehensive testing | 3 hours |
| Documentation updates | 2 hours |
| **Total Overhead** | **7 hours** |

### **Grand Total: 30 hours**

**Sprint Allocation**: 14-day sprint, ~2-3 hours per day = 28-42 hours available  
**Margin**: 30 hours fits comfortably within sprint capacity

### Phased Approach (Recommended)

**Week 1 (Days 1-7)**:
- Days 1-2: Stage 1 (Managers) + validation
- Days 3-4: Stage 2 (Providers) + validation
- Day 5: Stage 3 (Boundaries) + validation
- Days 6-7: Buffer for issues, testing

**Week 2 (Days 8-14)**:
- Days 8-9: Stage 4 (Detections) + validation
- Days 10-11: Stage 5 (UI/Utils) + consolidation
- Days 12-13: Comprehensive testing, documentation
- Day 14: Final validation, task completion

---

## Dependencies & Prerequisites

### External Dependencies (Already Available)
- ✅ Google Maps JavaScript API
- ✅ Azure Maps Web SDK
- ✅ jQuery 3.5.1 (to be removed in future sprint)

### Internal Dependencies (Must be Complete)
- ✅ TASK-041: ProviderStateManager foundation
- ✅ TASK-037: User journey validation and bug fixes
- ✅ TASK-040: Azure Maps visual consistency
- ✅ TASK-035: Memory management improvements

### Development Tools Needed
- **Code Editor**: VS Code or similar with ES6 module support
- **Browser**: Chrome/Edge with DevTools (for testing)
- **Git**: Version control for staging/rollback
- **Optional**: `madge` for circular dependency detection
- **Optional**: `webpack` for future bundling (not needed for refactoring)

### Knowledge Prerequisites
- ES6 module syntax (import/export)
- Class inheritance patterns
- Async/await patterns
- Git branching and merging
- Browser DevTools for debugging

---

## Post-Refactoring Opportunities

### Immediate Benefits (Sprint 02)
- ✅ Easier code navigation (find specific functionality)
- ✅ Faster feature development (isolated modules)
- ✅ Better testing capabilities (unit test individual modules)
- ✅ Reduced cognitive load (smaller files)

### Sprint 03+ Enhancements
1. **TypeScript Migration** (8-12 hours)
   - Add type definitions for all modules
   - Catch type errors at compile time
   - Improve IDE autocomplete

2. **jQuery Removal** (4-6 hours)
   - Replace remaining jQuery selectors with vanilla JS
   - Reduce bundle size by ~30KB
   - Remove external dependency

3. **Comprehensive Unit Testing** (16-20 hours)
   - Jest/Mocha test suites for all utilities
   - Mock providers for boundary testing
   - Automated regression testing

4. **Build Process** (4-6 hours)
   - Webpack bundling for production
   - Minification and tree-shaking
   - Source maps for debugging

5. **Performance Optimization** (6-8 hours)
   - Lazy loading for provider modules
   - Code splitting for faster initial load
   - Service worker for offline capability

6. **Additional Providers** (8-12 hours each)
   - Mapbox GL JS support
   - Leaflet support
   - OpenStreetMap support

---

## Approval & Sign-Off

### Design Review Checklist
- [ ] Module structure logical and maintainable
- [ ] Dependency graph acyclic and clean
- [ ] Migration strategy safe and incremental
- [ ] Testing strategy comprehensive
- [ ] Rollback plan defined
- [ ] Timeline realistic
- [ ] Risk mitigation adequate
- [ ] Success criteria measurable

### Approval Required Before Implementation
**Reviewer**: User / Project Stakeholder  
**Date Submitted**: February 18, 2026  
**Status**: ⏳ PENDING APPROVAL

**Approval Signature**: ___________________________  
**Date**: ___________________________

---

## Appendix A: File Organization Reference

### Complete Directory Structure (Post-Refactoring)

```
webapp/js/
├── towerscout.js                    # Main application (~500-800 lines)
├── config.js                        # Configuration constants (~100 lines)
│
├── managers/                        # State and lifecycle management
│   ├── ProviderStateManager.js      # Provider switching logic (~300 lines)
│   ├── TimerManager.js              # Timer lifecycle (~70 lines)
│   ├── EventListenerManager.js      # Event listener tracking (~100 lines)
│   └── ErrorHandler.js              # Centralized error handling (~200 lines)
│
├── providers/                       # Map provider implementations
│   ├── TSMap.js                     # Abstract base class (~150 lines)
│   ├── AzureMap.js                  # Azure Maps implementation (~1,400 lines)
│   └── GoogleMap.js                 # Google Maps implementation (~500 lines)
│
├── boundaries/                      # Search area boundary classes
│   ├── Boundary.js                  # Base boundary class (~80 lines)
│   ├── PolygonBoundary.js           # Polygon boundaries (~60 lines)
│   ├── CircleBoundary.js            # Circle boundaries (~90 lines)
│   └── SimpleBoundary.js            # Rectangle boundaries (~30 lines)
│
├── detection/                       # Detection result management
│   ├── PlaceRect.js                 # Base class for map rectangles (~100 lines)
│   ├── Tile.js                      # Tile processing (~120 lines)
│   └── Detection.js                 # Detection results and UI (~400 lines)
│
├── ui/                              # User interface components
│   ├── about.js                     # About screen overlay (~120 lines)
│   ├── progress.js                  # Detection progress tracking (~150 lines)
│   └── downloads.js                 # Export functionality (~300 lines)
│
└── utils/                           # Utility functions
    ├── geometry.js                  # Geographic calculations (~100 lines)
    ├── validation.js                # Input validation (~150 lines)
    └── search.js                    # Provider-agnostic search (~200 lines)
```

**Total Files**: 22 (vs. 1 monolithic file)  
**Total Lines**: ~5,400 lines (vs. 5,272 lines - slight increase due to imports/exports)  
**Average File Size**: ~245 lines (vs. 5,272 lines)  
**Largest File**: AzureMap.js (~1,400 lines - acceptable for complex provider implementation)

---

## Appendix B: Import/Export Patterns

### Configuration Module Pattern
```javascript
// config.js
export const CONFIG = { /* ... */ };
export const API_ENDPOINTS = { /* ... */ };

// Consuming module
import { CONFIG, API_ENDPOINTS } from './config.js';
```

### Class + Singleton Pattern
```javascript
// TimerManager.js
export class TimerManager { /* ... */ }
export const timerManager = new TimerManager();

// Consuming module
import { timerManager } from './managers/TimerManager.js';
// OR if you need the class
import { TimerManager, timerManager } from './managers/TimerManager.js';
```

### Class + Array Pattern
```javascript
// Detection.js
export class Detection extends PlaceRect { /* ... */ }
export let Detection_detections = [];
export let Detection_minConfidence = 0.15;
export let Detection_current = null;

// Consuming module
import { 
  Detection, 
  Detection_detections, 
  Detection_minConfidence, 
  Detection_current 
} from './detection/Detection.js';
```

### Inheritance Pattern
```javascript
// Boundary.js
export class Boundary { /* ... */ }

// PolygonBoundary.js
import { Boundary } from './Boundary.js';
export class PolygonBoundary extends Boundary { /* ... */ }

// CircleBoundary.js
import { PolygonBoundary } from './PolygonBoundary.js';
export class CircleBoundary extends PolygonBoundary { /* ... */ }
```

---

## Appendix C: Global Window Exposure (for Inline Event Handlers)

Some HTML templates use inline event handlers like `onclick="Detection.showDetection(5)"`. These require global window exposure.

### Pattern in towerscout.js (after all imports)
```javascript
// Expose necessary functions/classes to global scope for inline event handlers
window.Detection = Detection;
window.Tile = Tile;
window.adjustConfidence = adjustConfidence;
window.changeReviewMode = changeReviewMode;
// ... etc for any function called from HTML templates
```

### Better Long-Term Solution (Sprint 03+)
Replace inline event handlers with:
```javascript
// In towerscout.js initialization
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-detection-id]').forEach(element => {
    element.addEventListener('click', (e) => {
      const id = e.target.dataset.detectionId;
      Detection.showDetection(id, true);
    });
  });
});
```

---

## Appendix D: Circular Dependency Detection

### Using Madge Tool
```bash
# Install globally
npm install -g madge

# Check for circular dependencies
madge --circular webapp/js/

# Generate dependency graph (requires Graphviz)
madge --image graph.svg webapp/js/

# Check for orphaned modules
madge --orphans webapp/js/
```

### Expected Output (No Circular Dependencies)
```
✔ No circular dependencies found!
```

### If Circular Dependencies Found
```
✖ Found 1 circular dependency!

1) towerscout.js > providers/AzureMap.js > detection/Detection.js > towerscout.js
```

**Resolution**: Refactor to break cycle (e.g., use events, dependency injection, or shared state module)

---

## Appendix E: Validation Test Matrix

### Automated Validation Script
```javascript
// validate-refactoring.js
import { CONFIG } from './config.js';
import { timerManager } from './managers/TimerManager.js';
import { eventManager } from './managers/EventListenerManager.js';
import { TowerScoutErrorHandler } from './managers/ErrorHandler.js';
import { providerManager } from './managers/ProviderStateManager.js';
import { AzureMap } from './providers/AzureMap.js';
import { GoogleMap } from './providers/GoogleMap.js';
import { CircleBoundary } from './boundaries/CircleBoundary.js';
import { Detection, Detection_detections } from './detection/Detection.js';
import { Tile, Tile_tiles } from './detection/Tile.js';

function validateRefactoring() {
  const results = {
    modules: {},
    functionality: {},
    performance: {}
  };

  // Module Existence Checks
  results.modules.config = typeof CONFIG !== 'undefined';
  results.modules.timerManager = typeof timerManager !== 'undefined';
  results.modules.eventManager = typeof eventManager !== 'undefined';
  results.modules.errorHandler = typeof TowerScoutErrorHandler !== 'undefined';
  results.modules.providerManager = typeof providerManager !== 'undefined';
  results.modules.azureMap = typeof AzureMap !== 'undefined';
  results.modules.googleMap = typeof GoogleMap !== 'undefined';
  results.modules.boundaries = typeof CircleBoundary !== 'undefined';
  results.modules.detection = typeof Detection !== 'undefined';
  results.modules.tile = typeof Tile !== 'undefined';

  // Functionality Checks
  results.functionality.configValues = CONFIG.RETRY_DELAY_MS === 2000;
  results.functionality.timerCreation = timerManager.timers.size === 0;
  results.functionality.eventTracking = eventManager.listeners.size === 0;
  results.functionality.detectionArray = Array.isArray(Detection_detections);
  results.functionality.tileArray = Array.isArray(Tile_tiles);

  // Performance Metrics (basic)
  results.performance.moduleLoadTime = performance.now();

  return results;
}

// Run validation
console.log('🔍 Validating refactoring...');
const validation = validateRefactoring();
console.log('✅ Validation results:', validation);

// Check for failures
const failedModules = Object.entries(validation.modules)
  .filter(([key, value]) => !value)
  .map(([key]) => key);

if (failedModules.length > 0) {
  console.error('❌ Failed module checks:', failedModules);
} else {
  console.log('✅ All modules loaded successfully');
}

export { validateRefactoring };
```

### Manual Test Checklist (Printable)

```
TASK-038 Refactoring Validation Checklist
==========================================

[ ] Stage 1: Managers
    [ ] Page loads without errors
    [ ] timerManager accessible
    [ ] eventManager accessible
    [ ] TowerScoutErrorHandler accessible
    [ ] providerManager accessible
    [ ] Provider switching works

[ ] Stage 2: Providers
    [ ] Google Maps initializes
    [ ] Azure Maps initializes
    [ ] Provider switching functional
    [ ] getBoundariesStr() inherited correctly
    [ ] No duplicate method implementations

[ ] Stage 3: Boundaries
    [ ] Circle boundaries render
    [ ] Polygon boundaries render
    [ ] SimpleBoundary works
    [ ] Boundary serialization correct
    [ ] Geometry utilities functional

[ ] Stage 4: Detections
    [ ] Detections render on map
    [ ] Detection list generates
    [ ] Highlighting works
    [ ] Tile navigation works
    [ ] Arrays export correctly

[ ] Stage 5: UI & Utilities
    [ ] About screen functional
    [ ] Progress tracking works
    [ ] Downloads generate correctly
    [ ] Search functional
    [ ] Validation prevents bad inputs

[ ] Complete User Journey
    [ ] Search for location
    [ ] Draw polygon boundary
    [ ] Run detection
    [ ] Review results
    [ ] Export data
    [ ] Switch providers
    [ ] No console errors

Tester: ___________________
Date: _____________________
Result: PASS / FAIL
```

---

## End of Design Document

**Next Steps**:
1. ✅ Design review and approval
2. ⏳ Create task file: `TASK-038-frontend-refactoring.md`
3. ⏳ Update `current-tasks.md` status to IN_PROGRESS
4. ⏳ Begin Stage 1 implementation

**Questions? Concerns?** Address before beginning implementation.
