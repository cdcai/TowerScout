// Provider State Manager Module
// Eliminates race conditions and ensures consistent provider switching
// Extracted from monolithic towerscout.js - Stage 1

(function () {
  'use strict';

  // Provider State Manager - Eliminates race conditions and ensures consistent state
  class ProviderStateManager {
    constructor() {
      this.currentProvider = null;
      this.currentMap = null;
      this.switchingInProgress = false;
      this.providerSwitchQueue = Promise.resolve();
      this.initializationPromises = new Map();
      this.isInitializing = true;
      window.TowerScoutLogger.debug('🔧 ProviderStateManager initialized');

      // TASK-041 Phase 1: Initialization state tracking
      this.initializationState = {
        google: { styleLoaded: false, drawingManagerReady: false },
        azure: { styleLoaded: false, drawingManagerReady: false, dataSourceReady: false }
      };

      // TASK-043 Phase 1: Map instance storage with null-safety
      this.googleMapInstance = null;
      this.azureMapInstance = null;
      this.mapStateLock = false; // Simple lock for synchronous map state updates

      // TASK-043 Phase 2: Detection state storage with mutex protection
      this.detectionArray = [];
      this.minConfidence = 0.15; // Default confidence threshold
      this.detectionLock = false; // Mutex for detection array operations

      // TASK-043 Phase 3: Progress timer lifecycle management
      this.progressTimerId = null;
      this.progressActive = false;
      this.progressLock = false;

      // Phase 1 (Sprint 03): UI state management
      this.currentElementRef = null;        // Currently highlighted detection DOM element
      this.currentAddrElementRef = null;    // Currently highlighted address DOM element
      // Note: isInitializing already exists (line 15)

      // Phase 2 (Sprint 03): Tile state management
      this.tileArray = [];      // Tile array for detection processing
      this.tileLock = false;    // Mutex for tile array operations

      // Set initialization complete after initial setup (use setTimeout since timerManager not yet initialized)
      setTimeout(() => {
        this.isInitializing = false;
        window.TowerScoutLogger.debug('🎯 Provider initialization complete');
      }, 3000);
    }

    async switchProvider(targetProvider, mapInstance = null) {
      const switchTask = this.providerSwitchQueue.then(() =>
        this._performProviderSwitch(targetProvider, mapInstance)
      );

      this.providerSwitchQueue = switchTask.catch(error => {
        window.TowerScoutLogger.debug(`Provider switch queue recovered after failure: ${error.message}`);
      });

      return switchTask;
    }

    async _performProviderSwitch(targetProvider, mapInstance = null) {
      if (this.switchingInProgress) {
        throw new Error('Provider switch already in progress');
      }
      window.TowerScoutLogger.debug(`🔄 Switching provider from ${this.currentProvider} to ${targetProvider}`);
      this.switchingInProgress = true;

      // Store current state for rollback
      const rollbackState = {
        provider: this.currentProvider,
        map: this.currentMap
      };

      try {
        // ⭐ MEMORY MANAGEMENT: Cleanup previous provider BEFORE switching
        if (this.currentMap && typeof this.currentMap.cleanup === 'function') {
          window.TowerScoutLogger.debug(`🧹 Cleaning up ${this.currentProvider} before switch...`);
          try {
            this.currentMap.cleanup();
            window.TowerScoutLogger.debug(`✅ ${this.currentProvider} cleanup successful`);
          } catch (cleanupError) {
            console.warn(`⚠️ ${this.currentProvider} cleanup had errors (continuing):`, cleanupError.message);
            // Don't fail the switch due to cleanup errors - log and continue
          }
        }

        // Validate provider availability first
        if (!this.isProviderAvailable(targetProvider) && !mapInstance) {
          throw new Error(`${targetProvider} provider not available or not initialized`);
        }

        // Wait for initialization if needed
        if (targetProvider === 'azure' && (!window.azureMap || window.azureMap.initializationPromise)) {
          window.TowerScoutLogger.debug('🔄 Waiting for Azure Maps initialization...');
          await Promise.race([
            this.ensureAzureInitialized(),
            new Promise((_, reject) =>
              window.timerManager.setTimeout(() => reject(new Error('Azure Maps initialization timeout')), 30000)
            )
          ]);
        }

        // Get target map instance
        const availableMap = targetProvider === 'azure' ? window.azureMap :
          targetProvider === 'google' ? window.googleMap : mapInstance;

        if (!availableMap) {
          throw new Error(`${targetProvider} map instance not available after initialization`);
        }

        // Test basic map functionality before switching
        if (typeof availableMap.getBounds !== 'function') {
          throw new Error(`${targetProvider} map instance invalid - missing required methods`);
        }

        // Additional validation for Azure Maps - ensure map and subscription key are ready
        if (targetProvider === 'azure' && availableMap.map && !availableMap.subscriptionKey) {
          console.warn('⚠️ Azure Maps subscription key not available during switch');
        }

        // Additional validation for Google Maps - ensure map instance is ready  
        if (targetProvider === 'google') {
          window.TowerScoutLogger.debug('🔍 Validating Google Maps instance:', {
            hasMap: !!availableMap.map,
            mapType: availableMap.map ? typeof availableMap.map : 'undefined',
            hasGetCenter: availableMap.map ? typeof availableMap.map.getCenter : 'undefined'
          });

          if (!availableMap.map) {
            throw new Error('Google Maps instance not available');
          }

          // Check if Google Maps is ready - use more forgiving method
          try {
            if (typeof availableMap.map.getCenter === 'function') {
              const center = availableMap.map.getCenter();
              window.TowerScoutLogger.debug('🎯 Google Maps center check:', center);
              // Allow null/undefined center if map just loaded
              if (center === null || center === undefined) {
                console.warn('⚠️ Google Maps center not available yet, but map instance exists - allowing');
              }
            } else {
              console.warn('⚠️ Google Maps getCenter method not available yet - allowing anyway');
            }
          } catch (centerError) {
            console.warn('⚠️ Google Maps center check failed, but continuing:', centerError.message);
            // Don't throw error - allow the switch to proceed
          }
        }

        // Test that the map can actually provide bounds (critical for ML pipeline)
        try {
          window.TowerScoutLogger.debug(`🔍 Testing ${targetProvider} bounds availability...`);
          const testBounds = availableMap.getBounds();
          window.TowerScoutLogger.debug(`📐 ${targetProvider} bounds result:`, testBounds);

          if (!testBounds || testBounds.length !== 4) {
            console.warn(`⚠️ ${targetProvider} bounds test failed, but allowing switch to proceed`);
            // Don't throw error for Google Maps - it might need time to initialize
            if (targetProvider !== 'google') {
              throw new Error(`${targetProvider} map bounds test failed`);
            }
          } else {
            window.TowerScoutLogger.debug(`✅ ${targetProvider} bounds test passed`);
          }
        } catch (boundsError) {
          console.warn(`⚠️ ${targetProvider} bounds error:`, boundsError.message);
          // Be more forgiving for Google Maps bounds errors
          if (targetProvider !== 'google') {
            throw new Error(`${targetProvider} map bounds not available: ${boundsError.message}`);
          } else {
            console.warn('⚠️ Google Maps bounds not ready, but allowing switch to proceed');
          }
        }

        // Atomic state update
        this.currentProvider = targetProvider;
        this.currentMap = availableMap;

        window.TowerScoutLogger.debug(`✅ Provider switched: ${rollbackState.provider} → ${targetProvider}`);

        // ISSUE-002 FIX: Restore provider components after switch (drawing tools, etc.)
        if (typeof availableMap.restore === 'function') {
          try {
            window.TowerScoutLogger.debug(`🔄 Restoring ${targetProvider} components...`);
            availableMap.restore();
            window.TowerScoutLogger.debug(`✅ ${targetProvider} components restored`);
          } catch (restoreError) {
            console.warn(`⚠️ ${targetProvider} restoration had errors (continuing):`, restoreError.message);
            // Don't fail the switch due to restoration errors - log and continue
          }
        } else {
          window.TowerScoutLogger.debug(`ℹ️ ${targetProvider} does not have restoration method (expected for new providers)`);
        }

        // Validate the switch worked
        window.timerManager.setTimeout(() => {
          if (this.currentProvider !== targetProvider) {
            console.warn('⚠️ Provider state inconsistency detected');
          }
        }, 100);

        return true;

      } catch (error) {
        console.error('❌ Provider switch failed:', error);

        // Rollback to previous state
        if (rollbackState.provider && rollbackState.map) {
          window.TowerScoutLogger.debug(`🔄 Rolling back to ${rollbackState.provider}`);
          this.currentProvider = rollbackState.provider;
          this.currentMap = rollbackState.map;
        }

        // Use error handler for consistent error processing
        window.TowerScoutErrorHandler.handleProviderError(targetProvider, error, 'Provider Switch');
        throw error;
      } finally {
        this.switchingInProgress = false;
      }
    }

    runSynchronousStateMutation(lockName, operationName, mutation) {
      if (this[lockName]) {
        throw new Error(`${operationName} already in progress`);
      }

      try {
        this[lockName] = true;
        return mutation();
      } finally {
        this[lockName] = false;
      }
    }

    async ensureAzureInitialized() {
      if (!window.azureMap) {
        window.TowerScoutLogger.debug('🔄 Azure Maps not initialized, initializing...');
        await window.initAzureMap();
      } else if (window.azureMap.initializationPromise) {
        window.TowerScoutLogger.debug('🔄 Waiting for existing Azure Maps initialization...');
        await window.azureMap.initializationPromise;
      }

      if (!window.azureMap) {
        throw new Error('Azure Maps initialization failed');
      }
    }

    getProvider() {
      return this.currentProvider;
    }

    getMap() {
      return this.currentMap;
    }

    // TASK-041 Phase 1: Centralized access method
    getCurrentProvider() {
      return this.currentProvider;
    }

    // TASK-041 Phase 1: Comprehensive initialization check
    isFullyInitialized(provider = this.currentProvider) {
      if (!provider || !this.initializationState[provider]) {
        console.warn('⚠️ Provider not recognized or state missing:', provider);
        return false;
      }

      const state = this.initializationState[provider];

      if (provider === 'azure') {
        const ready = state.styleLoaded && state.drawingManagerReady && state.dataSourceReady;
        if (!ready) {
          window.TowerScoutLogger.debug('🔍 Azure initialization status:', {
            styleLoaded: state.styleLoaded,
            drawingManagerReady: state.drawingManagerReady,
            dataSourceReady: state.dataSourceReady
          });
        }
        return ready;
      } else if (provider === 'google') {
        const ready = state.styleLoaded && state.drawingManagerReady;
        if (!ready) {
          window.TowerScoutLogger.debug('🔍 Google initialization status:', {
            styleLoaded: state.styleLoaded,
            drawingManagerReady: state.drawingManagerReady
          });
        }
        return ready;
      }

      return false;
    }

    // TASK-041 Phase 1: Mark initialization milestones
    markInitialized(provider, milestone) {
      if (this.initializationState[provider]) {
        this.initializationState[provider][milestone] = true;
        window.TowerScoutLogger.debug(`✅ ${provider} - ${milestone} complete`);

        // Check if provider is now fully initialized
        if (this.isFullyInitialized(provider)) {
          window.TowerScoutLogger.debug(`🎉 ${provider} is now fully initialized and ready!`);
        }
      } else {
        console.warn(`⚠️ Attempted to mark milestone for unknown provider: ${provider}`);
      }
    }

    isProviderAvailable(provider) {
      return provider === 'azure' ? !!window.azureMap :
        provider === 'google' ? !!window.googleMap : false;
    }

    isSwitching() {
      return this.switchingInProgress;
    }

    // ========================================
    // TASK-043 Phase 1: Map State Management
    // ========================================

    /**
     * Set Google Maps instance with validation and state tracking
     * @param {GoogleMap} mapInstance - The Google Map instance to store
     * @throws {Error} If mapInstance is invalid
     */
    setGoogleMap(mapInstance) {
      if (!mapInstance) {
        console.warn('⚠️ Attempted to set null Google Maps instance');
        this.googleMapInstance = null;
        return;
      }

      // Validate map instance has required methods
      if (typeof mapInstance.getBounds !== 'function') {
        throw new Error('Invalid Google Maps instance - missing required methods');
      }

      window.TowerScoutLogger.debug('✅ Google Maps instance registered with ProviderStateManager');
      this.googleMapInstance = mapInstance;

      // Update currentMap if Google is the current provider
      if (this.currentProvider === 'google' || this.currentProvider === null) {
        this.currentMap = mapInstance;
      }
    }

    /**
     * Set Azure Maps instance with validation and state tracking
     * @param {AzureMap} mapInstance - The Azure Map instance to store
     * @throws {Error} If mapInstance is invalid
     */
    setAzureMap(mapInstance) {
      if (!mapInstance) {
        console.warn('⚠️ Attempted to set null Azure Maps instance');
        this.azureMapInstance = null;
        return;
      }

      // Validate map instance has required methods
      if (typeof mapInstance.getBounds !== 'function') {
        throw new Error('Invalid Azure Maps instance - missing required methods');
      }

      window.TowerScoutLogger.debug('✅ Azure Maps instance registered with ProviderStateManager');
      this.azureMapInstance = mapInstance;

      // Update currentMap if Azure is the current provider
      if (this.currentProvider === 'azure') {
        this.currentMap = mapInstance;
      }
    }

    /**
     * Get Google Maps instance with null-safety
     * @returns {GoogleMap|null} The Google Map instance or null if not initialized
     */
    getGoogleMap() {
      return this.googleMapInstance;
    }

    /**
     * Get Azure Maps instance with null-safety
     * @returns {AzureMap|null} The Azure Map instance or null if not initialized
     */
    getAzureMap() {
      return this.azureMapInstance;
    }

    /**
     * Set current map with atomic updates to prevent race conditions
     * @param {GoogleMap|AzureMap} mapInstance - The map instance to set as current
     * @param {string} provider - The provider name ('google' or 'azure')
     * @throws {Error} If another update is in progress or mapInstance is invalid
     */
    async setCurrentMapAtomic(mapInstance, provider) {
      return this.runSynchronousStateMutation('mapStateLock', 'Map state update', () => {
        if (!mapInstance) {
          throw new Error('Cannot set null map instance');
        }

        // Validate provider
        if (provider !== 'google' && provider !== 'azure') {
          throw new Error(`Invalid provider: ${provider}`);
        }

        // Atomic state update
        this.currentProvider = provider;
        this.currentMap = mapInstance;

        window.TowerScoutLogger.debug(`🔒 Current map set atomically: ${provider}`);
        return true;
      });
    }

    // ========================================
    // TASK-043 Phase 2: Detection State Management
    // ========================================

    /**
     * Get detections array - returns read-only copy for safe iteration
     * @returns {Array} Read-only copy of detection array
     */
    getDetections() {
      // Return copy to prevent unintended mutations during iteration
      return [...this.detectionArray];
    }

    /**
     * Get detections array length without copying (performance optimization)
     * @returns {number} Number of detections
     */
    getDetectionsLength() {
      return this.detectionArray.length;
    }

    /**
     * Set detections array with validation
     * @param {Array} detections - Array of Detection objects
     * @throws {Error} If detections is not an array
     */
    setDetections(detections) {
      if (!Array.isArray(detections)) {
        throw new Error('Detections must be an array');
      }
      this.detectionArray = detections;
      window.TowerScoutLogger.debug(`✅ Detections array updated: ${detections.length} items`);
    }

    /**
     * Clear detections array with mutex protection
     */
    clearDetections() {
      this.runSynchronousStateMutation('detectionLock', 'Clear detections', () => {
        this.detectionArray.length = 0;
        window.TowerScoutLogger.debug('🧹 Detections array cleared');
      });
    }

    /**
     * Add detection to array with mutex protection
     * @param {Detection} detection - Detection object to add
     */
    addDetection(detection) {
      this.runSynchronousStateMutation('detectionLock', 'Add detection', () => {
        this.detectionArray.push(detection);
      });
    }

    /**
     * Sort detections array with mutex protection to prevent corruption during UI updates
     * @param {Function} compareFn - Optional comparison function for Array.sort()
     */
    sortDetections(compareFn) {
      this.runSynchronousStateMutation('detectionLock', 'Sort detections', () => {
        this.detectionArray.sort(compareFn);
        window.TowerScoutLogger.debug(`🔀 Detections sorted: ${this.detectionArray.length} items`);
      });
    }

    /**
     * Get minimum confidence threshold
     * @returns {number} Confidence threshold (0-1)
     */
    getMinConfidence() {
      return this.minConfidence;
    }

    /**
     * Set minimum confidence threshold with validation
     * @param {number} value - Confidence threshold (must be 0-1)
     * @throws {Error} If value is not in valid range
     */
    setMinConfidence(value) {
      const numValue = parseFloat(value);
      if (isNaN(numValue) || numValue < 0 || numValue > 1) {
        throw new Error('Confidence threshold must be a number between 0 and 1');
      }
      this.minConfidence = numValue;
      window.TowerScoutLogger.debug(`✅ Confidence threshold updated: ${numValue}`);
    }

    /**
     * Direct access to detection array for legacy code (use with caution)
     * @returns {Array} Direct reference to internal detection array
     * @deprecated Use getDetections() for read access, add/remove methods for mutations
     */
    getDetectionsArrayDirect() {
      console.warn('⚠️ Direct array access detected. Consider using getDetections() or mutation methods.');
      return this.detectionArray;
    }

    // ========================================
    // TASK-043 Phase 3: Progress Timer Management
    // ========================================

    /**
     * Start progress timer with state guards to prevent multiple concurrent operations
     * @param {Function} callback - Progress update function to call on interval
     * @param {number} interval - Interval in milliseconds (default: 1000)
     * @returns {number} Timer ID from setInterval
     * @throws {Error} If progress operation already active
     */
    startProgressTimer(callback, interval = 1000) {
      return this.runSynchronousStateMutation('progressLock', 'Start progress timer', () => {
        if (this.progressActive) {
          throw new Error('Progress operation already active. Call stopProgressTimer() first.');
        }

        // Clear any existing timer (safety check)
        if (this.progressTimerId !== null) {
          console.warn('⚠️ Existing progress timer found, clearing...');
          if (window.timerManager && window.timerManager.clearInterval) {
            window.timerManager.clearInterval(this.progressTimerId);
          } else {
            clearInterval(this.progressTimerId);
          }
        }

        // Start new timer - use TimerManager for automatic cleanup tracking
        if (window.timerManager && window.timerManager.setInterval) {
          this.progressTimerId = window.timerManager.setInterval(callback, interval);
          window.TowerScoutLogger.debug(`⏱️ Progress timer started with TimerManager (ID: ${this.progressTimerId})`);
        } else {
          this.progressTimerId = setInterval(callback, interval);
          window.TowerScoutLogger.debug(`⏱️ Progress timer started (ID: ${this.progressTimerId})`);
        }

        this.progressActive = true;
        return this.progressTimerId;
      });
    }

    /**
     * Stop progress timer ensuring cleanup on all exit paths
     */
    stopProgressTimer() {
      this.runSynchronousStateMutation('progressLock', 'Stop progress timer', () => {
        if (this.progressTimerId !== null) {
          // Use TimerManager if available for tracked cleanup
          if (window.timerManager && window.timerManager.clearInterval) {
            window.timerManager.clearInterval(this.progressTimerId);
          } else {
            clearInterval(this.progressTimerId);
          }
          window.TowerScoutLogger.debug(`🛑 Progress timer stopped (ID: ${this.progressTimerId})`);
          this.progressTimerId = null;
        }

        this.progressActive = false;
      });
    }

    /**
     * Check if progress timer is active
     * @returns {boolean} True if progress operation is running
     */
    isProgressActive() {
      return this.progressActive;
    }

    /**
     * Get current progress timer ID (for debugging)
     * @returns {number|null} Timer ID or null if no timer active
     */
    getProgressTimerId() {
      return this.progressTimerId;
    }

    // =============================================================================    // Tile State Management (Phase 2 - Sprint 03)
    // Manages tile array for detection processing and navigation
    // =============================================================================

    /**
     * Get tiles array - returns read-only copy for safe iteration
     * @returns {Array} Read-only copy of tile array
     */
    getTiles() {
      // Return copy to prevent unintended mutations during iteration
      return [...this.tileArray];
    }

    /**
     * Get tiles array length without copying (performance optimization)
     * @returns {number} Number of tiles
     */
    getTilesLength() {
      return this.tileArray.length;
    }

    /**
     * Direct access to tile array for legacy code (use with caution)
     * @returns {Array} Direct reference to internal tile array
     * @deprecated Use getTiles() for read access, add/clear methods for mutations
     */
    getTilesArrayDirect() {
      console.warn('⚠️ Direct tile array access detected. Consider using getTiles() or mutation methods.');
      return this.tileArray;
    }

    /**
     * Set tiles array with validation
     * @param {Array} tiles - Array of Tile objects
     * @throws {Error} If tiles is not an array
     */
    setTiles(tiles) {
      if (!Array.isArray(tiles)) {
        throw new Error('Tiles must be an array');
      }
      this.tileArray = tiles;
      window.TowerScoutLogger.debug(`✅ Tile array updated: ${tiles.length} items`);
    }

    /**
     * Clear tiles array with mutex protection
     */
    clearTiles() {
      this.runSynchronousStateMutation('tileLock', 'Clear tiles', () => {
        this.tileArray.length = 0;
        window.TowerScoutLogger.debug('🧹 Tile array cleared');
      });
    }

    /**
     * Add tile to array with mutex protection
     * @param {Tile} tile - Tile object to add
     */
    addTile(tile) {
      this.runSynchronousStateMutation('tileLock', 'Add tile', () => {
        this.tileArray.push(tile);
      });
    }

    // =============================================================================    // UI State Management (Phase 1 - Sprint 03)
    // Manages currently highlighted detection elements for bidirectional highlighting
    // =============================================================================

    /**
     * Get currently highlighted detection element
     * @returns {HTMLElement|null} DOM element or null if none selected
     */
    getCurrentElement() {
      return this.currentElementRef;
    }

    /**
     * Set currently highlighted detection element
     * @param {HTMLElement|null} element - DOM element to highlight
     */
    setCurrentElement(element) {
      this.currentElementRef = element;
      if (element) {
        window.TowerScoutLogger.debug(`🎯 Current detection element set: ${element.id}`);
      }
    }

    /**
     * Get currently highlighted address element
     * @returns {HTMLElement|null} DOM element or null if none selected
     */
    getCurrentAddrElement() {
      return this.currentAddrElementRef;
    }

    /**
     * Set currently highlighted address element
     * @param {HTMLElement|null} element - DOM element to highlight
     */
    setCurrentAddrElement(element) {
      this.currentAddrElementRef = element;
      if (element) {
        window.TowerScoutLogger.debug(`📍 Current address element set: ${element.id}`);
      }
    }

    /**
     * Clear all UI highlighting (both detection and address elements)
     */
    clearUIHighlighting() {
      if (this.currentElementRef) {
        this.currentElementRef.style.fontWeight = "normal";
        this.currentElementRef.style.textDecoration = "";
      }
      if (this.currentAddrElementRef) {
        this.currentAddrElementRef.style.fontWeight = "normal";
        this.currentAddrElementRef.style.textDecoration = "";
      }
      this.currentElementRef = null;
      this.currentAddrElementRef = null;
      window.TowerScoutLogger.debug(`🧹 UI highlighting cleared`);
    }

    /**
     * Get initialization state (prevents provider switching during startup)
     * @returns {boolean} True if still initializing, false if ready
     */
    getIsInitializing() {
      return this.isInitializing;
    }

    /**
     * Set initialization state
     * @param {boolean} value - Initialization state
     */
    setIsInitializing(value) {
      this.isInitializing = value;
      window.TowerScoutLogger.debug(`🔧 Initialization state: ${value ? 'INITIALIZING' : 'COMPLETE'}`);
    }
  }

  // Create global instance
  window.providerManager = new ProviderStateManager();

  window.TowerScoutLogger.debug('✅ ProviderStateManager module loaded');
})();
