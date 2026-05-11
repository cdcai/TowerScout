# TYPE A - Frontend Detection Display Fix - December 2, 2025
**Objective**: Fix cooling tower detection display issue where backend detected towers correctly but frontend failed to show them on map
**Execution**: 
- Diagnosed confidence threshold mismatch between backend selection (EfficientNet >= 0.35) and frontend display (YOLOv5 >= 0.15)
- Updated Detection.update() method in towerscout.js to use OR logic: (primary >= 0.15 OR secondary >= 0.35)
- Added maxSecondary tracking for grouped detections to ensure proper confidence calculation
- Fixed generateList() and adjustConfidence() methods to handle both confidence types
**Output**: 
- Cooling towers now properly display on map when detected by backend
- Detection display logic matches backend selection criteria
- All existing detection accuracy preserved while fixing visualization bug
**Next**: Monitor for any edge cases in detection display logic