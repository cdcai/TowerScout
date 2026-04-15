# ISSUE-003 Performance Investigation

**Created**: 2026-03-23  
**Status**: Discovery completed; targeted Azure shape-index fix implemented, Azure init regression corrected, and local source/build validation completed  
**Related Tasks**: ISSUE-003, TASK-048, TASK-050

---

## Executive Summary

Large-dataset stress testing does **not** currently point to the detection list as the primary risk. The local harness shows list generation and confidence filtering staying roughly linear at 500-1000 visible detections, while the Azure Maps detection-update path scales poorly because it scans the entire `detectionDataSource` on every detection update.

The highest-signal finding is in `webapp/js/src/providers/AzureMap.js`: `updateMapRect()` and `colorMapRect()` repeatedly call `getShapes()` and then `filter(...)` by `detectionId`. That creates an O(n^2) access pattern during large detection loads, remounts, or provider refreshes.

**Current recommendation**: `NO-GO` for broad Sprint 04 optimization work such as virtual scrolling or clustering based on this harness alone. The targeted Azure shape-index refactor has now been implemented as the bounded quick win supported by the evidence.

---

## Implementation Update

### Code Changes
- `webapp/js/src/providers/AzureMap.js`
  - added an Azure-side `detectionShapeIndex` map keyed by `detectionId`
  - switched `updateMapRect()` and `colorMapRect()` to indexed lookups instead of repeated `getShapes().filter(...)`
  - added provider helpers to clear, remove, and reindex detection shapes so the cache stays aligned with sort/reset/manual-clear flows
- `webapp/js/src/detection/Detection.js`
  - `Detection.resetAll()` now delegates Azure overlay cleanup to the provider helper
  - `Detection.sort()` now reindexes Azure shapes after `detectionId` changes

### Local Validation
- `node --check webapp/js/src/providers/AzureMap.js`
- `node --check webapp/js/src/detection/Detection.js`
- `node webapp/build.js`
- mocked Node smoke test covering:
  - first update scans the data source once
  - repeated `updateMapRect()` / `colorMapRect()` calls reuse the indexed shape
  - `clearDetectionShapes()` clears both the Azure data source and the in-memory index

### Regression Follow-up
- Browser testing after the first implementation exposed an Azure restore/init regression: the app stayed in the "map is still loading" state when starting a circle boundary.
- Root cause was a stray `o.azureShape = shape;` statement accidentally left at the top of `initializeDrawingTools()` in `webapp/js/src/providers/AzureMap.js`.
- That line threw before Azure could mark `drawingManagerReady`, which blocked `providerManager.isFullyInitialized()` and prevented boundary creation.
- The stray statement was removed and `webapp/js/towerscout.js` was rebuilt. A fresh live-browser retest is still pending.

---

## Method

### Harness
- Created reproducible benchmark script: `.agent_work/context/archive/2026-04/ISSUE-003/issue-003-benchmark.js`
- Saved raw results: `.agent_work/context/archive/2026-04/ISSUE-003/ISSUE-003-benchmark-results.json`

### Scope Measured
- 100, 500, and 1000 visible detections
- Detection creation
- `Detection.sort()`
- `Detection.generateList()`
- `adjustConfidence()`
- Full remount onto a fresh map object to simulate a provider-side redraw path

### Important Limitation
- This is a **Node-based synthetic harness**, not a live browser + Google Maps/Azure Maps SDK profile.
- It measures the JavaScript/data-structure cost of the current code paths.
- It does **not** measure real DOM layout/paint, real Azure SDK rendering, or browser DevTools timings.

Because of that, the harness is best used for hotspot identification and relative scaling, not for claiming exact end-user render times.

---

## Key Results

### 500 Visible Detections

| Path | Google-like | Azure-like |
| --- | ---: | ---: |
| Create detections | 1.068 ms | 2.768 ms |
| `Detection.sort()` | 0.178 ms | 0.657 ms |
| `Detection.generateList()` | 1.701 ms | 1.099 ms |
| `adjustConfidence()` | 0.320 ms | 0.122 ms |
| Remount on fresh map | 1.241 ms | 2.558 ms |

### 1000 Visible Detections

| Path | Google-like | Azure-like |
| --- | ---: | ---: |
| Create detections | 0.717 ms | 3.657 ms |
| `Detection.sort()` | 0.253 ms | 0.169 ms |
| `Detection.generateList()` | 2.337 ms | 1.022 ms |
| `adjustConfidence()` | 0.551 ms | 2.457 ms |
| Remount on fresh map | 0.301 ms | 7.183 ms |

### Azure Shape Lookup Counts

| Scenario | Shape lookups |
| --- | ---: |
| 500 detections, initial load | 374,750 |
| 500 detections, fresh-map remount | 124,750 |
| 1000 detections, initial load | 1,499,500 |
| 1000 detections, fresh-map remount | 499,500 |

Those lookup counts are the clearest signal in this investigation. They scale exactly like repeated full-array scans, not keyed lookup.

---

## Findings

### 1. Detection list rendering is not the leading hotspot

`Detection.generateList()` in `webapp/js/src/detection/Detection.js` builds one large HTML string and assigns it once to `detectionsList.innerHTML`. In the harness, that remained well below the issue threshold even at 1000 visible detections.

This does **not** prove the DOM is free, but it does suggest list virtualization should not be the first optimization.

### 2. Azure detection updates were the quadratic hotspot

The investigation found this pattern in `webapp/js/src/providers/AzureMap.js` before the fix:
- `this.detectionDataSource.getShapes()`
- `shapes.filter(...)`
- compare each shape property to `detectionId`

The same lookup pattern also existed in `colorMapRect()`.

That means:
- first-time add of N visible detections repeatedly rescans already-added shapes
- remount/provider-refresh flows rescan all shapes again
- highlight/color changes also pay for a full scan

This was the main optimization target and is the area addressed by the implemented Azure shape index.

### 3. Google-like provider behavior is comparatively flat

The Google-style stub only performs direct rectangle updates, so its scaling stayed close to linear and materially lower than the Azure-like path in the remount benchmark.

Inference: the large-dataset risk is currently much more provider-specific than detection-list-specific.

### 4. Logging noise will distort real profiling and may add overhead

Two code areas are especially noisy:
- `Detection.sort()` in `webapp/js/src/detection/Detection.js` logs every detection before and after sort.
- `webapp/js/src/globals.js` routes `Detection_detections` through `providerManager.getDetectionsArrayDirect()`, and `getDetectionsArrayDirect()` in `webapp/js/src/managers/ProviderStateManager.js` emits a warning on direct access.

The harness triggered thousands of console calls at 500-1000 detections. The exact counts are synthetic and should not be treated as production timings, but the code paths are still noisy enough to interfere with profiling clarity. This should feed directly into TASK-048.

---

## Source-Level Evidence

### Azure Maps provider
- `webapp/js/src/providers/AzureMap.js`
  - `updateMapRect()` now uses an Azure-side `detectionShapeIndex` for hot-path lookups
  - `colorMapRect()` now reuses the same index instead of rescanning the full data source

### Detection list and detection lifecycle
- `webapp/js/src/detection/Detection.js`
  - `Detection.sort()` contains full-array debug logging
  - `Detection.generateList()` iterates all detections, rebuilds the full list, and calls `det.update()`
  - `selectAddr()` updates every detection sharing an address
  - `update()` delegates marker visibility to the provider map implementation

### Confidence filtering
- `webapp/js/src/detection/DetectionList.js`
  - `adjustConfidence()` iterates all detections, toggles list visibility, and calls `det.update()`
  - `changeReviewMode()` forces an additional full detection update pass

---

## Go / No-Go

### Broad optimization work this sprint
- **NO-GO**
- Reason: the local benchmark does not show evidence that detection-list rendering alone justifies major work such as virtual scrolling or clustering inside Sprint 04.

### Small targeted refactor if capacity remains
- **DONE**
- Implemented: Azure-side `Map<detectionId, shape>` cache so `updateMapRect()` and `colorMapRect()` stop scanning `getShapes()` on every call.
- Expected impact: removes the current O(n^2) lookup pattern with limited surface-area risk.

---

## Recommended Next Steps

1. Treat this report as both the discovery artifact and the implementation note for the targeted Azure fix.
2. Feed sort/debug/deprecation console-noise cleanup into TASK-048 before doing any serious browser profiling.
3. If a real browser regression is reported later, capture a live Azure Maps performance profile before considering virtualization or clustering.

---

## Bottom Line

The evidence so far says:
- detection list work is not the first bottleneck
- Azure detection shape lookup was the primary scaling risk
- broad Sprint 04 performance work should be deferred
- the targeted Azure lookup refactor was the only optimization with strong evidence behind it, and it has now been implemented
