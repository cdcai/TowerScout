// Global Variables Module
// Central location for all global variable declarations
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Geographic constants
  // The location of a spot in central NYC - default map center
  window.nyc = [-74.00820558171071, 40.71083794970947];

  // Default confidence threshold for detection filtering
  window.DEFAULT_CONFIDENCE = 0.15;

  // DOM element references - initialized after DOM ready
  window.input = null;
  window.upload = null;
  window.detectionsList = null;
  window.confSlider = null;
  window.reviewCheckBox = null;

  // Tile management - global tile array
  // REMOVED: window.Tile_tiles = [];  // Phase 2: Handled by property descriptor below

  // Detection management - global detection arrays and state
  window.Detection_detectionsAugmented = 0;
  window.Detection_current = null;

  // TASK-043 Phase 2: Detection state deprecation with soft migration
  // Provides backward compatibility while encouraging migration to providerManager
  Object.defineProperty(window, 'Detection_detections', {
    get() {
      // Return direct reference for backward compatibility
      // Mutations will still work but are discouraged
      if (window.providerManager) {
        return window.providerManager.getDetectionsArrayDirect();
      }
      return [];
    },
    set(value) {
      console.warn('⚠️ Direct Detection_detections assignment deprecated. Use providerManager.setDetections() instead.');
      if (window.providerManager) {
        window.providerManager.setDetections(value);
      }
    }
  });

  Object.defineProperty(window, 'Detection_minConfidence', {
    get() {
      if (window.providerManager) {
        return window.providerManager.getMinConfidence();
      }
      return window.DEFAULT_CONFIDENCE;
    },
    set(value) {
      console.warn('⚠️ Direct Detection_minConfidence assignment deprecated. Use providerManager.setMinConfidence() instead.');
      if (window.providerManager) {
        window.providerManager.setMinConfidence(value);
      }
    }
  });

  // Backward compatibility properties for currentProvider and currentMap
  // These provide getters/setters that delegate to providerManager
  Object.defineProperty(window, 'currentProvider', {
    get() {
      return window.providerManager ? window.providerManager.getProvider() : null;
    },
    set(value) {
      console.warn('Direct currentProvider assignment deprecated. Use providerManager.switchProvider()');
      // Allow for backward compatibility but log warning
      if (window.providerManager) {
        window.providerManager.currentProvider = value;
      }
    }
  });

  Object.defineProperty(window, 'currentMap', {
    get() {
      return window.providerManager ? window.providerManager.getMap() : null;
    },
    set(value) {
      console.warn('Direct currentMap assignment deprecated. Use providerManager.switchProvider()');
      // Allow for backward compatibility but log warning
      if (window.providerManager) {
        window.providerManager.currentMap = value;
      }
    }
  });

  // TASK-043 Phase 1: Map instance deprecation with soft migration
  // Provides backward compatibility while encouraging migration to providerManager
  Object.defineProperty(window, 'googleMap', {
    get() {
      return window.providerManager ? window.providerManager.getGoogleMap() : null;
    },
    set(value) {
      console.warn('⚠️ Direct window.googleMap assignment deprecated. Use providerManager.setGoogleMap() instead.');
      // Allow for backward compatibility but log warning
      if (window.providerManager) {
        window.providerManager.setGoogleMap(value);
      }
    }
  });

  Object.defineProperty(window, 'azureMap', {
    get() {
      return window.providerManager ? window.providerManager.getAzureMap() : null;
    },
    set(value) {
      console.warn('⚠️ Direct window.azureMap assignment deprecated. Use providerManager.setAzureMap() instead.');
      // Allow for backward compatibility but log warning
      if (window.providerManager) {
        window.providerManager.setAzureMap(value);
      }
    }
  });

  // Phase 1 (Sprint 03): UI state deprecation with soft migration
  // Provides backward compatibility while encouraging migration to providerManager
  Object.defineProperty(window, 'currentElement', {
    get() {
      return window.providerManager ? window.providerManager.getCurrentElement() : null;
    },
    set(value) {
      console.warn('⚠️ Direct window.currentElement assignment deprecated. Use providerManager.setCurrentElement() instead.');
      if (window.providerManager) {
        window.providerManager.setCurrentElement(value);
      }
    }
  });

  Object.defineProperty(window, 'currentAddrElement', {
    get() {
      return window.providerManager ? window.providerManager.getCurrentAddrElement() : null;
    },
    set(value) {
      console.warn('⚠️ Direct window.currentAddrElement assignment deprecated. Use providerManager.setCurrentAddrElement() instead.');
      if (window.providerManager) {
        window.providerManager.setCurrentAddrElement(value);
      }
    }
  });

  Object.defineProperty(window, 'isInitializing', {
    get() {
      return window.providerManager ? window.providerManager.getIsInitializing() : true;
    },
    set(value) {
      console.warn('⚠️ Direct window.isInitializing assignment deprecated. Use providerManager.setIsInitializing() instead.');
      if (window.providerManager) {
        window.providerManager.setIsInitializing(value);
      }
    }
  });

  // Phase 2 (Sprint 03): Tile state deprecation with soft migration  
  // Provides backward compatibility while encouraging migration to providerManager
  Object.defineProperty(window, 'Tile_tiles', {
    get() {
      return window.providerManager ? window.providerManager.getTilesArrayDirect() : [];
    },
    set(value) {
      console.warn('⚠️ Direct Tile_tiles assignment deprecated. Use providerManager.setTiles() instead.');
      if (window.providerManager) {
        window.providerManager.setTiles(value);
      }
    }
  });

  // Initialize DOM references safely after DOM is ready
  window.initializeDOMReferences = function () {
    console.log('🔧 Initializing DOM references...');

    window.input = document.getElementById("search");
    window.upload = document.getElementById("upload_file");
    window.detectionsList = document.getElementById("checkBoxes");
    window.confSlider = document.getElementById("conf");
    window.reviewCheckBox = document.getElementById("review");

    // Validate critical DOM elements exist
    const criticalElements = [
      { element: window.input, name: 'search input' },
      { element: window.confSlider, name: 'confidence slider' },
      { element: window.reviewCheckBox, name: 'review checkbox' }
    ];

    for (const { element, name } of criticalElements) {
      if (!element) {
        console.error(`❌ Critical DOM element missing: ${name}`);
        throw new Error(`Critical DOM element missing: ${name}. Check HTML template.`);
      }
    }

    // FIX NEW-ISSUE-003: Attach event listeners after validation
    // These were missing after code was moved from towerscout.js to globals.js
    window.confSlider.oninput = adjustConfidence;
    window.reviewCheckBox.onchange = changeReviewMode;

    // TASK-033 Phase 4: Browser refresh warning for unsaved manual towers
    window.onbeforeunload = function (e) {
      // Check if manual towers exist (conf=1.0 or idInTile===-1)
      const detections = window.Detection_detections || [];
      const manualTowers = detections.filter(d => d.conf === 1.0 || d.idInTile === -1);

      if (manualTowers.length > 0) {
        const message = `You have ${manualTowers.length} unsaved manual tower${manualTowers.length > 1 ? 's' : ''}. Export your dataset to save them before leaving.`;
        e.returnValue = message; // Chrome/Firefox
        return message; // Safari
      }
    };

    console.log('✅ DOM references initialized');
  };

  // TASK-033 Phase 4: Provider lock/unlock functions
  // Prevents provider switching after detection runs to avoid imagery mismatch
  window.lockProviderSwitching = function () {
    const detections = window.Detection_detections || [];
    const hasDetections = detections.length > 0;

    if (hasDetections) {
      // Disable User Interface radio buttons (form#uis)
      const uisRadios = document.querySelectorAll('form#uis input[type="radio"]');
      uisRadios.forEach(radio => {
        radio.disabled = true;
        radio.title = 'Clear all detections to switch providers. Switching providers with active detections causes imagery mismatch.';
      });

      // Disable Backend map provider radio buttons (form#providers)
      const providerRadios = document.querySelectorAll('form#providers input[type="radio"]');
      providerRadios.forEach(radio => {
        radio.disabled = true;
        radio.title = 'Clear all detections to switch providers. Switching providers with active detections causes imagery mismatch.';
      });

      // Add visual feedback - gray out the labels
      const uisLabels = document.querySelectorAll('form#uis label');
      uisLabels.forEach(label => {
        label.style.color = '#999';
        label.style.cursor = 'not-allowed';
      });

      const providerLabels = document.querySelectorAll('form#providers label');
      providerLabels.forEach(label => {
        label.style.color = '#999';
        label.style.cursor = 'not-allowed';
      });

      console.log('🔒 Provider switching locked (detections present)');
    }
  };

  window.unlockProviderSwitching = function () {
    const detections = window.Detection_detections || [];

    // Only unlock if NO detections remain (ML or manual)
    if (detections.length === 0) {
      // Enable User Interface radio buttons (form#uis)
      const uisRadios = document.querySelectorAll('form#uis input[type="radio"]');
      uisRadios.forEach(radio => {
        radio.disabled = false;
        radio.title = 'Select map provider';
      });

      // Enable Backend map provider radio buttons (form#providers)
      const providerRadios = document.querySelectorAll('form#providers input[type="radio"]');
      providerRadios.forEach(radio => {
        radio.disabled = false;
        radio.title = 'Select backend map provider';
      });

      // Restore label styles
      const uisLabels = document.querySelectorAll('form#uis label');
      uisLabels.forEach(label => {
        label.style.color = '';
        label.style.cursor = '';
      });

      const providerLabels = document.querySelectorAll('form#providers label');
      providerLabels.forEach(label => {
        label.style.color = '';
        label.style.cursor = '';
      });

      console.log('🔓 Provider switching unlocked (no detections)');
    } else {
      console.log(`🔒 Provider switching remains locked (${detections.length} detection(s) present)`);
    }
  };

  console.log('✅ Globals module loaded');
})();
