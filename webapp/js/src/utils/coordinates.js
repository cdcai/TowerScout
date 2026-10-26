// STAGE 5: Coordinate Utilities
// Haversine distance calculation and coordinate transformations
(function () {
  'use strict';

  /**
   * Convert degrees to radians
   * @param {number} x - Angle in degrees
   * @returns {number} Angle in radians
   */
  function rad(x) {
    return x * Math.PI / 180;
  }

  /**
   * Calculate Haversine distance between two points
   * @param {Array} p1 - First point [lng, lat]
   * @param {Array} p2 - Second point [lng, lat]
   * @returns {number} Distance in meters
   */
  function getDistance(p1, p2) {
    const R = 6378137; // Earth's mean radius in meters
    const dLat = rad(p2[1] - p1[1]);
    const dLong = rad(p2[0] - p1[0]);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(rad(p1[1])) * Math.cos(rad(p2[1])) *
      Math.sin(dLong / 2) * Math.sin(dLong / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c;
    return d;
  }

  // Expose to window for global access
  window.rad = rad;
  window.getDistance = getDistance;

  window.TowerScoutLogger.debug('✅ Coordinate utilities loaded');
})();
