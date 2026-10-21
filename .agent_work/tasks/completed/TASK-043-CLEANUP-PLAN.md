# TASK-043 Legacy Warning Cleanup Plan

**Date**: March 16, 2026  
**Sprint**: Sprint 03  
**Priority**: MEDIUM  
**Estimated Effort**: 2-4 hours  
**Context**: Following Phase 1 UI State Migration completion

---

## Objective

Clean up ~100+ console deprecation warnings from TASK-043 Sprint 02 soft deprecation pattern by migrating all legacy code to use ProviderStateManager methods.

## Background

**TASK-043 Sprint 02** introduced soft deprecation for:
1. `Detection_detections` array (direct access/assignment)
2. `Detection_minConfidence` (direct assignment)
3. `window.azureMap` (direct assignment)

Property descriptors in `globals.js` provide backward compatibility but emit warnings to guide migration. Phase 1 successfully migrated UI state variables (currentElement, currentAddrElement, isInitializing) with ZERO warnings - this cleanup extends that pattern to complete TASK-043.

---

## Scope Analysis

### Detection_detections Usage (22 actual usages - excluding .bak files)

**Direct Array Access** (needs `getDetectionsArrayDirect()` for index access):
1. `AzureMap.js:368` - `Detection_detections[props.detectionId]`
2. `AzureMap.js:1322` - `Detection_detections[props.detectionId]`
3. `Detection.js:96` (2x) - `Detection_detections[i].inside`, `.address`
4. `Detection.js:113` (2x) - `Detection_detections[i].inside`, `.address`
5. `Detection.js:118` - `let det = Detection_detections[i]`
6. `Detection.js:246` - `Detection_detections[id]` (conditional check)
7. `Detection.js:247` - `Detection_detections[id].highlight()`
8. `towerscout.js:4149` - `let det = Detection_detections[i]`
9. `export.js:212` - `const det = Detection_detections[i]`

**String Template for onclick handlers** (requires different approach):
10. `Detection.js:158` - `onclick='Detection_detections[" + det.id + "].selectAddr()'`
11. `Detection.js:197` - `onclick='Detection_detections[" + this.id + "].select()'`

**Direct Assignment** (needs `setDetections()`):
12. `AzureMap.js:1340` - `Detection_detections = dets`
13. `towerscout.js:2250` - `Detection_detections = dets`
14. `towerscout.js:2739` - `Detection_detections = dets`
15. `GoogleMap.js:640` - `Detection_detections = dets`

**Array Filter Method** (needs `getDetections()` for safe iteration):
16. `export.js:43` - `Detection_detections.filter(d => d.selected).length`

**Initialization** (no change needed - property descriptor handles it):
17. `store.js:31` - `window.Detection_detections = []`
18. `towerscout.js:3196` - `let Detection_detections = []` (duplicate declaration - should remove)

### Detection_minConfidence Usage (3 actual usages)

**Direct Assignment** (needs `setMinConfidence()`):
1. `DetectionList.js:16` - `Detection_minConfidence = confSlider.value / 100`

**Initialization** (no change needed):
2. `store.js:33` - `window.Detection_minConfidence = DEFAULT_CONFIDENCE`
3. `towerscout.js:3198` - `let Detection_minConfidence = DEFAULT_CONFIDENCE` (duplicate declaration - should remove)

### window.azureMap Usage (2 actual usages)

**Direct Assignment** (needs `setAzureMap()`):
1. **NONE** - store.js:10 and towerscout.js:50 are initializations (null), handled by property descriptor

**Initialization** (no change needed):
2. `store.js:10` - `window.azureMap = null`
3. `towerscout.js:50` - `window.azureMap = null` (duplicate declaration - should remove)

---

## Implementation Strategy

### Category 1: Direct Array Access (Index-based)

**Pattern**: `Detection_detections[i]` → `providerManager.getDetectionsArrayDirect()[i]`

**Rationale**: Index-based access requires direct reference. While `getDetectionsArrayDirect()` emits a warning, it's ONE consolidation warning vs. MANY individual warnings.

**Files to Update**:
- AzureMap.js (2 usages)
- Detection.js (6 usages - excluding onclick strings)
- towerscout.js (1 usage)
- export.js (1 usage)

**Total**: 10 updates

### Category 2: onclick String Templates (Special Case)

**Current Pattern**:
```javascript
onclick='Detection_detections[" + det.id + "].selectAddr(this.checked)'
```

**Challenge**: String is evaluated in global scope at runtime - can't use providerManager directly

**Solution Options**:
1. **Keep as-is**: Property descriptor handles it (backward compatibility working)
2. **Refactor to event listeners**: More modern but significant rework (~30 min each)
3. **Global helper function**: `window.getDetection(id)` that wraps providerManager

**Recommendation**: **Option 1 (Keep as-is)** - These 2 usages are edge cases, backward compatibility works, not worth 1+ hour refactor

**Total**: 0 updates (accept 2 warnings as intentional pattern)

### Category 3: Direct Assignment

**Pattern**: `Detection_detections = dets` → `providerManager.setDetections(dets)`

**Files to Update**:
- AzureMap.js:1340
- towerscout.js:2250, 2739
- GoogleMap.js:640

**Total**: 4 updates

### Category 4: Array Iteration/Methods

**Pattern**: `Detection_detections.filter(...)` → `providerManager.getDetections().filter(...)`

**Rationale**: `getDetections()` returns safe copy for iteration

**Files to Update**:
- export.js:43

**Total**: 1 update

### Category 5: Detection_minConfidence Assignment

**Pattern**: `Detection_minConfidence = value` → `providerManager.setMinConfidence(value)`

**Files to Update**:
- DetectionList.js:16

**Total**: 1 update

### Category 6: Duplicate Declarations (Cleanup)

**Pattern**: Remove duplicate `let` declarations in towerscout.js (property descriptors handle initialization)

**Files to Update**:
- towerscout.js:3196 - Remove `let Detection_detections = []`
- towerscout.js:3198 - Remove `let Detection_minConfidence = DEFAULT_CONFIDENCE`
- towerscout.js:50 - Remove duplicate `window.azureMap = null` declaration

**Total**: 3 removals

---

## Implementation Steps

### Step 1: Category 1 - Direct Array Access (10 updates, 30 min)

**AzureMap.js** (2 updates):
```javascript
// Line 368
const detection = providerManager.getDetectionsArrayDirect()[props.detectionId];

// Line 1322
const det = providerManager.getDetectionsArrayDirect()[props.detectionId];
```

**Detection.js** (6 updates):
```javascript
// Lines 96, 113 (logging)
const detections = providerManager.getDetectionsArrayDirect();
console.log(`  [${i}] inside=${detections[i].inside}, addr="${detections[i].address.substring(0, 30)}"`);

// Line 118
let det = providerManager.getDetectionsArrayDirect()[i];

// Lines 246-247 (conditional + call)
const detections = providerManager.getDetectionsArrayDirect();
if (id >= 0 && id < detections.length && detections[id]) {
  detections[id].highlight(center, false);
}
```

**towerscout.js** (1 update):
```javascript
// Line 4149
let det = providerManager.getDetectionsArrayDirect()[i];
```

**export.js** (1 update):
```javascript
// Line 212
const det = providerManager.getDetectionsArrayDirect()[i];
```

### Step 2: Category 3 - Direct Assignment (4 updates, 15 min)

```javascript
// Replace: Detection_detections = dets
// With:    providerManager.setDetections(dets)
```

**Files**:
- AzureMap.js:1340
- towerscout.js:2250, 2739
- GoogleMap.js:640

### Step 3: Category 4 - Array Iteration (1 update, 10 min)

**export.js:43**:
```javascript
// OLD:
const selected = Detection_detections.filter(d => d.selected).length;

// NEW:
const selected = providerManager.getDetections().filter(d => d.selected).length;
```

### Step 4: Category 5 - minConfidence Assignment (1 update, 10 min)

**DetectionList.js:16**:
```javascript
// OLD:
Detection_minConfidence = confSlider.value / 100;

// NEW:
providerManager.setMinConfidence(confSlider.value / 100);
```

### Step 5: Category 6 - Remove Duplicate Declarations (3 removals, 15 min)

**towerscout.js**:
```javascript
// Line 50: Remove duplicate azureMap declaration
// window.azureMap = null;  // REMOVE - handled by property descriptor in globals.js

// Line 3196: Remove duplicate Detection_detections declaration
// let Detection_detections = []  // REMOVE - handled by property descriptor in globals.js

// Line 3198: Remove duplicate Detection_minConfidence declaration
// let Detection_minConfidence = DEFAULT_CONFIDENCE;  // REMOVE - handled by property descriptor in globals.js
```

### Step 6: Rebuild Bundle (5 min)

```bash
cd c:/Users/bg90/TowerScout/webapp/js
node build.js
```

### Step 7: Testing (30-60 min)

**Test Workflow**:
1. Run comprehensive detection workflow
2. Monitor console for warnings
3. Validate expected warning count:
   - **BEFORE**: ~100+ warnings (many from Detection_detections direct access during ML processing)
   - **AFTER**: 3 warnings expected:
     - 1x `getDetectionsArrayDirect()` consolidation warning (acceptable)
     - 2x onclick string warnings (intentional backward compatibility)
   - **GOAL**: ~97% reduction in warning noise

**Manual Test Checklist**:
- [ ] Run detection (ML processing with array sorts)
- [ ] Filter by confidence (minConfidence changes)
- [ ] Export CSV (array iteration)
- [ ] Click detections (onclick handlers)
- [ ] Add manual tower (array manipulation)
- [ ] Switch providers (azureMap handling)
- [ ] Clear all (array clearing)

---

## Expected Outcomes

**Warning Reduction**:
- **BEFORE**: ~100+ warnings
- **AFTER**: ~3 warnings (intentional edge cases)
- **REDUCTION**: ~97% cleaner console

**Architecture Benefits**:
- Completes TASK-043 Sprint 02 migration pattern
- Consistent with Phase 1 UI State migration
- Better debugging experience (clear signal-to-noise)
- Easier to spot NEW issues vs. legacy warnings

**Time Estimate**:
- Implementation: 1.5-2 hours
- Testing: 0.5-1 hour
- Documentation: 0.5 hour
- **TOTAL**: 2.5-4 hours

---

## Rollback Plan

If critical issues arise:

```bash
# Quick rollback (5 minutes)
cd c:/Users/bg90/TowerScout/webapp/js/src
cp towerscout.js.backup towerscout.js
cp providers/AzureMap.js.backup providers/AzureMap.js
cp providers/GoogleMap.js.backup providers/GoogleMap.js
cp detection/Detection.js.backup detection/Detection.js
cp detection/DetectionList.js.backup detection/DetectionList.js
cp ui/export.js.backup ui/export.js

cd ..
node build.js
```

**Create backups BEFORE starting implementation**

---

## Success Criteria

- [x] All Category 1-6 updates implemented
- [ ] Bundle rebuilds successfully (0 errors)
- [ ] Console warnings reduced by ~97%
- [ ] All manual tests pass
- [ ] No regressions in detection, export, or highlighting functionality
- [ ] Documentation updated
