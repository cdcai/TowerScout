// Configuration Module
// Central configuration constants for TowerScout application
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Configuration constants
  // These values control retry logic, timeouts, and performance tuning
  window.CONFIG = {
    // Network retry configuration
    RETRY_DELAY_MS: 2000,                    // Base delay between retry attempts
    MAX_RETRIES: 3,                          // Maximum number of retry attempts

    // Drawing tools initialization
    DRAWING_TOOLS_RETRY_DELAY_MS: 500,       // Delay between drawing manager initialization retries
    DRAWING_TOOLS_MAX_RETRIES: 10,           // Max retries for drawing manager setup

    // Provider switching
    PROVIDER_SWITCH_DELAY_MS: 100,           // Delay to allow provider cleanup before switch
    MAP_VALIDATION_DELAY_MS: 1000,           // Delay for map validation after provider switch

    // UI timing
    ABOUT_SCREEN_DURATION_SEC: 6,            // Duration to display about screen
    PROGRESS_UPDATE_INTERVAL_MS: 100,        // Interval for progress bar updates

    // Performance tuning
    SECS_PER_TILE_DEFAULT: 0.25              // Estimated processing time per tile
  };

  console.log('✅ CONFIG module loaded');
})();
