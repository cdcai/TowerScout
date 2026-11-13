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

  // User input is latitude, longitude; map adapters accept [longitude, latitude].
  function parseCoordinateQuery(query) {
    const text = String(query).trim();
    const number = '[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)';
    const pair = new RegExp(`^(${number})(?:\\s*,\\s*|\\s+)(${number})$`);
    const unwrapped = text.startsWith('(') && text.endsWith(')')
      ? text.slice(1, -1).trim() : text;
    const match = unwrapped.match(pair);
    if (!match) {
      // Keep addresses and ZIP codes on their existing search paths.
      return /^[+\-\d.\s,()]+$/.test(text) && /[,\s]/.test(text)
        ? { error: true } : null;
    }
    const lat = Number(match[1]);
    const lng = Number(match[2]);
    return Number.isFinite(lat) && Number.isFinite(lng)
      && Math.abs(lat) <= 90 && Math.abs(lng) <= 180
      ? { lat, lng } : { error: true };
  }

  function handleCoordinateSearch(query, map) {
    const coordinates = parseCoordinateQuery(query);
    if (!coordinates) return false;
    if (coordinates.error) {
      TowerScoutErrorHandler.showUserNotification(
        'Enter decimal coordinates as latitude, longitude (for example, 40.7128, -74.0060). Latitude must be between -90 and 90; longitude between -180 and 180.',
        'warning', 8000);
      return true;
    }
    map.setCenter([coordinates.lng, coordinates.lat]);
    map.setZoom(17);
    // A prior Azure address marker must not describe the new coordinate location.
    if (map.searchDataSource) map.searchDataSource.clear();
    return true;
  }

  window.CoordinateSearch = { parse: parseCoordinateQuery, handle: handleCoordinateSearch };

  window.TowerScoutLogger.debug('✅ Coordinate utilities loaded');
})();
