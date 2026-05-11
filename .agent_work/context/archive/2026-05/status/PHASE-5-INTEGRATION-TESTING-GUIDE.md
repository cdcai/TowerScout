# Phase 5: Integration Testing Guide

**Date**: March 17, 2026  
**Sprint**: Sprint 03  
**Testing Duration**: 3-5 hours  
**Purpose**: Validate all Sprint 03 work with fresh eyes

---

## Testing Environment Setup

### Pre-Testing Checklist
- ✅ Flask server running: `http://localhost:5000`
- ⬜ Browser console open (F12)
- ⬜ Latest bundle loaded: 404.9 KB expected
- ⬜ Initial warning count documented

### Testing Browser Setup
```
1. Open http://localhost:5000 in browser
2. Open DevTools (F12)
3. Go to Console tab
4. Note initial warning count (expect ~3 warnings, down from 100+)
5. Clear console before each test for clean observations
```

---

## Test Suite Overview

**Total Tests**: 5 major test scenarios  
**Estimated Time**: 3-5 hours

1. **Test 1: Detection Workflow** (60-90 min) - Core ML detection
2. **Test 2: Manual Tower Addition** (60-90 min) - TASK-033 validation
3. **Test 3: Export System** (30-45 min) - TASK-036 validation
4. **Test 4: Provider Switching** (30-45 min) - TASK-039 validation
5. **Test 5: Edge Cases** (30 min) - Stress testing

---

## TEST 1: Detection Workflow (60-90 min)

### Objective
Validate core ML detection with all architectural migrations (Phase 1, Phase 2, TASK-043).

### Test 1A: Google Maps Detection (30 min)

**Steps**:
1. **Initial State**:
   - Load http://localhost:5000
   - Verify Google Maps loads
   - Check console for errors (should be clean)
   - Note warning count (expect ~3)

2. **Search by Zipcode**:
   - Enter: `94102` (San Francisco, small test area)
   - Click "Detect Towers"
   - **Expect**: Tile estimation shown (~20-30 tiles)
   - Click "Yes, start detection"

3. **Monitor Detection Progress**:
   - **Expect**: Progress bar updates smoothly
   - **Expect**: No console errors during processing
   - **Expect**: Detection completes in <30 seconds for ~20-30 tiles

4. **Review Results**:
   - **Expect**: Detections appear in right panel
   - **Expect**: Map markers appear with confidence badges
   - **Expect**: Warning count still low (~3, maybe +1-2 from getTilesArrayDirect)

5. **Test Highlighting (Phase 1 UI State)**:
   - Click detection #1 in results list
     - **Expect**: Detection text highlights (bold + underline)
     - **Expect**: Parent address label highlights
     - **Expect**: Map marker highlights (check for visual change)
   - Click detection #2 in results list
     - **Expect**: Detection #1 unhighlights (normal weight)
     - **Expect**: Detection #2 highlights
   - Click detection #1 again
     - **Expect**: Proper toggle behavior

6. **Test Confidence Filtering**:
   - Move confidence slider to 70%
     - **Expect**: Lower confidence detections hide
     - **Expect**: Map markers update
     - **Expect**: Count updates in panel
   - Move slider back to 0%
     - **Expect**: All detections return

7. **Test Detection Selection**:
   - Uncheck 2-3 detections via checkboxes
     - **Expect**: Map markers disappear for unchecked
     - **Expect**: Detections remain in list (grayed out or similar)
   - Re-check detections
     - **Expect**: Map markers reappear

**✅ SUCCESS CRITERIA**:
- No JavaScript errors in console
- Warning count remains low (~3-5 warnings max)
- All highlighting works (currentElement, currentAddrElement migration success)
- Tile operations work (Tile_tiles migration success)
- Detection operations work (Detection_detections migration success)

### Test 1B: Azure Maps Detection (30 min)

**Steps**:
1. **Switch to Azure Maps**:
   - Click "Azure Maps" button in top-right
   - **Expect**: Map provider switches smoothly
   - **Expect**: Previous detections clear (if any)
   - **Expect**: No console errors

2. **Repeat Test 1A Steps 2-7** on Azure Maps:
   - Same zipcode search: `94102`
   - Same detection workflow
   - Same highlighting tests
   - Same confidence filtering
   - Same selection tests

**✅ SUCCESS CRITERIA**:
- Azure Maps detection works identically to Google Maps
- Provider switching doesn't break state management
- Warning count remains consistent

---

## TEST 2: Manual Tower Addition (60-90 min)

### Objective
Validate TASK-033 manual tower addition feature with all enhancements.

### Test 2A: Add Manual Tower on Google Maps (30 min)

**Steps**:
1. **Start Fresh**:
   - Reload http://localhost:5000
   - Switch to Google Maps (if not already)
   - Search for: `94102`

2. **Enable Manual Tower Mode**:
   - Click "Add Manual Tower" button
   - **Expect**: Drawing mode activates
   - **Expect**: Cursor changes to crosshair
   - **Expect**: Instructions appear

3. **Draw Manual Tower**:
   - Click corners of a building to form polygon
   - Right-click to complete polygon
   - **Expect**: Manual tower dialog appears
   - **Expect**: Address pre-filled (or blank if no geocoding)

4. **Save Manual Tower**:
   - Edit address if needed: "123 Test St, San Francisco, CA"
   - Click "Save" (or equivalent)
   - **Expect**: Purple bordered marker appears on map
   - **Expect**: Manual tower appears in results list with purple badge
   - **Expect**: Manual tower has 100% confidence
   - **Expect**: Manual tower checkbox works like ML detections

5. **Test Manual Tower Highlighting**:
   - Click manual tower in results list
     - **Expect**: Highlights correctly
     - **Expect**: Map marker highlights
   - Click ML detection
     - **Expect**: Manual tower unhighlights
     - **Expect**: ML detection highlights

6. **Test Manual Tower Selection**:
   - Uncheck manual tower
     - **Expect**: Purple marker disappears
   - Re-check manual tower
     - **Expect**: Purple marker reappears

**✅ SUCCESS CRITERIA**:
- Manual tower drawing works smoothly
- Purple borders and badges appear correctly
- Manual towers integrate with ML detections in results list
- Highlighting and selection work for manual towers

### Test 2B: Add Manual Tower on Azure Maps (15 min)

**Steps**:
1. Switch to Azure Maps
2. Repeat Test 2A steps 2-6
3. **Expect**: Manual tower feature works identically

### Test 2C: Mixed ML + Manual Towers (15 min)

**Steps**:
1. **On Google Maps**:
   - Run detection on `94102`
   - Add 2 manual towers
   - **Expect**: Results list shows both ML and manual towers
   - **Expect**: ML towers have teal/blue markers
   - **Expect**: Manual towers have purple markers
   - **Expect**: Both types highlight correctly
   - **Expect**: Both types respond to confidence slider (manual always visible)

2. **Test Confidence Filtering with Mixed**:
   - Set slider to 70%
   - **Expect**: Low-confidence ML towers hide
   - **Expect**: Manual towers always visible (100% confidence)

**✅ SUCCESS CRITERIA**:
- ML and manual towers coexist properly
- Visual distinction clear (purple vs teal)
- All interactions work for both types

---

## TEST 3: Export System (30-45 min)

### Objective
Validate TASK-036 export system with manual tower support.

### Test 3A: CSV Export (10 min)

**Prerequisites**:
- Have Google Maps loaded
- Have 5+ ML detections from Test 1
- Have 2+ manual towers from Test 2

**Steps**:
1. **Export All Towers**:
   - Click "Export" or "Export CSV" button
   - **Expect**: CSV file downloads
   - Open CSV in Excel/text editor

2. **Verify CSV Contents**:
   - **Expect**: Headers: Address, Latitude, Longitude, Confidence, Type (or similar)
   - **Expect**: ML detections present with confidence < 100%
   - **Expect**: Manual towers present with confidence = 100%
   - **Expect**: Manual towers have "Manual" or "User" type indicator
   - **Expect**: All addresses present
   - **Expect**: Coordinates look reasonable (37.78°N, -122.41°W for SF)

3. **Test Filtered Export**:
   - Uncheck 2 detections
   - Set confidence slider to 60%
   - Export again
   - **Expect**: CSV only includes selected + above-threshold towers
   - **Expect**: Manual towers always included (if selected)

**✅ SUCCESS CRITERIA**:
- CSV exports successfully
- Manual towers included with correct metadata
- Filtering works correctly

### Test 3B: KML Export (10 min)

**Steps**:
1. **Export KML**:
   - Click "Export KML" button (or similar)
   - **Expect**: KML file downloads

2. **Verify KML Contents**:
   - Open KML in text editor
   - **Expect**: Valid KML structure (`<kml>`, `<Document>`, `<Placemark>` tags)
   - **Expect**: ML detection placemarks
   - **Expect**: Manual tower placemarks
   - **Expect**: Coordinates in correct format (lon,lat,0)
   - **Expect**: Descriptions include confidence and type

3. **Test in Google Earth** (if available):
   - Open KML in Google Earth
   - **Expect**: Markers appear at correct locations
   - **Expect**: Purple markers for manual towers distinct from blue/teal for ML

**✅ SUCCESS CRITERIA**:
- KML exports successfully
- Manual towers included with distinct styling
- File viewable in Google Earth

### Test 3C: YOLO Dataset Export (10-15 min)

**Steps**:
1. **Export YOLO Dataset**:
   - Click "Export Dataset" or similar
   - **Expect**: ZIP file downloads

2. **Verify ZIP Contents**:
   - Extract ZIP file
   - **Expect**: `images/` folder with tile images
   - **Expect**: `labels/` folder with .txt files
   - **Expect**: `contents.txt` manifest file

3. **Verify YOLO Labels**:
   - Open 2-3 .txt files from `labels/`
   - **Expect**: YOLO format: `<class_id> <x_center> <y_center> <width> <height>`
   - **Expect**: Coordinates normalized (0.0-1.0 range)
   - **Expect**: Manual towers have class ID (probably 0 or special ID)

4. **Verify Contents Manifest**:
   - Open `contents.txt`
   - **Expect**: Lists all images and labels
   - **Expect**: Manual towers marked with source indicator

**✅ SUCCESS CRITERIA**:
- YOLO dataset exports successfully
- Manual towers included in training data
- Labels in correct format

---

## TEST 4: Provider Switching (30-45 min)

### Objective
Validate TASK-039 Google Maps API upgrade with provider state management.

### Test 4A: Basic Provider Switching (15 min)

**Steps**:
1. **Start on Google Maps**:
   - Load http://localhost:5000
   - Verify Google Maps active
   - Search `94102`
   - Run detection (small area)
   - **Expect**: 5+ detections

2. **Switch to Azure Maps**:
   - Click "Azure Maps" button
   - **Expect**: Map switches smoothly
   - **Expect**: Detections clear (expected behavior)
   - **Expect**: No console errors

3. **Run Detection on Azure Maps**:
   - Same search: `94102`
   - Run detection
   - **Expect**: Detection works
   - **Expect**: Results populate

4. **Switch Back to Google Maps**:
   - Click "Google Maps" button
   - **Expect**: Map switches smoothly
   - **Expect**: Detections clear (expected behavior)
   - **Expect**: No console errors

**✅ SUCCESS CRITERIA**:
- Provider switching works both directions
- No state corruption
- No console errors

### Test 4B: Drawing Tools on Both Providers (15 min)

**Steps**:
1. **Google Maps Polygon Drawing**:
   - Switch to Google Maps
   - Click "Draw Search Area" (or similar)
   - Draw custom polygon with 5-6 points
   - Right-click to complete
   - **Expect**: Polygon appears
   - **Expect**: Tile estimation appears
   - **Expect**: Can run detection on drawn area

2. **Azure Maps Polygon Drawing**:
   - Switch to Azure Maps
   - Draw custom polygon with 5-6 points
   - Click "Complete" (or similar Azure method)
   - **Expect**: Polygon appears
   - **Expect**: Tile estimation appears
   - **Expect**: Can run detection on drawn area

3. **Test Manual Tower on Both**:
   - Google Maps: Add manual tower
   - Azure Maps: Add manual tower
   - **Expect**: Both work correctly

**✅ SUCCESS CRITERIA**:
- Drawing tools work on both providers
- Provider-specific controls work correctly
- No interference between providers

### Test 4C: Google Maps PlaceAutocomplete (New API) (15 min)

**Steps**:
1. **Test Autocomplete Search**:
   - Switch to Google Maps
   - Click in search box
   - Type: "Golden Gate Park"
   - **Expect**: Autocomplete suggestions appear below input
   - **Expect**: Suggestions include "Golden Gate Park, San Francisco, CA"
   - Click a suggestion
   - **Expect**: Map zooms to location
   - **Expect**: No deprecated API warnings in console

2. **Test Zipcode Search**:
   - Clear search
   - Type: `94117`
   - Hit Enter (or click search)
   - **Expect**: Map zooms to zipcode area
   - **Expect**: Boundary polygon appears

3. **Test Address Search**:
   - Clear search
   - Type: "1600 Pennsylvania Ave, Washington DC"
   - Select from autocomplete
   - **Expect**: Map zooms to location

**✅ SUCCESS CRITERIA**:
- PlaceAutocompleteElement works (new Web Component API)
- No deprecation warnings
- Search functionality fully operational

---

## TEST 5: Edge Cases (30 min)

### Objective
Stress test for race conditions, performance, and error handling.

### Test 5A: Rapid Operations (10 min)

**Steps**:
1. **Rapid Provider Switching**:
   - Switch Google → Azure → Google → Azure quickly (5 switches in 10 seconds)
   - **Expect**: No console errors
   - **Expect**: Maps continue to work
   - **Expect**: No broken state

2. **Rapid Detection Cancel**:
   - Start detection on large area (100+ tiles)
   - Cancel immediately
   - Start again
   - Cancel again
   - Start third time, let complete
   - **Expect**: Cancellation works
   - **Expect**: Third detection completes normally
   - **Expect**: No orphaned processes

3. **Rapid Highlighting**:
   - With 10+ detections loaded
   - Rapidly click through results list (10 clicks in 5 seconds)
   - **Expect**: Highlighting updates smoothly
   - **Expect**: No visual glitches
   - **Expect**: No console errors

**✅ SUCCESS CRITERIA**:
- No race conditions observed
- Cancellation works reliably
- UI remains responsive

### Test 5B: Large Dataset (10 min)

**Steps**:
1. **Large Area Detection**:
   - Search for larger area: `10001` (Manhattan - ~80-100 tiles)
   - Run detection
   - **Expect**: Processing completes (may take 2-3 minutes)
   - **Expect**: Results load successfully
   - **Expect**: UI remains responsive with 100+ detections

2. **Test Operations with Large Dataset**:
   - Test highlighting (should still be responsive)
   - Test confidence filtering (should update quickly)
   - Test selection/deselection (should work)
   - Add manual tower (should still work)

**✅ SUCCESS CRITERIA**:
- Large datasets handled gracefully
- UI doesn't freeze or hang
- All operations still functional

### Test 5C: Clear All & Reset (10 min)

**Steps**:
1. **Clear All Detections**:
   - With detections + manual towers loaded
   - Click "Clear All" or "New Search"
   - **Expect**: All detections cleared
   - **Expect**: All manual towers cleared
   - **Expect**: Map returns to initial state
   - **Expect**: Results panel empty

2. **Browser Refresh**:
   - With detections loaded
   - Refresh browser (F5)
   - **Expect**: Session clears (expected behavior)
   - **Expect**: App returns to initial state
   - **Expect**: No errors on reload

3. **Multiple Session Workflow**:
   - Run detection → clear → run again → clear → run third time
   - **Expect**: Each session works independently
   - **Expect**: No data leakage between sessions
   - **Expect**: Memory doesn't balloon

**✅ SUCCESS CRITERIA**:
- Clear all works completely
- Sessions isolated properly
- No memory leaks observed

---

## Post-Testing Assessment

### Test Results Summary

**Record for each test**:
- ✅ PASS / ❌ FAIL / ⚠️ PARTIAL
- Console error count
- Console warning count
- Issues/bugs discovered
- Performance observations

### Example Results Template:
```
TEST 1A: Google Maps Detection - ✅ PASS
- Errors: 0
- Warnings: 3 (expected)
- Notes: All highlighting worked perfectly, confidence filtering smooth

TEST 1B: Azure Maps Detection - ✅ PASS
- Errors: 0
- Warnings: 3 (expected)
- Notes: Identical to Google Maps

TEST 2A: Manual Tower Addition - ⚠️ PARTIAL
- Errors: 1 (polygon not saving)
- Warnings: 3
- Issues: Need to investigate polygon save logic
- Notes: Purple border works, but save dialog buggy

... etc ...
```

---

## Decision Point: Phase 3 Assessment

### After completing all tests, decide on Phase 3 (DOM migration)

**SKIP Phase 3 if**:
- ✅ All 5 tests PASS or have minor issues
- ✅ No DOM-related bugs discovered
- ✅ Current architecture sufficient
- ✅ Warning count acceptable

**PROCEED with Phase 3 if**:
- ❌ DOM access issues discovered
- ❌ Inconsistent state management causing problems
- ❌ Testing reveals edge cases requiring DOM migration
- ❌ Want architectural completeness

**Effort**: 2-3 hours to complete Phase 3 (DOM elements migration)

---

## Rollback Procedures (If Needed)

### If Critical Issues Found:

**Phase 1 Rollback** (UI State):
```bash
cd c:/Users/bg90/TowerScout/webapp/js/src
cp managers/ProviderStateManager.js.backup managers/ProviderStateManager.js
cp globals.js.backup globals.js
cp detection/Detection.js.backup detection/Detection.js
cp towerscout.js.backup towerscout.js
cp store.js.backup store.js
npm run build
```

**TASK-043 Rollback** (Warning Cleanup):
```bash
cd c:/Users/bg90/TowerScout/webapp/js/src
cp detection/Detection.js.backup.task043 detection/Detection.js
cp maps/AzureMap.js.backup.task043 maps/AzureMap.js
cp maps/GoogleMap.js.backup.task043 maps/GoogleMap.js
cp towerscout.js.backup.task043 towerscout.js
cp ui/DetectionList.js.backup.task043 ui/DetectionList.js
cp export/export.js.backup.task043 export/export.js
npm run build
```

**Phase 2 Rollback** (Tile State):
```bash
cd c:/Users/bg90/TowerScout/webapp/js/src
cp detection/Tile.js.backup.phase2 detection/Tile.js
cp managers/ProviderStateManager.js.backup.phase2 managers/ProviderStateManager.js
cp globals.js.backup.phase2 globals.js
cp maps/GoogleMap.js.backup.phase2 maps/GoogleMap.js
cp maps/AzureMap.js.backup.phase2 maps/AzureMap.js
cp export/export.js.backup.phase2 export/export.js
cp towerscout.js.backup.phase2 towerscout.js
cp store.js.backup.phase2 store.js
npm run build
```

---

## Success Criteria for Phase 5

**PHASE 5 COMPLETE when**:
- ✅ All 5 test scenarios executed
- ✅ Results documented in test results template
- ✅ Decision made on Phase 3 (proceed or skip)
- ✅ Any critical issues identified and logged
- ✅ Sprint 03 readiness confirmed

**Expected Outcome**: 🟢 All tests PASS, Phase 3 optional, ready for Phase 6 documentation

---

## Next Steps After Phase 5

1. **Update Task Status**:
   - Mark TASK-039 Phase 5 as COMPLETE in `current-tasks.md`
   - Update `completed-tasks.md` with Phase 5 results

2. **Make Phase 3 Decision**:
   - If SKIP: Proceed directly to Phase 6 (documentation)
   - If PROCEED: Implement Phase 3, then test, then Phase 6

3. **Phase 6 Documentation** (1-2 hours):
   - Update `copilot-instructions.md`
   - Create `Google-Maps-API-Migration-Guide.md`
   - Update README with Sprint 03 achievements
   - Document new features (manual towers, export system)

4. **Sprint 03 Closeout**:
   - Final completed-tasks.md update
   - Sprint retrospective notes
   - Plan Sprint 04 priorities

---

## Confidence Assessment

**Testing Outlook**: 🟢 **OPTIMISTIC**
- Fresh perspective after 1-day break
- Comprehensive test coverage planned
- All major functionality pre-validated during implementation
- Rollback procedures documented

**Expected Testing Outcome**: 🟢 **LIKELY SUCCESS**
- All architectural migrations followed consistent patterns
- Bundle builds successful (0 errors)
- User validated Phase 1-4B before deferral

**Phase 3 Prediction**: 🟡 **LIKELY OPTIONAL**
- Core state (detections, tiles, UI) already migrated
- DOM elements less critical for functionality
- Will confirm during testing

---

**Ready to begin testing?** Open http://localhost:5000 and start with Test 1A! 🚀
