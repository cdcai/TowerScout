# TASK-036 Export System Testing Checklist

**Testing Date**: March 13, 2026  
**Build Version**: 396.1 KB (27 modules)  
**Test Environment**: Windows 11, Chrome/Firefox  
**Server Status**: ✅ Running on http://localhost:5000

## Export Error Handling Validation

### Test 1: CSV Export - No Detections
**Scenario**: Attempt CSV export without running detection

**Steps**:
1. Load application at http://localhost:5000
2. Click "Download results (CSV)" button immediately
3. Observe notification message

**Expected Result**:
- ❌ Error notification: "No detection data available. Please run a detection search first."
- 🚫 No CSV file downloaded
- 📝 Console log showing validation failure

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 2: CSV Export - No Selections
**Scenario**: Export CSV with all detections unchecked

**Steps**:
1. Run detection on small area (e.g., zipcode 94102)
2. Uncheck all detection checkboxes in results panel
3. Click "Download results (CSV)"
4. Observe notification

**Expected Result**:
- ❌ Error notification: "No detections are selected. Please select at least one detection to export."
- 🚫 No CSV file downloaded
- 📝 Console shows total count and 0 selected

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 3: CSV Export - Success Scenario
**Scenario**: Export CSV with valid detections

**Steps**:
1. Run detection on small area
2. Ensure at least one detection is checked
3. Click "Download results (CSV)"
4. Observe notification and file download

**Expected Result**:
- ✅ Success notification: "CSV exported successfully: X detections"
- 📥 CSV file downloads (e.g., "tower_locations.csv")
- 📊 CSV contains: Latitude, Longitude, Confidence, Address, Source
- 📝 Console logs export count

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 4: KML Export - No Detections
**Scenario**: Attempt KML export without detection data

**Steps**:
1. Refresh page to clear session
2. Click "Download results (KML)" button
3. Observe notification

**Expected Result**:
- ❌ Error notification: "No detection data available. Please run a detection search first."
- 🚫 No KML file downloaded

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 5: KML Export - All Filtered Out
**Scenario**: Export KML when threshold filters all detections

**Steps**:
1. Run detection on area
2. Adjust confidence threshold to 100% (filters out all)
3. Click "Download results (KML)"
4. Observe notification

**Expected Result**:
- ⚠️ Warning notification: "No detections match current criteria. Try adjusting the confidence threshold or selecting more detections."
- 🚫 No KML file downloaded
- 📝 Console shows skip count details

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 6: KML Export - Success with Mixed Sources
**Scenario**: Export KML with ML + manual towers

**Steps**:
1. Run detection on area
2. Add 1-2 manual towers using polygon tool
3. Keep default threshold (50%)
4. Click "Download results (KML)"
5. Observe notification and file

**Expected Result**:
- ✅ Success notification: "KML exported successfully: X detections exported, Y skipped"
- 📥 KML file downloads (e.g., "tower_locations.kml")
- 🗺️ KML viewable in Google Earth
- 📝 Console shows export and skip counts

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 7: Dataset Export - No Detections
**Scenario**: Attempt dataset export without tiles

**Steps**:
1. Refresh page
2. Click "Download Dataset (Full Tiles)" button
3. Observe notification

**Expected Result**:
- ❌ Error notification: "No detection data available. Please run a detection search first."
- 🚫 No ZIP file downloaded

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 8: Dataset Export - No Selections
**Scenario**: Export dataset with no towers selected

**Steps**:
1. Run detection
2. Uncheck all detections
3. Click "Download Dataset (Full Tiles)"
4. Observe notification

**Expected Result**:
- ❌ Error notification: "No detections are selected. Please select at least one detection to export."
- 🚫 No ZIP file downloaded

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 9: Dataset Export - Success with README
**Scenario**: Successful dataset export includes README

**Steps**:
1. Run detection on small area (2-5 tiles recommended)
2. Ensure detections are selected
3. Click "Download Dataset (Full Tiles)"
4. Wait for ZIP generation
5. Extract ZIP file
6. Check contents

**Expected Result**:
- ✅ Success notification appears after processing
- 📥 ZIP file downloads (e.g., "tower_detections_dataset.zip")
- 📁 ZIP contains:
  - `README.txt` **← KEY TEST ITEM**
  - `contents.txt`
  - `train/images/*.jpg`
  - `train/labels/*.txt`
- 📖 README.txt includes:
  - Dataset structure explanation
  - YOLO label format documentation
  - YOLOv5 training instructions
  - Detection types explanation
  - Citation information
- 📝 Console shows "added README.txt to dataset"

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

**Critical Validation**: Verify README.txt exists at root level alongside contents.txt

---

### Test 10: Export During Detection Processing
**Scenario**: Attempt export while detection is running

**Steps**:
1. Start detection on large area (50+ tiles)
2. Immediately try to export CSV/KML/Dataset
3. Observe behavior

**Expected Result**:
- Either: Export disabled during processing
- Or: Exports current partial results with notification

**Status**: [ ] Pass [ ] Fail [ X ] Not Tested (reasoning: the progress bar overlays the screen during detection so this is not possible)

---

### Test 11: Server Error Handling
**Scenario**: Server returns error during dataset export

**Steps**:
1. Run detection
2. Stop Flask server (`Ctrl+C` in terminal)
3. Try to export dataset
4. Observe notification

**Expected Result**:
- ❌ Error notification: "Dataset export failed: [error details]"
- 🚫 No ZIP download
- 📝 Console shows fetch failure

**Status**: [ X ]Pass [ ] Fail [ ] Not Tested 

---

## ML Documentation Validation

### Test 12: README Content Verification
**Scenario**: Verify README has all required sections

**Steps**:
1. Export dataset successfully (Test 9)
2. Open README.txt in text editor
3. Verify sections present:

**Required Sections** (check all):
- [ ] "About This Dataset" header
- [ ] "Dataset Contents" section
- [ ] "File Structure" explanation
- [ ] "Label Format (YOLO)" with example
- [ ] "Detection Types" (ML vs Manual)
- [ ] "Using This Dataset for Training" with YOLOv5 commands
- [ ] "Dataset Metadata" reference to contents.txt
- [ ] "Quality Notes" about confidence scores
- [ ] "Citation" with Lancet Digital Health paper
- [ ] "Support" with GitHub links
- [ ] "License" (CC-BY-NC-SA-4.0)

**Expected Result**: All sections present and properly formatted

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 13: YOLO Format Example Accuracy
**Scenario**: Verify YOLO format example is correct

**Steps**:
1. Read YOLO format section in README.txt
2. Compare with actual label files in train/labels/
3. Verify format matches: `<class> <center_x> <center_y> <width> <height>`

**Expected Result**:
- Example: `0 0.5123 0.4876 0.0625 0.0834`
- All coordinates normalized (0.0-1.0 range)
- Format matches actual label files

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 14: Training Command Validation
**Scenario**: Verify YOLOv5 training command is correct

**Steps**:
1. Locate "Using This Dataset" section
2. Check training command syntax

**Expected Command**:
```bash
python train.py --img 640 --batch 16 --epochs 100 \
  --data data.yaml --weights yolov5s.pt
```

**Status**:  [ X ] Pass [ ] Fail [ ] Not Tested

---

## Cross-Browser Testing

### Test 15: Chrome Validation
**Browser**: Google Chrome (latest)

**Tests to Repeat**:
- [ ] Test 3: CSV Export Success
- [ ] Test 6: KML Export Success
- [ ] Test 9: Dataset Export with README

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 16: Firefox Validation
**Browser**: Mozilla Firefox (latest)

**Tests to Repeat**:
- [ ] Test 3: CSV Export Success
- [ ] Test 6: KML Export Success
- [ ] Test 9: Dataset Export with README

**Status**: [ ] Pass [ ] Fail [ X ] Not Tested

---

## Regression Testing

### Test 17: Manual Tower Export (TASK-033)
**Scenario**: Verify manual towers export correctly

**Steps**:
1. Run detection
2. Add manual tower using polygon tool
3. Export CSV, KML, Dataset
4. Verify manual tower included in all formats

**Expected Result**:
- CSV: Manual tower row with source="manual"
- KML: Manual tower marker visible
- Dataset: Manual tower label in .txt file

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

### Test 18: Dataset Restoration (TASK-033)
**Scenario**: Restore previously exported dataset

**Steps**:
1. Export dataset (Test 9)
2. Refresh page
3. Use "Restore from dataset" feature
4. Re-upload exported ZIP
5. Verify restoration

**Expected Result**:
- Map shows restored tower locations
- Tiles load correctly
- Manual towers preserved

**Status**: [ X ] Pass [ ] Fail [ ] Not Tested

---

## Testing Summary

**Date Completed**: March 16, 2026  
**Tester**: User (bg90)  
**Total Tests**: 18  
**Passed**: 16  
**Failed**: 0  
**Not Tested**: 2 (Test 10: not feasible due to UI overlay; Test 16: Firefox not tested)  

**Critical Failures** (if any):
- [X] None

**Bug Discovered During Testing**:
- **Dataset Restoration Failure**: README.txt at ZIP root caused ValueError when parsing file paths
- **Root Cause**: Code assumed all ZIP files had folder structure (with "/")
- **Fix Applied**: Modified upload_dataset() and adapt_filenames() to handle root-level files
- **Status**: ✅ FIXED - Dataset restoration working with README.txt in ZIP

**Notes**:
- All export validation and error handling working as expected
- README.txt successfully included in dataset exports
- Error messages are clear and user-friendly
- No regressions in TASK-033 manual tower functionality
- Cross-browser testing completed for Chrome (Firefox not tested)

**Sign-off**: 
- [X] All export error handling working as expected
- [X] README.txt included in dataset ZIP exports
- [X] All error messages user-friendly and clear
- [X] No regressions in existing functionality

**TASK-036 Status**: ✅ COMPLETE - All acceptance criteria met, production-ready

---

## Automated Test Creation (Future)

**Identified Test Cases for Automation**:
1. Export validation logic (unit tests for validateDetections)
2. Notification system (test all message types)
3. ZIP structure validation (verify README at root)
4. Cross-format consistency (same data in CSV/KML/Dataset)

**Test File Candidates**:
- `tests/unit/test_export_validation.js`
- `tests/integration/test_export_system.py`
- `tests/integration/test_dataset_readme.py`
