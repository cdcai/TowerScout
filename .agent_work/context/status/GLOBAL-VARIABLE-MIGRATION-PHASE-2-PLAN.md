# Global Variable Migration Phase 2: Tile State

**Date**: March 16, 2026  
**Sprint**: Sprint 03  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 hours  
**Context**: Following Phase 1 (UI State) and TASK-043 cleanup completion

---

## Objective

Migrate `Tile_tiles` array to centralized ProviderStateManager for consistent state management and better testability.

## Background

**Phase 1 (Completed)**: UI state variables (currentElement, currentAddrElement, isInitializing)  
**TASK-043 Cleanup (Completed)**: Detection_detections, Detection_minConfidence, azureMap  
**Phase 2 (Current)**: Tile_tiles array migration

The pattern is proven and context is fresh from previous work.

---

## Scope Analysis

### Tile_tiles Usage (33 occurrences)

**Initialization** (3 occurrences):
1. `globals.js:23` - `window.Tile_tiles = []`
2. `store.js:36` - `window.Tile_tiles = []`
3. `towerscout.js:3193` - `let Tile_tiles = []` (duplicate declaration - should remove)

**Array Access by Index** (18 occurrences):
- `Detection.js:188-189` (2x) - Access tile metadata
- `Tile.js:29` - Loop iteration
- `Tile.js:51, 62, 73` - Navigation (centerInMap)
- `GoogleMap.js:511` - Get tile for processing
- `AzureMap.js:1181` - Get tile for processing
- `export.js:318` (3x) - Get tile metadata for export
- `towerscout.js:2200, 2700, 4109, 4202` (7x) - Get tile by ID

**Array Length** (11 occurrences):
- `Tile.js:13` - Clear array (`Tile_tiles.length = 0`)
- `Tile.js:20` - Get current length for new ID
- `Tile.js:28, 48, 59, 70` - Loop/navigation calculations
- `towerscout.js:3450, 3452` - Progress display

**Array Push** (1 occurrence):
- `Tile.js:22` - Add new tile

**Type Check** (1 occurrence):
- `AzureMap.js:1146` - Conditional check for undefined/empty

---

## Implementation Strategy

### ProviderStateManager Extensions

Add tile state management methods (similar to detection methods):

```javascript
// Tile State Management (Phase 2 - Sprint 03)
this.tileArray = [];
this.tileLock = false;

getTiles() {
  // Returns copy for safe iteration
  return [...this.tileArray];
}

getTilesArrayDirect() {
  // Direct access for index operations (with warning)
  console.warn('⚠️ Direct tile array access detected. Consider using getTiles() for iteration.');
  return this.tileArray;
}

getTilesLength() {
  // Optimized length access without copying
  return this.tileArray.length;
}

addTile(tile) {
  // Thread-safe tile addition
  while (this.tileLock) {}
  try {
    this.tileLock = true;
    this.tileArray.push(tile);
  } finally {
    this.tileLock = false;
  }
}

clearTiles() {
  // Thread-safe array clearing
  while (this.tileLock) {}
  try {
    this.tileLock = true;
    this.tileArray.length = 0;
    console.log('🧹 Tile array cleared');
  } finally {
    this.tileLock = false;
  }
}

setTiles(tiles) {
  // Replace entire array with validation
  if (!Array.isArray(tiles)) {
    throw new Error('Tiles must be an array');
  }
  this.tileArray = tiles;
  console.log(`✅ Tile array updated: ${tiles.length} items`);
}
```

### Property Descriptor in globals.js

Add soft deprecation pattern:

```javascript
Object.defineProperty(window, 'Tile_tiles', {
  get() {
    if (window.providerManager) {
      return window.providerManager.getTilesArrayDirect();
    }
    return [];
  },
  set(value) {
    console.warn('⚠️ Direct Tile_tiles assignment deprecated. Use providerManager.setTiles() instead.');
    if (window.providerManager) {
      window.providerManager.setTiles(value);
    }
  }
});
```

### Migration Categories

**Category 1: Array Access (18 updates)**
- **Pattern**: `Tile_tiles[index]` → `providerManager.getTilesArrayDirect()[index]`
- **Files**: Detection.js (2), Tile.js (4), GoogleMap.js (1), AzureMap.js (1), export.js (3), towerscout.js (7)

**Category 2: Array Length (10 updates)**
- **Pattern**: `Tile_tiles.length` → `providerManager.getTilesLength()`
- **Exception**: `Tile_tiles.length = 0` → `providerManager.clearTiles()`
- **Files**: Tile.js (7), towerscout.js (2)

**Category 3: Array Push (1 update)**
- **Pattern**: `Tile_tiles.push(tile)` → `providerManager.addTile(tile)`
- **Files**: Tile.js (1)

**Category 4: Type Check (1 update)**
- **Pattern**: Keep as-is (property descriptor handles backward compatibility)
- **Files**: AzureMap.js (1)

**Category 5: Duplicate Declaration (1 removal)**
- **Pattern**: Remove `let Tile_tiles = []` from towerscout.js
- **Files**: towerscout.js (1)

---

## Implementation Steps

### Step 1: Extend ProviderStateManager (30 min)

**File**: `webapp/js/src/managers/ProviderStateManager.js`

Add tile state management methods after detection methods (~80 lines).

### Step 2: Add Property Descriptor (10 min)

**File**: `webapp/js/src/globals.js`

Add Tile_tiles property descriptor after Phase 1 descriptors (~15 lines).

### Step 3: Migrate Array Access (30 min)

**18 updates across 6 files**:

**Detection.js** (2 updates):
```javascript
// Lines 188-189
if (providerManager.getTilesArrayDirect()[this.tile] && providerManager.getTilesArrayDirect()[this.tile].metadata) {
  meta = providerManager.getTilesArrayDirect()[this.tile].metadata;
}
```

**Tile.js** (4 updates):
```javascript
// Line 29
let t = providerManager.getTilesArrayDirect()[i]

// Lines 51, 62, 73
providerManager.getTilesArrayDirect()[index].centerInMap();
```

**GoogleMap.js** (1 update):
```javascript
// Line 511
let tile = providerManager.getTilesArrayDirect()[tileArrayIndex];
```

**AzureMap.js** (1 update):
```javascript
// Line 1181
let tile = providerManager.getTilesArrayDirect()[tileArrayIndex];
```

**export.js** (3 updates):
```javascript
// Line 318
const tiles = providerManager.getTilesArrayDirect();
const tileMeta = (tiles[det.tile] && tiles[det.tile].metadata) ? tiles[det.tile].metadata : '';
```

**towerscout.js** (7 updates):
```javascript
// Lines 2200, 2700, 4109
let/const tile = providerManager.getTilesArrayDirect()[tileId];

// Line 4202
const tiles = providerManager.getTilesArrayDirect();
let tileMeta = (tiles[det.tile] && tiles[det.tile].metadata) ? tiles[det.tile].metadata : '';
```

### Step 4: Migrate Array Length (10 updates - 20 min)

**Tile.js** (7 updates):
```javascript
// Line 13 (SPECIAL CASE - clear array)
providerManager.clearTiles();

// Line 20
this.id = (id !== undefined) ? id : providerManager.getTilesLength();

// Lines 28, 48, 59 (3x), 70
providerManager.getTilesLength()
```

**towerscout.js** (2 updates):
```javascript
// Lines 3450, 3452
disableProgress(processingTime, providerManager.getTilesLength());
```

### Step 5: Migrate Array Push (1 update - 5 min)

**Tile.js** (1 update):
```javascript
// Line 22
providerManager.addTile(this);
```

### Step 6: Remove Duplicate Declaration (1 update - 5 min)

**towerscout.js** (1 update):
```javascript
// Line 3193
// REMOVED: let Tile_tiles = [];  // Handled by property descriptor in globals.js
```

### Step 7: Rebuild Bundle (5 min)

```bash
cd c:/Users/bg90/TowerScout/webapp
node build.js
```

### Step 8: Testing (30-45 min)

Test workflow that exercises tile operations:
- Run detection (creates tiles)
- Review tiles (navigation)
- Export dataset (tile metadata)
- Provider switching (tile array persistence)

---

## Expected Outcomes

**Warning Reduction**: None expected (Tile_tiles had no soft deprecation warnings before)  
**Architecture Benefits**:
- Consistent state management pattern
- Thread-safe tile operations
- Better testability (mockable tile state)
- Completes Phase 2 of 3 in migration roadmap

**Bundle Size Change**: ~+1-2 KB (ProviderStateManager methods + property descriptor)

---

## Time Estimate

- Step 1: ProviderStateManager extension (30 min)
- Step 2: Property descriptor (10 min)
- Step 3: Array access migration (30 min)
- Step 4: Array length migration (20 min)
- Step 5: Array push migration (5 min)
- Step 6: Duplicate removal (5 min)
- Step 7: Bundle rebuild (5 min)
- Step 8: Testing (30-45 min)

**TOTAL**: 2-3 hours

---

## Success Criteria

- [ ] ProviderStateManager has 6 new tile methods
- [ ] Property descriptor added in globals.js
- [ ] All 31 usages migrated (18 access + 10 length + 1 push + 1 removal + 1 type check unchanged)
- [ ] Bundle rebuilds successfully (0 errors)
- [ ] All tile operations work correctly
- [ ] No regressions in detection, navigation, or export
- [ ] Phase 2 complete, ready for Phase 3

---

## Rollback Plan

Same as TASK-043 cleanup - backups created before modifications.
