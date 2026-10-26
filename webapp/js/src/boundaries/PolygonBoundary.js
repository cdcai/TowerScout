// TowerScout - PolygonBoundary Module
// Handles polygon drawing, boundary management, and helper utilities
// TASK-038 Stage 2: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  function setDrawingIntent(context) {
    if (!currentMap) {
      return;
    }

    if (typeof currentMap.setPendingDrawingContext === 'function') {
      currentMap.setPendingDrawingContext(context);
    }
  }

  function enableDrawingForIntent(context) {
    window.TowerScoutLogger.debug('enable drawing requested', {
      context: context,
      hasCurrentMap: !!currentMap,
      currentProvider: currentProvider,
      hasGoogleMap: !!googleMap,
      hasAzureMap: !!azureMap,
      windowCurrentProvider: window.currentProvider,
      windowCurrentMap: !!window.currentMap,
      windowGoogleMap: !!window.googleMap
    });

    // Defensive null checks
    if (!currentMap) {
      console.error('currentMap is not initialized');
      TowerScoutErrorHandler.showUserNotification(
        'Map is still initializing. Please wait a moment and try again.',
        'warning'
      );
      return;
    }

    setDrawingIntent(context);

    // TASK-039: If Google Maps, manage drawing mode
    if (currentProvider === 'google' && googleMap) {
      window.TowerScoutLogger.debug('Google Maps detected, checking drawing state...');

      // Check if drawing is in progress
      if (googleMap.isDrawing) {
        window.TowerScoutLogger.debug('Drawing already in progress');
        TowerScoutErrorHandler.showUserNotification(
          'Drawing in progress. Right-click outside to complete your polygon.',
          'info'
        );
        return;
      }

      // Search mode consumes drawn polygons as boundaries.
      if (context === 'search' && googleMap.hasShapes && googleMap.hasShapes()) {
        window.TowerScoutLogger.debug('Consuming drawn polygon(s) as search boundary...');
        drawnBoundary();
        return;
      }

      // No shapes yet, enable drawing
      window.TowerScoutLogger.debug('No shapes drawn yet, enabling drawing mode...');
      googleMap.enablePolygonDrawing(context);
      window.TowerScoutLogger.debug('Drawing mode enabled');
      return;
    }

    // Azure Maps: Consume drawn shapes as search boundary, or show instructions
    if (currentProvider === 'azure' && azureMap) {
      if (context === 'search' && azureMap.hasShapes && azureMap.hasShapes()) {
        window.TowerScoutLogger.debug('Consuming drawn polygon(s) as search boundary...');
        drawnBoundary();
      } else {
        const message = context === 'search'
          ? 'Use the drawing tools on the right side of the map to draw a search area. Then click "Custom Shape" again.'
          : 'Use the drawing tools on the right side of the map to draw around towers. Then click "Save Towers" to add detections.';

        TowerScoutErrorHandler.showUserNotification(
          message,
          'info',
          5000
        );
      }
      return;
    }
  }

  // TASK-033: Enable custom drawing mode without auto-consuming shapes
  // This allows user to choose: "Run detection" (search boundary) OR "Add Locations" (manual tower)
  function enableCustomDrawing() {
    enableDrawingForIntent('search');
  }

  function enableManualTowerDrawing() {
    enableDrawingForIntent('manual');
  }

  // Retrieve drawn polygons from current map and add to both providers
  // TASK-039: Enhanced to initiate custom drawing mode for Google Maps
  // TASK-033: Now only called by "Run detection", not by "Custom shape" button
  function drawnBoundary(options = {}) {
    const skipValidation = options.skipValidation === true;

    // Defensive null checks
    if (!currentMap) {
      console.error('currentMap is not initialized');
      TowerScoutErrorHandler.showUserNotification(
        'Map is still initializing. Please wait a moment and try again.',
        'warning'
      );
      return false;
    }

    // TASK-041 Phase 1: Don't require both providers, just work with initialized ones
    window.TowerScoutLogger.debug('using custom boundary polygon(s)');
    if (!skipValidation && currentMap.validateDrawnShapes) {
      const validation = currentMap.validateDrawnShapes({
        showNotification: true,
        label: 'custom shape'
      });

      if (!validation.valid) {
        return false;
      }
    }

    let boundaries = currentMap.retrieveDrawnBoundaries();

    if (!boundaries || boundaries.length === 0) {
      console.warn('No drawn boundaries found');
      TowerScoutErrorHandler.showUserNotification(
        'No custom shapes drawn. Please use the polygon tool to draw a boundary first.',
        'info'
      );
      return false;
    }

    // TASK-041 Phase 1: Add boundaries to initialized providers only
    for (let b of boundaries) {
      if (googleMap && typeof googleMap.addBoundary === 'function') {
        googleMap.addBoundary(b);
      }
      if (azureMap && typeof azureMap.addBoundary === 'function') {
        azureMap.addBoundary(b);
      }
    }

    window.TowerScoutLogger.debug(`Added ${boundaries.length} custom boundary/boundaries`);
    return true;
  }

  // Clear all boundaries from all initialized providers
  function clearBoundaries() {
    // Get current map via provider manager (align with Phase 1 pattern)
    const currentMap = providerManager.getMap();

    // Only require current provider to be initialized (not both)
    if (!currentMap) {
      console.error('Current map provider not initialized');
      TowerScoutErrorHandler.showUserNotification(
        'Map provider is still initializing. Please wait a moment.',
        'warning'
      );
      return;
    }

    window.TowerScoutLogger.debug('Clearing all boundaries');

    // Clear boundaries on initialized providers only (both if available)
    if (googleMap && typeof googleMap.resetBoundaries === 'function') {
      googleMap.resetBoundaries();
    }

    if (azureMap && typeof azureMap.resetBoundaries === 'function') {
      azureMap.resetBoundaries();
    }

    window.TowerScoutLogger.debug('Boundaries cleared');
  }

  // Helper: Convert array of [lng, lat] to Google Maps LatLng objects
  function parseLatLngArray(a) {
    let result = [];
    for (let p of a) {
      result.push({ lat: p[1], lng: p[0] });
    }
    return result;
  }

  // Helper: Calculate bounds for a polygon (Google Maps specific)
  function polyBounds(ps) {
    let bounds = new google.maps.LatLngBounds();

    for (let p of ps) {
      bounds.extend(p);
    }
    return bounds;
  }

  // Export to window for global access (IIFE pattern)
  window.drawnBoundary = drawnBoundary;
  window.enableCustomDrawing = enableCustomDrawing;
  window.enableManualTowerDrawing = enableManualTowerDrawing;
  window.clearBoundaries = clearBoundaries;
  window.parseLatLngArray = parseLatLngArray;
  window.polyBounds = polyBounds;

  window.TowerScoutLogger.debug('PolygonBoundary module loaded');
})();
