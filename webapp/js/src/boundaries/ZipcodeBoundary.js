// TowerScout - ZipcodeBoundary Module
// Handles zipcode polygon lookup and validation using Census TIGER data
// TASK-038 Stage 2: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  //
  // zipcode lookup
  //

  // Fetch zipcode polygon from backend and display as boundary
  function getZipcodePolygon(z) {
    if (z.startsWith("zipcode ")) {
      z = z.substring(8);
    } else if (z[0] === '"') {
      z = z.substring(1, 6);
    }
    fetch('/getzipcode?zipcode=' + z, { method: "GET" })
      .then(response => response.json())
      .then(response => {
        let polygons = parseZipcodeResult(response);
        if (polygons.length > 0) {
          currentMap.resetBoundaries();
          for (let polygon of polygons) {
            currentMap.addBoundary(new PolygonBoundary(polygon[0]));
          }
          currentMap.showBoundaries();
        }
      })
      .catch(error => {
        console.log(error);
      });
  }

  // Parse GeoJSON response from zipcode lookup
  function parseZipcodeResult(result) {
    if (result['type'] !== 'FeatureCollection') {
      return [];
    }

    let features = result['features'];
    let f = features[0];
    let geom = f['geometry']
    let coords = geom['coordinates'];
    return geom['type'] === 'Polygon' ? [coords] : coords;
  }

  // Export to window for global access (IIFE pattern)
  window.getZipcodePolygon = getZipcodePolygon;
  window.parseZipcodeResult = parseZipcodeResult;

  console.log('✅ ZipcodeBoundary module loaded');
})();
