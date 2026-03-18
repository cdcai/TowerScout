// TowerScout - Provider Initialization Module
// Handles initialization of Google Maps and Azure Maps providers
// TASK-038 Stage 3: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  // Initialize and add the Google Maps provider
  function initGoogleMap() {
    const gmap = new GoogleMap();

    // TASK-043 Phase 1: Use providerManager to register map instance
    providerManager.setGoogleMap(gmap);

    setMyLocation();

    // TASK-041 Phase 1: Mark Google Maps initialization milestones
    // Style is loaded immediately for Google Maps (synchronous)
    providerManager.markInitialized('google', 'styleLoaded');

    // Drawing manager is created in GoogleMap constructor, so mark as ready
    providerManager.markInitialized('google', 'drawingManagerReady');

    // Update provider manager if Google is the preferred provider
    if (providerManager.currentProvider === 'google' || providerManager.currentProvider === null) {
      providerManager.currentMap = gmap;
      console.log('✅ Google Maps initialized and set as current provider');
    }

    // Initialize provider-aware search system
    initializeProviderAwareSearch();
  }

  // Initialize and add the Azure Maps provider
  async function initAzureMap() {
    console.log('Initializing Azure Maps...');

    let retryCount = 0;
    const maxRetries = CONFIG.MAX_RETRIES;
    const retryDelay = CONFIG.RETRY_DELAY_MS;

    while (retryCount < maxRetries) {
      try {
        // Add timeout wrapper for initialization
        const initWithTimeout = Promise.race([
          (async () => {
            const amap = new AzureMap();
            await amap.initializationPromise;
            return amap;
          })(),
          new Promise((_, reject) =>
            timerManager.setTimeout(() => reject(new Error('Azure Maps initialization timeout')), 30000)
          )
        ]);

        const amap = await initWithTimeout;

        // TASK-043 Phase 1: Use providerManager to register Azure Maps instance
        providerManager.setAzureMap(amap);

        // Validate Azure Maps is properly initialized
        if (!amap || !amap.map || typeof amap.getBounds !== 'function') {
          throw new Error('Azure Maps initialization incomplete - missing required methods');
        }

        // If Azure is selected but currentMap is not set properly, fix it
        if (currentUI && currentUI.value === "azure") {
          console.log('Setting Azure Maps as current map');
          providerManager.currentMap = amap;
        } else if (providerManager.currentProvider === 'azure') {
          console.log('Setting Azure Maps as provider manager current map');
          providerManager.currentMap = amap;
        }

        console.log('✅ Azure Maps initialization complete');
        return amap;

      } catch (error) {
        retryCount++;
        console.error(`❌ Azure Maps initialization failed (attempt ${retryCount}/${maxRetries}):`, error);

        if (retryCount >= maxRetries) {
          // Final failure - use error handler
          TowerScoutErrorHandler.handleProviderError('azure', error, 'Initialization');

          // Clear failed Azure Maps instance - TASK-043: Use providerManager
          azureMap = null;
          providerManager.setAzureMap(null);

          // If this was the only provider, show fatal error
          if (!googleMap) {
            TowerScoutErrorHandler.showFatalError(
              'Failed to initialize any map providers. Please check your internet connection and refresh the page.'
            );
          }

          throw error;
        } else {
          // Wait before retry
          console.log(`⏳ Retrying Azure Maps initialization in ${retryDelay}ms...`);
          await new Promise(resolve => timerManager.setTimeout(resolve, retryDelay));
        }
      }
    }
  }

  // Export to window for global access (IIFE pattern)
  window.initGoogleMap = initGoogleMap;
  window.initAzureMap = initAzureMap;

  console.log('✅ Provider initialization module loaded');
})();

