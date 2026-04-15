/**
 * STAGE 5 - UI & Final Integration
 * Module: search.js
 * Purpose: Primary detection workflow and result processing
 * 
 * Functions:
 * - getObjects(estimate): Main detection workflow with boundary validation and tile estimation
 * - processObjects(result, startTime): Result processing with error handling
 * - cancelRequest(): Abort detection request
 * - enableProgress(tiles): Initialize progress indicator
 * - disableProgress(time, actualTiles): Hide progress indicator and update statistics
 * - progressFunction(): Update progress display and poll live detection status
 * - setProgress(val): Set progress bar value
 * - fatalError(msg): Display fatal error dialog
 * 
 * Dependencies:
 * - detection/Detection.js (Detection class)
 * - detection/Tile.js (Tile class)
 * - boundaries/SimpleBoundary.js
 * - providers/ProviderManager.js
 * - managers/ErrorHandler.js
 * - CONFIG (global configuration)
 * 
 * Exposed to window: getObjects, processObjects, cancelRequest, fatalError
 */

(function () {
  'use strict';

  // ===== Module-level variables for progress management =====
  // TASK-043 Phase 3: progressTimer now managed by ProviderStateManager  
  // let progressTimer = null; // DEPRECATED - use providerManager.startProgressTimer/stopProgressTimer
  let totalSecsEstimated = 0;
  let secsElapsed = 0;
  let numTiles = 0;
  let secsPerTile = CONFIG.SECS_PER_TILE_DEFAULT;
  let dataPoints = 0;
  let progressIndeterminate = false;
  let lastEstimate = null;
  let activeDetectionRequest = null;
  let detectionRequestSeq = 0;
  let progressPollInFlight = false;
  let lastProgressPollAt = 0;
  let progressStatusSeen = false;
  const TERMINAL_PROGRESS_STATUSES = new Set(['completed', 'cancelled', 'error']);

  async function getResponseErrorMessage(response, fallbackMessage) {
    const contentType = response.headers.get('content-type') || '';

    try {
      if (contentType.includes('application/json')) {
        const payload = await response.json();
        return payload.error || payload.message || fallbackMessage;
      }

      const text = (await response.text()).trim();
      return text || fallbackMessage;
    } catch (error) {
      return fallbackMessage;
    }
  }

  function getProgressElements() {
    return {
      container: document.getElementById('progress_div'),
      progress: document.getElementById('progress'),
      title: document.getElementById('progress_status_title'),
      detail: document.getElementById('progress_status_detail')
    };
  }

  function setProgressStatus(title, detail) {
    const elements = getProgressElements();
    if (elements.title) {
      elements.title.textContent = title || 'Detection in progress';
    }
    if (elements.detail) {
      elements.detail.textContent = detail || '';
    }
  }

  function resetProgressStatus(tiles) {
    if (Number.isFinite(tiles) && tiles > 0) {
      setProgressStatus(
        'Preparing detection',
        `Preparing ${tiles} tile(s) for processing and waiting for live phase updates.`
      );
      return;
    }

    setProgressStatus(
      'Starting detection',
      'Waiting for live phase updates from the active detection run.'
    );
  }

  async function fetchDetectionProgress() {
    const response = await fetch('/api/detection/progress', {
      cache: 'no-store'
    });

    if (!response.ok) {
      throw new Error(`Detection progress request failed: ${response.status}`);
    }

    return await response.json();
  }

  function getProgressStateTimestampMs(progressState) {
    if (!progressState) {
      return NaN;
    }

    const isoValue = progressState.updated_at || progressState.started_at || '';
    return Date.parse(isoValue);
  }

  function shouldIgnoreStaleTerminalProgress(progressState) {
    if (!progressState || !TERMINAL_PROGRESS_STATUSES.has(progressState.status)) {
      return false;
    }

    const requestState = activeDetectionRequest;
    if (!requestState || requestState.cancelled !== false) {
      return false;
    }

    const progressTimestampMs = getProgressStateTimestampMs(progressState);
    if (!Number.isFinite(progressTimestampMs)) {
      return false;
    }

    return progressTimestampMs < requestState.startedAtMs;
  }

  function renderDetectionProgressState(progressState) {
    if (!progressState || progressState.status === 'idle') {
      return;
    }

    if (shouldIgnoreStaleTerminalProgress(progressState)) {
      return;
    }

    progressStatusSeen = true;
    setProgressStatus(
      progressState.title || 'Detection in progress',
      progressState.detail || 'Detection is running.'
    );
  }

  async function maybePollDetectionProgress(force = false) {
    if (progressPollInFlight) {
      return;
    }

    const now = Date.now();
    if (!force && now - lastProgressPollAt < CONFIG.DETECTION_PROGRESS_POLL_INTERVAL_MS) {
      return;
    }

    lastProgressPollAt = now;
    progressPollInFlight = true;

    try {
      const progressState = await fetchDetectionProgress();
      renderDetectionProgressState(progressState);
    } catch (error) {
      window.TowerScoutLogger.debug('Detection progress poll unavailable:', error?.message || error);
      if (!progressStatusSeen) {
        setProgressStatus(
          'Detection in progress',
          progressIndeterminate
            ? 'Live phase details are temporarily unavailable. Detection is still running.'
            : 'Using estimated progress while live phase details are temporarily unavailable.'
        );
      }
    } finally {
      progressPollInFlight = false;
    }
  }

  // ===== Main Detection Workflow =====

  function getObjects(estimate) {
    //let center = currentMap.getCenterUrl();

    if (!currentMap) {
      const fallbackMap = providerManager.getMap();
      if (fallbackMap) {
        currentMap = fallbackMap;
      }
    }
    if (!currentMap) {
      TowerScoutErrorHandler.showUserNotification(
        'Map is still initializing. Please wait a moment and try again.',
        'warning'
      );
      return;
    }

    if (Detection_detections.length > 0) {
      if (!window.confirm("This will erase current detections. Proceed?")) {
        return;
      }
    }

    let engine = $('input[name=model]:checked', '#engines').val()
    let provider = $('input[name=provider]:checked', '#providers').val()
    window.TowerScoutLogger.debug('🎯 Detection provider value:', provider, '| Type:', typeof provider);
    window.TowerScoutLogger.debug('🎯 Provider validation - Azure:', provider === 'azure', '| Google:', provider === 'google');

    // TASK-045: Clear old boundaries from previous detection cycles before calculating new bounds
    // This ensures each detection run is independent and prevents boundary accumulation
    window.TowerScoutLogger.debug('🧹 TASK-045: Clearing previous boundaries before detection');
    window.TowerScoutLogger.debug('   Current boundaries count:', currentMap.boundaries ? currentMap.boundaries.length : 0);

    // Check if user has drawn new shapes that need to be converted to boundaries
    const hasNewShapes = currentMap.hasShapes && currentMap.hasShapes();

    if (hasNewShapes) {
      const validation = currentMap.validateDrawnShapes
        ? currentMap.validateDrawnShapes({
          showNotification: true,
          label: 'custom shape'
        })
        : { valid: true };

      if (!validation.valid) {
        return;
      }

      // Clear old boundaries and retrieve fresh drawn shapes
      window.TowerScoutLogger.debug('   User has drawn new shapes - clearing old boundaries and retrieving new ones');
      currentMap.resetBoundaries();

      // Sync boundary clearing to other provider if available
      if (currentMap === window.googleMap && window.azureMap) {
        window.azureMap.resetBoundaries();
      } else if (currentMap === window.azureMap && window.googleMap) {
        window.googleMap.resetBoundaries();
      }

      // Now retrieve the newly drawn boundaries
      if (!drawnBoundary({ skipValidation: true })) {
        return;
      }
      window.TowerScoutLogger.debug('   New boundaries retrieved:', currentMap.boundaries ? currentMap.boundaries.length : 0);
    }

    // TASK-041 Phase 2 Step 2.6: Use boundary bounding box instead of viewport bounds
    // This ensures tiles are generated only for the drawn search area, not the entire viewport
    let bounds = currentMap.getBoundaryBoundsUrl();
    window.TowerScoutLogger.debug('🗺️ Using bounds for tile generation:', bounds);
    window.TowerScoutLogger.debug('   Final boundaries count for detection:', currentMap.boundaries ? currentMap.boundaries.length : 0);

    let boundaries = currentMap.getBoundariesStr();

    // Auto-create viewport boundary if no polygons are drawn
    if (boundaries === "[]") {
      window.TowerScoutLogger.debug("No boundary selected, automatically using current viewport as detection area");
      const bounds = currentMap.getBounds();
      currentMap.addBoundary(new SimpleBoundary(bounds));
      // TASK-041 Phase 1: Sync boundaries to initialized providers only
      // Access map instances via window to avoid IIFE scope issues
      if (currentMap === window.googleMap && window.azureMap) {
        window.azureMap.addBoundary(new SimpleBoundary(bounds));
      } else if (currentMap === window.azureMap && window.googleMap) {
        window.googleMap.addBoundary(new SimpleBoundary(bounds));
      }
      boundaries = currentMap.getBoundariesStr();
    }
    let kinds = ["None", "Polygon", "Multiple polygons"]
    if (estimate) {
      window.TowerScoutLogger.info("Estimating tile count for the selected search area...");
    } else {
      window.TowerScoutLogger.info("Starting cooling tower detection...");
    }

    // erase the previous set of towers and tiles
    Detection.resetAll();
    Tile.resetAll();

    // first, play the request, but get an estimate of the number of tiles
    const formData = new FormData();
    formData.append('bounds', bounds);
    formData.append('engine', engine);
    formData.append('provider', provider);
    formData.append('polygons', boundaries);
    formData.append('estimate', "yes");

    fetch("/getobjects", { method: "POST", body: formData, })
      .then(async (result) => {
        if (!result.ok) {
          const message = await getResponseErrorMessage(result, `HTTP ${result.status}: ${result.statusText}`);
          throw new Error(message);
        }

        // Check if result is JSON error instead of tile count
        const contentType = result.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await result.json();
          throw new Error(errorData.error || errorData.message || 'Server error');
        }
        return result.text();
      })
      .then(result => {
        // Validate result is a number
        const tileCount = Number(result);
        if (isNaN(tileCount)) {
          throw new Error(`Invalid tile count response: ${result}`);
        }

        if (tileCount === -1) {
          fatalError("Tile limit for this session exceeded. Please close browser to continue.")
          return;
        }
        window.TowerScoutLogger.info("Estimated " + tileCount + " tile(s), expected time: "
          + (Math.round(tileCount * secsPerTile * 10) / 10) + " s");
        // let nt = estimateNumTiles(currentMap.getZoom());
        // window.TowerScoutLogger.debug("  Estimated tiles:" + nt);
        if (estimate) {
          return;
        }

        // actual retrieval process starts here
        let nt = tileCount;
        enableProgress(nt);
        setProgress(0);
        let startTime = performance.now();

        // now, the actual request

        Detection.resetAll();
        formData.delete("estimate");

        const detectionCall = TowerScoutErrorHandler.wrapNetworkCall(
          async () => {
            const response = await fetch("/getobjects", { method: "POST", body: formData });
            if (!response.ok) {
              const message = await getResponseErrorMessage(response, `HTTP ${response.status}: ${response.statusText}`);
              throw new Error(message);
            }
            return await response.json();
          },
          'Cooling Tower Detection'
        );

        detectionCall()
          .then(result => {
            if (!result || !Array.isArray(result)) {
              throw new Error('Invalid detection response format');
            }
            processObjects(result, startTime);
          })
          .catch(error => {
            console.error('❌ Detection pipeline error:', error);
            disableProgress(0, 0);
          });
      })
      .catch(error => {
        console.error('❌ Tile estimation error:', error);
        let msg = error.message || 'Unknown error occurred';
        if (msg.includes('zipcode')) {
          TowerScoutErrorHandler.showUserNotification(
            'Invalid ZIP code or search area. Please adjust your search boundaries.',
            'error'
          );
        } else if (msg.toLowerCase().includes('validation error')) {
          TowerScoutErrorHandler.showUserNotification(
            msg.replace(/^Validation error:\s*/i, ''),
            'error'
          );
        } else {
          TowerScoutErrorHandler.handleNetworkError(error, 'Tile Estimation');
        }
      });
  }

  function buildRequestFingerprint(payload) {
    return JSON.stringify({
      bounds: payload.bounds,
      engine: payload.engine,
      provider: payload.provider,
      polygons: payload.polygons
    });
  }

  function getActiveDetectionProvider() {
    return document.querySelector('#providers input[name="provider"]:checked')?.value || 'auto';
  }

  function buildDetectionPayload() {
    const engine = $('input[name=model]:checked', '#engines').val();
    const provider = $('input[name=provider]:checked', '#providers').val();

    window.TowerScoutLogger.debug('Detection provider value:', provider, '| Type:', typeof provider);
    window.TowerScoutLogger.debug('Provider validation - Azure:', provider === 'azure', '| Google:', provider === 'google');
    window.TowerScoutLogger.debug('TASK-045: Clearing previous boundaries before detection');
    window.TowerScoutLogger.debug('   Current boundaries count:', currentMap.boundaries ? currentMap.boundaries.length : 0);

    const hasNewShapes = currentMap.hasShapes && currentMap.hasShapes();
    if (hasNewShapes) {
      const validation = currentMap.validateDrawnShapes
        ? currentMap.validateDrawnShapes({
          showNotification: true,
          label: 'custom shape'
        })
        : { valid: true };

      if (!validation.valid) {
        return null;
      }

      window.TowerScoutLogger.debug('   User has drawn new shapes - clearing old boundaries and retrieving new ones');
      currentMap.resetBoundaries();

      if (currentMap === window.googleMap && window.azureMap) {
        window.azureMap.resetBoundaries();
      } else if (currentMap === window.azureMap && window.googleMap) {
        window.googleMap.resetBoundaries();
      }

      if (!drawnBoundary({ skipValidation: true })) {
        return null;
      }

      window.TowerScoutLogger.debug('   New boundaries retrieved:', currentMap.boundaries ? currentMap.boundaries.length : 0);
    }

    const bounds = currentMap.getBoundaryBoundsUrl();
    window.TowerScoutLogger.debug('Using bounds for tile generation:', bounds);
    window.TowerScoutLogger.debug('   Final boundaries count for detection:', currentMap.boundaries ? currentMap.boundaries.length : 0);

    let boundaries = currentMap.getBoundariesStr();
    if (boundaries === '[]') {
      window.TowerScoutLogger.debug('No boundary selected, automatically using current viewport as detection area');
      const viewportBounds = currentMap.getBounds();
      currentMap.addBoundary(new SimpleBoundary(viewportBounds));
      if (currentMap === window.googleMap && window.azureMap) {
        window.azureMap.addBoundary(new SimpleBoundary(viewportBounds));
      } else if (currentMap === window.azureMap && window.googleMap) {
        window.googleMap.addBoundary(new SimpleBoundary(viewportBounds));
      }
      boundaries = currentMap.getBoundariesStr();
    }

    return {
      bounds,
      engine,
      provider,
      polygons: boundaries
    };
  }

  function buildDetectionFormData(payload) {
    const formData = new FormData();
    formData.append('bounds', payload.bounds);
    formData.append('engine', payload.engine);
    formData.append('provider', payload.provider);
    formData.append('polygons', payload.polygons);
    return formData;
  }

  async function requestTileEstimate(payload) {
    const response = await fetch('/api/detection/estimate', {
      method: 'POST',
      body: buildDetectionFormData(payload)
    });

    if (!response.ok) {
      const message = await getResponseErrorMessage(response, `HTTP ${response.status}: ${response.statusText}`);
      throw new Error(message);
    }

    const result = await response.json();
    const tileCount = Number(result.tileCount);
    const estimatedSeconds = Number(result.estimatedSeconds);

    if (!Number.isFinite(tileCount)) {
      throw new Error(`Invalid tile count response: ${JSON.stringify(result)}`);
    }

    return {
      tileCount,
      estimatedSeconds: Number.isFinite(estimatedSeconds) ? estimatedSeconds : tileCount * secsPerTile
    };
  }

  async function startDetectionRequest(payload, fingerprint) {
    const startTime = performance.now();
    const requestId = ++detectionRequestSeq;
    const requestState = {
      id: requestId,
      cancelled: false,
      controller: new AbortController(),
      startedAtMs: Date.now()
    };
    activeDetectionRequest = requestState;
    const cachedEstimate = lastEstimate && lastEstimate.fingerprint === fingerprint ? lastEstimate : null;

    if (cachedEstimate) {
      enableProgress(cachedEstimate.tileCount);
      setProgress(0);
    } else {
      enableProgress(null);
      window.TowerScoutLogger.info('Starting detection without a fresh estimate. Progress is indeterminate until results return.');
    }

    Detection.resetAll();

    const detectionCall = TowerScoutErrorHandler.wrapNetworkCall(
      async () => {
        const response = await fetch('/getobjects', {
          method: 'POST',
          body: buildDetectionFormData(payload),
          signal: requestState.controller.signal
        });
        if (!response.ok) {
          const message = await getResponseErrorMessage(response, `HTTP ${response.status}: ${response.statusText}`);
          throw new Error(message);
        }
        return await response.json();
      },
      'Cooling Tower Detection'
    );

    try {
      void maybePollDetectionProgress(true);
      const result = await detectionCall();
      if (requestState.cancelled || activeDetectionRequest?.id !== requestId) {
        window.TowerScoutLogger.info('Ignoring stale detection response from a cancelled or superseded request.');
        return;
      }

      if (!result || !Array.isArray(result)) {
        throw new Error('Invalid detection response format');
      }

      processObjects(result, startTime);
    } catch (error) {
      if (requestState.controller.signal.aborted || error?.name === 'AbortError') {
        window.TowerScoutLogger.info('Detection request fetch aborted on the client.');
        return;
      }

      throw error;
    } finally {
      if (activeDetectionRequest?.id === requestId) {
        activeDetectionRequest = null;
      }
    }
  }

  async function getObjectsV2(estimate) {
    if (!currentMap) {
      const fallbackMap = providerManager.getMap();
      if (fallbackMap) {
        currentMap = fallbackMap;
      }
    }
    if (!currentMap) {
      TowerScoutErrorHandler.showUserNotification(
        'Map is still initializing. Please wait a moment and try again.',
        'warning'
      );
      return;
    }

    if (Detection_detections.length > 0) {
      if (!window.confirm('This will erase current detections. Proceed?')) {
        return;
      }
    }

    const payload = buildDetectionPayload();
    if (!payload) {
      return;
    }

    const fingerprint = buildRequestFingerprint(payload);

    if (estimate) {
      window.TowerScoutLogger.info('Estimating tile count for the selected search area...');
    } else {
      window.TowerScoutLogger.info('Starting cooling tower detection...');
    }

    Detection.resetAll();
    Tile.resetAll();

    try {
      if (estimate) {
        const estimateResult = await requestTileEstimate(payload);
        if (estimateResult.tileCount === -1) {
          fatalError('Tile limit for this session exceeded. Please close browser to continue.');
          return;
        }

        lastEstimate = {
          fingerprint,
          tileCount: estimateResult.tileCount,
          estimatedSeconds: estimateResult.estimatedSeconds
        };

        window.TowerScoutLogger.info(
          'Estimated ' + estimateResult.tileCount + ' tile(s), expected time: '
          + (Math.round(estimateResult.estimatedSeconds * 10) / 10) + ' s'
        );
        return;
      }

      await startDetectionRequest(payload, fingerprint);
    } catch (error) {
      console.error('Detection workflow error:', error);
      disableProgress(0, 0);

      const msg = error.message || 'Unknown error occurred';
      if (msg.includes('zipcode')) {
        TowerScoutErrorHandler.showUserNotification(
          'Invalid ZIP code or search area. Please adjust your search boundaries.',
          'error'
        );
      } else if (msg.toLowerCase().includes('validation error')) {
        TowerScoutErrorHandler.showUserNotification(
          msg.replace(/^Validation error:\s*/i, ''),
          'error'
        );
      } else {
        TowerScoutErrorHandler.handleNetworkError(error, estimate ? 'Tile Estimation' : 'Cooling Tower Detection');
      }
    }
  }

  function processObjects(result, startTime) {
    if (!Array.isArray(result)) {
      console.error('❌ Invalid result format in processObjects:', result);
      TowerScoutErrorHandler.showUserNotification(
        'Detection failed: Invalid response from server',
        'error'
      );
      disableProgress(0, 0);
      return;
    }

    window.TowerScoutLogger.debug("Results: " + result.length + " tiles");

    // Process detection objects with error handling
    let processedDetections = 0;
    let processedTiles = 0;

    Detection.withVisibilityUpdatesPaused(() => {
      for (let r of result) {
        try {
          if (r['class'] === 0) {
            // Create detection with server-provided address data
            new Detection(
              r['x1'], r['y1'], r['x2'], r['y2'],
              r['class_name'], r['conf'], r['tile'], r['id_in_tile'],
              r['inside'], r['selected'], r['secondary'],
              r['address'], r['address_confidence'], r['address_provider']
            );
            processedDetections++;
          } else if (r['class'] === 1) {
            // Create tile - TASK-033 Phase 3: Pass tile ID from backend
            new Tile(r['x1'], r['y1'], r['x2'], r['y2'], r['metadata'], r['url'], r['id']);
            processedTiles++;
          }
        } catch (objectError) {
        console.error('❌ Error processing individual object:', objectError);
        // Continue processing other objects
          }
      }
    });

    window.TowerScoutLogger.info(`Processed ${processedDetections} detection(s) and ${processedTiles} tile record(s).`);
    window.TowerScoutLogger.debug(`📊 ${Detection_detections.length} total detections with server-provided addresses.`);

    Detection.sort();
    Detection.generateList();

    // TASK-033 Phase 4: Lock provider switching after ML detection completes
    if (typeof lockProviderSwitching === 'function') {
      lockProviderSwitching();
    }

    let time = (performance.now() - startTime) / 1000;
    disableProgress(time, processedTiles);
    window.TowerScoutLogger.info("Detection request completed in " + time + " s.");
  }

  function cancelRequest() {
    const requestState = activeDetectionRequest;
    if (requestState) {
      requestState.cancelled = true;
      requestState.controller.abort();
      activeDetectionRequest = null;
    }

    setProgressStatus(
      'Cancelling detection',
      'Waiting for the active detection run to stop...'
    );

    fetch("/abort", { method: "POST" })
      .then(result => {
        disableProgress(0, 0);
        window.TowerScoutLogger.info("Detection request cancelled.");
      })
      .catch(error => {
        console.error('❌ Cancel request error:', error);
      });
  }

  // ===== Progress Management =====

  function enableProgress(tiles) {
    const elements = getProgressElements();
    elements.container.style.display = "flex";
    const progressElement = elements.progress;

    // TASK-043 Phase 3: Use state manager for timer lifecycle management
    // Clear any existing progress timer to prevent memory leaks
    if (providerManager.isProgressActive()) {
      providerManager.stopProgressTimer();
    }
    progressIndeterminate = !Number.isFinite(tiles) || tiles <= 0;
    progressPollInFlight = false;
    lastProgressPollAt = 0;
    progressStatusSeen = false;
    resetProgressStatus(tiles);

    if (progressIndeterminate) {
      progressElement.removeAttribute('value');
    } else {
      progressElement.value = '0';
      progressElement.setAttribute('value', '0');
    }

    numTiles = Number.isFinite(tiles) ? tiles : 0;
    totalSecsEstimated = progressIndeterminate ? 0 : secsPerTile * numTiles;
    secsElapsed = 0;
    providerManager.startProgressTimer(progressFunction, CONFIG.PROGRESS_UPDATE_INTERVAL_MS);
  }

  function disableProgress(time, actualTiles) {
    const elements = getProgressElements();
    elements.container.style.display = "none";
    const progressElement = elements.progress;

    // TASK-043 Phase 3: Use state manager for guaranteed cleanup
    providerManager.stopProgressTimer();
    progressIndeterminate = false;
    progressPollInFlight = false;
    lastProgressPollAt = 0;
    progressStatusSeen = false;
    progressElement.value = '0';
    progressElement.setAttribute('value', '0');
    setProgressStatus('Preparing detection', 'Waiting for detection progress updates...');

    if (time !== 0 && actualTiles > 0) {
      let secsPerTileLast = time / actualTiles;
      secsPerTile = (secsPerTile * dataPoints + secsPerTileLast) / (dataPoints + 1);
      dataPoints++;
    }
  }

  function progressFunction() {
    if (!progressIndeterminate && totalSecsEstimated > 0) {
      secsElapsed += CONFIG.PROGRESS_UPDATE_INTERVAL_MS / 1000;
      setProgress(secsElapsed / totalSecsEstimated * 100);
    }

    if (activeDetectionRequest) {
      void maybePollDetectionProgress();
    }
  }

  function setProgress(val) {
    if (progressIndeterminate) {
      return;
    }
    const clamped = Math.max(0, Math.min(100, val));
    document.getElementById("progress").value = String(clamped);
  }

  // ===== Error Handling =====

  function fatalError(msg) {
    const div = document.getElementById("fatal_div");
    div.style.display = "flex";
    div.innerHTML = `
      <div style="background: white; padding: 30px; border-radius: 8px; 
                  max-width: 500px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <p style="color: #d32f2f; font-weight: bold; font-size: 18px; margin-bottom: 15px;">
          ⚠️ Error
        </p>
        <p style="color: #333; margin-bottom: 20px;">${msg}</p>
        <button onclick="this.closest('#fatal_div').style.display='none'; location.reload();" 
                style="background: #1976d2; color: white; border: none; padding: 10px 20px; 
                       border-radius: 4px; cursor: pointer; margin-right: 10px;">
          Refresh Application
        </button>
        <button onclick="this.closest('#fatal_div').style.display='none'" 
                style="background: #757575; color: white; border: none; padding: 10px 20px; 
                       border-radius: 4px; cursor: pointer;">
          Dismiss
        </button>
      </div>
    `;
  }

  // ===== Expose to window for inline HTML handlers =====
  window.getObjects = getObjectsV2;
  window.processObjects = processObjects;
  window.cancelRequest = cancelRequest;
  window.fatalError = fatalError;

  window.TowerScoutLogger.debug('✅ Search module loaded (detection workflow, progress management)');

})();
