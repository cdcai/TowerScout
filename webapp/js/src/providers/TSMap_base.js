// TowerScout - TSMap Base Class
// Abstract base class for all map providers
// TASK-038 Stage 3: Extracted from monolithic towerscout.js

(function() {
  'use strict';

class TSMap {
  getBounds() {
    throw new Error("not implemented")
  }

  getBoundsUrl() {
    let b = this.getBounds();
    return [b[3], b[0], b[1], b[2]].join(","); // assemble in google format w, s, e, n
  }

  // TASK-041 Phase 2 Step 2.3: Boundary bounding box calculation
  // Use drawn boundaries instead of viewport for tile generation
  getBoundaryBounds() {
    // If no boundaries drawn, fall back to viewport bounds
    if (!this.boundaries || this.boundaries.length === 0) {
      window.TowerScoutLogger.debug('📍 No boundaries drawn, using viewport bounds');
      return this.getBounds();
    }

    window.TowerScoutLogger.debug(`📐 Calculating bounding box for ${this.boundaries.length} boundary/boundaries`);

    // Calculate bounding box from all boundaries
    let minLng = Infinity, maxLng = -Infinity;
    let minLat = Infinity, maxLat = -Infinity;

    for (let boundary of this.boundaries) {
      if (!boundary.points || boundary.points.length === 0) {
        console.warn('⚠️ Boundary has no points, skipping');
        continue;
      }

      for (let point of boundary.points) {
        const [lng, lat] = point;
        minLng = Math.min(minLng, lng);
        maxLng = Math.max(maxLng, lng);
        minLat = Math.min(minLat, lat);
        maxLat = Math.max(maxLat, lat);
      }
    }

    // Verify we got valid bounds
    if (!isFinite(minLng) || !isFinite(maxLng) || !isFinite(minLat) || !isFinite(maxLat)) {
      console.warn('⚠️ Invalid boundary bounds calculated, falling back to viewport');
      return this.getBounds();
    }

    const bounds = [minLng, maxLat, maxLng, minLat]; // [west, north, east, south]
    window.TowerScoutLogger.debug('✅ Boundary bounding box:', {
      west: minLng.toFixed(6),
      north: maxLat.toFixed(6),
      east: maxLng.toFixed(6),
      south: minLat.toFixed(6)
    });

    return bounds;
  }

  getBoundaryBoundsUrl() {
    let b = this.getBoundaryBounds();
    return [b[3], b[0], b[1], b[2]].join(","); // assemble in google format w, s, e, n
  }

  // Memory Management: Abstract cleanup method - must be implemented by subclasses
  cleanup() {
    throw new Error("cleanup() must be implemented by subclass")
  }

  setCenter() {
    throw new Error("not implemented")
  }

  getCenter() {
    let b = this.getBounds();
    return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
  }

  getCenterUrl() {
    let c = this.getCenter();
    return c[0] + "," + c[1];
  }

  getZoom() {
    throw new Error("not implemented")
  }

  setZoom(z) {
    throw new Error("not implemented")
  }
  fitCenter() {
    throw new Error("not implemented")
  }

  search(place) {
    throw new Error("not implemented")
  }

  makeMapRect(o) {
    throw new Error("not implemented")
  }

  updateMapRect(o) {
    throw new Error("not implemented")
  }

  getBoundariesStr() {
    throw new Error("not implemented")
  }
}

  // Export to window for global access (IIFE pattern)
  window.TSMap = TSMap;

  window.TowerScoutLogger.debug('✅ TSMap base class loaded');
})();
