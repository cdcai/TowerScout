// TowerScout - GoogleMap Module
// Google Maps provider implementation
// TASK-038 Stage 3: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  // TASK-039 Phase 4B: GLOBAL singleton pattern to prevent duplicate Web Components
  // Multiple GoogleMap instances can be created, but only ONE PlaceAutocompleteElement should exist
  let globalAutocompleteElement = null;
  let isGloballyInitializingSearch = false;

  class GoogleMap extends TSMap {
    constructor() {
      super();
      // make the map 
      this.map = new google.maps.Map(document.getElementById("googleMap"), {
        zoom: 19,
        //center: nyc,
        mapTypeId: google.maps.MapTypeId.SATELLITE, // Start with satellite imagery for detection
        fullscreenControl: false,
        streetViewControl: false,
        scaleControl: true,
        mapTypeControl: false, // Disable map type control to prevent switching away from satellite
        maxZoom: 21,
        tilt: 0,
        styles: [
          {
            featureType: 'poi', // Points of interest
            stylers: [{ visibility: 'off' }]
          },
          {
            featureType: 'transit', // Transit stations
            stylers: [{ visibility: 'off' }]
          },
          {
            featureType: 'administrative.locality', // City labels
            elementType: 'labels',
            stylers: [{ visibility: 'off' }]
          },
          {
            featureType: 'road', // Road labels and lines
            elementType: 'labels',
            stylers: [{ visibility: 'off' }]
          }
        ]
      });
      this.boundaries = [];
      this.mapEventListeners = []; // Track map-specific event listeners for cleanup

      // TASK-039: Custom drawing implementation (replaces deprecated DrawingManager)
      this.isDrawing = false;
      this.drawingContext = null; // Track drawing context: 'search' or 'manual'
      this.drawingNotificationId = null; // Track persistent notification
      this.currentDrawingPoints = [];
      this.currentDrawingMarkers = [];
      this.currentDrawingPolyline = null;
      this.drawingClickListener = null;
      this.drawingDblClickListener = null;

      this.newShapes = [];

      // TASK-041 Phase 2 Step 2.1: Track created shapes for explicit cleanup
      this.activeShapes = {
        circles: [],      // Circle boundaries created via circle tool
        polygons: [],     // Polygon boundaries drawn by user
        markers: []       // Future: detection result markers
      };

      // TASK-039 Phase 4B: Store input reference for lazy initialization
      this.originalInput = input;

      // TASK-039 Phase 4B: Use GLOBAL singleton pattern (not instance variable)
      // Multiple GoogleMap instances may exist, but only ONE Web Component

      // TASK-039 Phase 4B: Initialize search (PlaceAutocompleteElement Web Component)
      this.initializeSearch();

      // Bias the PlaceAutocompleteElement results towards current map's viewport.
      // Note: locationBias expects LatLngBounds object directly (not wrapped)
      this.map.addListener("bounds_changed", () => {
        if (currentProvider === 'google') {
          // Auto-recreate search if needed (e.g., after provider switch)
          // BUT prevent race condition from concurrent bounds_changed events
          // Use GLOBAL element reference and flag
          if (!globalAutocompleteElement && !isGloballyInitializingSearch) {
            console.log('🔄 Autocomplete element missing, reinitializing...');
            this.initializeSearch();
          }

          if (globalAutocompleteElement) {
            const bounds = this.map.getBounds();
            if (bounds) {
              // Pass LatLngBounds directly to locationBias property
              globalAutocompleteElement.locationBias = bounds;
            }
          }
        }
      });

      // Note: Event listener setup moved to initializeSearch() method
    }

    // TASK-039 Phase 4B: Initialize PlaceAutocompleteElement Web Component
    // Extracted into separate method for reuse during provider switching
    initializeSearch() {
      // CRITICAL: ALWAYS hide the standard search input when Google Maps is active
      // This must happen BEFORE any early returns
      const input = document.getElementById('search');
      if (input) {
        input.style.display = 'none';
        console.log('🔧 Standard search input hidden for Google Maps');
      }

      // CRITICAL: Use GLOBAL flag to prevent concurrent initialization across ALL instances
      if (isGloballyInitializingSearch) {
        console.log('⚠️ [GLOBAL] Search initialization already in progress, skipping...');
        return;
      }

      // Skip if GLOBAL element already exists
      if (globalAutocompleteElement) {
        console.log('✅ [GLOBAL] PlaceAutocompleteElement already initialized (skipping)');
        // Store reference to this instance too for backward compatibility
        this.autocompleteElement = globalAutocompleteElement;
        return;
      }

      // Set GLOBAL flag to prevent concurrent calls
      isGloballyInitializingSearch = true;
      console.log('🔧 Initializing PlaceAutocompleteElement Web Component... [VERSION: 2026-03-11-FIX8-GLOBAL]');

      // DIAGNOSTIC: Check what's actually in the DOM RIGHT NOW
      const allElements = document.querySelectorAll('gmp-place-autocomplete');
      console.log(`🔍 [DIAGNOSTIC] DOM contains ${allElements.length} gmp-place-autocomplete element(s) BEFORE creation`);
      if (allElements.length > 0) {
        allElements.forEach((el, idx) => {
          console.log(`   └─ Element ${idx + 1}: parent=${el.parentElement?.id || 'unknown'}, display=${el.style.display}`);
        });
      }

      // Validate originalInput reference (use different variable name to avoid conflict)
      const originalInput = this.originalInput;
      if (!originalInput) {
        console.error('❌ Original input reference not found');
        isGloballyInitializingSearch = false;  // Clear GLOBAL flag on error
        return;
      }

      // ULTRA-DEFENSIVE: Find and remove ANY existing gmp-place-autocomplete elements in the entire document
      const existingElements = document.querySelectorAll('gmp-place-autocomplete');
      if (existingElements.length > 0) {
        console.warn(`⚠️ Found ${existingElements.length} orphaned gmp-place-autocomplete element(s), removing...`);
        existingElements.forEach((el, idx) => {
          console.log(`🧹 Removing orphaned element ${idx + 1}/${existingElements.length}`);
          if (el.parentElement) {
            el.parentElement.removeChild(el);
          }
        });
      }

      // Create PlaceAutocompleteElement Web Component
      const autocompleteElement = new google.maps.places.PlaceAutocompleteElement({
        // locationBias will be set dynamically via bounds_changed listener
        // includedPrimaryTypes is NOT set here to allow all geocoding types (addresses, cities, etc.)
      });

      // Append to container in HTML
      const container = document.getElementById('google-autocomplete-container');
      if (container) {
        // CRITICAL: Clear container RIGHT BEFORE appending (timing-sensitive fix)
        const childCount = container.childNodes.length;
        if (childCount > 0) {
          console.warn(`⚠️ Container has ${childCount} child(ren) RIGHT BEFORE append, clearing...`);
          while (container.firstChild) {
            console.log('🧹🧹 Removing child immediately before append');
            container.removeChild(container.firstChild);
          }
        }

        // Now append the new element
        container.appendChild(autocompleteElement);

        // CRITICAL: Set explicit width/height constraints on both container and Web Component
        // Web Components with Shadow DOM ignore external CSS, so we use inline styles
        container.style.display = 'inline-block';
        container.style.width = '40%';
        container.style.verticalAlign = '10%';

        // Set size on the Web Component element itself to match Azure search input
        autocompleteElement.style.width = '100%';
        autocompleteElement.style.maxWidth = '100%';
        autocompleteElement.style.height = '21px';  // Match Azure input height exactly
        autocompleteElement.style.minHeight = '21px';
        autocompleteElement.style.fontSize = '12px';  // Small font reduces em-based internal heights
        autocompleteElement.style.display = 'block';

        // Set placeholder text to match Azure Maps user experience
        autocompleteElement.placeholder = 'Search with Google Maps...';

        // POST-APPEND VERIFICATION: Ensure only ONE gmp-place-autocomplete element exists
        const finalCheck = container.querySelectorAll('gmp-place-autocomplete');
        if (finalCheck.length > 1) {
          console.error(`❌ DUPLICATE DETECTED: Found ${finalCheck.length} gmp-place-autocomplete elements after append!`);
          // Keep only the last one (our new element), remove all others
          for (let i = 0; i < finalCheck.length - 1; i++) {
            console.log(`🧹🧹🧹 Emergency removal of duplicate ${i + 1}`);
            container.removeChild(finalCheck[i]);
          }
        }

        console.log('📐 PlaceAutocompleteElement sizing applied: container width 30%, height 21px (matches Azure)');
      } else {
        console.error('❌ google-autocomplete-container not found in DOM');
        isGloballyInitializingSearch = false;  // Clear GLOBAL flag on error
        return;
      }

      // Store GLOBAL reference for all instances to use
      globalAutocompleteElement = autocompleteElement;
      this.autocompleteElement = autocompleteElement;  // Also store instance reference

      // DIAGNOSTIC: Verify only ONE element exists after creation
      const allElementsAfterCreation = document.querySelectorAll('gmp-place-autocomplete');
      console.log(`🔍 [DIAGNOSTIC] DOM contains ${allElementsAfterCreation.length} gmp-place-autocomplete element(s) AFTER creation`);
      if (allElementsAfterCreation.length > 1) {
        console.error(`❌ [DIAGNOSTIC] DUPLICATE CREATION - ${allElementsAfterCreation.length} elements exist!`);
        allElementsAfterCreation.forEach((el, idx) => {
          console.error(`   └─ Element ${idx + 1}: parent=${el.parentElement?.id || 'unknown'}, display=${el.style.display}`);
        });
      }

      // Listen for the gmp-select event fired when the user selects a prediction
      // Note: This is async pattern with placePrediction.toPlace() and fetchFields()
      autocompleteElement.addEventListener('gmp-select', async (event) => {
        // Only handle if Google Maps is the current provider
        if (currentProvider !== 'google') {
          console.log('Ignoring Google Places search - not current provider');
          return;
        }

        try {
          let i = 0;
          // Get the place prediction from the event
          const placePrediction = event.placePrediction;

          if (!placePrediction) {
            console.log('No place prediction available');
            return;
          }

          // Convert prediction to Place object (async)
          const place = placePrediction.toPlace();

          // Fetch required fields (async)
          await place.fetchFields({
            fields: ['location', 'viewport', 'displayName', 'formattedAddress', 'addressComponents']
          });

          if (!place.location) {
            console.log("No location available for selected place.");
            return;
          }

          // Normalize to match existing code expectations
          // New API uses different property names (location vs geometry.location, displayName vs name, etc.)
          const normalizedPlace = {
            geometry: {
              location: place.location,
              viewport: place.viewport
            },
            name: place.displayName,
            formatted_address: place.formattedAddress,
            address_components: place.addressComponents
          };

          // Store as array for compatibility with existing code
          this.places = [normalizedPlace];

          // Get the search query from the autocomplete element's input value
          // Use the selected place's display name as the query
          input.value = place.displayName || place.formattedAddress || '';
        } catch (error) {
          console.error('Error handling place selection:', error);
          return;
        }

        // Check for zipcode special case using the actual input value
        let p = input.value;
        if ((p.length === 5 && !isNaN(p)) ||
          (p.length === 7 && p[0] == '"' && p[6] == '"' && !isNaN(p.substring(1, 6))) ||
          (p.startsWith("zipcode "))) {
          // special case: zipcode
          getZipcodePolygon(p);
          return;
        }

        // Google Maps handles its own search through PlaceAutocompleteElement
        console.log('Google Maps handling search through PlaceAutocompleteElement Web Component');
        this.getBoundsPolygon(input.value, this.places[0]);
      });

      // TASK-039: All drawing functionality moved to custom methods below
      // No DrawingManager initialization needed

      // TASK-041 Phase 1: Initialization milestones marked in initGoogleMap()
      // after constructor completes (styleLoaded, drawingManagerReady)

      // Clear GLOBAL initialization flag
      isGloballyInitializingSearch = false;
      console.log('✅ [GLOBAL] PlaceAutocompleteElement initialized successfully');
    }

    // TASK-039: Custom polygon drawing implementation
    enablePolygonDrawing() {
      if (this.isDrawing) {
        console.log('Drawing already in progress');
        return;
      }

      console.log('🎨 Enabling custom polygon drawing mode');

      // Track drawing context based on whether detections exist
      const hasDetections = window.providerManager && window.providerManager.getDetectionsLength() > 0;
      this.drawingContext = hasDetections ? 'manual' : 'search';
      console.log('📍 Drawing context:', this.drawingContext, '(detections:', hasDetections ? 'YES' : 'NO', ')');

      // Show persistent instructions based on context (0 timeout = persistent until polygon complete)
      const message = this.drawingContext === 'search'
        ? 'Draw your search area. Click to add points, right-click outside to complete.'
        : 'Draw around the tower. Click to add points, right-click outside to complete.';

      this.drawingNotificationId = TowerScoutErrorHandler.showUserNotification(
        message,
        'info',
        0 // Persistent notification
      );

      // Set flag to prevent multiple drawing sessions
      this.isDrawing = true;
      this.currentDrawingPoints = [];
      this.currentDrawingMarkers = [];

      // Change cursor to crosshair
      this.map.setOptions({
        draggableCursor: 'crosshair'
      });

      // Add left-click listener for drawing points
      this.drawingClickListener = this.map.addListener('click', (event) => {
        if (!this.isDrawing) return;

        this.currentDrawingPoints.push(event.latLng);

        // Add marker to show point
        const marker = new google.maps.Marker({
          position: event.latLng,
          map: this.map,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 4,
            fillColor: 'green',
            fillOpacity: 1,
            strokeColor: 'white',
            strokeWeight: 1
          }
        });
        this.currentDrawingMarkers.push(marker);

        // Update preview polyline
        if (this.currentDrawingPoints.length > 1) {
          if (this.currentDrawingPolyline) {
            this.currentDrawingPolyline.setPath(this.currentDrawingPoints);
          } else {
            this.currentDrawingPolyline = new google.maps.Polyline({
              path: this.currentDrawingPoints,
              map: this.map,
              strokeColor: 'green',
              strokeWeight: 2,
              strokeOpacity: 0.8
            });
          }
        }

        console.log(`Point added: ${event.latLng.lat()}, ${event.latLng.lng()} (Total: ${this.currentDrawingPoints.length})`);
      });

      // Add right-click (contextmenu) listener to complete polygon
      this.drawingRightClickListener = this.map.addListener('rightclick', (event) => {
        console.log('🖱️ Right-click detected - completing polygon');
        if (!this.isDrawing) return;

        // Prevent default context menu
        event.stop();

        // Complete the polygon
        this.completePolygon();
      });
    }

    completePolygon() {
      if (this.currentDrawingPoints.length < 3) {
        console.warn('Polygon requires at least 3 points');
        TowerScoutErrorHandler.showUserNotification(
          'Polygon needs at least 3 points. Continue clicking to add more points.',
          'warning'
        );
        return;
      }

      console.log(`✅ Completing polygon with ${this.currentDrawingPoints.length} points`);

      // Create final polygon
      const polygon = new google.maps.Polygon({
        paths: this.currentDrawingPoints,
        strokeColor: '#800080',
        strokeWeight: 2,
        fillColor: '#800080',
        fillOpacity: 0.1,
        editable: true,
        draggable: true,
        map: this.map
      });

      // Store shape (matching current pattern for compatibility)
      this.newShapes.push(polygon);
      console.log(`new polygon with ${this.currentDrawingPoints.length} points`);

      // Capture context BEFORE cleanup resets it
      const completionContext = this.drawingContext;

      // Dismiss persistent drawing instruction notification
      if (this.drawingNotificationId) {
        TowerScoutErrorHandler.dismissNotification(this.drawingNotificationId);
        this.drawingNotificationId = null;
      }

      // Clean up drawing state (this resets drawingContext to null)
      this.cancelDrawing();

      // Context-aware completion notification using captured context
      const message = completionContext === 'search'
        ? 'Polygon complete! Click "Custom Shape" again to use as search area, or "Estimate Tiles" to proceed.'
        : 'Polygon complete! Click "Save Towers" button below to add it to the detection list.';

      TowerScoutErrorHandler.showUserNotification(
        message,
        'success',
        6000
      );
    }

    cancelDrawing() {
      console.log('🛑 Cancelling drawing mode');

      // Dismiss persistent notification if exists
      if (this.drawingNotificationId) {
        TowerScoutErrorHandler.dismissNotification(this.drawingNotificationId);
        this.drawingNotificationId = null;
      }

      // Remove event listeners
      if (this.drawingClickListener) {
        google.maps.event.removeListener(this.drawingClickListener);
        this.drawingClickListener = null;
      }
      if (this.drawingRightClickListener) {
        google.maps.event.removeListener(this.drawingRightClickListener);
        this.drawingRightClickListener = null;
      }

      // Clear temporary markers
      for (let marker of this.currentDrawingMarkers) {
        marker.setMap(null);
      }
      this.currentDrawingMarkers = [];

      // Clear preview polyline
      if (this.currentDrawingPolyline) {
        this.currentDrawingPolyline.setMap(null);
        this.currentDrawingPolyline = null;
      }

      // Reset state
      this.isDrawing = false;
      this.drawingContext = null; // Reset drawing context
      this.currentDrawingPoints = [];
      this.map.setOptions({
        draggableCursor: null
      });
    }

    retrieveDrawnBoundaries() {
      let polys = [];

      for (let s of this.newShapes) {
        if (typeof s.bounds !== "undefined") {
          // rectangles have bounds
          let ne = s.bounds.getNorthEast();
          let sw = s.bounds.getSouthWest();
          polys.push(new SimpleBoundary([sw.lng(), ne.lat(), ne.lng(), sw.lat()]));
        } else {
          // polygons do not
          let poly = [];
          s.getPath().forEach((e, i) => { poly.push([e.lng(), e.lat()]); });
          polys.push(new PolygonBoundary(poly));
        }
      }
      this.clearShapes()
      return polys;
    }

    hasShapes() {
      return this.newShapes.length !== 0;
    }

    addShapes() {
      let bounds;

      for (let s of this.newShapes) {
        if (typeof s.bounds === "undefined") {
          bounds = new google.maps.LatLngBounds();
          s.getPath().forEach((e) => {
            bounds = bounds.extend(e);
          });
        } else {
          bounds = s.bounds;
        }
        s.setMap(null);

        let x1 = bounds.getSouthWest().lng();
        let y1 = bounds.getNorthEast().lat();
        let x2 = bounds.getNorthEast().lng();
        let y2 = bounds.getSouthWest().lat();

        // TASK-033 Phase 2: Create only ONE detection per drawn polygon (use center tile)
        // This prevents multiple detections when polygon spans tile boundaries
        let centerX = (x1 + x2) / 2;
        let centerY = (y1 + y2) / 2;
        let tileIds = Tile.getTileIds(centerX, centerY, centerX, centerY);

        if (tileIds.length > 0) {
          let tileArrayIndex = tileIds[0];
          let tile = providerManager.getTilesArrayDirect()[tileArrayIndex];
          // TASK-033 Phase 3: Use tile.id (not array index) for export matching
          let tileId = tile.id;

          // Clamp bounds to tile boundaries
          x1 = Math.max(x1, tile.x1);
          x1 = Math.min(x1, tile.x2);
          x2 = Math.max(x2, tile.x1);
          x2 = Math.min(x2, tile.x2);
          y1 = Math.max(y1, tile.y2);
          y1 = Math.min(y1, tile.y1);
          y2 = Math.max(y2, tile.y2);
          y2 = Math.min(y2, tile.y1);

          let det = new Detection(x1, y1, x2, y2,
            'added', 1.0, tileId, -1, true, true); // id_in_tile parameter

          // TASK-033: Geocode manual tower location to get address
          this.geocodeDetection(det);

          det.update();
        }
      }
      this.newShapes = [];

      // TASK-033: Custom drawing cleanup (removed legacy drawingManager.setDrawingMode call)
      // No longer needed - custom drawing system handles state via isDrawing flag
      if (this.isDrawing) {
        this.cancelDrawing();
      }

      Detection.generateList();
      adjustConfidence();

      // TASK-033 Phase 4: Lock provider switching after manual towers added
      if (typeof lockProviderSwitching === 'function') {
        lockProviderSwitching();
      }
    }

    // TASK-033: Geocode detection coordinates to get building address
    async geocodeDetection(detection) {
      try {
        const center = detection.getCenter();
        const lat = center[1];
        const lng = center[0];

        console.log(`🌍 Geocoding manual tower at ${lat}, ${lng}...`);

        const response = await fetch('/api/geocode/reverse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            lat: lat,
            lng: lng,
            provider: 'auto'
          })
        });

        if (!response.ok) {
          throw new Error(`Geocoding failed: ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.address) {
          detection.address = data.address;
          detection.addressConfidence = data.confidence;
          detection.addressProvider = data.provider;
          console.log(`✅ Geocoded address: ${data.address}`);
        } else {
          // Fallback to coordinates
          detection.address = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
          detection.addressConfidence = 0.0;
          detection.addressProvider = 'fallback';
          console.warn(`⚠️ Geocoding failed, using coordinates`);
        }

        // TASK-033: Update detection list to show the new address
        Detection.generateList();

      } catch (error) {
        console.error('❌ Geocoding error:', error);
        // Fallback to coordinates
        const center = detection.getCenter();
        detection.address = `${center[1].toFixed(6)}, ${center[0].toFixed(6)}`;
        detection.addressConfidence = 0.0;
        detection.addressProvider = 'error';

        // Update list even with fallback address
        Detection.generateList();
      }
    }

    clearShapes() {
      // Remove unsaved drawn polygons only
      // Note: To delete saved manual towers, uncheck them in the detection list
      // TASK-039: Cancel active drawing if in progress
      if (this.isDrawing) {
        this.cancelDrawing();
      }

      // Clear all drawn shapes from map
      for (let shape of this.newShapes) {
        shape.setMap(null);
      }
      this.newShapes = [];
    }

    clearAll() {
      this.clearShapes();
      // TASK-033 Phase 2: Properly remove manual towers from map before removing from array
      // First hide all manual tower rectangles (conf=1.0)
      for (let det of Detection_detections) {
        if (det.conf === 1.0) {
          this.updateMapRect(det, false); // Remove rectangle from map
        }
      }

      // Then remove manual detections from array
      let dets = [];
      for (let det of Detection_detections) {
        if (det.conf !== 1.0) {
          det.id = dets.length;
          dets.push(det);
        }
      }
      providerManager.setDetections(dets);

      // TASK-033 Phase 2: Refresh UI list after removing manual towers
      Detection.generateList();

      // TASK-033 Phase 4: Unlock provider switching after clearing all manual towers
      if (typeof unlockProviderSwitching === 'function') {
        unlockProviderSwitching();
      }
    }



    getBoundsPolygon(query, place) {
      googleMap.resetBoundaries();
      // Google Maps provider-specific search - only affects Google Maps

      // Handle null/undefined place for Enter-to-search fallback
      const hasPlace = place && place.geometry && place.formatted_address;
      console.log("Querying place outline for: " + query + (hasPlace ? (" (" + place.name + ")") : " (no Place)"));
      if (query[0] === '"' && query.endsWith('"')) {
        // hand this to openstreetmap "as is"
        query = query.substring(1, query.length - 1);
      } else if (hasPlace) {
        // take the google idea of what this is instead
        query = place.formatted_address;
      } // else use the raw query string

      // Fit bounds using place viewport when available, otherwise keep current view
      const viewport = hasPlace ? place.geometry.viewport : googleMap.map.getBounds();
      if (viewport) {
        googleMap.map.fitBounds(viewport);
      }

      $.ajax({
        url: "https://nominatim.openstreetmap.org/search.php",
        data: {
          q: query,
          polygon_geojson: "1",
          format: "json",
        },
        success: function (result) {
          let x = result[0];
          if (typeof x === 'undefined') {
            //googleMap.map.setCenter(place.geometry.location);
            // Fit to place viewport if present; otherwise keep current bounds
            if (hasPlace && place.geometry && place.geometry.viewport) {
              googleMap.map.fitBounds(place.geometry.viewport);
            }
            //googleMap.map.setZoom(19);
            // No Azure Maps dependency - Google provider handles Google Maps only
            return;
          }
          console.log(" Display name: " + x['display_name'] + ": " + x['boundingbox']);
          if (x["geojson"]["type"] == "Polygon" || x["geojson"]["type"] == "MultiPolygon") {
            let bounds = null;
            let ps = x["geojson"]["coordinates"];
            for (let p of ps) {
              if (x["geojson"]["type"] == "MultiPolygon") {
                p = p[0];
              }
              //console.log(" Polygon: " + p);
              //let polyData = parseLatLngArray(p);
              googleMap.addBoundary(new PolygonBoundary(p));
              // Only update Google Maps when Google is the provider
            }
            //console.log(bounds.toUrlValue());
          } else if (x["geojson"]["type"] == "LineString" || x["geojson"]["type"] == "Point") {
            googleMap.map.fitBounds(place.geometry.viewport, 0)
          }
          if (googleMap.boundaries.length > 0) {
            googleMap.showBoundaries();
            // Only show Google Maps boundaries when Google is the provider
          }
        }
      });
    }


    // TASK-039 Phase 4B: Updated for PlaceAutocompleteElement Web Component
    // Biases search results towards current map viewport
    // Note: locationBias expects LatLngBounds object directly (not wrapped)
    biasSearchBox() {
      // TASK-039 Phase 4B: Bias PlaceAutocompleteElement instead of SearchBox
      // Auto-recreate if missing (e.g., after provider switch)
      // BUT prevent race condition from concurrent calls - use GLOBAL references
      if (!globalAutocompleteElement && !isGloballyInitializingSearch) {
        console.log('🔄 PlaceAutocompleteElement not found in biasSearchBox, reinitializing...');
        this.initializeSearch();
      }

      if (globalAutocompleteElement && this.map) {
        const bounds = this.map.getBounds();
        if (bounds) {
          // Pass LatLngBounds directly to locationBias property
          globalAutocompleteElement.locationBias = bounds;
          console.log('🎯 PlaceAutocompleteElement biased to current map bounds');
        }
      }
    }

    getBounds() {
      let bounds = this.map.getBounds();
      let ne = bounds.getNorthEast();
      let sw = bounds.getSouthWest();
      return [sw.lng(), ne.lat(), ne.lng(), sw.lat()];
    }

    fitBounds(x1, y1, x2, y2) {
      let bounds = google.maps.LatLngBounds({
        north: y1,
        south: y2,
        east: x2,
        west: x1
      });
      this.map.fitBounds(bounds);
    }

    setCenter(c) {
      this.map.setCenter({ lat: c[1], lng: c[0] });
      //this.map.setZoom(19);
    }

    getZoom() {
      return this.map.getZoom();
    }

    setZoom(z) {
      this.map.setZoom(z);
    }

    makeMapRect(o, listener) {
      const rectangle = new google.maps.Rectangle({
        strokeColor: o.color,
        strokeOpacity: 1.0,
        strokeWeight: 1,
        fillColor: o.fillColor,
        fillOpacity: o.opacity,
        clickable: typeof listener !== 'undefined',
        bounds: {
          north: o.y1,
          south: o.y2,
          east: o.x2,
          west: o.x1,
        },
      });
      if (typeof listener !== 'undefined') {
        rectangle.addListener("click", listener);
        rectangle.setOptions({ zIndex: 1000 });
      } else {
        rectangle.setOptions({ zIndex: 0 });
      }
      return rectangle;
    }

    colorMapRect(o, color) {
      o.mapRect.setOptions({ strokeColor: color, fillColor: color, fillOpacity: o.opacity });
    }

    updateMapRect(o, onoff) {
      let r = o.mapRect;
      r.setMap(onoff ? this.map : null)
    }

    resetBoundaries() {
      console.log('🧹 Google Maps: Resetting boundaries...');
      const boundaryCount = this.boundaries.length;

      for (let b of this.boundaries) {
        if (b && b.object) {
          b.object.setMap(null); // Remove from map visually
          b.object = null; // Release reference
        }
      }
      this.boundaries = [];

      // Clear activeShapes tracking
      this.activeShapes.circles = [];
      this.activeShapes.polygons = [];

      console.log(`✅ Google Maps: Removed ${boundaryCount} boundaries from map`);
    }

    clearCircles() {
      console.log(`🔄 Clearing ${this.activeShapes.circles.length} circle(s) from Google Maps...`);

      if (this.activeShapes.circles.length === 0) {
        console.log('✅ No circles to clear');
        return;
      }

      // Step 1: Remove circle polygons from map
      for (let circle of this.activeShapes.circles) {
        if (circle) {
          circle.setMap(null);
        }
      }
      console.log('  - Removed circle polygons from map');

      // Step 2: Filter circles from boundaries array
      const beforeCount = this.boundaries.length;
      this.boundaries = this.boundaries.filter(b => !b.isCircle);
      const removedCount = beforeCount - this.boundaries.length;
      console.log(`  - Removed ${removedCount} circle boundary reference(s)`);

      // Step 3: Clear tracking array
      const clearedCount = this.activeShapes.circles.length;
      this.activeShapes.circles = [];

      console.log(`✅ Cleared ${clearedCount} circle(s)`);
    }

    addBoundary(b) {
      // add to active bounds
      b.index = this.boundaries.length;

      // now make GoogleMap objects and link to them
      let points = b.points.map(p => ({ lng: p[0], lat: p[1] }));
      const poly = new google.maps.Polygon({
        paths: points,
        strokeColor: "#0000FF",
        strokeOpacity: 1,
        strokeWeight: 2,
        fillColor: "#00FF00",
        fillOpacity: 0,
        clickable: false,
      });
      poly.setMap(googleMap.map);
      b.object = poly;
      b.objectBounds = new google.maps.LatLngBounds();
      for (let p of points) {
        b.objectBounds.extend(p);
      }

      this.boundaries.push(b);

      // TASK-041 Phase 2 Step 2.2: Track circle boundaries for cleanup
      if (b.isCircle) {
        this.activeShapes.circles.push(poly);
        console.log('  - Tracked circle in activeShapes (total:', this.activeShapes.circles.length + ')');
      }


    }

    hasNonCircleBoundaries() {
      return this.boundaries.some(boundary => !boundary.isCircle);
    }

    showBoundaries() {
      // set map bounds to fit union of all active boundaries
      let bounds = new google.maps.LatLngBounds();
      for (let b of this.boundaries) {
        bounds = bounds.union(b.objectBounds);
      }
      this.map.fitBounds(bounds, 0);
    }

    getBoundaryBoundsUrl() {
      // set map bounds to fit union of all active boundaries
      let bounds = new google.maps.LatLngBounds();
      for (let b of this.boundaries) {
        bounds = bounds.union(b.objectBounds);
      }
      return bounds.toUrlValue();
    }

    getBoundariesStr() {
      let result = [];
      for (let b of this.boundaries) {
        result.push(b.toString())
      }
      return "[" + result.join(",") + "]";
    }

    // Memory Management: Cleanup Methods

    cleanupDrawingManager() {
      if (this.drawingManager) {
        console.log('🧹 Cleaning up Google DrawingManager...');

        // Remove all event listeners from drawing manager
        try {
          if (typeof google !== 'undefined' && google.maps && google.maps.event) {
            google.maps.event.clearInstanceListeners(this.drawingManager);
          }
        } catch (e) {
          console.warn('⚠️ Error clearing drawing manager listeners:', e.message);
        }

        // Remove from map
        try {
          this.drawingManager.setMap(null);
        } catch (e) {
          console.warn('⚠️ Error removing drawing manager from map:', e.message);
        }

        // TASK-033: Don't null drawingManager to prevent errors in legacy code paths
        // this.drawingManager = null;
        console.log('✅ Google DrawingManager cleaned up (reference preserved)');
      }
    }

    cleanupMapListeners() {
      if (this.mapEventListeners.length > 0) {
        console.log(`🧹 Cleaning up ${this.mapEventListeners.length} Google map listeners...`);

        for (const listener of this.mapEventListeners) {
          try {
            if (listener.listener && typeof google !== 'undefined' && google.maps && google.maps.event) {
              google.maps.event.removeListener(listener.listener);
            }
          } catch (e) {
            console.warn(`⚠️ Error removing listener ${listener.eventType}:`, e.message);
          }
        }

        this.mapEventListeners = [];
        console.log('✅ Google map listeners cleaned up');
      }
    }

    cleanupSearch() {
      console.log('🧹 Cleaning up Google search infrastructure...');

      // DIAGNOSTIC: Check what's in the DOM before cleanup
      const allElementsBefore = document.querySelectorAll('gmp-place-autocomplete');
      console.log(`🔍 [DIAGNOSTIC] DOM contains ${allElementsBefore.length} gmp-place-autocomplete element(s) BEFORE cleanup`);

      // TASK-039 Phase 4B: Remove PlaceAutocompleteElement Web Component (use GLOBAL reference)
      const container = document.getElementById('google-autocomplete-container');

      if (globalAutocompleteElement) {
        try {
          // Remove from DOM
          if (container && globalAutocompleteElement.parentElement === container) {
            container.removeChild(globalAutocompleteElement);
            console.log('✅ [GLOBAL] PlaceAutocompleteElement removed from container');
          }

          // Clear event listeners
          if (typeof google !== 'undefined' && google.maps && google.maps.event) {
            google.maps.event.clearInstanceListeners(globalAutocompleteElement);
          }

          globalAutocompleteElement = null;
          this.autocompleteElement = null;
          console.log('✅ [GLOBAL] autocompleteElement reference cleared');

        } catch (e) {
          console.warn('⚠️ Error cleaning up PlaceAutocompleteElement:', e.message);
        }
      }

      // DEFENSIVE: Clear ALL remaining children from container
      if (container) {
        while (container.firstChild) {
          console.log('🧹 Removing orphaned child from autocomplete container');
          container.removeChild(container.firstChild);
        }
        container.style.display = 'none';
        console.log('✅ Container cleared and hidden');
      }

      // Show the original input for other providers
      if (this.originalInput) {
        this.originalInput.style.display = 'inline';
        console.log('✅ Original search input restored');
      }

      // Clear GLOBAL initialization flag in case it was stuck
      isGloballyInitializingSearch = false;

      // Clear places cache
      this.places = null;

      // DIAGNOSTIC: Verify cleanup actually removed the elements
      const allElementsAfter = document.querySelectorAll('gmp-place-autocomplete');
      console.log(`🔍 [DIAGNOSTIC] DOM contains ${allElementsAfter.length} gmp-place-autocomplete element(s) AFTER cleanup`);
      if (allElementsAfter.length > 0) {
        console.error('❌ [DIAGNOSTIC] Cleanup FAILED - elements still in DOM!');
        allElementsAfter.forEach((el, idx) => {
          console.error(`   └─ Orphan ${idx + 1}: parent=${el.parentElement?.id || 'unknown'}, display=${el.style.display}`);
        });
      }

      console.log('✅ [GLOBAL] Google search infrastructure cleaned up');
    }

    cleanup() {
      console.log('🧹 Starting Google Maps cleanup...');

      try {
        // 1. Cleanup drawing manager
        this.cleanupDrawingManager();

        // 2. Cleanup map event listeners
        this.cleanupMapListeners();

        // 3. Cleanup search infrastructure
        this.cleanupSearch();

        // 4. Reset boundaries (already correct implementation)
        this.resetBoundaries();

        // 5. Clear drawn shapes
        if (this.newShapes && this.newShapes.length > 0) {
          this.clearShapes();
        }

        console.log('✅ Google Maps cleanup complete');
      } catch (error) {
        console.error('❌ Error during Google Maps cleanup:', error);
        // Don't throw - allow cleanup to complete partially
      }
    }

    // ISSUE-002 FIX: Restore method to re-attach components after provider switch
    restore() {
      console.log('🔄 Restoring Google Maps components after provider switch...');

      try {
        // Re-initialize search if needed
        if (this.map) {
          console.log('🔍 Re-biasing search to current map bounds...');
          // Trigger bounds_changed to update PlaceAutocompleteElement
          google.maps.event.trigger(this.map, 'bounds_changed');
        }

        console.log('✅ Google Maps restoration complete');
      } catch (error) {
        console.error('❌ Error during Google Maps restoration:', error);
        // Don't throw - allow app to continue even if restoration has issues
      }
    }

  }

  // Export to window for global access (IIFE pattern)
  window.GoogleMap = GoogleMap;

  console.log('✅ GoogleMap module loaded');
})();
