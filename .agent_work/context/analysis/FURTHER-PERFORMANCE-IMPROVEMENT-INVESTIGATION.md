# Further Performance Improvement Investigation

**Created**: 2026-03-31  
**Status**: Static hotspot analysis complete; no fresh live-browser or backend phase-timing capture was available in this pass  
**Related Tasks**: ISSUE-003, TASK-048, TASK-050

---

## Executive Summary

The Azure shape-lookup fix from ISSUE-003 addressed one real frontend hotspot, but it did **not** eliminate the main remaining opportunities under extreme loads. Based on code-path review, the strongest follow-on opportunities are:

1. **Stop duplicate work before and after detection execution**
   - the app currently performs an estimate request and then an actual detection request, repeating tile generation and polygon filtering
   - the frontend also walks the full detection set multiple times during initial hydration
2. **Cut blocking post-processing from the critical path**
   - reverse geocoding still runs inline before the detection response returns
   - the geocoding cache rewrites a JSON file on each cache insert
3. **Reduce tile-pipeline I/O**
   - map tiles are downloaded to disk, then reopened from disk for model inference
   - the secondary classifier still saves debug images to `uploads/` during inference
4. **Reduce browser main-thread and overlay churn**
   - detection creation, sorting, list generation, filtering, and map visibility updates are currently synchronous and repeated
   - Google still creates one rectangle object per detection and one rectangle object per tile object
5. **Remove profiling noise first**
   - the current codebase contains very heavy backend `print()` and frontend `console.*()` volume, which will distort both perceived performance and future profiling

**Best next quick wins**:
- remove or gate debug image writes in `ts_en.py`
- reduce logging noise in backend and provider JS paths
- eliminate duplicate frontend visibility passes (`generateList()` + `adjustConfidence()` + extra `adjustConfidence()` call)
- avoid creating map rectangles for non-rendered tile metadata objects

**Best next medium-size refactors**:
- reuse estimate results for the actual detection request
- move geocoding off the blocking response path, or at minimum dedupe and batch it better
- add a shared imagery cache for the detection pipeline instead of downloading the same tiles repeatedly

---

## Scope And Method

This investigation used:

- the prior ISSUE-003 findings
- static review of the active detection pipeline in:
  - `webapp/towerscout.py`
  - `webapp/ts_maps.py`
  - `webapp/ts_yolov5.py`
  - `webapp/ts_en.py`
  - `webapp/ts_imgutil.py`
  - `webapp/ts_geocoding.py`
  - `webapp/ts_geocache.py`
  - `webapp/js/src/ui/search.js`
  - `webapp/js/src/detection/*.js`
  - `webapp/js/src/providers/*.js`

Constraints of this pass:

- `logs/performance.log` exists locally but was empty during this review
- `logs/performance.jsonl` was not present
- no live browser trace, network waterfall, or server phase-timing sample was captured here

So the findings below are **evidence-backed hotspot analysis**, not measured end-user timings.

---

## Current Hot Path

### Backend Request Flow

1. Frontend calls `/getobjects` once for tile estimation and again for the real detection run in `webapp/js/src/ui/search.js`.
2. Backend validates input in `webapp/towerscout.py`.
3. Backend creates tiles with `map.make_tiles(...)`, then filters them with:
   - `ts_maps.check_tile_against_bounds(...)`
   - `ts_imgutil.tileIntersectsPolygons(...)`
4. Backend downloads all imagery through `Map.get_sat_maps(...)` in `webapp/ts_maps.py`.
5. YOLOv5 reopens each tile image from disk and runs inference in `webapp/ts_yolov5.py`.
6. EfficientNet re-checks medium-confidence detections in `webapp/ts_en.py`.
7. Backend transforms coordinates, filters detections against boundaries again, reverse-geocodes detections, persists large session artifacts, and returns one large JSON payload.

### Frontend Result Flow

1. `processObjects(...)` in `webapp/js/src/ui/search.js` iterates the entire response.
2. It instantiates:
   - a `Detection` object for each detection
   - a `Tile` object for each tile payload item
3. It then performs:
   - `Detection.sort()`
   - `Detection.generateList()`
   - `adjustConfidence()`
4. `Detection.generateList()` itself also calls `adjustConfidence()`
5. `adjustConfidence()` loops every detection and calls `det.update()`, which drives map visibility changes.

Under extreme loads, that means the app still has several whole-array passes even after the Azure lookup fix.

---

## Findings

## 1. Duplicate Estimate And Execution Work Still Inflates Backend Search Time

**Evidence**

- `webapp/js/src/ui/search.js:135` sends an estimate request to `/getobjects`
- `webapp/js/src/ui/search.js:182` sends the real detection request to `/getobjects`
- `webapp/towerscout.py:1182` and `webapp/towerscout.py:1183` recompute tile filtering on the backend

**Why it matters**

Large search areas already pay for tile generation and polygon intersection logic once to get the estimate. The real request immediately repeats that same work. For very large circles or polygons, this is avoidable latency before any imagery download or model inference begins.

**Opportunity**

- cache the estimated tile plan by request signature:
  - provider
  - engine
  - bounds
  - polygon hash
  - crop settings
- return an estimate token from the first call
- allow the second call to reuse the prepared tile plan instead of regenerating it

**Expected impact**: medium  
**Risk**: low to medium  
**Rank**: quick win / safe refactor

---

## 2. Tile Filtering Uses Repeated Geometry Construction That Will Scale Poorly

**Evidence**

- `webapp/towerscout.py:1183` filters every tile through `ts_imgutil.tileIntersectsPolygons(...)`
- `webapp/ts_imgutil.py:37` builds a new Shapely `Polygon` for every tile check
- `webapp/towerscout.py:1354` later filters every detection through `resultIntersectsPolygons(...)`
- `webapp/ts_imgutil.py:57` builds another Shapely `Polygon` per detection for that pass

**Why it matters**

For large circles or complex polygons, the system first generates a full bounding-box tile grid and only then throws tiles away with geometry checks. That is acceptable at modest sizes, but it becomes expensive when tile counts grow sharply.

**Opportunity**

- precompute prepared geometries once per request
- short-circuit with polygon bounding boxes before constructing Shapely objects
- for circle boundaries, generate only the intersecting tile rows/columns directly instead of full-box generation plus rejection
- consider an STRtree or prepared-union approach if multiple polygons become common

**Expected impact**: medium  
**Risk**: medium  
**Rank**: safe refactor

---

## 3. Reverse Geocoding Still Blocks The Main Detection Response

**Evidence**

- `webapp/towerscout.py:1384` starts address lookup after detection post-processing
- `webapp/towerscout.py:1423` calls `geocoding_service.reverse_geocode(...)` inline for uncached detections
- `webapp/ts_geocoding.py:385` performs reverse geocoding sequentially per detection
- `webapp/ts_geocoding.py:257` and `webapp/ts_geocoding.py:332` use blocking `requests.get(...)`

**Why it matters**

Under heavy detection loads, users wait not only for imagery download and model inference, but also for all reverse-geocoding work before the response returns. This is especially costly when detections fan out across many rooftops.

**Opportunity**

- split the response into:
  - fast initial detection response with coordinates/confidence
  - deferred address augmentation pass
- or batch geocoding work with bounded concurrency if the provider/API rules allow it
- dedupe geocoding by spatial cluster before making network calls
- only geocode visible/selected detections on first render, then backfill the rest

**Expected impact**: high when detection count is high  
**Risk**: medium, because address availability is part of the review workflow  
**Rank**: high-value refactor

---

## 4. Geocoding Cache Persistence Has Write Amplification

**Evidence**

- `webapp/towerscout.py:1405` creates a new `GeocodingCache` for each request
- `webapp/ts_geocache.py:122` loads the full file cache during initialization
- `webapp/ts_geocache.py:282` writes new results through `put(...)`
- `webapp/ts_geocache.py:312` calls `_save_file_cache()` on each `put(...)`
- `webapp/ts_geocache.py:149` rewrites the full JSON cache file

**Why it matters**

If a large result set causes many cache misses, the cache file can be repeatedly rewritten during the same request. That introduces extra disk I/O precisely when the request is already doing network and model work.

**Opportunity**

- keep one long-lived cache instance in memory instead of recreating it per request
- batch cache writes and flush once per request
- move the cache to SQLite or Redis instead of rewriting a whole JSON file
- if keeping file cache, append journal entries and compact later instead of full-file rewrite on each insert

**Expected impact**: medium to high on cold or low-hit geocoding runs  
**Risk**: low to medium  
**Rank**: quick win / safe refactor

---

## 5. Detection Imagery Download Bypasses The Existing Proxy Cache

**Evidence**

- `webapp/ts_maps.py:37` builds provider URLs directly in `get_sat_maps(...)`
- `webapp/ts_maps.py:53` downloads them immediately via `gather_urls(...)`
- `webapp/towerscout.py:812` defines `/api/maps/<provider>/<service>` with caching support
- `webapp/towerscout.py:846` through `webapp/towerscout.py:869` implement proxy-side cache lookup and write

**Why it matters**

The app already has a cacheable map-proxy path, but the core detection workflow does not appear to reuse it. Repeated or overlapping searches can therefore redownload the same imagery instead of reusing cached tile bytes.

**Opportunity**

- introduce a shared detection-tile cache keyed by provider URL or tile signature
- optionally route detection downloads through the same cache mechanism used by `/api/maps/...`
- keep cache entries provider-specific and TTL-controlled

**Expected impact**: medium on overlapping searches; low on entirely unique searches  
**Risk**: medium  
**Rank**: safe refactor

---

## 6. Tile Processing Still Pays Heavy Disk I/O

**Evidence**

- `webapp/towerscout.py:1229` downloads tile files to a temp directory
- `webapp/towerscout.py:1246` adds the downloaded filenames to tile records
- `webapp/ts_yolov5.py:106` reopens each image from disk with `Image.open(...)`
- `webapp/ts_yolov5.py:129` copies images again when the secondary classifier is enabled

**Why it matters**

The current path is:

1. download bytes
2. write bytes to disk
3. reopen bytes from disk
4. crop/copy in memory
5. optionally save more debug images later

That is workable, but it is not optimal for large batches.

**Opportunity**

- keep tile bytes in memory through detection when export is not needed yet
- if disk persistence must remain, use a memory-backed temp location or defer file persistence until export
- read metadata and image bytes through one object rather than multiple reopen passes

**Expected impact**: medium  
**Risk**: medium  
**Rank**: safe refactor

---

## 7. EfficientNet Secondary Classification Has A Clear Debug-I/O Hotspot

**Evidence**

- `webapp/ts_en.py:123` runs the secondary classifier per detection
- `webapp/ts_en.py:144` saves the full source image to `uploads/`
- `webapp/ts_en.py:145` saves the cropped detection image to `uploads/`

**Why it matters**

For every medium-confidence detection, the system writes two debug images. Under extreme loads, this can add substantial disk I/O and filesystem churn and can crowd the uploads directory.

**Opportunity**

- remove these writes from the default path
- or gate them strictly behind an explicit debug flag
- batch secondary classifier inputs instead of single-detection inference where practical

**Expected impact**: high for detection-heavy searches with many intermediate-confidence objects  
**Risk**: low  
**Rank**: best quick win on the model-processing side

---

## 8. Frontend Hydration Still Repeats Full Detection Passes

**Evidence**

- `webapp/js/src/detection/PlaceRect.js:20` creates a map rectangle/feature during object construction
- `webapp/js/src/detection/Detection.js:92` calls `this.update()` during each `Detection` construction
- `webapp/js/src/detection/Detection.js:181` calls `det.update()` again while building the list
- `webapp/js/src/detection/Detection.js:189` calls `adjustConfidence()` from `generateList()`
- `webapp/js/src/ui/search.js:264` through `webapp/js/src/ui/search.js:266` then call `Detection.sort()`, `Detection.generateList()`, and `adjustConfidence()` again
- `webapp/js/src/detection/DetectionList.js:17` through `webapp/js/src/detection/DetectionList.js:32` loop every detection and call `det.update()`

**Why it matters**

Initial result hydration is still doing multiple whole-array visibility passes:

- constructor-time update
- list-generation update
- `adjustConfidence()` update from inside `generateList()`
- another `adjustConfidence()` update immediately afterward in `processObjects(...)`

At extreme result counts, that is a real main-thread cost even if each individual pass is simple.

**Opportunity**

- remove the redundant `adjustConfidence()` call in `processObjects(...)` if `generateList()` already owns it
- stop calling `det.update()` during `generateList()`; build the DOM first, then perform one visibility pass
- hydrate detections in a paused/inactive state, then apply one post-hydration update

**Expected impact**: high on the frontend under large result sets  
**Risk**: low to medium  
**Rank**: best browser quick win after logging cleanup

---

## 9. Frontend Result Processing Is Fully Synchronous

**Evidence**

- `webapp/js/src/ui/search.js:222` through `webapp/js/src/ui/search.js:266` process the full response in one synchronous block
- `webapp/js/src/detection/Detection.js:185` replaces the whole list HTML in one shot
- `webapp/js/src/detection/DetectionList.js:17` loops the full detection set for filtering and update

**Why it matters**

Even if the total amount of work is acceptable, doing it all in one turn creates a long main-thread task. Under extreme loads, that causes UI stalls and makes the app feel frozen.

**Opportunity**

- process detections in chunks using `requestAnimationFrame`
- stage list rendering and map overlay rendering separately
- defer non-critical metadata decoration until after the first frame
- preserve the current full render path for small result sets and only switch to chunked mode above a threshold

**Expected impact**: medium to high on perceived responsiveness  
**Risk**: medium  
**Rank**: high-value refactor

---

## 10. Tile Metadata Objects Still Create Map Overlay Objects

**Evidence**

- `webapp/js/src/ui/search.js:250` through `webapp/js/src/ui/search.js:253` instantiate a `Tile` object for each tile result
- `webapp/js/src/detection/PlaceRect.js:20` creates a map rectangle/feature during construction
- `webapp/js/src/providers/GoogleMap.js:820` through `webapp/js/src/providers/GoogleMap.js:839` always create a `google.maps.Rectangle` in `makeMapRect(...)`
- `webapp/js/src/providers/AzureMap.js:722` explicitly says tiles are metadata-only and not visual elements, but a feature object is still constructed before the skip path

**Why it matters**

Tile objects exist primarily for metadata, export, and review support, but they still flow through map-rectangle creation. On Google especially, that means one `google.maps.Rectangle` instance per tile even when tiles are not shown.

**Opportunity**

- stop inheriting visible map-rectangle behavior for metadata-only tiles
- create a lightweight tile data model with no provider overlay object by default
- materialize tile overlays only when a review mode actually needs them

**Expected impact**: medium  
**Risk**: medium because tile review/export code depends on the current object model  
**Rank**: safe refactor

---

## 11. Browser Overlay Count Is Still A Likely Ceiling Under Extreme Loads

**Evidence**

- `webapp/js/src/providers/GoogleMap.js:835` shows one Google rectangle overlay per detection
- `webapp/js/src/providers/AzureMap.js:863` and `webapp/js/src/providers/AzureMap.js:939` still manage one Azure shape per detection, even though lookup is now indexed

**Why it matters**

The Azure lookup fix removed a bad access pattern, but the app still renders one overlay per detection. At sufficiently high counts, the limiting factor becomes raw overlay count, event handling, and paint/update churn.

**Opportunity**

- viewport culling: only render detections inside current bounds
- low-zoom clustering by address or proximity
- switch to a canvas/WebGL-backed overlay for large result sets instead of one provider-native object per detection

**Expected impact**: high only at very large counts  
**Risk**: high  
**Rank**: defer until browser profile proves overlay count is now the dominant bottleneck

---

## 12. Logging Noise Will Distort Any Future Profiling

**Evidence**

- `webapp/towerscout.py` currently contains **178** `print(...)` calls
- `webapp/js/src/providers/AzureMap.js` currently contains **178** `console.log|warn|error` calls
- `webapp/js/src/providers/GoogleMap.js` currently contains **79** `console.log|warn|error` calls

**Why it matters**

At extreme loads, logging becomes real work:

- backend stdout/stderr writes
- frontend console formatting and DevTools overhead
- noise that makes true hotspots harder to isolate

This also interacts with many of the loops above, because several logs occur per tile, per detection, or per visibility update.

**Opportunity**

- move verbose logs behind `TOWERSCOUT_DEBUG`
- keep only user-meaningful warnings/errors in the default path
- remove per-detection and per-tile logging from normal operation

**Expected impact**: medium and broadly distributed  
**Risk**: low  
**Rank**: best cross-cutting quick win

---

## Prioritized Improvement Backlog

| Priority | Area | Recommendation | Impact | Risk | Suggested Bucket |
| --- | --- | --- | --- | --- | --- |
| 1 | Tile processing | Remove or debug-gate `img.save(...)` and `det_img.save(...)` in `ts_en.py` | high | low | quick win |
| 2 | Logging | Gate backend/frontend verbose logging under debug mode | medium | low | quick win |
| 3 | Browser rendering | Remove duplicate `adjustConfidence()` / `det.update()` passes during hydration | high | low-medium | quick win |
| 4 | Browser rendering | Stop creating map overlay objects for metadata-only tile objects | medium | medium | safe refactor |
| 5 | Backend latency | Reuse estimate tile plan for actual detection execution | medium | medium | safe refactor |
| 6 | Backend latency | Batch or defer geocoding instead of blocking the initial response | high | medium | high-value refactor |
| 7 | Backend latency | Replace per-insert geocoding cache rewrites with batched or persistent cache writes | medium-high | low-medium | safe refactor |
| 8 | Tile pipeline | Add shared imagery cache for detection downloads | medium | medium | safe refactor |
| 9 | Browser responsiveness | Chunk large result hydration with `requestAnimationFrame` | medium-high | medium | high-value refactor |
| 10 | Geometry | Precompute/prep polygon intersection logic and generate fewer rejected tiles | medium | medium | safe refactor |
| 11 | Overlays | Add viewport culling / clustering / canvas rendering for huge result sets | high at extreme scale | high | defer until measured |
| 12 | Model tuning | Revisit YOLO/secondary batch sizes and concurrency using real hardware traces | variable | medium-high | defer until measured |

---

## Recommended Execution Order

### Phase 1: Quick Wins Before More Profiling

1. Remove or debug-gate secondary-classifier image saves.
2. Reduce backend and provider logging noise.
3. Remove duplicate frontend hydration/update passes.
4. Stop allocating provider overlay objects for metadata-only tiles.

### Phase 2: Backend Refactors With Strong Evidence

1. Reuse estimate results for actual detection execution.
2. Fix geocoding cache write amplification.
3. Decide whether geocoding should block initial render at all.
4. Introduce a shared imagery cache for repeated searches.

### Phase 3: Measured Work Only

1. Capture real performance logs with tile download / model / geocoding phase timings.
2. Capture a live browser performance profile with 500, 1000, and 2000+ detections.
3. Only then decide whether overlay clustering, virtualization, or canvas rendering is justified.

---

## Bottom Line

The next performance gains are unlikely to come from one dramatic algorithmic fix like ISSUE-003. The highest-probability wins now are:

- **cutting duplicate passes**
- **removing blocking geocoding and debug I/O**
- **reducing logging noise**
- **avoiding unnecessary frontend object/overlay creation**

If those are addressed first, the follow-up browser and backend profiles should be much cleaner and will give a better signal on whether larger architectural changes such as clustering, virtualization, or canvas/WebGL overlays are actually worth the complexity.
