// TowerScout - CircleBoundary Module
// Handles circle boundary generation and rendering
// TASK-038 Stage 2: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  //
  // boundaries: simple, circle, polygon
  //

  class Boundary {
    constructor(kind) {
      this.kind = kind;
    }

    toString() {
      throw new Error("not implemented");
    }
  }

  class PolygonBoundary extends Boundary {
    constructor(points) {
      super("polygon");
      this.points = points;
    }

    toString() {
      return JSON.stringify(this.points);
    }
  }

  class SimpleBoundary extends PolygonBoundary {
    constructor(bounds) {
      super("simple:" + bounds);
      this.points = [[bounds[0], bounds[1]],
      [bounds[2], bounds[1]],
      [bounds[2], bounds[3]],
      [bounds[0], bounds[3]],
      [bounds[0], bounds[1]]
      ];
    }
  }

  class CircleBoundary extends PolygonBoundary {
    constructor(center, radius) {
      super("circle: " + center + ", " + radius + " m");
      this.isCircle = true; // Flag to identify circle boundaries

      // Use Azure Maps compatible circle generation
      console.log('Generating circle with center:', center, 'radius:', radius);
      this.points = this.generateCircle(center, radius, 64); // Use 64 segments for smooth circle
      console.log('Generated circle with', this.points.length, 'points');
    }

    // Generate circle using proper geographic calculations
    generateCircle(center, radiusMeters, segments = 64) {
      const points = [];
      const earthRadius = 6378137; // Earth radius in meters
      const centerLat = center[1];
      const centerLng = center[0];
      const latRad = centerLat * Math.PI / 180;

      for (let i = 0; i < segments; i++) {
        const angle = (i * 2 * Math.PI) / segments;

        // Calculate offset in degrees
        const latOffset = (radiusMeters * Math.cos(angle)) / earthRadius * (180 / Math.PI);
        const lngOffset = (radiusMeters * Math.sin(angle)) / (earthRadius * Math.cos(latRad)) * (180 / Math.PI);

        const lat = centerLat + latOffset;
        const lng = centerLng + lngOffset;
        points.push([lng, lat]);
      }

      // Close the polygon by adding the first point at the end
      if (points.length > 0) {
        points.push([points[0][0], points[0][1]]);
      }

      return points;
    }
  }

  // UI function for creating circle boundaries from radius input
  function circleBoundary() {
    // TASK-041 Phase 1: Get map via provider manager
    const map = providerManager.getMap();
    const provider = providerManager.getCurrentProvider();

    // TASK-041 Phase 1: Check comprehensive initialization
    if (!providerManager.isFullyInitialized()) {
      console.warn(`⏳ ${provider} is still initializing, please wait...`);
      TowerScoutErrorHandler.showUserNotification(
        'Map is still loading. Please wait a moment and try again.',
        'warning'
      );
      return;
    }

    // Defensive null checks (fallback)
    if (!map) {
      console.error('❌ Map is not available from provider manager');
      TowerScoutErrorHandler.showUserNotification(
        'Map is not available. Please refresh the page.',
        'error'
      );
      return;
    }

    // radius? construct a circle
    let radius = document.getElementById("radius").value;
    if (radius !== "") {
      console.log('🔵 Creating circle with radius:', radius, 'meters');

      // convert to m
      radius = Number(radius);

      if (isNaN(radius) || radius <= 0) {
        console.warn('Invalid radius value:', radius);
        TowerScoutErrorHandler.showUserNotification(
          'Please enter a valid radius (positive number).',
          'warning'
        );
        return;
      }

      // TASK-041 Phase 1: Use map from provider manager
      // make circle - use current map center
      let centerCoords = map.getCenter();
      console.log('🎯 Circle center coordinates:', centerCoords);

      // TASK-041 Phase 2 Step 2.2: Clear previous circles (surgical removal, preserves polygons)
      console.log('🔄 Clearing previous circles before creating new one...');

      // Clear circles from both providers (only if initialized)
      if (googleMap && typeof googleMap.clearCircles === 'function') {
        googleMap.clearCircles();
      }
      if (azureMap && typeof azureMap.clearCircles === 'function') {
        azureMap.clearCircles();
      }

      // Show user feedback
      TowerScoutErrorHandler.showUserNotification('Updating search area...', 'info', 1500);

      // Add new circle
      let circleBoundary = new CircleBoundary(centerCoords, radius);
      console.log('Circle boundary points:', circleBoundary.points.length);
      console.log('Circle boundary sample points:', circleBoundary.points.slice(0, 5));
      console.log('Circle boundary isCircle flag:', circleBoundary.isCircle);

      // Add boundary to initialized providers only
      if (googleMap) {
        googleMap.addBoundary(circleBoundary);
        console.log('After add - Google boundaries:', googleMap.boundaries.length);
      }
      if (azureMap) {
        azureMap.addBoundary(circleBoundary);
        console.log('After add - Azure boundaries:', azureMap.boundaries.length);
        console.log('Azure searchDataSource exists:', !!azureMap.searchDataSource);

        // Check if boundary was actually added to data source
        if (azureMap.searchDataSource) {
          let shapes = azureMap.searchDataSource.getShapes();
          console.log('Total shapes in data source:', shapes.length);
          let boundaryShapes = shapes.filter(s => s.getProperties().type === 'boundary');
          console.log('Boundary shapes in data source:', boundaryShapes.length);
        }
      }

      // DON'T call showBoundaries() to avoid map reset - boundary should render automatically
      console.log('✅ Circle boundary created (should render automatically)');
    } else {
      console.warn('⚠️ No radius value entered');
    }
  }

  // Export to window for global access (IIFE pattern)
  window.Boundary = Boundary;
  window.PolygonBoundary = PolygonBoundary;
  window.SimpleBoundary = SimpleBoundary;
  window.CircleBoundary = CircleBoundary;
  window.circleBoundary = circleBoundary;

  console.log('✅ CircleBoundary module loaded');
})();
