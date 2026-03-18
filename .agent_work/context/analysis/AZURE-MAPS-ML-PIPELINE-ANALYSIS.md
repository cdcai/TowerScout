# Azure Maps ML Pipeline Critical Analysis

**Date**: January 15, 2026  
**Analysis Type**: Technical Deep Dive  
**Scope**: Azure Maps Integration with Cooling Tower Detection Pipeline

## Executive Summary

**CRITICAL FINDING**: Azure Maps implementation has **fundamental ML pipeline incompatibilities** that prevent accurate cooling tower detection. The detection system is hardcoded to use Google Maps boundaries regardless of selected provider.

**Impact**: Azure Maps will produce **incorrect or no detection results**, making it unusable for outbreak investigations.

## Critical Code Analysis

### **🚨 PRIMARY ISSUE: Hardcoded Google Maps Detection Logic**

**Location**: `webapp/js/towerscout.js` Lines 2664-2671  
**Function**: `getObjects()` - Core detection pipeline

```javascript
// PROBLEMATIC CODE - Always uses Google Maps even for Azure provider
let boundaries = googleMap.getBoundariesStr();  // Hardcoded to Google Maps!

// Auto-create viewport boundary if no polygons are drawn
if (boundaries === "[]") {
  console.log("No boundary selected, automatically using current viewport as detection area");
  googleMap.addBoundary(new SimpleBoundary(googleMap.getBounds()));  // Google bounds
  azureMap.addBoundary(new SimpleBoundary(googleMap.getBounds()));   // Uses Google bounds!
  boundaries = googleMap.getBoundariesStr();                         // Google string format
}
```

**Problem Analysis**:
1. **Provider Agnostic Call**: `let bounds = currentMap.getBoundsUrl();` correctly uses current provider
2. **Provider Hardcoded Logic**: `let boundaries = googleMap.getBoundariesStr();` always uses Google Maps
3. **Coordinate Mismatch**: Azure Maps receives Google Maps coordinate data
4. **Wrong Tile Selection**: ML models process incorrect geographic areas
5. **Invalid Results**: Detection results irrelevant to user's intended search area

### **🔍 DETECTION FLOW ANALYSIS**

#### **Current Broken Flow (Azure Maps)**:
```
User draws boundary on Azure Maps [lng,lat coordinates]
    ↓
getObjects() function called
    ↓
bounds = azureMap.getBoundsUrl()  ✅ CORRECT (uses Azure coordinates)
    ↓
boundaries = googleMap.getBoundariesStr()  ❌ WRONG (uses Google coordinates)
    ↓
Backend receives mismatched coordinate data
    ↓
Tile generation uses incorrect geographic bounds
    ↓
YOLOv5 processes wrong satellite imagery
    ↓
EfficientNet classifies irrelevant geographic areas
    ↓
Results: Wrong detections or no detections
```

#### **Required Correct Flow (Azure Maps)**:
```
User draws boundary on Azure Maps [lng,lat coordinates]
    ↓
getObjects() function called
    ↓
bounds = azureMap.getBoundsUrl()  ✅ CORRECT
    ↓
boundaries = azureMap.getBoundariesStr()  ✅ REQUIRED FIX
    ↓
Backend receives consistent coordinate data
    ↓
Tile generation uses correct geographic bounds
    ↓
YOLOv5 processes accurate satellite imagery
    ↓
EfficientNet classifies intended geographic areas
    ↓
Results: Accurate cooling tower detections
```

## Missing Method Analysis

**Critical Gap**: `AzureMap` class lacks required method for detection pipeline

```javascript
// MISSING IN AZURE MAPS CLASS:
getBoundariesStr() {
  return JSON.stringify(this.boundaries.map(b => b.toString()));
}
```

**Current State**:
- ✅ `GoogleMap.getBoundariesStr()` - Implemented
- ❌ `AzureMap.getBoundariesStr()` - Missing
- ❌ `TSMap.getBoundariesStr()` - Not defined in base class

## Coordinate System Impact

### **Google Maps (Working)**:
- **Input**: User draws polygon → [lat,lng] coordinates
- **Processing**: `googleMap.getBoundariesStr()` → Correct format
- **Output**: Backend receives accurate geographic bounds
- **Result**: Correct tile selection and detection results

### **Azure Maps (Broken)**:
- **Input**: User draws polygon → [lng,lat] coordinates  
- **Processing**: `googleMap.getBoundariesStr()` → Wrong coordinate system
- **Output**: Backend receives mismatched geographic bounds
- **Result**: Incorrect tile selection, wrong detection areas

## ML Model Compatibility Assessment

### **✅ Models Will Work Correctly Once Fixed**:
1. **YOLOv5 Requirements**: 640x640px satellite tiles (provider agnostic)
2. **EfficientNet Requirements**: Image classification (provider agnostic)
3. **Backend Pipeline**: `/getobjects` endpoint works with any coordinate system
4. **Tile Generation**: `ts_imgutil.make_tiles()` processes any valid bounds
5. **Detection Logic**: ML models don't care about map provider source

### **❌ Current Failure Points**:
1. **Wrong Geographic Areas**: Models analyze incorrect locations
2. **Coordinate Mismatches**: Boundary data doesn't match user intent
3. **Irrelevant Results**: Detections from unintended geographic regions

## Solution Requirements

### **Phase 1: Critical Fixes (Immediate)**
1. **Provider-Agnostic Detection Logic**:
   ```javascript
   // Replace hardcoded googleMap references
   let boundaries = currentMap.getBoundariesStr();
   ```

2. **Implement Missing Azure Method**:
   ```javascript
   // In AzureMap class
   getBoundariesStr() {
     return JSON.stringify(this.boundaries.map(b => b.toString()));
   }
   ```

3. **Base Class Method Definition**:
   ```javascript
   // In TSMap base class
   getBoundariesStr() {
     throw new Error('getBoundariesStr() must be implemented by provider');
   }
   ```

### **Phase 2: Coordinate Normalization**
1. **Consistent Boundary Handling**: Normalize coordinate systems between providers
2. **Validation Testing**: Ensure boundary data matches user-drawn areas
3. **End-to-End Verification**: Validate detection results match intended locations

## Risk Assessment

### **Current Risk Level**: 🚨 **CRITICAL**
- **Azure Maps Completely Unusable**: Will not produce valid cooling tower detections
- **User Experience Broken**: Search areas won't match detection results  
- **Outbreak Investigation Impact**: Tool unreliable for Azure Maps users
- **Data Integrity**: Wrong geographic data could mislead health officials

### **Impact on Existing Functionality**:
- **Google Maps**: ✅ Unaffected (continues working correctly)
- **Azure Maps**: ❌ Fundamentally broken for detection use cases
- **Provider Switching**: ❌ Produces inconsistent results
- **User Trust**: ❌ Tool appears unreliable when using Azure provider

## Validation Strategy

### **Pre-Fix Testing**:
1. Draw boundary on Azure Maps
2. Run detection request
3. Verify backend receives wrong coordinate data
4. Confirm ML models process incorrect geographic areas

### **Post-Fix Testing**:
1. Draw same boundary on Azure Maps
2. Run detection request  
3. Verify backend receives correct coordinate data
4. Confirm ML models process intended geographic areas
5. Validate detection results match user expectations

## Conclusion

The Azure Maps integration requires **immediate critical fixes** to the ML detection pipeline before it can be considered functional. The current implementation creates a **false sense of capability** - users can interact with Azure Maps but will receive meaningless detection results.

**Priority**: Fix ML pipeline dependencies before addressing any other Azure Maps issues.