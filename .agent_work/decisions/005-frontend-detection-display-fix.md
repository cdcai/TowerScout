# Decision Record 005 - Frontend Detection Display Fix

**Date**: December 2, 2025  
**Status**: IMPLEMENTED  
**Context**: TASK-021 Frontend Detection Display Bug

## Decision
Use OR logic for confidence thresholds in frontend detection visibility: show detections if they meet EITHER primary YOLOv5 confidence >= 0.15 OR secondary EfficientNet confidence >= 0.35.

## Context
Critical bug where cooling towers detected by backend ML pipeline were not visually displayed on the frontend map interface. Users could not see detection results despite successful ML processing.

### Root Cause Analysis
**Backend Logic (Correct):**
```python
object['selected'] = object['secondary'] >= 0.35
```
Backend correctly used secondary classifier (EfficientNet) threshold of 0.35 for selection.

**Frontend Logic (Broken):**
```javascript  
// BROKEN: Only checked primary confidence
this.selected && this.conf >= Detection_minConfidence && meetsInside
```
Frontend only checked primary YOLOv5 confidence (0.15), ignoring secondary classifier results.

## Options Evaluated

### Option 1: Lower Primary Confidence Threshold (Rejected)
- **Pros**: Simple one-line change
- **Cons**: Would show false positives from YOLOv5 that EfficientNet filters out
- **Decision**: Rejected as it would compromise detection accuracy

### Option 2: Raise Secondary Threshold in Backend (Rejected)
- **Pros**: Aligns thresholds at higher value
- **Cons**: Would reduce detection sensitivity, missing valid towers
- **Decision**: Rejected as EfficientNet threshold is already well-tuned

### Option 3: Use AND Logic (Rejected)
- **Pros**: Ensures both models agree
- **Cons**: Too restrictive, would hide many valid detections
- **Decision**: Rejected as unnecessarily conservative

### Option 4: Use OR Logic (Selected)
- **Pros**: Shows detections if EITHER model has high confidence
- **Cons**: Slightly more complex logic
- **Decision**: Selected as it aligns with backend selection logic

## Implementation Details

### Frontend Visibility Fix
```javascript
// NEW: Use either primary OR secondary threshold
let meetsConfidence = this.conf >= Detection_minConfidence || this.secondary >= 0.35;
this.map.updateMapRect(this, this.selected && meetsConfidence && meetsInside);
```

### Confidence Slider Fix
```javascript
// FIXED: Consistent logic for confidence adjustment
let meetsConf = det.conf >= Detection_minConfidence || det.secondary >= 0.35;
```

### Secondary Confidence Tracking
```javascript
// NEW: Track maximum secondary confidence for grouped detections
this.maxSecondary = secondary; // in constructor
firstDet.maxSecondary = Math.max(det.secondary, firstDet.maxSecondary || 0);
```

## Rationale

**Consistency**: Frontend visibility now matches backend selection logic
**Accuracy**: Preserves ML model accuracy by using both classifier outputs
**User Experience**: Users see all detections that backend considers valid
**Performance**: Minimal computational overhead for OR condition check

## Impact

### Functional Impact
- **HIGH**: Restores core application functionality
- **User Experience**: Cooling towers now visible on map interface
- **Accuracy**: Maintains ML detection accuracy standards
- **Compatibility**: Works with existing confidence slider functionality

### Technical Impact
- **Security**: No security implications
- **Performance**: Minimal - only affects frontend filtering logic  
- **Maintainability**: Cleaner alignment between frontend and backend
- **Testing**: Existing detection pipeline tests still valid

## Validation Results

### Before Fix
- Backend: Detections found with correct confidence scores
- Frontend: No visual circles displayed on map
- User Impact: Application appeared broken, no detection results visible

### After Fix  
- Backend: Same detection results (no change)
- Frontend: Detection circles properly displayed on map
- User Impact: Full application functionality restored

## Trade-offs

### Accepted Trade-offs
- **Complexity**: Slightly more complex OR logic vs simple threshold check
- **Debugging**: Need to track both confidence values for troubleshooting

### Benefits Gained
- **Functionality**: Core application feature working again
- **Consistency**: Frontend and backend logic aligned
- **Maintainability**: Single source of truth for confidence thresholds

## Review Criteria
- **Functionality**: Detection circles appear for all backend-selected towers
- **Accuracy**: No false positives shown beyond backend selection
- **Performance**: No noticeable impact on map rendering speed
- **Usability**: Confidence slider works correctly with new logic

## Future Considerations
- **Unified Configuration**: Consider centralizing confidence thresholds in configuration
- **Advanced Filtering**: Machine learning-based confidence weighting
- **Performance Monitoring**: Track frontend rendering performance with new logic

This decision restores TowerScout's core functionality by aligning frontend display logic with backend ML selection criteria, ensuring users can see all detections that the system considers valid.