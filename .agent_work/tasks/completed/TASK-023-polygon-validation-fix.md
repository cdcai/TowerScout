# TYPE A - Polygon Validation Fix - December 2, 2025
**Objective**: Fix "Validation error: At least one polygon is required" that occurred when users clicked "Run Detection" without drawing boundaries
**Execution**:
- Identified UX workflow gap where auto-viewport functionality was commented out in towerscout.js
- Restored auto-viewport boundary creation: when no polygons drawn, automatically use current map viewport as detection area
- Updated JavaScript logic to add viewport boundary for both Google Maps and Azure Maps providers
- Maintained existing validation requirements while providing intuitive fallback behavior
**Output**:
- Users can now run detection immediately without manually drawing polygons
- Current map viewport automatically becomes detection area when no boundaries specified  
- Validation error eliminated while preserving polygon data structure validation
- Backwards compatible with existing polygon drawing functionality
**Next**: Monitor user experience with auto-viewport detection areas