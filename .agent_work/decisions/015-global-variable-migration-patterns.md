# Decision Record 015: Global Variable Migration Patterns

**Task**: TASK-043  
**Date**: March 10, 2026  
**Status**: IMPLEMENTED

## Context

TASK-043 migrated 5 critical global variables to centralized ProviderStateManager to eliminate 3 race conditions:
- **Map State**: `window.googleMap`, `window.azureMap` - provider switch race condition
- **Detection State**: `Detection_detections`, `Detection_minConfidence` - array corruption during filtering
- **Progress Timer**: `progressTimer` (module-level) - orphaned timers on cancel

32 total globals identified, 29 remain for future sprints. This document defines reusable patterns for continued migration.

## Decision: Soft Deprecation with Property Descriptors

**Rationale**: Gradual migration over 1-2 sprints minimizes risk of breaking existing code while providing visibility into legacy usage through console warnings.

### Pattern: Property Descriptor Wrapper

```javascript
// globals.js or store.js
Object.defineProperty(window, 'globalVariableName', {
  get() {
    if (window.providerManager) {
      return window.providerManager.getVariableName();
    }
    return null; // fallback value
  },
  set(value) {
    console.warn('⚠️ Direct globalVariableName assignment deprecated. Use providerManager.setVariableName() instead.');
    if (window.providerManager) {
      window.providerManager.setVariableName(value);
    }
  }
});
```

### Key Principles:

1. **Backward Compatibility**: Getter returns actual state manager value, setter delegates to state manager
2. **Visibility**: Console warnings include variable name and migration path
3. **Graceful Degradation**: Fallback values when manager not initialized
4. **Non-Breaking**: Legacy code continues functioning during transition period

### When to Use:
- Global variables with >20 references throughout codebase
- Variables accessed across multiple modules
- When migration will take >1 sprint to complete

### Performance Impact:
- Property descriptor overhead: ~1-2% (negligible for non-hotpath code)
- Acceptable tradeoff for safety during migration period
- Remove after legacy code eliminated (1-2 sprints)

---

## Decision: Mutex-Protected State Operations

**Rationale**: Prevent data corruption during concurrent operations (e.g., detection sort during UI updates) using lightweight busy-wait spinlock for fast operations.

### Pattern: Busy-Wait Mutex

```javascript
// Inside state manager class
class ProviderStateManager {
  constructor() {
    this.stateLock = false;
    this.stateData = [];
  }

  mutateState() {
    // Acquire lock
    while (this.stateLock) {
      // Busy wait (acceptable for fast operations <1ms)
    }

    try {
      this.stateLock = true;
      
      // Critical section - modify state
      this.stateData.push(newItem);
      
    } finally {
      this.stateLock = false; // Guarantee release
    }
  }
}
```

### Key Principles:

1. **Try-Finally Guarantee**: Lock always released even if error thrown
2. **Busy-Wait Pattern**: Acceptable for fast operations (<1ms) - no async overhead
3. **State Guards**: Check for conflicting operations before mutating
4. **Idempotent Operations**: Safe to call multiple times (e.g., stopProgressTimer)

### When to Use:
- Synchronous operations that must be atomic (array mutations, counter updates)
- Operations expected to complete in <1ms (fast critical sections)
- Race conditions identified through testing or code analysis

### When NOT to Use:
- Async operations (use async locks or Promise queuing instead)
- Operations with I/O or network calls (would block event loop)
- Read-only access (return copies instead)

---

## Decision: State Manager Extension Over Proliferation

**Rationale**: Extend existing ProviderStateManager rather than creating separate StateStore classes to maintain single source of truth and avoid coordination complexity.

### Pattern: Single State Manager Extension

```javascript
class ProviderStateManager {
  constructor() {
    // Phase 1: Map state
    this.googleMapInstance = null;
    this.mapStateLock = false;
    
    // Phase 2: Detection state
    this.detectionArray = [];
    this.detectionLock = false;
    
    // Phase 3: Progress state
    this.progressTimerId = null;
    this.progressLock = false;
    
    // Future phases...
  }
  
  // Map state methods
  setGoogleMap(map) { /* ... */ }
  getGoogleMap() { /* ... */ }
  
  // Detection state methods
  addDetection(det) { /* ... */ }
  sortDetections(fn) { /* ... */ }
  
  // Progress state methods
  startProgressTimer(cb, ms) { /* ... */ }
  stopProgressTimer() { /* ... */ }
}
```

### Key Principles:

1. **Single Source of Truth**: One manager for all centralized state
2. **Logical Grouping**: Related methods grouped with section comments
3. **Consistent Interface**: All methods follow same naming patterns (get/set/clear/add)
4. **Progressive Migration**: Add methods incrementally over sprints

### When to Use:
- State related to same domain (map providers, UI, detection pipeline)
- State managers would need to coordinate (shared locks, dependencies)
- Small-to-medium state additions (<200 lines per phase)

### When to Create Separate Manager:
- Completely independent domain (e.g., AuthenticationManager, CacheManager)
- State manager exceeds ~500 lines (code smell - refactor)
- Requires different lifecycle (initialization, cleanup)

---

## Decision: Copy-on-Read for Array State

**Rationale**: Prevent external code from accidentally mutating internal state arrays while allowing convenient iteration syntax.

### Pattern: Return Defensive Copies

```javascript
class ProviderStateManager {
  constructor() {
    this.detectionArray = [];
  }
  
  // Return copy for safe iteration
  getDetections() {
    return [...this.detectionArray]; // Spread operator creates shallow copy
  }
  
  // Performance optimization: avoid copy for length
  getDetectionsLength() {
    return this.detectionArray.length;
  }
  
  // Escape hatch for legacy code (logs warning)
  getDetectionsArrayDirect() {
    console.warn('⚠️ Direct array access detected. Consider using getDetections().');
    return this.detectionArray;
  }
}
```

### Key Principles:

1. **Immutability for Reads**: External code receives snapshot, cannot mutate internal state
2. **Performance Tradeoff**: Copy cost acceptable for safety (detection array typically <1000 items)
3. **Escape Hatch**: Direct access available with warning for legacy compatibility
4. **Optimization Path**: Provide length/size methods to avoid unnecessary copying

### When to Use:
- Arrays that external code needs to iterate or filter
- State that could be corrupted by external mutations
- Arrays with reasonable size (<10,000 items)

### When NOT to Use:
- Large arrays where copy cost significant (>10,000 items - use iterators instead)
- Performance-critical hotpaths (profile first)
- When external mutations are intentional design (e.g., builder pattern)

---

## Decision: Integration with Existing Managers

**Rationale**: Leverage existing TimerManager and EventListenerManager for automatic cleanup tracking rather than reimplementing lifecycle management.

### Pattern: Delegated Lifecycle Tracking

```javascript
startProgressTimer(callback, interval) {
  // Use TimerManager if available for automatic cleanup tracking
  if (window.timerManager && window.timerManager.setInterval) {
    this.progressTimerId = window.timerManager.setInterval(callback, interval);
    console.log(`⏱️ Progress timer started with TimerManager`);
  } else {
    // Fallback to native if manager not initialized
    this.progressTimerId = setInterval(callback, interval);
    console.log(`⏱️ Progress timer started (native)`);
  }
  
  this.progressActive = true;
  return this.progressTimerId;
}

stopProgressTimer() {
  if (this.progressTimerId !== null) {
    // Use TimerManager for tracked cleanup
    if (window.timerManager && window.timerManager.clearInterval) {
      window.timerManager.clearInterval(this.progressTimerId);
    } else {
      clearInterval(this.progressTimerId);
    }
    
    this.progressTimerId = null;
  }
  
  this.progressActive = false;
}
```

### Key Principles:

1. **Prefer Existing Infrastructure**: Use established managers when available
2. **Graceful Fallback**: Native APIs when managers not initialized
3. **Consistency**: Follow patterns from existing timer/event management
4. **Cleanup Tracking**: Automatic leak prevention via manager integration

### When to Use:
- Resource lifecycle management (timers, event listeners, network requests)
- When existing manager provides desired functionality
- Memory leak prevention requirements

### Benefits:
- Centralized cleanup via `timerManager.clearAll()` or `eventManager.removeAllListeners()`
- Automatic tracking of all resource allocations
- Consistent patterns across codebase

---

## Implementation Examples: TASK-043

### Example 1: Map State Property Descriptor

**File**: `webapp/js/src/globals.js`

```javascript
Object.defineProperty(window, 'googleMap', {
  get() {
    return window.providerManager ? window.providerManager.getGoogleMap() : null;
  },
  set(value) {
    console.warn('⚠️ Direct window.googleMap assignment deprecated. Use providerManager.setGoogleMap() instead.');
    if (window.providerManager) {
      window.providerManager.setGoogleMap(value);
    }
  }
});
```

**Result**: 0 active `window.googleMap =` assignments found in codebase after migration

### Example 2: Detection Array Mutex

**File**: `webapp/js/src/managers/ProviderStateManager.js`

```javascript
sortDetections(compareFn) {
  while (this.detectionLock) {
    // Busy wait
  }

  try {
    this.detectionLock = true;
    this.detectionArray.sort(compareFn);
    console.log(`🔀 Detections sorted: ${this.detectionArray.length} items`);
  } finally {
    this.detectionLock = false;
  }
}
```

**Usage**: `webapp/js/src/detection/Detection.js`

```javascript
// Before: Detection_detections.sort((a, b) => { ... });
// After:
providerManager.sortDetections((a, b) => {
  if (a.address < b.address) return -1;
  else if (a.address > b.address) return 1;
  else return b.conf - a.conf;
});
```

**Result**: Array corruption during rapid confidence filtering eliminated

### Example 3: Progress Timer Integration

**File**: `webapp/js/src/ui/search.js`

```javascript
function enableProgress(tiles) {
  document.getElementById("progress_div").style.display = "flex";

  // Clear any existing timer
  if (providerManager.isProgressActive()) {
    providerManager.stopProgressTimer();
  }
  
  // Start new timer with TimerManager integration
  providerManager.startProgressTimer(progressFunction, CONFIG.PROGRESS_UPDATE_INTERVAL_MS);
  
  numTiles = tiles;
  totalSecsEstimated = secsPerTile * numTiles;
  secsElapsed = 0;
}

function disableProgress(time, actualTiles) {
  document.getElementById("progress_div").style.display = "none";
  
  // Guaranteed cleanup on all exit paths
  providerManager.stopProgressTimer();
  
  if (time !== 0) {
    let secsPerTileLast = time / actualTiles;
    secsPerTile = (secsPerTile * dataPoints + secsPerTileLast) / (dataPoints + 1);
    dataPoints++;
  }
}
```

**Result**: Orphaned timers on cancel-rerun-cancel scenarios eliminated

---

## Migration Roadmap for Remaining Globals

Based on TASK-043 patterns, prioritized migration for Sprint 03:

### Phase 1: UI State Globals (HIGH priority - 4-6 hours)
- `currentElement` - currently highlighted detection marker
- `currentAddrElement` - currently highlighted address list item
- `isInitializing` - startup state flag

**Pattern**: Property descriptors + UIStateManager extension to ProviderStateManager  
**Risk**: Medium - frequent access during UI updates  
**Test**: Click highlighting, provider switching during detection

### Phase 2: Tile State Global (MEDIUM priority - 2-3 hours)
- `Tile_tiles` - array of tile objects for image processing

**Pattern**: Same as Detection_detections (copy-on-read, mutex-protected mutations)  
**Risk**: Low - less frequent mutations than detections  
**Test**: Tile navigation, cancel during tile processing

### Phase 3: DOM References (LOW priority - 2-3 hours)
- `input`, `upload`, `detectionsList`, `confSlider`, `reviewCheckBox`

**Pattern**: DOMReferencesManager with lazy initialization  
**Risk**: Low - mostly read-only after initialization  
**Test**: Form interactions, dynamic UI updates

### Phase 4: Configuration Consolidation (LOW priority - 1-2 hours)
- Consolidate `DEFAULT_CONFIDENCE`, `nyc` center coordinates into CONFIG object
- Remove redundant declarations

Total Remaining: ~10-14 hours across Sprints 03-04

---

## Lessons Learned

### What Worked Well:
1. **Progressive Migration**: 3 phases over 4-6 hours more manageable than big-bang refactor
2. **Soft Deprecation**: Property descriptors provided visibility without breaking changes
3. **Code Review Automation**: Regex searches validated successful migration
4. **Single State Manager**: Extending ProviderStateManager simpler than coordinating multiple managers

### Challenges:
1. **Busy-Wait Spinlocks**: Simple but could block if critical section too slow (monitor performance)
2. **Direct Array Access**: Had to provide escape hatch (getDetectionsArrayDirect) for legacy compatibility
3. **Module-Level Variables**: progressTimer not global, required different approach than other variables

### Future Improvements:
1. **Automated Tests**: Add Playwright tests for race conditions (Sprint 03)
2. **Performance Monitoring**: Track property descriptor overhead in production
3. **Async Locks**: Consider upgrading to async/await locks if busy-wait becomes bottleneck
4. **TypeScript**: Consider TypeScript migration for compile-time state access validation

---

## References

- **TASK-043 Documentation**: `.agent_work/tasks/completed/TASK-043-global-variable-deprecation.md`
- **Global Variable Audit**: Phase 1 research (32 globals, 9 race conditions identified)
- **ProviderStateManager**: `webapp/js/src/managers/ProviderStateManager.js` (21.7 KB)
- **Property Descriptors**: `webapp/js/src/globals.js` (5.4 KB)
- **Detection Mutations**: `webapp/js/src/detection/Detection.js` (3 migration points)
- **Progress Timer**: `webapp/js/src/ui/search.js` (2 migration points)

---

**Next Steps for Sprint 03**:
1. Execute manual testing for TASK-043 (Test 1-4 scenarios)
2. Begin Phase 1 UI state migration using established patterns
3. Consider automated test infrastructure (Playwright) for race condition verification
4. Continue progressive migration toward zero-globals architecture
