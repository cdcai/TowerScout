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
 * - progressFunction(): Update progress display
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
    console.log('🎯 Detection provider value:', provider, '| Type:', typeof provider);
    console.log('🎯 Provider validation - Azure:', provider === 'azure', '| Google:', provider === 'google');

    // TASK-045: Clear old boundaries from previous detection cycles before calculating new bounds
    // This ensures each detection run is independent and prevents boundary accumulation
    console.log('🧹 TASK-045: Clearing previous boundaries before detection');
    console.log('   Current boundaries count:', currentMap.boundaries ? currentMap.boundaries.length : 0);

    // Check if user has drawn new shapes that need to be converted to boundaries
    const hasNewShapes = currentMap.hasShapes && currentMap.hasShapes();

    if (hasNewShapes) {
      // Clear old boundaries and retrieve fresh drawn shapes
      console.log('   User has drawn new shapes - clearing old boundaries and retrieving new ones');
      currentMap.resetBoundaries();

      // Sync boundary clearing to other provider if available
      if (currentMap === window.googleMap && window.azureMap) {
        window.azureMap.resetBoundaries();
      } else if (currentMap === window.azureMap && window.googleMap) {
        window.googleMap.resetBoundaries();
      }

      // Now retrieve the newly drawn boundaries
      drawnBoundary();
      console.log('   New boundaries retrieved:', currentMap.boundaries ? currentMap.boundaries.length : 0);
    }

    // TASK-041 Phase 2 Step 2.6: Use boundary bounding box instead of viewport bounds
    // This ensures tiles are generated only for the drawn search area, not the entire viewport
    let bounds = currentMap.getBoundaryBoundsUrl();
    console.log('🗺️ Using bounds for tile generation:', bounds);
    console.log('   Final boundaries count for detection:', currentMap.boundaries ? currentMap.boundaries.length : 0);

    let boundaries = currentMap.getBoundariesStr();

    // Auto-create viewport boundary if no polygons are drawn
    if (boundaries === "[]") {
      console.log("No boundary selected, automatically using current viewport as detection area");
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
      console.log("Estimate request in progress");
    } else {
      console.log("Detection request in progress");
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
      .then(result => {
        if (!result.ok) {
          throw new Error(`HTTP ${result.status}: ${result.statusText}`);
        }

        // Check if result is JSON error instead of tile count
        const contentType = result.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return result.json().then(errorData => {
            throw new Error(errorData.error || 'Server error');
          });
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
        console.log("Number of tiles: " + tileCount + ", estimated time: "
          + (Math.round(tileCount * secsPerTile * 10) / 10) + " s");
        // let nt = estimateNumTiles(currentMap.getZoom());
        // console.log("  Estimated tiles:" + nt);
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
              throw new Error(`Detection failed: HTTP ${response.status} - ${response.statusText}`);
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
            TowerScoutErrorHandler.handleNetworkError(error, 'Cooling Tower Detection');
            disableProgress(0, 0);
          });
      })
      .catch(error => {
        console.error('❌ Tile estimation error:', error);
        TowerScoutErrorHandler.handleNetworkError(error, 'Tile Estimation');
        let msg = error.message || 'Unknown error occurred';
        if (msg.includes('zipcode')) {
          TowerScoutErrorHandler.showUserNotification(
            'Invalid ZIP code or search area. Please adjust your search boundaries.',
            'error'
          );
        } else {
          TowerScoutErrorHandler.showUserNotification(
            'Detection failed: ' + msg,
            'error'
          );
        }
      });
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

    console.log("Results: " + result.length + " tiles");

    // Process detection objects with error handling
    let processedDetections = 0;
    let processedTiles = 0;

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

    console.log(`✅ Processed ${processedDetections} detections and ${processedTiles} tiles`);
    console.log(`📊 ${Detection_detections.length} total detections with server-provided addresses.`);

    Detection.sort();
    Detection.generateList();
    adjustConfidence();  // Update detection visibility based on confidence threshold

    // TASK-033 Phase 4: Lock provider switching after ML detection completes
    if (typeof lockProviderSwitching === 'function') {
      lockProviderSwitching();
    }

    let time = (performance.now() - startTime) / 1000;
    disableProgress(time, result.length);
    console.log("Request completed in " + time + " s");
  }

  function cancelRequest() {
    disableProgress(0, 0);

    fetch("/abort", { method: "POST" })
      .then(result => {
        console.log("Request cancelled");
      })
      .catch(error => {
        console.error('❌ Cancel request error:', error);
      });
  }

  // ===== Progress Management =====

  function enableProgress(tiles) {
    document.getElementById("progress_div").style.display = "flex";

    // TASK-043 Phase 3: Use state manager for timer lifecycle management
    // Clear any existing progress timer to prevent memory leaks
    if (providerManager.isProgressActive()) {
      providerManager.stopProgressTimer();
    }
    providerManager.startProgressTimer(progressFunction, CONFIG.PROGRESS_UPDATE_INTERVAL_MS);

    numTiles = tiles;
    totalSecsEstimated = secsPerTile * numTiles;
    secsElapsed = 0;
  }

  function disableProgress(time, actualTiles) {
    document.getElementById("progress_div").style.display = "none";

    // TASK-043 Phase 3: Use state manager for guaranteed cleanup
    providerManager.stopProgressTimer();

    if (time !== 0) {
      let secsPerTileLast = time / actualTiles;
      secsPerTile = (secsPerTile * dataPoints + secsPerTileLast) / (dataPoints + 1);
      dataPoints++;
    }
  }

  function progressFunction() {
    secsElapsed += 0.1;
    setProgress(secsElapsed / totalSecsEstimated * 100);
  }

  function setProgress(val) {
    document.getElementById("progress").value = String(val);
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
  window.getObjects = getObjects;
  window.processObjects = processObjects;
  window.cancelRequest = cancelRequest;
  window.fatalError = fatalError;

  console.log('✅ Search module loaded (detection workflow, progress management)');

})();
