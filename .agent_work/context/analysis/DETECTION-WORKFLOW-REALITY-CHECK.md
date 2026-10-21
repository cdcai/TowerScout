# Detection Workflow Reality Check

**Analysis Date:** April 2, 2026  
**Scope:** Full TowerScout detection workflow from UI initialization through `Estimate tiles`, `Find towers`, backend detection/geocoding, and frontend map/right-panel rendering for both Google Maps and Azure Maps.  
**Method:** Static code trace across frontend and backend modules. This pass did not include live browser/runtime validation.

---

## Executive Summary

The current detection workflow works, but it is more complex, less standardized, and less provider-consistent than it appears from the UI.

The biggest confirmed issues are:

1. **Cancellation is logically broken**: the active frontend cancel path sends `POST /abort`, but the Flask route only accepts `GET` (`webapp/js/src/ui/search.js:309-318`, `webapp/towerscout.py:1070-1074`).
2. **`Find towers` always does a full estimate first**: every detection run performs a full tile-estimation request before the actual detection request, so preprocessing work is duplicated by design (`webapp/js/src/ui/search.js:156-217`).
3. **Abort state depends on that estimate preflight**: the backend only allocates the abort event in the `estimate == "yes"` branch, so the actual detection path is implicitly coupled to the estimate call (`webapp/towerscout.py:1210-1216`).
4. **Duplicate suppression is too weak and can keep the wrong detection**: duplicates are removed only when adjacent sorted detections are within 1 meter of each other by `x1,y1`, and the current sort order can discard the higher-confidence result (`webapp/towerscout.py:1388-1401`).
5. **Geocoding provider consistency is not guaranteed**: the main detection path tries to prefer the selected backend provider, but the cache is provider-blind, and manual-tower reverse geocoding always uses `provider: "auto"` which is Azure-first when both keys exist (`webapp/towerscout.py:1420-1451`, `webapp/ts_geocoding.py:154-161`, `webapp/js/src/providers/GoogleMap.js:655-664`, `webapp/js/src/providers/AzureMap.js:1480-1489`).
6. **Google and Azure search flows are not standardized**: Google search is Google Places plus OpenStreetMap Nominatim polygon lookup, while Azure search is Azure Search via backend proxy and intentionally does not auto-create boundaries (`webapp/js/src/providers/GoogleMap.js:748-810`, `webapp/js/src/providers/AzureMap.js:1604-1729`).
7. **There are secondary broken paths and redundant initialization layers** that make the workflow harder to reason about and more fragile than it needs to be (`webapp/js/src/utils/apiHelpers.js:20-97`, `webapp/ts_geocoding.py:492-567`, `webapp/ts_maps.py:57-63`, `webapp/ts_maps.py:155-163`).

My overall conclusion is:

- The **imagery-to-detection coordinate pipeline is mostly sound** and is not the main source of the Google/Azure geocoding symptom.
- The more serious problems are **provider-selection drift, provider-blind caching, weak dedupe, duplicated preprocessing, and inconsistent search/geocoding control flow**.

---

## End-to-End Workflow Trace

## 1. Initialization and Provider Setup

### What happens

- The page initializes provider management and then tries to sync with backend provider defaults (`webapp/js/src/towerscout.js:3799-3960`).
- `fillProviders()` calls `/getproviders`, builds the backend provider radio buttons, initializes the selected provider map instance, and also forces the UI map radio to the same provider (`webapp/js/src/towerscout.js:3803-3894`).
- A second sync layer, `syncUIWithBackendProviders()`, also fetches `/getproviders`, sets `providerManager.currentProvider`, and tries to update DOM elements with IDs `providers-google` / `providers-azure` (`webapp/js/src/utils/apiHelpers.js:20-97`).

### What is good

- Backend provider defaulting is explicit through `/getproviders`.
- Initial map/provider state is at least intentionally tied to the backend default.

### What is not good

- `syncUIWithBackendProviders()` references DOM IDs that do not match the radio IDs created by `fillProviders()` (`google_provider` / `azure_provider`), so that sync is partially dead code (`webapp/js/src/utils/apiHelpers.js:41-42`, `webapp/js/src/towerscout.js:3826-3829`).
- Provider initialization is doing the same conceptual work in multiple places.
- The app still has a split between:
  - **UI provider**: which map/search experience is active.
  - **Backend provider**: which imagery source is used for detection.
  - **Geocoding provider**: which is sometimes tied to backend provider, sometimes `auto`.

That split is the root of several downstream inconsistencies.

---

## 2. Search and Boundary Definition

### Shared entry point

- Pressing Enter in the search box routes search based on the current UI provider, not the backend detection provider (`webapp/js/src/towerscout.js:763-821`).

### Google UI path

- Google uses `PlaceAutocompleteElement` for search selection (`webapp/js/src/providers/GoogleMap.js:284-349`).
- After that, `getBoundsPolygon()` calls **OpenStreetMap Nominatim directly from the browser** to resolve polygon geometry and sometimes auto-create boundaries (`webapp/js/src/providers/GoogleMap.js:748-810`).

### Azure UI path

- Azure uses its own search proxy endpoint, via `searchAddress()` -> `/api/maps/azure/search` (`webapp/js/src/providers/AzureMap.js:1688-1729`).
- Azure search centers the map and adds a marker, but explicitly does **not** create a boundary (`webapp/js/src/providers/AzureMap.js:1643-1647`).

### Assessment

This is not standardized.

- Google search is a **hybrid Google + OSM flow**.
- Azure search is a **pure Azure flow**.
- The frontend already contains a generic `/api/geocode/forward` backend endpoint, but the active search UI does not use it.

That means search behavior, search logs, and resulting boundary behavior differ materially between providers before detection even starts.

---

## 3. `Estimate tiles` and `Find towers`

### Current flow

From `getObjects()` (`webapp/js/src/ui/search.js:57-249`):

1. Validate current map state.
2. Read selected model and backend detection provider.
3. Convert unsaved drawn shapes into persisted boundaries if needed.
4. Compute `bounds` from the current boundary bounding box.
5. If no boundary exists, auto-create a viewport boundary.
6. Clear detections and tiles.
7. Send `POST /getobjects` with `estimate=yes`.
8. If the user clicked `Estimate tiles`, stop there.
9. If the user clicked `Find towers`, use the tile count returned by step 7, then send a second `POST /getobjects` without `estimate`.

### Why this is bloated

Every `Find towers` click forces:

- one full backend request for tile estimation
- one full backend request for actual processing

And if the user already clicked `Estimate tiles` first, then later clicks `Find towers`, the same tiling/bounds work is performed again.

On the backend, the estimate request still does:

- request validation
- map provider instantiation
- tile generation
- viewport filtering
- polygon intersection filtering

before returning only the tile count (`webapp/towerscout.py:1098-1216`).

This is clean from a UI simplicity standpoint, but it is objectively inefficient.

### Extra workflow smell

The abort event is allocated only in the estimate branch:

- `exit_events.alloc(id(session))` happens only when `estimate == "yes"` (`webapp/towerscout.py:1210-1216`).

That means the actual long-running detection request relies on the estimate preflight to create the abort state first. That is a hidden dependency between two separate HTTP requests.

---

## 4. Backend Detection Pipeline

### Standardized parts

Once `/getobjects` is in the actual detection path, the processing is mostly provider-agnostic:

1. Instantiate `GoogleMap` or `AzureMaps` based on the selected backend provider (`webapp/towerscout.py:1148-1177`).
2. Generate tiles through the shared `Map.make_tiles()` logic (`webapp/towerscout.py:1179-1186`, `webapp/ts_maps.py:100-131`).
3. Filter tiles by viewport bounds and polygon intersection (`webapp/towerscout.py:1197-1203`).
4. Download imagery asynchronously (`webapp/towerscout.py:1242-1250`, `webapp/ts_maps.py:37-55`, `webapp/ts_maps.py:138-301`).
5. Run YOLOv5 plus EfficientNet secondary classification (`webapp/towerscout.py:1263-1276`, `webapp/ts_yolov5.py:70-196`, `webapp/ts_en.py:133-160`).
6. Convert normalized detection boxes back to global lat/lng using shared math (`webapp/towerscout.py:1327-1338`).

### Coordinate transformation assessment

The Azure coordinate-order concern is understandable, but the evidence in code points to this:

- Azure imagery URL generation explicitly converts internal coordinates to `lng,lat` only at URL-generation time (`webapp/ts_azure_maps.py:96-139`).
- Google imagery URL generation uses `lat,lng` directly (`webapp/ts_gmaps.py:24-32`).
- After model inference, the backend converts all boxes back into TowerScout's shared geographic coordinate space before geocoding (`webapp/towerscout.py:1327-1338`).

So the main workflow does **not** look like it is accidentally reverse-geocoding Google detections with Azure coordinate ordering.

The stronger problem is **provider selection and provider-blind cache reuse**, not coordinate-order corruption.

---

## 5. Duplicate Detection Handling

### What the code does

After boundary filtering, detections are sorted by:

```python
results.sort(key=lambda x: x['y1']*2*180+2*x['x1']+x['conf'])
```

Then duplicates are removed only if adjacent items have `x1,y1` points within 1 meter:

```python
if ts_maps.get_distance(results[i]['x1'], results[i]['y1'],
                        results[i+1]['x1'], results[i+1]['y1']) < 1:
    results.remove(results[i+1])
```

Source: `webapp/towerscout.py:1388-1401`

### Why this is weak

1. It compares only the **top-left corner**, not the detection center or overlap area.
2. It only checks **adjacent** detections after sorting.
3. The 1-meter threshold is too small for overlapping-tile duplicates where the same tower can be boxed slightly differently.
4. Because `conf` is part of the sort key in ascending order, the later item can easily be the **higher-confidence** duplicate, which is the one currently removed.

### Likely user-visible effect

This is a very plausible explanation for the duplicate-tower symptom:

- overlapping tiles produce two detections for the same structure
- the boxes differ by more than 1 meter at `x1,y1`
- both survive
- they become separate detections in the map/list

Even when dedupe does trigger, it is not guaranteed to keep the better instance.

---

## 6. Geocoding and Address Assignment

## Main detection path

The main detection pipeline does attempt to use the selected backend provider for geocoding:

- `create_geocoding_service(... preferred_provider=provider)` (`webapp/towerscout.py:1422-1425`)

That part is good.

## Why provider consistency still breaks

### A. The cache is provider-blind

The geocoding cache key uses only clustered coordinates:

- no provider dimension
- no backend provider dimension
- no UI provider dimension

Source: `webapp/ts_geocache.py:168-197`

So this sequence is possible:

1. Azure geocodes a rooftop point and caches it.
2. Later, Google detection requests the same or nearby point.
3. The Google run gets the cached Azure address/provider without making a Google request.

That means the user can absolutely observe Azure reverse-geocoding artifacts inside a Google detection run, even though the detection code tried to prefer Google.

### B. Manual tower geocoding always uses `provider: "auto"`

Both provider UIs geocode manual towers like this:

- Google manual tower geocode: `provider: 'auto'` (`webapp/js/src/providers/GoogleMap.js:655-664`)
- Azure manual tower geocode: `provider: 'auto'` (`webapp/js/src/providers/AzureMap.js:1480-1489`)

Then the reverse-geocode endpoint creates `GeocodingService(...)` with no preferred provider in the constructor, so the service default remains `"auto"` (`webapp/towerscout.py:773-777`).

And `"auto"` means:

- Azure first if Azure key exists
- Google second if Google key exists

because providers are appended in Azure, then Google order (`webapp/ts_geocoding.py:154-161`, `webapp/ts_geocoding.py:604-611`).

So manual tower reverse geocoding is explicitly **not** tied to the selected UI/backend provider. It is effectively Azure-first.

### C. The reverse endpoint checks cache before honoring provider preference

`/api/geocode/reverse`:

1. reads `preferred_provider = data.get('provider', 'auto')`
2. creates `GeocodingService(...)` with default constructor preference
3. checks `GeocodingCache()` first
4. only if cache misses, calls `geocoding.reverse_geocode(lat, lng, preferred_provider)`

Source: `webapp/towerscout.py:768-799`

So even if a caller passes `provider: "google"`, a cached Azure result still wins before provider preference is applied.

## Address accuracy on the same building

The current approach geocodes each surviving detection by its box center after dedupe (`webapp/towerscout.py:1430-1451`).

That leads to three accuracy problems:

1. **Per-box center variance**: towers on the same roof can have slightly different centers and land on different entrances, roads, or building records.
2. **Provider-blind 50m cluster cache**: some towers reuse a prior address while others just over a cache boundary get independently geocoded.
3. **Exact-string grouping in the UI**: the right panel groups by exact `address` string, so small formatting differences split one building into multiple groups (`webapp/js/src/detection/Detection.js:160-190`).

This means the "same building, different addresses" symptom is expected from the current logic. It is not just a random API quirk; the workflow makes that outcome likely.

---

## 7. Result Hydration and Display

### Backend output shape

The backend prepends tile metadata records (`class: 1`) ahead of actual detections (`class: 0`) before returning JSON (`webapp/towerscout.py:1512-1534`).

### Frontend hydration

`processObjects()` iterates the combined result array:

- creates `Detection` objects for `class === 0`
- creates `Tile` objects for `class === 1`
- sorts detections by exact address
- generates the right-panel list

Source: `webapp/js/src/ui/search.js:252-306`

### Visibility logic

After list generation:

- list visibility and map visibility are driven by confidence threshold plus `inside` filtering
- each detection updates its provider-specific overlay via `updateMapRect()`

Source: `webapp/js/src/detection/Detection.js:329-347`, `webapp/js/src/detection/DetectionList.js:8-34`

### Assessment

This part is mostly coherent.

The right-panel/map rendering issues are much more likely to be caused by:

- weak dedupe
- address inconsistency
- provider-specific geocode/cache behavior

than by the final hydration code itself.

---

## Specific Answers to the Reported Observations

## 1. "Google geocoding appears to be using Azure"

**Assessment:** Partly confirmed.

### Confirmed cases

- Manual tower reverse geocoding is Azure-first whenever both keys exist, because it sends `provider: "auto"` (`webapp/js/src/providers/GoogleMap.js:655-664`, `webapp/js/src/providers/AzureMap.js:1480-1489`, `webapp/ts_geocoding.py:154-161`).
- The shared geocoding cache can return a previously cached Azure result during a Google detection run (`webapp/ts_geocache.py:168-197`, `webapp/towerscout.py:1437-1445`).

### Not supported by the code

- I did **not** find evidence that Azure's `lng,lat` tile coordinate convention is directly corrupting Google reverse geocoding coordinates in the main detection path.
- The imagery provider transformation is isolated, and the backend normalizes all detections into a shared geographic coordinate system before geocoding.

### Bottom line

The likely bug is **provider selection/cache leakage**, not a raw coordinate-order bug.

## 2. "Duplicate detections sometimes appear for a single tower"

**Assessment:** Confirmed risk.

The current dedupe logic is not strong enough for overlapping-tile detection duplicates and can even discard the higher-confidence instance (`webapp/towerscout.py:1388-1401`).

## 3. "Towers on the same building sometimes have different addresses"

**Assessment:** Expected with the current logic.

The workflow geocodes per detection center after weak dedupe and uses a provider-blind spatial cache, then groups by exact address string. That combination will naturally split same-building towers into separate address groups.

---

## Additional Confirmed Problems

## 1. Cancel flow is broken

- Frontend active path: `POST /abort` (`webapp/js/src/ui/search.js:309-318`)
- Backend route: `GET /abort` only (`webapp/towerscout.py:1070-1074`)

This means cancellation can fail while the overlay is already hidden and the user is told the request was cancelled.

## 2. Progress estimate learning is wrong

`disableProgress(time, actualTiles)` is called with `result.length`, not actual tile count (`webapp/js/src/ui/search.js:304-306`, `webapp/js/src/ui/search.js:338-347`).

Because `result.length` includes both tiles and detections, runs with more detections artificially reduce the learned `secsPerTile`.

## 3. Forward geocoding endpoint looks dead/broken

The backend exposes `/api/geocode/forward` (`webapp/towerscout.py:703-739`), but the active frontend search flow does not use it.

Worse, the forward geocoding helper methods call `_track_request(...)`, but that method does not exist in `GeocodingService` (`webapp/ts_geocoding.py:510`, `webapp/ts_geocoding.py:564`).

That strongly suggests the forward-geocoding service path is currently broken or at least untested.

## 4. Tile-download error handling has a hidden failure mode

`ts_maps.py` raises `MapProviderError` and `NetworkError` in multiple places, but those symbols are not imported in that file (`webapp/ts_maps.py:57-63`, `webapp/ts_maps.py:155-163`, plus no matching import at the top of the file).

So some tile-download failure paths will likely raise `NameError` instead of the intended structured exception, obscuring the real problem.

## 5. Browser-side state management is more complicated than needed

`ProviderStateManager` uses busy-wait lock loops in browser JavaScript (`webapp/js/src/managers/ProviderStateManager.js:463-510`, `webapp/js/src/managers/ProviderStateManager.js:556-603`).

That adds complexity without providing real cross-thread safety in the browser's single-threaded execution model.

This is more of a cleanup concern than a direct user-visible bug, but it is part of why the workflow feels harder than it should.

---

## Recommendations

## Priority 0: Correctness fixes

1. **Fix cancellation first**
   - Standardize `/abort` on `POST`.
   - Allocate abort state at actual detection start, not only in the estimate branch.
   - Free abort state in a `finally`-style path so failed detections do not leak state.

2. **Replace duplicate suppression**
   - Deduplicate by detection center distance and/or IoU, not `x1,y1`.
   - Deduplicate before geocoding.
   - Keep the best candidate by `max(conf, secondary)` or explicit merged score.

3. **Make geocoding cache provider-aware**
   - Include provider in the cache key.
   - Or maintain per-provider caches.
   - Do not let cached Azure reverse-geocode results satisfy Google-preferred requests unless that fallback is explicitly intended and surfaced.

4. **Stop using `provider: "auto"` for manual tower geocoding**
   - Pass the active backend detection provider, or at minimum the active UI provider.
   - Align manual-tower geocoding rules with main detection geocoding rules.

## Priority 1: Simplify the workflow

1. **Split estimate from detection cleanly**
   - Add a dedicated estimate endpoint, or
   - let `/getobjects` return an estimate token that can be reused by the actual detection call.

2. **Remove the hidden estimate -> detect abort dependency**
   - The long-running request should be independently cancellable.

3. **Reduce provider state ambiguity**
   - Make these concepts explicit in code and UI:
     - `ui_map_provider`
     - `detection_imagery_provider`
     - `geocoding_provider`
   - Then decide which ones are intentionally coupled and which are not.

## Priority 2: Standardize provider behavior

1. **Unify search semantics**
   - Choose one contract for both providers:
     - search only centers map, then user defines boundary
     - or search can optionally create a place boundary for both providers
   - The current Google hybrid (Google Places + OSM polygon) vs Azure native search split is difficult to reason about.

2. **Either remove `/api/geocode/forward` or wire the app to use it**
   - Right now the app has a generic forward-geocoding abstraction that the UI does not use.
   - If kept, fix the `_track_request` bug and make it the standard search entry point.

## Priority 3: Improve address quality

1. **Cluster detections before geocoding**
   - Group likely same-structure detections first.
   - Geocode one representative point per cluster.
   - Propagate the canonical address to the whole cluster.

2. **Add address normalization for grouping**
   - Normalize suite/building formatting before `Detection.sort()` / `Detection.generateList()`.
   - Keep raw provider address separately if needed for export fidelity.

3. **Consider building-aware geocoding**
   - If provider capabilities allow it, prefer premise/building centroid behavior over per-box center reverse geocoding.

---

## Recommended Refactor Shape

If I were simplifying this workflow without changing the product behavior, I would move toward this structure:

1. **One search abstraction**
   - Provider-specific search implementation behind one frontend contract.

2. **One estimate contract**
   - Pure tile-count and cost/time estimate.

3. **One detection contract**
   - Accepts a normalized search boundary plus backend provider.
   - Allocates its own cancellable job state.

4. **One geocoding policy**
   - Main detections and manual towers both use the same provider-selection rules.
   - Cache keys include provider.
   - Geocoding happens after dedupe/cluster.

5. **One result model**
   - `tile metadata`
   - `raw detections`
   - `deduped detections`
   - `geocoded detection groups`

The current system has most of these pieces already, but the boundaries between them are still blurry.

---

## Final Assessment

The workflow is not fundamentally broken, but it is carrying too much historical layering:

- duplicate provider-sync logic
- split UI vs backend provider behavior
- mixed search implementations
- provider-blind geocode caching
- weak dedupe
- duplicated request phases

The specific Google/Azure geocoding concern is real, but the evidence points to **provider-selection drift and cache reuse**, not to a raw Azure/Google coordinate transform mismatch.

If you want the highest-value cleanup path, I would do it in this order:

1. fix cancel/abort lifecycle
2. fix provider-aware geocoding and cache keys
3. replace duplicate suppression
4. eliminate the mandatory estimate preflight from `Find towers`
5. standardize search behavior across Google and Azure

