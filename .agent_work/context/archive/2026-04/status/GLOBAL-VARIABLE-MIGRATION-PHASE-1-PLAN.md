# Global Variable Migration - Phase 1: UI State

**Date**: March 16, 2026  
**Sprint**: Sprint 03  
**Estimated Effort**: 4-6 hours  
**Priority**: HIGH (synergy with TASK-033 UI work)

## Context

Building on TASK-043 (Sprint 02), which migrated 5 critical globals and fixed 3 race conditions. Phase 1 focuses on UI state variables that manage detection highlighting and initialization state.

**TASK-043 Achievements**:
- ✅ Map state: `window.googleMap`, `window.azureMap`
- ✅ Detection state: `Detection_detections`, `Detection_minConfidence`
- ✅ Progress timer: `progressTimer` (module-level)
- ✅ Patterns established: Property descriptors, busy-wait mutex, copy-on-read

## Phase 1 Scope

### Target Variables (3)

1. **`currentElement`** (7 usages)
   - **Purpose**: Currently highlighted detection list item DOM element
   - **Used in**: Detection.js highlight() method
   - **Pattern**: Visual styling (fontWeight, textDecoration)
   - **Risk**: Low - read/write, not concurrent

2. **`currentAddrElement`** (7 usages)
   - **Purpose**: Currently highlighted address label DOM element
   - **Used in**: Detection.js highlight() method  
   - **Pattern**: Visual styling + scrolling
   - **Risk**: Low - read/write, not concurrent

3. **`isInitializing`** (14+ usages)
   - **Purpose**: Flag to prevent provider switching during startup
   - **Used in**: Provider switching guard clauses
   - **Status**: ⚠️ **PARTIALLY MIGRATED** - already in ProviderStateManager!
   - **Action**: Complete migration (remove local declarations, update remaining usages)
   - **Risk**: Low - ProviderStateManager already has this property

### Current Usage Analysis

**currentElement + currentAddrElement**:
- Declared in: `src/store.js` (lines 17-18)
- Used in: `src/detection/Detection.js` (lines 256-281)
- Pattern: Read to check if null, then reset styles, then write new value
- No concurrent access risk (UI thread only)

**isInitializing**:
- Declared in: `src/store.js` (line 19) + `src/towerscout.js` (line 47) **← DUPLICATE!**
- Managed by: `ProviderStateManager` (already has `this.isInitializing` property)
- Used in: ErrorHandler.js (already using `providerManager.isInitializing`)
- Remaining legacy: src/towerscout.js direct assignments (lines 60, 71, 4653)

## Implementation Plan

### Step 1: Extend ProviderStateManager (1.5 hours)

**File**: `webapp/js/src/managers/ProviderStateManager.js`

Add UI state storage and methods:

```javascript
// In constructor (after line 37):
// Phase 1 (Sprint 03): UI state management
this.currentElementRef = null;        // Currently highlighted detection DOM element
this.currentAddrElementRef = null;    // Currently highlighted address DOM element
// Note: isInitializing already exists (line 15)

// After progress timer methods (~line 615):
// =============================================================================
// UI State Management (Phase 1 - Sprint 03)
// Manages currently highlighted detection elements for bidirectional highlighting
// =============================================================================

/**
 * Get currently highlighted detection element
 * @returns {HTMLElement|null} DOM element or null if none selected
 */
getCurrentElement() {
  return this.currentElementRef;
}

/**
 * Set currently highlighted detection element
 * @param {HTMLElement|null} element - DOM element to highlight
 */
setCurrentElement(element) {
  this.currentElementRef = element;
  if (element) {
    console.log(`🎯 Current detection element set: ${element.id}`);
  }
}

/**
 * Get currently highlighted address element
 * @returns {HTMLElement|null} DOM element or null if none selected
 */
getCurrentAddrElement() {
  return this.currentAddrElementRef;
}

/**
 * Set currently highlighted address element
 * @param {HTMLElement|null} element - DOM element to highlight
 */
setCurrentAddrElement(element) {
  this.currentAddrElementRef = element;
  if (element) {
    console.log(`📍 Current address element set: ${element.id}`);
  }
}

/**
 * Clear all UI highlighting (both detection and address elements)
 */
clearUIHighlighting() {
  if (this.currentElementRef) {
    this.currentElementRef.style.fontWeight = "normal";
    this.currentElementRef.style.textDecoration = "";
  }
  if (this.currentAddrElementRef) {
    this.currentAddrElementRef.style.fontWeight = "normal";
    this.currentAddrElementRef.style.textDecoration = "";
  }
  this.currentElementRef = null;
  this.currentAddrElementRef = null;
  console.log(`🧹 UI highlighting cleared`);
}

/**
 * Get initialization state (prevents provider switching during startup)
 * @returns {boolean} True if still initializing, false if ready
 */
getIsInitializing() {
  return this.isInitializing;
}

/**
 * Set initialization state
 * @param {boolean} value - Initialization state
 */
setIsInitializing(value) {
  this.isInitializing = value;
  console.log(`🔧 Initialization state: ${value ? 'INITIALIZING' : 'COMPLETE'}`);
}
```

**Validation**: ProviderStateManager grows by ~80 lines (acceptable)

---

### Step 2: Add Property Descriptors (30 minutes)

**File**: `webapp/js/src/globals.js`

Add soft deprecation wrappers after existing descriptors (~line 76):

```javascript
// TASK-043 Phase 1 (Sprint 03): UI state deprecation
Object.defineProperty(window, 'currentElement', {
  get() {
    return window.providerManager ? window.providerManager.getCurrentElement() : null;
  },
  set(value) {
    console.warn('⚠️ Direct window.currentElement assignment deprecated. Use providerManager.setCurrentElement() instead.');
    if (window.providerManager) {
      window.providerManager.setCurrentElement(value);
    }
  }
});

Object.defineProperty(window, 'currentAddrElement', {
  get() {
    return window.providerManager ? window.providerManager.getCurrentAddrElement() : null;
  },
  set(value) {
    console.warn('⚠️ Direct window.currentAddrElement assignment deprecated. Use providerManager.setCurrentAddrElement() instead.');
    if (window.providerManager) {
      window.providerManager.setCurrentAddrElement(value);
    }
  }
});

Object.defineProperty(window, 'isInitializing', {
  get() {
    return window.providerManager ? window.providerManager.getIsInitializing() : true;
  },
  set(value) {
    console.warn('⚠️ Direct window.isInitializing assignment deprecated. Use providerManager.setIsInitializing() instead.');
    if (window.providerManager) {
      window.providerManager.setIsInitializing(value);
    }
  }
});
```

**Validation**: Maintains backward compatibility, logs warnings

---

### Step 3: Update Detection.js highlighting (1 hour)

**File**: `webapp/js/src/detection/Detection.js`

Replace direct global access in highlight() method (lines 256-281):

```javascript
highlight(center, scroll) {
  let firstDet = this.firstDet;

  // TASK-043 Phase 1: Use providerManager for UI state
  // Clear previous highlighting
  if (providerManager.getCurrentAddrElement() !== null) {
    providerManager.clearUIHighlighting();
  }

  // Highlight the address (parent element)
  let element = document.getElementById('addrlabel' + firstDet.id);
  element.style.fontWeight = "bolder";
  element.style.textDecoration = "underline";
  providerManager.setCurrentAddrElement(element);

  // Make sure parent element is open
  element.parentNode.firstChild.classList.add('caret-down');
  element.parentNode.lastChild.classList.add('active');

  // Highlight the individual detection
  element = document.getElementById(this.labelId);
  if (scroll) {
    providerManager.getCurrentAddrElement().scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  element.style.fontWeight = "bolder";
  element.style.textDecoration = "underline";
  providerManager.setCurrentElement(element);
  document.getElementById("detection").value = this.indexInList;

  if (center) {
    this.centerInMap();
  }

  if (Detection_current !== null) {
    Detection_current.resetHighlight();
  }
  Detection_current = this;
}
```

**Validation**: Highlighting functionality unchanged, uses state manager

---

### Step 4: Update src/towerscout.js initialization (1 hour)

**File**: `webapp/js/src/towerscout.js`

**Remove duplicate isInitializing declaration** (line 47):
```javascript
// Remove this line (now managed by ProviderStateManager):
// let isInitializing = true; // Flag to prevent provider switching during startup
```

**Update direct assignments** (lines 60, 71, 4653):
```javascript
// Line 60 - In provider initialization callback:
// Before: this.isInitializing = true;
// After: 
if (window.providerManager) {
  window.providerManager.set IsInitializing(true);
}

// Line 71 - After provider ready:
// Before: this.isInitializing = false;
// After:
if (window.providerManager) {
  window.providerManager.setIsInitializing(false);
}

// Line 4653 - In $(document).ready:
// Before: isInitializing = false;
// After:
if (window.providerManager) {
  window.providerManager.setIsInitializing(false);
}
```

**Update console.log references** (lines 3945, 3995):
```javascript
// Before: console.log(`🔄 Attempting to switch to Google Maps (isInitializing: ${isInitializing})`);
// After: console.log(`🔄 Attempting to switch to Google Maps (isInitializing: ${window.providerManager.getIsInitializing()})`);
```

**Validation**: No direct isInitializing assignments, all routed through providerManager

---

### Step 5: Remove store.js declarations (15 minutes)

**File**: `webapp/js/src/store.js`

Comment out migrated variables (lines 17-19):

```javascript
// UI state tracking
// TASK-043 Phase 1 (Sprint 03): Migrated to ProviderStateManager
// Property descriptors in globals.js provide backward compatibility
// window.currentElement = null;           // Currently selected detection marker
// window.currentAddrElement = null;       // Currently selected address list item
// window.isInitializing = true;           // Prevents provider switching during startup
```

**Validation**: Property descriptors in globals.js maintain backward compatibility

---

### Step 6: Rebuild and Test (1.5 hours)

**Build**:
```bash
cd webapp && node build.js
```

**Expected**: Bundle ~346-350 KB (small increase for new methods)

**Manual Testing Checklist**:

1. **Test 1: Detection Highlighting**
   - Run detection on small area
   - Click detection in list → verify highlighting works
   - Click different detection → verify previous unhighlights
   - Click map marker → verify bidirectional highlighting
   - **Expected**: All highlighting functional, no errors

2. **Test 2: Provider Switching Guard**
   - Load application → try switching providers immediately
   - **Expected**: Blocked during initialization, allowed after page load
   - Check console for "Initialization state: COMPLETE" message

3. **Test 3: Deprecation Warnings**
   - Open browser console
   - Run detection, interact with UI
   - **Expected**: No deprecation warnings (all code uses state manager)

4. **Test 4: Manual Tower Integration** (TASK-033 regression)
   - Add manual tower
   - Click manual tower in list
   - **Expected**: Purple border highlights, bidirectional works

**Code Review Verification**:
```bash
# Should find NO direct assignments in src/ (only in globals.js descriptors):
grep -r "currentElement = " webapp/js/src/ --exclude-dir=*.bak
grep -r "currentAddrElement = " webapp/js/src/ --exclude-dir=*.bak
grep -r "isInitializing = " webapp/js/src/ --exclude-dir=*.bak
```

**Expected Result**: Only matches in globals.js property descriptors

---

### Step 7: Documentation (30 minutes)

**Update Files**:
1. Create migration completion document
2. Update current-tasks.md (mark Phase 1 complete)
3. Update ProviderStateManager JSDoc comments
4. Add Phase 1 completion to completed-tasks.md

---

## Success Criteria

- [ ] ProviderStateManager extended with 6 new UI state methods
- [ ] Property descriptors added for all 3 variables
- [ ] Detection.js updated to use state manager
- [ ] src/towerscout.js duplicate declarations removed
- [ ] All direct global assignments migrated
- [ ] Bundle rebuilds successfully without errors
- [ ] Manual testing passed (4 test scenarios)
- [ ] Code review clean (no direct assignments found)
- [ ] Zero deprecation warnings in browser console
- [ ] No regressions in TASK-033 manual tower highlighting

## Estimated Timeline

- Step 1: Extend ProviderStateManager - 1.5 hours
- Step 2: Property descriptors - 30 minutes
- Step 3: Update Detection.js - 1 hour
- Step 4: Update towerscout.js - 1 hour
- Step 5: Remove store.js declarations - 15 minutes
- Step 6: Build and test - 1.5 hours
- Step 7: Documentation - 30 minutes

**Total**: 5.25 hours (within 4-6 hour estimate)

## Risk Assessment

**Low Risk**:
- UI state not concurrent (single-threaded UI updates)
- No mutex/locks needed (unlike detection array)
- Property descriptors maintain backward compatibility
- isInitializing already partially migrated

**Mitigation**:
- Comprehensive manual testing of highlighting
- Regression testing with TASK-033 features
- Can roll back if issues discovered (property descriptors allow quick revert)

## Next Phase

**Phase 2: Tile State** (2-3 hours)
- `Tile_tiles` array migration
- Follow same pattern as Detection_detections
- Scheduled after Phase 1 validation complete
