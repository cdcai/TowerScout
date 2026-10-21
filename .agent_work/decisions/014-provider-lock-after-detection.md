# Decision Record 014: Provider Lock After Detection

**Date**: March 13, 2026  
**Context**: TASK-033 Phase 4 - Manual Tower Addition  
**Status**: APPROVED  
**Impact**: User Experience, State Management, Data Integrity

## Decision

**Disable map provider switching (Google Maps ↔ Azure Maps) after detection runs complete** (ML detection OR manual tower addition).

Provider dropdown will be locked with tooltip: *"Clear all detections to switch providers. Switching providers with active detections causes imagery mismatch."*

## Context

During TASK-033 Phase 4 planning, we evaluated whether to allow provider switching after detection results are loaded. Three options were considered:

1. **Allow switching** (current behavior)
2. **Disable switching** after detection runs
3. **Warn + clear** on switch attempt

## Problem Statement

**Imagery Mismatch Issue**:
- Detection coordinates calculated relative to specific map provider's imagery
- Google Maps and Azure Maps use different:
  - Satellite imagery sources
  - Imagery capture dates
  - Tile boundaries and zoom levels
  - Coordinate projection precision
- Switching providers after detection causes visible misalignment between detection rectangles and actual image features

**User Confusion**:
- Users may switch providers to "compare imagery quality"
- Misaligned detections appear as false positives
- Manual towers drawn on one provider become inaccurate on another

**Testing Complexity**:
- Cross-provider persistence working (TASK-041)
- But coordinate precision issues create edge cases
- Extensive testing required for each provider combination

## Options Evaluated

### Option A: Allow Provider Switching (Current)
**Pros**:
- Flexibility for imagery comparison
- Provider fallback if one service fails
- Already implemented and tested

**Cons**:
- ❌ Detection coordinate mismatch (imagery sources differ)
- ❌ User confusion when markers don't align
- ❌ Increased support burden explaining misalignment
- ❌ Complex state management for coordinate remapping

### Option B: Disable Provider Switching (Selected) ✅
**Pros**:
- ✅ Prevents imagery mismatch issues
- ✅ Simpler state management (no coordinate remapping)
- ✅ Clearer user mental model (one detection = one provider)
- ✅ Reduces testing surface area
- ✅ Better data integrity for outbreak investigations

**Cons**:
- Users must "Clear All" to switch providers
- Loss of mid-workflow provider comparison
- Requires tooltip/UI feedback for disabled state

### Option C: Warn + Clear on Switch
**Pros**:
- Maintains flexibility
- User explicitly acknowledges data loss

**Cons**:
- Data loss risk (accidental clicks)
- Dialog fatigue for users
- Still requires testing cross-provider coordinate handling

## Rationale

**Selected: Option B (Disable Provider Switching)**

### Primary Reasons:

1. **Data Integrity for Outbreak Investigations** (Mission-Critical):
   - TowerScout used in Legionnaires' disease investigations
   - Coordinate precision essential for field team accuracy
   - Misaligned markers could direct teams to wrong buildings
   - **Risk**: False positives/negatives in outbreak response

2. **Simplified User Mental Model**:
   - One detection session = one map provider
   - Clear separation: Choose provider → Run detection → Export results
   - Export preserves data; refresh resets session
   - Aligns with existing "no session persistence" design (AC-007 deferred)

3. **Technical Simplicity**:
   - No coordinate remapping logic needed
   - No cross-provider coordinate precision testing
   - Reduces state management complexity
   - Leverages existing "Clear All" functionality

4. **User Workflow Analysis**:
   - Users primarily choose provider at session start
   - Mid-workflow provider switching rare in actual usage
   - Export functionality provides save mechanism before switching
   - **Acceptable trade-off**: Require "Clear All" for provider change

### Implementation Cost:
- **Disable approach**: 1 hour (dropdown disable + tooltip)
- **Warn approach**: 2-3 hours (dialog + clear handlers + testing)
- **Coordinate remapping**: 8-12 hours (precision testing + edge cases)

## Implementation Details

### UI Changes:
```javascript
// After detection completes
$('#provider-dropdown').prop('disabled', true);
$('#provider-dropdown').attr('title', 
  'Clear all detections to switch providers. ' +
  'Switching providers with active detections causes imagery mismatch.'
);

// After "Clear All" removes all detections
$('#provider-dropdown').prop('disabled', false);
$('#provider-dropdown').attr('title', 'Select map provider');
```

### Lock Triggers:
- ML detection completes with results
- Manual tower added
- Dataset restored

### Unlock Triggers:
- "Clear All" removes all manual towers
- Detection results cleared (threshold filter or boundary clear)
- New session started

## Impact Assessment

### Functional Impact:
- **Breaking Change**: Yes (removes mid-workflow provider switching)
- **Mitigation**: "Clear All" button provides exit path
- **User Education**: Tooltip explains lock reason and workaround

### Performance Impact:
- Minimal (disable/enable DOM element)
- No network requests or state changes

### Testing Impact:
- **Reduced**: No cross-provider coordinate precision testing
- **Simplified**: Provider switch testing only pre-detection
- **Maintained**: TASK-041 provider stability work still valid

### Maintenance Impact:
- **Reduced complexity**: No coordinate remapping logic
- **Fewer edge cases**: Single-provider session model
- **Clear boundaries**: Provider choice is session-level decision

### User Experience Impact:
**Positive**:
- Prevents confusing coordinate misalignment
- Clearer mental model (one session = one provider)
- Tooltip provides actionable guidance

**Negative**:
- Loss of mid-workflow provider comparison
- Requires "Clear All" to switch
- May surprise users expecting switching

## Future Considerations

### If Provider Switching Needed Later:
1. **Coordinate Remapping System**:
   - Store original provider per detection
   - Calculate coordinate offsets between providers
   - Adjust bounding boxes during switch
   - **Effort**: 8-12 hours implementation + testing

2. **Smart Provider Comparison**:
   - Side-by-side view mode (split screen)
   - Show same detection on both providers simultaneously
   - No coordinate remapping needed
   - **Effort**: 16-24 hours (new UI mode)

3. **Detection Preservation with Warning**:
   - Allow switch but mark detections as "imagery different"
   - Visual indicator of potential misalignment
   - **Effort**: 4-6 hours (warning system)

### Related Enhancement Opportunities:
- **AC-013 Alternative**: If polygon editing implemented, unlock during editing only
- **Multi-Provider Export**: Export includes provider metadata for reproduction
- **Provider Recommendation**: Suggest provider based on location/coverage

## Review Conditions

**Reassess this decision if**:
1. User feedback indicates provider switching is critical mid-workflow
2. Coordinate remapping precision becomes technically feasible
3. Provider imagery convergence reduces mismatch issues
4. Side-by-side comparison mode is implemented

**Review Date**: Sprint 04 retrospective (March 26, 2026)

## References

- **TASK-033**: Manual Tower Addition Feature
- **TASK-041**: Provider State Management Stability
- **AC-008**: Provider switching preservation (pre-detection)
- **Outbreak Investigation Workflow**: Coordinate precision requirements

## Sign-off

**Decision Made By**: User + AI Copilot (collaborative design review)  
**Approval Date**: March 13, 2026  
**Implementation Target**: TASK-033 Phase 4  
**Expected Completion**: March 13-14, 2026
