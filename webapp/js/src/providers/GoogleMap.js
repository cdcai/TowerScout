// TowerScout - GoogleMap Module
// Google Maps provider implementation
// TASK-038 Stage 3: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  // The shared location control owns search input and suggestion state.

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

      this.initializeSearch();
    }

    extractBoundaryPointsFromShape(shape) {
      if (typeof shape.bounds !== 'undefined') {
        const ne = shape.bounds.getNorthEast();
        const sw = shape.bounds.getSouthWest();
        return [
          [sw.lng(), ne.lat()],
          [ne.lng(), ne.lat()],
          [ne.lng(), sw.lat()],
          [sw.lng(), sw.lat()],
          [sw.lng(), ne.lat()]
        ];
      }

      const points = [];
      shape.getPath().forEach((point) => {
        points.push([point.lng(), point.lat()]);
      });
      return points;
    }

    validateDrawnShapes(options = {}) {
      const showNotification = options.showNotification === true;
      const label = options.label || 'custom shape';
      const remediation = options.remediation || 'edit_or_redraw';
      const shapes = options.shapes || this.newShapes;
      const polygons = [];

      for (const shape of shapes) {
        const points = this.extractBoundaryPointsFromShape(shape);
        if (points) {
          polygons.push(points);
        }
      }

      const validation = window.PolygonValidation.validatePolygonCollection(polygons);
      if (!validation.valid && showNotification) {
        TowerScoutErrorHandler.showUserNotification(
          window.PolygonValidation.getUserMessage(validation, label, { remediation }),
          'warning',
          6000
        );
      }

      return validation;
    }

    initializeSearch() {
      window.LocationSearch.init();
    }

    // TASK-039: Custom polygon drawing implementation
    enablePolygonDrawing(contextOverride = null) {
      if (this.isDrawing) {
        window.TowerScoutLogger.debug('Drawing already in progress');
        return;
      }

      window.TowerScoutLogger.debug('🎨 Enabling custom polygon drawing mode');

      // Track drawing context explicitly when the triggering action is known.
      const hasDetections = window.providerManager && window.providerManager.getDetectionsLength() > 0;
      this.drawingContext = contextOverride || (hasDetections ? 'manual' : 'search');
      window.TowerScoutLogger.debug('📍 Drawing context:', this.drawingContext, '(detections:', hasDetections ? 'YES' : 'NO', ')');

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

        window.TowerScoutLogger.debug(`Point added: ${event.latLng.lat()}, ${event.latLng.lng()} (Total: ${this.currentDrawingPoints.length})`);
      });

      // Add right-click (contextmenu) listener to complete polygon
      this.drawingRightClickListener = this.map.addListener('rightclick', (event) => {
        window.TowerScoutLogger.debug('🖱️ Right-click detected - completing polygon');
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

      window.TowerScoutLogger.debug(`✅ Completing polygon with ${this.currentDrawingPoints.length} points`);

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
      window.TowerScoutLogger.debug(`new polygon with ${this.currentDrawingPoints.length} points`);

      // Capture context BEFORE cleanup resets it
      const completionContext = this.drawingContext;

      const validation = this.validateDrawnShapes({ shapes: [polygon] });

      // Dismiss persistent drawing instruction notification
      if (this.drawingNotificationId) {
        TowerScoutErrorHandler.dismissNotification(this.drawingNotificationId);
        this.drawingNotificationId = null;
      }

      // Clean up drawing state (this resets drawingContext to null)
      this.cancelDrawing();

      if (!validation.valid) {
        TowerScoutErrorHandler.showUserNotification(
          window.PolygonValidation.getUserMessage(validation, 'custom shape', { remediation: 'edit_or_redraw' }),
          'warning',
          6000
        );
        return;
      }

      // Context-aware completion notification using captured context
      const message = completionContext === 'search'
        ? 'Polygon complete! Click "Custom Shape" again to use as search area, or "Estimate Tiles" to proceed.'
        : 'Polygon complete! Click "Save Towers" button below to add it to the detection list.';

      TowerScoutErrorHandler.showUserNotification(
        message,
        'success',
        9000
      );
    }

    cancelDrawing() {
      window.TowerScoutLogger.debug('🛑 Cancelling drawing mode');

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
      const validation = this.validateDrawnShapes();
      if (!validation.valid) {
        console.warn('⚠️ Invalid drawn Google boundary detected, leaving shape in place for editing');
        return [];
      }

      let polys = [];

      for (let s of this.newShapes) {
        if (typeof s.bounds !== "undefined") {
          // rectangles have bounds
          let ne = s.bounds.getNorthEast();
          let sw = s.bounds.getSouthWest();
          polys.push(new SimpleBoundary([sw.lng(), ne.lat(), ne.lng(), sw.lat()]));
        } else {
          // polygons do not
          let poly = this.extractBoundaryPointsFromShape(s);
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
            'added', 1.0, tileId, -1,
            this.manualTowerInside(x1, y1, x2, y2), true);

          // TASK-033: Geocode manual tower location to get address
          this.geocodeDetection(det);
        }
      }
      this.newShapes = [];

      // TASK-033: Custom drawing cleanup (removed legacy drawingManager.setDrawingMode call)
      // No longer needed - custom drawing system handles state via isDrawing flag
      if (this.isDrawing) {
        this.cancelDrawing();
      }

      Detection.generateList();

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

        window.TowerScoutLogger.debug(`🌍 Geocoding manual tower at ${lat}, ${lng}...`);

        const response = await fetch('/api/geocode/reverse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            lat: lat,
            lng: lng,
            provider: document.querySelector('#providers input[name="provider"]:checked')?.value || 'google'
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
          window.TowerScoutLogger.debug(`✅ Geocoded address: ${data.address}`);
        } else {
          // Fallback to coordinates
          detection.address = `Coordinates: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
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
        detection.address = `Coordinates: ${center[1].toFixed(6)}, ${center[0].toFixed(6)}`;
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



    getBoundsPolygon(query, place, isCurrent = () => true) {
      if (!isCurrent()) return;
      if (window.CoordinateSearch.handle(query, this)) return;
      googleMap.resetBoundaries();
      // Google Maps provider-specific search - only affects Google Maps

      // Handle null/undefined place for Enter-to-search fallback
      const hasPlace = place && place.geometry && place.formatted_address;
      window.TowerScoutLogger.debug("Querying place outline for: " + query + (hasPlace ? (" (" + place.name + ")") : " (no Place)"));
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
          if (!isCurrent()) return;
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
          window.TowerScoutLogger.debug(" Display name: " + x['display_name'] + ": " + x['boundingbox']);
          if (x["geojson"]["type"] == "Polygon" || x["geojson"]["type"] == "MultiPolygon") {
            let bounds = null;
            let ps = x["geojson"]["coordinates"];
            for (let p of ps) {
              if (x["geojson"]["type"] == "MultiPolygon") {
                p = p[0];
              }
              //window.TowerScoutLogger.debug(" Polygon: " + p);
              //let polyData = parseLatLngArray(p);
              googleMap.addBoundary(new PolygonBoundary(p));
              // Only update Google Maps when Google is the provider
            }
            //window.TowerScoutLogger.debug(bounds.toUrlValue());
          } else if (x["geojson"]["type"] == "LineString" || x["geojson"]["type"] == "Point") {
            if (hasPlace && place.geometry.viewport) {
              googleMap.map.fitBounds(place.geometry.viewport, 0);
            }
          }
          if (googleMap.boundaries.length > 0) {
            googleMap.showBoundaries();
            // Only show Google Maps boundaries when Google is the provider
          }
        }
      });
    }


    // The shared control reads the active viewport for each suggestion request.
    biasSearchBox() {}

    getBounds() {
      let bounds = this.map.getBounds();
      if (!bounds) {
        const center = this.map.getCenter();
        if (center && typeof center.lng === 'function' && typeof center.lat === 'function') {
          return [center.lng(), center.lat(), center.lng(), center.lat()];
        }
        return [nyc[0], nyc[1], nyc[0], nyc[1]];
      }
      let ne = bounds.getNorthEast();
      let sw = bounds.getSouthWest();
      return [sw.lng(), ne.lat(), ne.lng(), sw.lat()];
    }

    fitBounds(x1, y1, x2, y2, padding) {
      let bounds = {
        north: y1,
        south: y2,
        east: x2,
        west: x1
      };
      this.map.fitBounds(bounds, padding);
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
      if (!o.mapRect) {
        return;
      }
      o.mapRect.setOptions({ strokeColor: color, fillColor: color, fillOpacity: o.opacity });
    }

    updateMapRect(o, onoff) {
      if (!o.mapRect) {
        return;
      }
      let r = o.mapRect;
      r.setMap(onoff ? this.map : null)
    }

    resetBoundaries() {
      window.TowerScoutLogger.debug('🧹 Google Maps: Resetting boundaries...');
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

      window.TowerScoutLogger.debug(`✅ Google Maps: Removed ${boundaryCount} boundaries from map`);
    }

    clearCircles() {
      window.TowerScoutLogger.debug(`🔄 Clearing ${this.activeShapes.circles.length} circle(s) from Google Maps...`);

      if (this.activeShapes.circles.length === 0) {
        window.TowerScoutLogger.debug('✅ No circles to clear');
        return;
      }

      // Step 1: Remove circle polygons from map
      for (let circle of this.activeShapes.circles) {
        if (circle) {
          circle.setMap(null);
        }
      }
      window.TowerScoutLogger.debug('  - Removed circle polygons from map');

      // Step 2: Filter circles from boundaries array
      const beforeCount = this.boundaries.length;
      this.boundaries = this.boundaries.filter(b => !b.isCircle);
      const removedCount = beforeCount - this.boundaries.length;
      window.TowerScoutLogger.debug(`  - Removed ${removedCount} circle boundary reference(s)`);

      // Step 3: Clear tracking array
      const clearedCount = this.activeShapes.circles.length;
      this.activeShapes.circles = [];

      window.TowerScoutLogger.debug(`✅ Cleared ${clearedCount} circle(s)`);
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
        window.TowerScoutLogger.debug('  - Tracked circle in activeShapes (total:', this.activeShapes.circles.length + ')');
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
        window.TowerScoutLogger.debug('🧹 Cleaning up Google DrawingManager...');

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
        window.TowerScoutLogger.debug('✅ Google DrawingManager cleaned up (reference preserved)');
      }
    }

    cleanupMapListeners() {
      if (this.mapEventListeners.length > 0) {
        window.TowerScoutLogger.debug(`🧹 Cleaning up ${this.mapEventListeners.length} Google map listeners...`);

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
        window.TowerScoutLogger.debug('✅ Google map listeners cleaned up');
      }
    }

    cleanupSearch() {
      window.LocationSearch.invalidate();
    }

    cleanup() {
      window.TowerScoutLogger.debug('🧹 Starting Google Maps cleanup...');

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

        window.TowerScoutLogger.debug('✅ Google Maps cleanup complete');
      } catch (error) {
        console.error('❌ Error during Google Maps cleanup:', error);
        // Don't throw - allow cleanup to complete partially
      }
    }

    // ISSUE-002 FIX: Restore method to re-attach components after provider switch
    restore() {
      window.TowerScoutLogger.debug('🔄 Restoring Google Maps components after provider switch...');

      try {
        // Re-initialize search if needed
        if (this.map) {
          window.TowerScoutLogger.debug('🔍 Re-biasing search to current map bounds...');
          // Trigger bounds_changed to update PlaceAutocompleteElement
          google.maps.event.trigger(this.map, 'bounds_changed');
        }

        window.TowerScoutLogger.debug('✅ Google Maps restoration complete');
      } catch (error) {
        console.error('❌ Error during Google Maps restoration:', error);
        // Don't throw - allow app to continue even if restoration has issues
      }
    }

  }

  // Export to window for global access (IIFE pattern)
  window.GoogleMap = GoogleMap;

  window.TowerScoutLogger.debug('✅ GoogleMap module loaded');
})();
