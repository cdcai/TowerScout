// STAGE 5: Export Functions
// CSV, KML, and dataset download functionality
(function () {
  'use strict';

  /**
   * Show user-friendly notification message
   * @param {string} message - Message to display
   * @param {string} type - Type of message: 'error', 'warning', 'success', 'info'
   */
  function showNotification(message, type = 'error') {
    const icon = {
      'error': '❌',
      'warning': '⚠️',
      'success': '✅',
      'info': 'ℹ️'
    }[type] || 'ℹ️';

    alert(`${icon} ${message}`);
    window.TowerScoutLogger.debug(`[${type.toUpperCase()}] ${message}`);
  }

  /**
   * Validate detections array before export
   * @returns {Object} Validation result with status and counts
   */
  function validateDetections() {
    if (!window.Detection_detections || !Array.isArray(window.Detection_detections)) {
      return {
        valid: false,
        error: 'No detection data available. Please run a detection search first.'
      };
    }

    const total = Detection_detections.length;
    if (total === 0) {
      return {
        valid: false,
        error: 'No detections found. Please run a detection search or add manual towers first.'
      };
    }

    const selected = providerManager.getDetections().filter(d => d.selected).length;
    if (selected === 0) {
      return {
        valid: false,
        error: 'No detections are selected. Please select at least one detection by checking the boxes in the detection list.'
      };
    }

    return {
      valid: true,
      total: total,
      selected: selected
    };
  }

  /**
   * Download helper - creates temporary anchor and triggers download
   * @param {string} filename - Name of file to download
   * @param {string} data - File content
   */
  function download(filename, data) {
    try {
      const blob = new Blob([data], { type: 'text/csv' });
      const elem = window.document.createElement('a');
      elem.href = window.URL.createObjectURL(blob);
      elem.download = filename;
      document.body.appendChild(elem);
      elem.click();
      document.body.removeChild(elem);
      window.TowerScoutLogger.debug(`✅ ${filename} downloaded successfully`);
    } catch (error) {
      showNotification(`Failed to download ${filename}: ${error.message}`, 'error');
      throw error;
    }
  }

  /**
   * Download detection results as dataset ZIP
   * Includes selected detections and manual additions in YOLO format
   */
  function download_dataset() {
    window.TowerScoutLogger.debug("📦 Preparing dataset export...");

    // Validate detections exist and are selected
    const validation = validateDetections();
    if (!validation.valid) {
      showNotification(validation.error, 'warning');
      return;
    }

    const include = [];
    const additions = [];
    let skippedManualTowers = 0;

    for (let det of Detection_detections) {
      // Include selected ML detections above threshold
      if (det.idInTile !== -1 && det.conf >= Detection_minConfidence && det.selected) {
        include.push({ 'tile': det.tile, 'detection': det.idInTile, 'id': det.originalId });
      }

      // Include manual towers
      if (det.idInTile === -1) {
        // TASK-033 Phase 3: det.tile stores the tile ID (not array index)
        // Need to find the tile in array by matching its ID
        const tile = Tile_tiles.find(t => t.id === det.tile);

        if (!tile) {
          console.error(`❌ Manual tower references non-existent tile ID: ${det.tile}`);
          skippedManualTowers++;
          continue;
        }

        window.TowerScoutLogger.debug(`🔍 MANUAL TOWER EXPORT: det.tile=${det.tile}, tile.id=${tile.id}, arrayIndex=${Tile_tiles.indexOf(tile)}`);
        additions.push({
          'tile': det.tile,  // Use tile ID (matches backend session tile['index'])
          'centerx': (((det.x1 + det.x2) / 2) - tile.x1) / (tile.x2 - tile.x1),
          'centery': (((det.y1 + det.y2) / 2) - tile.y1) / (tile.y2 - tile.y1),
          'w': (det.x2 - det.x1) / (tile.x2 - tile.x1),
          'h': (det.y1 - det.y2) / (tile.y1 - tile.y2)
        });
      }
    }

    // Check if anything will be exported
    const totalExports = include.length + additions.length;
    if (totalExports === 0) {
      showNotification(
        'No detections meet the export criteria. Please check:\n' +
        '• At least one detection is selected (checked)\n' +
        '• Confidence threshold is not too high\n' +
        '• Detections exist in the detection list',
        'warning'
      );
      return;
    }

    window.TowerScoutLogger.debug(`📦 Dataset export: ${include.length} ML detections, ${additions.length} manual towers`);
    if (additions.length > 0) {
      window.TowerScoutLogger.debug(`   Manual tower tile IDs:`, additions.map(a => a.tile));
    }
    if (skippedManualTowers > 0) {
      console.warn(`⚠️ Skipped ${skippedManualTowers} manual towers with invalid tile references`);
    }

    const formData = new FormData();
    formData.append("include", JSON.stringify(include));
    formData.append("additions", JSON.stringify(additions));

    // Show processing indicator
    window.TowerScoutLogger.debug('⏳ Generating dataset ZIP...');

    fetch("getdataset", { method: 'POST', body: formData })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.blob();
      })
      .then(blob => {
        if (blob.size === 0) {
          throw new Error('Server returned an empty file');
        }

        const elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = "dataset.zip";
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);

        window.TowerScoutLogger.debug(`✅ Dataset downloaded successfully (${(blob.size / 1024).toFixed(1)} KB)`);
        showNotification(
          `Dataset exported successfully!\n${include.length} ML detections + ${additions.length} manual towers`,
          'success'
        );
      })
      .catch(error => {
        console.error("❌ Dataset export failed:", error);
        showNotification(
          `Dataset export failed: ${error.message}\n\n` +
          'Please try again or contact support if the problem persists.',
          'error'
        );
      });
  }

  /**
   * Download detection results as CSV
   * Format: id, selected, inside_boundary, meets_threshold, lat, lng, distance, address, confidence, source
   * TASK-033: Added 'source' column to indicate ML vs Manual detections
   */
  function download_csv() {
    window.TowerScoutLogger.debug("📄 Preparing CSV export...");

    // Validate detections exist
    if (!window.Detection_detections || !Array.isArray(window.Detection_detections)) {
      showNotification('No detection data available. Please run a detection search first.', 'warning');
      return;
    }

    if (Detection_detections.length === 0) {
      showNotification('No detections to export. Please run a detection search or add manual towers first.', 'warning');
      return;
    }

    try {
      let text = "id,selected,inside_boundary,meets threshold,latitude (deg),longitude (deg),distance from center (m),address,confidence,source\n";
      let exportedCount = 0;
      const detections = providerManager.getDetectionsArrayDirect();

      for (let i = 0; i < detections.length; i++) {
        const det = detections[i];

        // Validate detection has required data
        if (!det.getCenter || typeof det.getCenter !== 'function') {
          console.warn(`⚠️ Detection ${i} missing getCenter() method, skipping...`);
          continue;
        }

        // TASK-033: Determine source - Manual towers have idInTile === -1
        const source = (det.idInTile === -1) ? 'Manual' : 'ML';

        text += [
          i,
          det['selected'],
          reviewCheckBox.checked || det.inside,
          det['conf'] >= confSlider.value / 100,
          det.getCenter()[1].toFixed(8),
          det.getCenter()[0].toFixed(8),
          getDistance(det.getCenter(), currentMap.getCenter()).toFixed(1),
          ('"' + (det['address'] || 'Unknown') + '"'),
          det['conf'].toFixed(2),
          source
        ].join(",") + "\n";
        exportedCount++;
      }

      if (exportedCount === 0) {
        showNotification('No valid detections to export.', 'warning');
        return;
      }

      download("detections.csv", text);
      window.TowerScoutLogger.debug(`✅ CSV exported: ${exportedCount} detections`);
      showNotification(`CSV exported successfully: ${exportedCount} detections`, 'success');

    } catch (error) {
      console.error("❌ CSV export failed:", error);
      showNotification(`CSV export failed: ${error.message}`, 'error');
    }
  }

  /**
   * Download detection results as KML for Google Earth
   * Includes styled markers and detection metadata
   */
  function download_kml() {
    window.TowerScoutLogger.debug("🌍 Preparing KML export...");

    // Validate detections exist
    if (!window.Detection_detections || !Array.isArray(window.Detection_detections)) {
      showNotification('No detection data available. Please run a detection search first.', 'warning');
      return;
    }

    if (Detection_detections.length === 0) {
      showNotification('No detections to export. Please run a detection search or add manual towers first.', 'warning');
      return;
    }

    try {
      let text = '<?xml version="1.0" encoding="UTF-8"?>\n';
      text += '<kml xmlns="http://www.opengis.net/kml/2.2">\n';
      text += "  <Document>\n";

      // Add KML styles
      text += "<Style id='icon-1736-0F9D58-normal'><IconStyle><color>ffffa0a0</color><scale>1</scale>";
      text += "<Icon><href>https://maps.google.com/mapfiles/kml/pal4/icon35.png</href></Icon>";
      text += "</IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>\n";

      text += "<Style id='icon-1736-0F9D58-highlight'><IconStyle><color>ffa0a0ff</color><scale>1</scale>";
      text += "<Icon><href>https://maps.google.com/mapfiles/kml/pal4/icon35.png</href></Icon>";
      text += "</IconStyle><LabelStyle><scale>1</scale></LabelStyle></Style>\n";

      text += "<StyleMap id='icon-1736-0F9D58'><Pair><key>normal</key><styleUrl>";
      text += "#icon-1736-0F9D58-normal</styleUrl></Pair><Pair><key>highlight</key>";
      text += "<styleUrl>#icon-1736-0F9D58-highlight</styleUrl></Pair></StyleMap>\n\n";

      text += "<Style id='icon-1736-0F9D58-nodesc-normal'><IconStyle><color>ffffa0a0</color><scale>1</scale>";
      text += "<Icon><href>http://maps.google.com/mapfiles/kml/pal4/icon35.png</href></Icon>";
      text += "</IconStyle><LabelStyle><scale>0</scale></LabelStyle>";
      text += "<BalloonStyle><text><![CDATA[<h3>$[name]</h3>]]></text></BalloonStyle></Style>\n";

      text += "<Style id='icon-1736-0F9D58-nodesc-highlight'><IconStyle><color>ffa0a0ff</color><scale>1</scale>";
      text += "<Icon><href>http://maps.google.com/mapfiles/kml/pal4/icon35.png</href></Icon>";
      text += "</IconStyle><LabelStyle><scale>1</scale></LabelStyle>";
      text += "<BalloonStyle><text><![CDATA[<h3>$[name]</h3>]]></text></BalloonStyle></Style>\n";

      text += "<StyleMap id='icon-1736-0F9D58-nodesc'><Pair><key>normal</key><styleUrl>";
      text += "#icon-1736-0F9D58-nodesc-normal</styleUrl></Pair><Pair><key>highlight</key>";
      text += "<styleUrl>#icon-1736-0F9D58-nodesc-highlight</styleUrl></Pair></StyleMap>\n\n";

      // Add placemarks for each detection
      let exportedCount = 0;
      let skippedCount = 0;

      for (let det of Detection_detections) {
        const inside = reviewCheckBox.checked || det.inside;

        if (det.conf >= Detection_minConfidence && det.selected && inside) {
          // Validate detection has required data
          if (!det.getCenter || typeof det.getCenter !== 'function') {
            console.warn(`⚠️ Detection missing getCenter() method, skipping...`);
            skippedCount++;
            continue;
          }

          text += "    <Placemark>\n";
          text += '      <name>' + (det.address || 'Unknown Location') + '</name>\n';

          const tiles = providerManager.getTilesArrayDirect();
          const tileMeta = (tiles[det.tile] && tiles[det.tile].metadata) ? tiles[det.tile].metadata : '';
          text += '      <description>P(' + det.conf.toFixed(2) + ') at ' + (det.address || 'Unknown') + ' ' + tileMeta + '</description>\n';
          text += "      <styleUrl>#icon-1736-0F9D58</styleUrl>\n";
          text += '      <Point>\n';
          text += '        <altitudeMode>relativeToGround</altitudeMode>\n';
          text += '        <extrude>1</extrude>\n';
          text += '        <coordinates>' + det.getCenter()[0] + ',' + det.getCenter()[1] + ',300</coordinates>\n';
          text += '      </Point>\n';
          text += "    </Placemark>\n";
          exportedCount++;
        }
      }

      text += "  </Document>\n";
      text += '</kml>\n';

      if (exportedCount === 0) {
        showNotification(
          'No detections meet the KML export criteria. Please check:\n' +
          '• At least one detection is selected (checked)\n' +
          '• Confidence threshold setting\n' +
          '• Review mode boundary settings',
          'warning'
        );
        return;
      }

      download("detections.kml", text);
      window.TowerScoutLogger.debug(`✅ KML exported: ${exportedCount} detections${skippedCount > 0 ? ` (${skippedCount} skipped)` : ''}`);
      showNotification(`KML exported successfully: ${exportedCount} detections`, 'success');

    } catch (error) {
      console.error("❌ KML export failed:", error);
      showNotification(`KML export failed: ${error.message}`, 'error');
    }
  }

  // Expose functions to window for inline HTML handlers
  window.download_dataset = download_dataset;
  window.download_csv = download_csv;
  window.download_kml = download_kml;

  window.TowerScoutLogger.debug('✅ Export functions loaded');
})();
