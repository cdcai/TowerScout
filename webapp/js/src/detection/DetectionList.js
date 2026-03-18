// STAGE 4: DetectionList - UI list rendering and filtering
(function () {
  'use strict';

  /**
   * Adjust detection visibility based on confidence slider and review mode
   * Called when confidence slider changes or review mode toggles
   */
  function adjustConfidence() {
    // Validate DOM elements are available
    if (!confSlider || !reviewCheckBox) {
      console.error('❌ Required DOM elements not initialized for adjustConfidence');
      return;
    }

    providerManager.setMinConfidence(confSlider.value / 100);
    for (let det of providerManager.getDetections()) {
      let meetsInside = reviewCheckBox.checked || det.inside;
      // TASK-043 FIX: Use max confidence from either classifier for filtering
      // This preserves both YOLOv5 and EfficientNet detections while allowing slider to work
      let maxConf = Math.max(det.conf, det.secondary || 0);
      let meetsConf = maxConf >= Detection_minConfidence;

      // TASK-033 Phase 3: Defensive check for firstDet (may be null during restoration)
      if (det.firstDet) {
        let maxAddrConf = Math.max(det.firstDet.maxConf, det.firstDet.maxSecondary || 0);
        let meetsAddrConf = maxAddrConf >= Detection_minConfidence;
        det.firstDet.showAddr(meetsAddrConf && meetsInside);
      }

      det.show(meetsConf && meetsInside);
      det.update();
    }

    const confPercentElement = document.getElementById('confpercent');
    if (confPercentElement) {
      confPercentElement.innerText = confSlider.value;
    }
  }

  /**
   * Toggle between normal mode and review mode
   * Normal mode: Only show detections inside boundary with confidence threshold
   * Review mode: Show all detections in tiles (for comprehensive labeling)
   */
  function changeReviewMode() {
    // Validate DOM elements are available
    if (!reviewCheckBox || !confSlider) {
      console.error('❌ Required DOM elements not initialized for changeReviewMode');
      return;
    }

    const mode = reviewCheckBox.checked ? 'Label' : 'Find';
    console.log(`🔄 Switching review mode to: ${mode}`);

    if (reviewCheckBox.checked) {
      confSlider.value = 0;  // Label mode: show all detections in tiles
    } else {
      confSlider.value = Math.round(DEFAULT_CONFIDENCE * 100);  // Find mode: only inside boundary
    }

    // Adjust confidence filtering (updates list visibility)
    adjustConfidence();

    // FIX NEW-ISSUE-003: Force map visibility update for all detections
    // adjustConfidence() updates the list, but we need to explicitly update map markers
    console.log(`🗺️ Updating map visibility for ${Detection_detections.length} detections`);
    for (let det of Detection_detections) {
      det.update();  // This will correctly show/hide map markers based on new mode
    }

    console.log(`✅ Review mode switched to: ${mode}`);
  }

  /**
   * Update API usage display with geocoding statistics
   */
  function updateApiUsageDisplay() {
    // Update API usage display from session data
    fetch('/api-usage')
      .then(response => response.json())
      .then(data => {
        if (data.geocoding_usage) {
          const usage = data.geocoding_usage;
          const usageElement = document.getElementById('apiUsage');
          if (usageElement) {
            const limited = data.geocoding_limited ? " <span style='color:#f39c12'>(Geocoding rate limit reached)</span>" : "";
            usageElement.innerHTML = `
              <small>
                API Usage: Google ${usage.google_requests || 0}, Azure ${usage.azure_requests || 0}
                (${usage.successful_requests || 0}/${usage.total_requests || 0} successful)${limited}
              </small>
            `;
          }
        }
      })
      .catch(error => {
        console.log('Could not fetch API usage:', error);
      });
  }

  /**
   * Legacy function for post-augmentation processing
   * Maintained for backward compatibility with existing code
   * Addresses now come from server, but this ensures existing callers don't break
   */
  function afterAugment() {
    Detection.sort();
    Detection.generateList();
    adjustConfidence();
  }

  // Expose functions to global scope for inline HTML handlers and legacy code
  window.adjustConfidence = adjustConfidence;
  window.changeReviewMode = changeReviewMode;
  window.updateApiUsageDisplay = updateApiUsageDisplay;
  window.afterAugment = afterAugment;

  console.log('✅ DetectionList module loaded');
})();
