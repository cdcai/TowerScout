// Global State Store Module
// Centralized state management for map instances and application state
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Map provider instances
  window.googleMap = null;
  window.azureMap = null;
  window.currentMap = null;

  // ML engine instances (lazy-loaded)
  window.engines = {};

  // UI state tracking
  // Phase 1 (Sprint 03): Migrated to ProviderStateManager
  // Property descriptors in globals.js provide backward compatibility
  // window.currentElement = null;           // Currently selected detection marker
  // window.currentAddrElement = null;       // Currently selected address list item
  // window.isInitializing = true;           // Prevents provider switching during startup

  // Provider manager instance (created in ProviderStateManager.js)
  window.providerManager = null;

  // Manager instances (created in their respective modules)
  window.timerManager = null;
  window.eventManager = null;

  // Detection and Tile state (Stage 4)
  window.Detection_detections = [];
  window.Detection_detectionsAugmented = 0;
  window.Detection_minConfidence = window.DEFAULT_CONFIDENCE || 0.5;
  window.Detection_current = null;

  // REMOVED: window.Tile_tiles = [];  // Phase 2: Now handled by property descriptor in globals.js

  window.TowerScoutLogger.debug('✅ Store module loaded');
})();
