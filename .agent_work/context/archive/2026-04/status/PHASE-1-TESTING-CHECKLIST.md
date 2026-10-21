# Global Variable Migration Phase 1 - Testing Checklist

**Date**: March 16, 2026  
**Sprint**: Sprint 03  
**Build**: 400.5 KB (27 modules, 0 errors)  
**Status**: Implementation Complete, Ready for Testing

---

## Pre-Testing Verification

### Code Review ✅
- [X] ProviderStateManager extended with 6 UI state methods
- [X] Property descriptors added for currentElement, currentAddrElement, isInitializing
- [X] Detection.js updated to use providerManager
- [X] src/towerscout.js duplicate declarations removed
- [X] isInitializing assignments updated to use setIsInitializing()
- [X] store.js declarations commented out
- [X] Bundle rebuilt successfully (400.5 KB)

### Bundle Analysis ✅
**Size Changes**:
- Previous: 396.1 KB (after TASK-036)
- Current: 400.5 KB (+4.4 KB)
- **Breakdown**:
  - ProviderStateManager: +2.7 KB (UI state methods)
  - globals.js: +5.1 KB (property descriptors)
  - Detection.js: +0.1 KB (refactored highlight)
  - towerscout.js (src): -0.5 KB (removed declarations)

**Expected**: Size increase acceptable for added functionality

---

## Manual Testing Checklist

### Test 1: Detection Highlighting (HIGH PRIORITY)
**Objective**: Verify bidirectional highlighting still works with state manager

**Steps**:
1. Load http://localhost:5000
2. Run detection on small area (e.g., zipcode "94102")
3. Click detection in results list
   - **Expect**: Detection highlights (bold + underline)
   - **Expect**: Address label highlights (parent element)
   - **Expect**: Map marker highlights (**Check for green color**)

4. Click different detection in list
   - **Expect**: Previous detection unhighlights (normal weight)
   - **Expect**: New detection highlights

5. Click map marker directly
   - **Expect**: Corresponding list item highlights
   - **Expect**: Previous highlight clears

6. Scroll detection into view
   - **Expect**: Scrolls smoothly to detection in list

**Console Check**:
- Look for: `🎯 Current detection element set: [element-id]`
- Look for: `📍 Current address element set: [addrlabel-id]`
- Look for: `🧹 UI highlighting cleared`
- **Should NOT see**: Deprecation warnings (⚠️)

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

### Test 2: Manual Tower Highlighting (TASK-033 Regression)
**Objective**: Verify manual towers highlight correctly

**Steps**:
1. Load page and run detection
2. Add manual tower using polygon draw tool
   - **Expect**: Purple border appears
   - **Expect**: "✋ Manual" badge in list

3. Click manual tower in list
   - **Expect**: Purple border highlights
   - **Expect**: Address label highlights
   - **Expect**: Bidirectional highlighting works

4. Add multiple manual towers
5. Click between ML towers and manual towers
   - **Expect**: Highlighting switches correctly
   - **Expect**: Colors appropriate (green for ML, purple for manual)

**Console Check**:
- Look for: `🎯 Current detection element set:` messages
- **Should NOT see**: JavaScript errors
- **Should NOT see**: Deprecation warnings

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

### Test 3: Provider Switching Guard (isInitializing)
**Objective**: Verify initialization flag prevents early provider switching

**Steps**:
1. Open http://localhost:5000 in new incognito window (fresh load)
2. **Immediately** try clicking Azure Maps radio button
   - **Expect**: Switching blocked or delayed
   - **Expect**: Console message about initialization

3. Wait 3-4 seconds
4. Check console for: `🎯 Provider initialization complete`
5. Try clicking Azure Maps radio button again
   - **Expect**: Switching works

6. Switch back to Google Maps
   - **Expect**: Switching works

**Console Check**:
- Look for: `🔧 Initialization state: INITIALIZING`
- Look for: `🔧 Initialization state: COMPLETE` (after ~3 seconds)
- Look for: `🔄 Attempting to switch to Azure Maps (isInitializing: false)`
- **Should NOT see**: Deprecation warnings

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

### Test 4: No Deprecation Warnings (Critical)
**Objective**: Verify all code uses state manager (no warnings)

**Steps**:
1. Open browser console (F12)
2. Clear console
3. Refresh page
4. Perform comprehensive workflow:
   - Run detection
   - Click detections in list
   - Click map markers
   - Add manual tower
   - Click manual tower
   - Export CSV
   - Switch providers
   - Run another detection

5. Review console log

**Expected Results**:
- ✅ Should see: `🎯 Current detection element set:` messages
- ✅ Should see: `📍 Current address element set:` messages
- ✅ Should see: `🧹 UI highlighting cleared` messages
- ✅ Should see: `🔧 Initialization state:` messages
- ❌ **Should NOT see**: `⚠️ Direct window.currentElement assignment deprecated`
- ❌ **Should NOT see**: `⚠️ Direct window.currentAddrElement assignment deprecated`
- ❌ **Should NOT see**: `⚠️ Direct window.isInitializing assignment deprecated`

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

### Test 5: Dataset Restoration (TASK-033 Regression)
**Objective**: Verify highlighting persists after dataset restore

**Steps**:
1. Run detection with manual towers
2. Export dataset (ZIP)
3. Refresh page
4. Restore dataset (upload ZIP)
   - **Expect**: Detections + manual towers restored
   - **Expect**: Purple borders on manual towers

5. Click detections in restored list
   - **Expect**: Highlighting works correctly
   - **Expect**: Manual towers highlight with purple border
   - **Expect**: ML towers highlight with green

6. Click map markers
   - **Expect**: Bidirectional highlighting works

**Console Check**:
- Look for: UI state logging messages
- **Should NOT see**: Errors about missing elements
- **Should NOT see**: Deprecation warnings

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

### Test 6: Rapid Clicking (Race Condition Check)
**Objective**: Verify no race conditions in UI state updates

**Steps**:
1. Run detection with 20+ results
2. Rapidly click different detections in list (5-10 clicks/second)
   - **Expect**: Highlighting keeps up
   - **Expect**: No visual glitches
   - **Expect**: No JavaScript errors

3. Rapidly click map markers
   - **Expect**: List highlighting updates correctly

4. Mix clicking list and map markers rapidly
   - **Expect**: Stays synchronized

**Console Check**:
- Look for: Multiple `🎯 Current detection element set:` in quick succession
- **Should NOT see**: Errors about null elements
- **Should NOT see**: "Cannot read property 'style' of null"

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

### Test 7: Edge Cases
**Objective**: Test unusual scenarios

**Test 7a**: Click detection, then clear all
- Run detection
- Click detection (highlights)
- Click "Clear All" button
- **Expect**: No errors, highlighting cleared

**Test 7b**: Click detection, then run new detection
- Run detection
- Click detection (highlights)
- Run new detection
- **Expect**: Previous highlighting cleared automatically
- **Expect**: New detections clickable

**Test 7c**: Provider switch during highlighted state
- Run detection on Google Maps
- Click detection (highlights)
- Switch to Azure Maps
- **Expect**: Highlighting cleared (or persists if same coordinates)
- **Expect**: No JavaScript errors

**Status**: [x] Pass [ ] Fail [ ] Not Tested

**Issues Found**:
_______________________________________________________________

---

## Performance Testing (Optional)

### Performance Check 1: Highlighting Speed
- Run detection with 50+ results
- Click through 10 detections rapidly
- **Measure**: Subjective responsiveness
- **Expected**: No noticeable slowdown vs TASK-033

### Performance Check 2: Memory Leaks
- Run 5 detections in sequence (clearing between each)
- Add/remove manual towers 10 times
- **Check**: Browser dev tools memory profiler
- **Expected**: Memory doesn't grow significantly

**Status**: [ ] Pass [ ] Fail [ ] Not Tested

---

## Testing Summary

**Date Completed**: _______________  
**Tester**: _______________  
**Browser**: Chrome / Firefox / Edge (circle one)  
**Total Tests**: 7 primary + 2 performance  

**Results**:
- Tests Passed: _____
- Tests Failed: _____  
- Critical Issues: _____

**Critical Failures** (if any):
- [ ] None
- [ ] List failures here:

_______________________________________________________________

**Sign-Off**:
- [ ] All highlighting functionality works correctly
- [ ] No deprecation warnings in console
- [ ] No regressions in TASK-033 features
- [ ] Provider switching guard works
- [ ] Dataset restoration works
- [ ] Performance acceptable

**Phase 1 Status**: [ ] COMPLETE [ ] NEEDS FIXES

---

## Rollback Procedure (If Needed)

If critical issues found:

1. **Quick rollback** (5 minutes):
   ```bash
   cd c:/Users/bg90/TowerScout/webapp/js
   cp towerscout.js.backup towerscout.js
   ```

2. **Investigate issues** in source files

3. **Re-implement fixes**

4. **Re-test**

**Rollback NOT recommended unless**:
- Highlighting completely broken
- JavaScript errors prevent basic functionality
- Multiple test failures
