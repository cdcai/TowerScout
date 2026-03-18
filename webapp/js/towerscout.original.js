// TowerScout
// A tool for identifying cooling towers from satellite and aerial imagery

// TowerScout Team:
// Karen Wong, Gunnar Mein, Thaddeus Segura, Jia Lu
// Licensed under CC-BY-NC-SA-4.0
// (see LICENSE.TXT in the root of the repository for details)

// TowerScout.js
// client-side logic

// Configuration constants
const CONFIG = {
  RETRY_DELAY_MS: 2000,
  MAX_RETRIES: 3,
  DRAWING_TOOLS_RETRY_DELAY_MS: 500,
  DRAWING_TOOLS_MAX_RETRIES: 10,
  PROVIDER_SWITCH_DELAY_MS: 100,
  MAP_VALIDATION_DELAY_MS: 1000,
  ABOUT_SCREEN_DURATION_SEC: 6,
  PROGRESS_UPDATE_INTERVAL_MS: 100,
  SECS_PER_TILE_DEFAULT: 0.25
};

// maps
// The location of a spot in central NYC
const nyc = [-74.00820558171071, 40.71083794970947];

// main state
let googleMap = null;
let azureMap = null;
let currentMap;
let engines = {};
let currentElement = null;
let currentAddrElement = null;
let isInitializing = true; // Flag to prevent provider switching during startup

// Provider State Manager - Eliminates race conditions and ensures consistent state
class ProviderStateManager {
  constructor() {
    this.currentProvider = null;
    this.currentMap = null;
    this.switchingInProgress = false;
    this.initializationPromises = new Map();
    this.isInitializing = true;
    console.log('🔧 ProviderStateManager initialized');

    // TASK-041 Phase 1: Initialization state tracking
    this.initializationState = {
      google: { styleLoaded: false, drawingManagerReady: false },
      azure: { styleLoaded: false, drawingManagerReady: false, dataSourceReady: false }
    };

    // Set initialization complete after initial setup (use setTimeout since timerManager not yet initialized)
    setTimeout(() => {
      this.isInitializing = false;
      console.log('🎯 Provider initialization complete');
    }, 3000);
  }

  async switchProvider(targetProvider, mapInstance = null) {
    if (this.switchingInProgress) {
      console.warn('🚫 Provider switch already in progress, queuing request...');
      // Wait for current switch to complete
      await new Promise(resolve => {
        const checkSwitching = () => {
          if (!this.switchingInProgress) {
            resolve();
          } else {
            timerManager.setTimeout(checkSwitching, 50);
          }
        };
        checkSwitching();
      });
      return;
    }

    console.log(`🔄 Switching provider from ${this.currentProvider} to ${targetProvider}`);
    this.switchingInProgress = true;

    // Store current state for rollback
    const rollbackState = {
      provider: this.currentProvider,
      map: this.currentMap
    };

    try {
      // ⭐ MEMORY MANAGEMENT: Cleanup previous provider BEFORE switching
      if (this.currentMap && typeof this.currentMap.cleanup === 'function') {
        console.log(`🧹 Cleaning up ${this.currentProvider} before switch...`);
        try {
          this.currentMap.cleanup();
          console.log(`✅ ${this.currentProvider} cleanup successful`);
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
      if (targetProvider === 'azure' && (!azureMap || azureMap.initializationPromise)) {
        console.log('🔄 Waiting for Azure Maps initialization...');
        await Promise.race([
          this.ensureAzureInitialized(),
          new Promise((_, reject) =>
            timerManager.setTimeout(() => reject(new Error('Azure Maps initialization timeout')), 30000)
          )
        ]);
      }

      // Get target map instance
      const availableMap = targetProvider === 'azure' ? azureMap :
        targetProvider === 'google' ? googleMap : mapInstance;

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
        console.log('🔍 Validating Google Maps instance:', {
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
            console.log('🎯 Google Maps center check:', center);
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
        console.log(`🔍 Testing ${targetProvider} bounds availability...`);
        const testBounds = availableMap.getBounds();
        console.log(`📐 ${targetProvider} bounds result:`, testBounds);

        if (!testBounds || testBounds.length !== 4) {
          console.warn(`⚠️ ${targetProvider} bounds test failed, but allowing switch to proceed`);
          // Don't throw error for Google Maps - it might need time to initialize
          if (targetProvider !== 'google') {
            throw new Error(`${targetProvider} map bounds test failed`);
          }
        } else {
          console.log(`✅ ${targetProvider} bounds test passed`);
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

      console.log(`✅ Provider switched: ${rollbackState.provider} → ${targetProvider}`);

      // Validate the switch worked
      timerManager.setTimeout(() => {
        if (this.currentProvider !== targetProvider) {
          console.warn('⚠️ Provider state inconsistency detected');
        }
      }, 100);

      return true;

    } catch (error) {
      console.error('❌ Provider switch failed:', error);

      // Rollback to previous state
      if (rollbackState.provider && rollbackState.map) {
        console.log(`🔄 Rolling back to ${rollbackState.provider}`);
        this.currentProvider = rollbackState.provider;
        this.currentMap = rollbackState.map;
      }

      // Use error handler for consistent error processing
      TowerScoutErrorHandler.handleProviderError(targetProvider, error, 'Provider Switch');
      throw error;
    } finally {
      this.switchingInProgress = false;
    }
  }

  async ensureAzureInitialized() {
    if (!azureMap) {
      console.log('🔄 Azure Maps not initialized, initializing...');
      await initAzureMap();
    } else if (azureMap.initializationPromise) {
      console.log('🔄 Waiting for existing Azure Maps initialization...');
      await azureMap.initializationPromise;
    }

    if (!azureMap) {
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
        console.log('🔍 Azure initialization status:', {
          styleLoaded: state.styleLoaded,
          drawingManagerReady: state.drawingManagerReady,
          dataSourceReady: state.dataSourceReady
        });
      }
      return ready;
    } else if (provider === 'google') {
      const ready = state.styleLoaded && state.drawingManagerReady;
      if (!ready) {
        console.log('🔍 Google initialization status:', {
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
      console.log(`✅ ${provider} - ${milestone} complete`);

      // Check if provider is now fully initialized
      if (this.isFullyInitialized(provider)) {
        console.log(`🎉 ${provider} is now fully initialized and ready!`);
      }
    } else {
      console.warn(`⚠️ Attempted to mark milestone for unknown provider: ${provider}`);
    }
  }

  isProviderAvailable(provider) {
    return provider === 'azure' ? !!azureMap :
      provider === 'google' ? !!googleMap : false;
  }

  isSwitching() {
    return this.switchingInProgress;
  }
}

// Global provider manager instance
const providerManager = new ProviderStateManager();

// Timer Management System - Prevents memory leaks from uncleaned timers
class TimerManager {
  constructor() {
    this.timers = new Set();
    this.intervals = new Set();
    console.log('🔧 TimerManager initialized');
  }

  setTimeout(callback, delay, ...args) {
    const timer = setTimeout(() => {
      this.timers.delete(timer);
      callback(...args);
    }, delay);
    this.timers.add(timer);
    return timer;
  }

  setInterval(callback, delay, ...args) {
    const interval = setInterval(() => {
      callback(...args);
    }, delay);
    this.intervals.add(interval);
    return interval;
  }

  clearTimeout(timer) {
    if (this.timers.has(timer)) {
      this.timers.delete(timer);
      clearTimeout(timer);
      return true;
    }
    return false;
  }

  clearInterval(interval) {
    if (this.intervals.has(interval)) {
      this.intervals.delete(interval);
      clearInterval(interval);
      return true;
    }
    return false;
  }

  clearAll() {
    console.log(`🧹 Cleaning up ${this.timers.size} timers and ${this.intervals.size} intervals`);

    this.timers.forEach(timer => clearTimeout(timer));
    this.intervals.forEach(interval => clearInterval(interval));

    this.timers.clear();
    this.intervals.clear();
  }

  getStats() {
    return {
      activeTimers: this.timers.size,
      activeIntervals: this.intervals.size
    };
  }
}

// Global timer manager instance
const timerManager = new TimerManager();

// Event Listener Management - Prevents event listener leaks
class EventListenerManager {
  constructor() {
    this.listeners = new Map();
    console.log('🔧 EventListenerManager initialized');
  }

  addEventListener(element, event, callback, options = {}) {
    if (!element) {
      console.warn('⚠️ Cannot add event listener to null element');
      return null;
    }

    const wrappedCallback = (...args) => {
      try {
        callback(...args);
      } catch (error) {
        console.error('Event listener error:', error);
      }
    };

    element.addEventListener(event, wrappedCallback, options);

    // Store for cleanup
    const key = `${element.tagName || 'WINDOW'}-${event}`;
    if (!this.listeners.has(key)) {
      this.listeners.set(key, []);
    }
    this.listeners.get(key).push({
      element,
      event,
      callback: wrappedCallback,
      options
    });

    return wrappedCallback;
  }

  removeEventListener(element, event, callback) {
    if (!element) return false;

    element.removeEventListener(event, callback);

    // Remove from tracking
    const key = `${element.tagName || 'WINDOW'}-${event}`;
    const eventListeners = this.listeners.get(key);
    if (eventListeners) {
      const index = eventListeners.findIndex(l => l.callback === callback);
      if (index >= 0) {
        eventListeners.splice(index, 1);
        return true;
      }
    }
    return false;
  }

  removeAllListeners(element = null) {
    if (element) {
      // Remove listeners for specific element
      for (const [key, listeners] of this.listeners) {
        const filtered = listeners.filter(l => {
          if (l.element === element) {
            element.removeEventListener(l.event, l.callback, l.options);
            return false;
          }
          return true;
        });
        this.listeners.set(key, filtered);
      }
    } else {
      // Remove all listeners
      for (const [key, listeners] of this.listeners) {
        listeners.forEach(({ element, event, callback, options }) => {
          try {
            element.removeEventListener(event, callback, options);
          } catch (error) {
            console.warn('Failed to remove event listener:', error);
          }
        });
      }
      this.listeners.clear();
    }
  }

  getStats() {
    let totalListeners = 0;
    for (const listeners of this.listeners.values()) {
      totalListeners += listeners.length;
    }
    return {
      listenerTypes: this.listeners.size,
      totalListeners
    };
  }
}

// Global event listener manager
const eventManager = new EventListenerManager();

// Error Boundary System - Comprehensive error handling with graceful degradation
class TowerScoutErrorHandler {
  static setupGlobalErrorHandling() {
    // Catch all unhandled JavaScript errors
    window.addEventListener('error', (e) => {
      console.error('🚨 Global JavaScript error:', e.error);
      this.handleCriticalError(e.error, 'JavaScript Runtime Error');
    });

    // Catch all unhandled promise rejections
    window.addEventListener('unhandledrejection', (e) => {
      console.error('🚨 Unhandled promise rejection:', e.reason);
      this.handleAsyncError(e.reason, 'Promise Rejection');
      e.preventDefault(); // Prevent default browser error display
    });

    console.log('✅ Global error handling initialized');
  }

  static async handleProviderError(provider, error, context = 'Provider Operation') {
    console.error(`❌ ${provider} ${context} error:`, error);

    // Don't attempt automatic fallback from provider switching to prevent circular calls
    if (context === 'Provider Switch') {
      // For provider switch failures, just show error - let switchProvider handle rollback
      this.showUserNotification(`${provider} Maps unavailable. Using previous provider.`, 'warning');
      return false;
    }

    // For other provider errors (not during switching), attempt fallback
    const fallbackProvider = provider === 'azure' ? 'google' : 'azure';

    try {
      // Prevent premature failures during initial map loading
      if (providerManager.isProviderAvailable(fallbackProvider) && !providerManager.isInitializing) {
        console.log(`🔄 Attempting fallback to ${fallbackProvider}...`);
        await providerManager.switchProvider(fallbackProvider);
        this.showUserNotification(`Switched to ${fallbackProvider} Maps due to ${provider} error`, 'warning');
        return true;
      } else if (providerManager.isInitializing) {
        // During initial load, wait for proper initialization
        console.log('⏳ Maps still initializing, delaying error handling...');
        return true;
      } else {
        throw new Error(`No fallback provider available. ${fallbackProvider} not accessible.`);
      }
    } catch (fallbackError) {
      console.error('❌ Provider fallback failed:', fallbackError);
      // Only show fatal error if not during initial load
      if (!providerManager.isInitializing) {
        this.showFatalError(`All map providers failed. Please refresh the page.`);
      }
      return false;
    }
  }

  static handleNetworkError(error, operation = 'Network Operation') {
    console.error(`🌐 Network error during ${operation}:`, error);

    const isOffline = !navigator.onLine;
    const isTimeout = error.name === 'TimeoutError' || error.message.includes('timeout');
    const isRateLimit = error.message.includes('429') || error.message.includes('rate');

    if (isOffline) {
      this.showUserNotification('You appear to be offline. Please check your internet connection.', 'error');
    } else if (isTimeout) {
      this.showUserNotification('Request timed out. The server may be busy, please try again.', 'warning');
    } else if (isRateLimit) {
      this.showUserNotification('Rate limit exceeded. Please wait a moment before trying again.', 'warning');
    } else {
      this.showUserNotification(`Network error: ${error.message || 'Connection failed'}`, 'error');
    }
  }

  static handleCriticalError(error, source = 'Unknown') {
    console.error(`🚨 Critical error from ${source}:`, error);

    const errorMessage = error.message || error.toString() || 'Unknown error occurred';

    // Check if it's a provider-related error
    if (errorMessage.includes('Maps') || errorMessage.includes('provider')) {
      const provider = errorMessage.includes('Azure') ? 'azure' : 'google';
      this.handleProviderError(provider, error, source);
    } else {
      // Generic critical error handling
      this.showUserNotification(`Critical error: ${errorMessage}`, 'error');
    }
  }

  static handleAsyncError(reason, source = 'Async Operation') {
    console.error(`⚡ Async error from ${source}:`, reason);

    // Check if it's a network-related promise rejection
    if (reason && (reason.name === 'TypeError' && reason.message.includes('fetch')) ||
      (typeof reason === 'string' && reason.includes('network'))) {
      this.handleNetworkError(reason, source);
    } else {
      this.handleCriticalError(reason, source);
    }
  }

  static showUserNotification(message, type = 'info') {
    console.log(`📢 User notification [${type}]: ${message}`);

    // Create or update notification element
    let notification = document.getElementById('error-notification');
    if (!notification) {
      notification = document.createElement('div');
      notification.id = 'error-notification';
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 400px;
        padding: 12px 16px;
        border-radius: 4px;
        color: white;
        font-family: Arial, sans-serif;
        font-size: 14px;
        z-index: 10000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: opacity 0.3s ease;
      `;
      document.body.appendChild(notification);
    }

    // Set color based on type
    const colors = {
      info: '#3498db',
      warning: '#f39c12',
      error: '#e74c3c',
      success: '#27ae60'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    notification.style.opacity = '1';
    notification.style.display = 'block';

    // Auto-hide after 5 seconds
    timerManager.setTimeout(() => {
      if (notification) {
        notification.style.opacity = '0';
        timerManager.setTimeout(() => {
          if (notification && notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      }
    }, 5000);
  }

  static showFatalError(message) {
    console.error('💀 Fatal error:', message);

    const fatalDiv = document.getElementById('fatal_div');
    if (fatalDiv) {
      const contentDiv = fatalDiv.querySelector('div');
      if (contentDiv) {
        contentDiv.innerHTML = `
          <h3>Application Error</h3>
          <p>${message}</p>
          <p>Please refresh the page to continue.</p>
          <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px;">Refresh Page</button>
        `;
      }
      fatalDiv.style.display = 'flex';
    }
  }

  static wrapAsyncOperation(operation, operationName = 'Async Operation') {
    return async (...args) => {
      try {
        return await operation(...args);
      } catch (error) {
        this.handleAsyncError(error, operationName);
        throw error; // Re-throw to allow caller to handle if needed
      }
    };
  }

  static wrapNetworkCall(networkCall, operationName = 'Network Call') {
    return async (...args) => {
      try {
        return await networkCall(...args);
      } catch (error) {
        this.handleNetworkError(error, operationName);
        throw error; // Re-throw to allow caller to handle if needed
      }
    };
  }
}

// DOM element validation with error handling
function validateDOMElement(elementId, required = true) {
  try {
    const element = document.getElementById(elementId);

    if (!element) {
      const message = `DOM element '${elementId}' not found`;
      if (required) {
        console.error('❌', message);
        TowerScoutErrorHandler.showUserNotification(
          `Page loading error: Missing ${elementId} element. Please refresh the page.`,
          'error'
        );
        return null;
      } else {
        console.warn('⚠️', message + ' (optional)');
        return null;
      }
    }

    console.log(`✅ DOM element '${elementId}' validated`);
    return element;
  } catch (error) {
    console.error(`❌ Error validating DOM element '${elementId}':`, error);
    if (required) {
      TowerScoutErrorHandler.handleCriticalError(error, `DOM Validation - ${elementId}`);
    }
    return null;
  }
}

// UI state management (keeping separate from provider state)
let currentUI = null;

// Backward compatibility: currentProvider and currentMap as getters/setters
Object.defineProperty(window, 'currentProvider', {
  get() { return providerManager.getProvider(); },
  set(value) {
    console.warn('Direct currentProvider assignment deprecated. Use providerManager.switchProvider()');
    // Allow for backward compatibility but log warning
    providerManager.currentProvider = value;
  }
});

Object.defineProperty(window, 'currentMap', {
  get() { return providerManager.getMap(); },
  set(value) {
    console.warn('Direct currentMap assignment deprecated. Use providerManager.switchProvider()');
    // Allow for backward compatibility but log warning
    providerManager.currentMap = value;
  }
});

// DOM element references - initialized after DOM ready
let input = null;
let upload = null;
let detectionsList = null;
let confSlider = null;
let reviewCheckBox = null;
const DEFAULT_CONFIDENCE = 0.15

// Initialize DOM references safely after DOM is ready
function initializeDOMReferences() {
  console.log('🔧 Initializing DOM references...');

  input = document.getElementById("search");
  upload = document.getElementById("upload_file");
  detectionsList = document.getElementById("checkBoxes");
  confSlider = document.getElementById("conf");
  reviewCheckBox = document.getElementById("review");

  // Validate critical DOM elements exist
  const criticalElements = [
    { element: input, name: 'search input' },
    { element: confSlider, name: 'confidence slider' },
    { element: reviewCheckBox, name: 'review checkbox' }
  ];

  for (const { element, name } of criticalElements) {
    if (!element) {
      console.error(`❌ Critical DOM element missing: ${name}`);
      throw new Error(`Critical DOM element missing: ${name}. Check HTML template.`);
    }
  }

  // Safe to add event listeners now
  confSlider.oninput = adjustConfidence;
  reviewCheckBox.onchange = changeReviewMode;

  console.log('✅ DOM references initialized successfully');
}

// Provider-aware search system

// Global search handler that routes to appropriate provider
function initializeProviderAwareSearch() {
  console.log('Initializing provider-aware search system');

  // Add event listener for search input
  if (input) {
    eventManager.addEventListener(input, 'keypress', function (e) {
      if (e.key === 'Enter') {
        handleGlobalSearch();
      }
    });

    // Also handle programmatic searches
    window.executeSearch = handleGlobalSearch;
  }
}

function handleGlobalSearch() {
  console.log('🔍 Global search triggered');

  // Validate DOM elements are available
  if (!input) {
    console.error('❌ Search input not initialized. DOM not ready?');
    return;
  }

  const query = input.value.trim();
  if (!query) {
    console.log('🚫 Empty search value');
    return;
  }

  console.log(`🔍 Current provider: ${currentProvider}`);
  console.log(`🔍 Azure check result: ${currentProvider === 'azure'}, Google check result: ${currentProvider === 'google'}`);

  // Handle zipcode searches (provider-independent)
  if ((query.length === 5 && !isNaN(query)) ||
    (query.length === 7 && query[0] == '"' && query[6] == '"' && !isNaN(query.substring(1, 6))) ||
    (query.startsWith("zipcode "))) {
    console.log('🏢 Processing zipcode search:', query);
    getZipcodePolygon(query);
    return;
  }

  // Route search based on current provider
  if (currentProvider === 'azure' && azureMap) {
    console.log('🗺️ Routing search to Azure Maps');
    azureMap.getBoundsPolygon(query, null); // No Google place object needed
  } else if (currentProvider === 'google' && googleMap) {
    console.log('🌍 Routing search to Google Maps');

    // Ensure Google Maps is properly initialized before search
    try {
      if (!googleMap.map || !googleMap.map.getCenter) {
        console.warn('⚠️ Google Maps not ready for search, ensuring initialization...');
        throw new Error('Google Maps not ready');
      }

      // Execute the search
      googleMap.getBoundsPolygon(query, null);
    } catch (searchError) {
      console.error('❌ Google Maps search failed:', searchError);
      console.warn('🔄 Attempting to reinitialize Google Maps...');

      // Try to reinitialize Google Maps
      loadGoogleMaps().then(() => {
        console.log('✅ Google Maps reinitialized, retrying search...');
        if (googleMap && googleMap.map) {
          googleMap.getBoundsPolygon(query, null);
        }
      }).catch(initError => {
        console.error('❌ Failed to reinitialize Google Maps:', initError);
        alert('Google Maps search unavailable. Please try switching to Azure Maps.');
      });
    }
  } else {
    console.warn('⚠️ No active map provider for search. Provider:', currentProvider, 'Available maps:', { azure: !!azureMap, google: !!googleMap });

    // Auto-switch to available provider if current one is not ready
    if (azureMap) {
      console.log('🔄 Auto-switching to Azure Maps for search');
      setMap('azure');
      // Retry search with Azure
      setTimeout(() => azureMap.getBoundsPolygon(query, null), 100);
    } else if (googleMap) {
      console.log('🔄 Auto-switching to Google Maps for search');
      setMap('google');
      // Retry search with Google after brief delay
      setTimeout(() => {
        if (googleMap && googleMap.map) {
          googleMap.getBoundsPolygon(query, null);
        }
      }, 100);
    }
  }
}

// About screen variables - Fixed: Declare aboutSecs properly
let aboutOp = 0;
let aboutInterval = 20;
let aboutIncrement = 20;
let aboutTimer = null;
let aboutCurrentTotal = 0;
let aboutSecs = 0;  // CRITICAL FIX: Missing variable declaration

function about(aboutTotal) {
  if (typeof aboutTotal === "undefined") {
    aboutTotal = 6;
  }

  // CRITICAL FIX: Proper dismissal logic instead of acceleration
  if (aboutTotal === 0) {
    // Clear any existing timer
    if (aboutTimer !== null) {
      clearTimeout(aboutTimer);
      aboutTimer = null;
    }
    // Immediate dismissal
    let adiv = document.getElementById("about_div");
    if (adiv) {
      adiv.style.display = "none";
      removeClickDismissHandler();
    }
    return;
  }

  // Clear any existing timer before starting new one
  if (aboutTimer !== null) {
    clearTimeout(aboutTimer);
    aboutTimer = null;
  }

  aboutOp = 1;
  aboutSecs = 0;
  aboutIncrement = 20;
  aboutInterval = 20;
  aboutCurrentTotal = aboutTotal;

  // Add click-to-dismiss functionality
  addClickDismissHandler();

  aboutTimer = timerManager.setTimeout(aboutTimerFunc, aboutInterval, aboutTotal);

  // FAILSAFE: Force dismiss after 10 seconds if something goes wrong
  timerManager.setTimeout(() => {
    const adiv = document.getElementById("about_div");
    if (adiv && adiv.style.display !== "none") {
      console.warn('⚠️ About screen failsafe triggered - forcing dismissal');
      adiv.style.display = "none";
      removeClickDismissHandler();
      if (aboutTimer !== null) {
        clearTimeout(aboutTimer);
        aboutTimer = null;
      }
    }
  }, 10000);
}

function aboutTimerFunc(aboutTotal) {
  let adiv = document.getElementById("about_div");

  let op = aboutOpacity(aboutSecs, aboutTotal)
  //console.log(op, aboutSecs, aboutTotal)
  if (op <= 0 || aboutSecs >= aboutTotal) {
    adiv.style.display = "none";
    removeClickDismissHandler(); // Clean up event listeners
    aboutTimer = null;
    return;
  }

  adiv.style.display = "flex";
  adiv.style.opacity = op;
  aboutSecs += aboutIncrement / 1000;
  aboutTimer = timerManager.setTimeout(aboutTimerFunc, aboutInterval, aboutTotal);
}

function aboutOpacity(secs, total) {
  //return Math.max(0, (total + 1) / total * (1 + 1 / (secs - total)))
  return -1 / Math.pow(secs - (total + 1), 4) + 1;
}

// ENHANCEMENT: Click-to-dismiss functionality for about screen
function addClickDismissHandler() {
  const aboutDiv = document.getElementById("about_div");
  if (aboutDiv && !aboutDiv.hasAttribute('data-click-handler')) {
    eventManager.addEventListener(aboutDiv, 'click', handleAboutClick);
    aboutDiv.setAttribute('data-click-handler', 'true');
    aboutDiv.style.cursor = 'pointer';
  }
}

function removeClickDismissHandler() {
  const aboutDiv = document.getElementById("about_div");
  if (aboutDiv && aboutDiv.hasAttribute('data-click-handler')) {
    eventManager.removeAllListeners(aboutDiv);
    aboutDiv.removeAttribute('data-click-handler');
    aboutDiv.style.cursor = 'default';
  }
}

function handleAboutClick(e) {
  // Only dismiss if clicking the background, not the content
  if (e.target.id === 'about_div') {
    about(0); // Trigger immediate dismissal
  }
}

// Initialize and add the map
function initGoogleMap() {
  googleMap = new GoogleMap();
  setMyLocation();

  // TASK-041 Phase 1: Mark Google Maps initialization milestones
  // Style is loaded immediately for Google Maps (synchronous)
  providerManager.markInitialized('google', 'styleLoaded');

  // Drawing manager is created in GoogleMap constructor, so mark as ready
  providerManager.markInitialized('google', 'drawingManagerReady');

  // Update provider manager if Google is the preferred provider
  if (providerManager.currentProvider === 'google' || providerManager.currentProvider === null) {
    providerManager.currentMap = googleMap;
    currentMap = googleMap;
    console.log('✅ Google Maps initialized and set as current provider');
  }

  // Initialize provider-aware search system
  initializeProviderAwareSearch();
}

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
          azureMap = new AzureMap();
          await azureMap.initializationPromise;
          return azureMap;
        })(),
        new Promise((_, reject) =>
          timerManager.setTimeout(() => reject(new Error('Azure Maps initialization timeout')), 30000)
        )
      ]);

      await initWithTimeout;

      // Validate Azure Maps is properly initialized
      if (!azureMap || !azureMap.map || typeof azureMap.getBounds !== 'function') {
        throw new Error('Azure Maps initialization incomplete - missing required methods');
      }

      // If Azure is selected but currentMap is not set properly, fix it
      if (currentUI && currentUI.value === "azure") {
        console.log('Setting Azure Maps as current map');
        providerManager.currentMap = azureMap;
        currentMap = azureMap;
      } else if (providerManager.currentProvider === 'azure') {
        console.log('Setting Azure Maps as provider manager current map');
        providerManager.currentMap = azureMap;
        currentMap = azureMap;
      }

      console.log('✅ Azure Maps initialization complete');
      return azureMap;

    } catch (error) {
      retryCount++;
      console.error(`❌ Azure Maps initialization failed (attempt ${retryCount}/${maxRetries}):`, error);

      if (retryCount >= maxRetries) {
        // Final failure - use error handler
        TowerScoutErrorHandler.handleProviderError('azure', error, 'Initialization');

        // Clear failed Azure Maps instance
        azureMap = null;

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

//
// Abstract Map base class
//

class TSMap {
  getBounds() {
    throw new Error("not implemented")
  }

  getBoundsUrl() {
    let b = this.getBounds();
    return [b[3], b[0], b[1], b[2]].join(","); // assemble in google format w, s, e, n
  }

  // TASK-041 Phase 2 Step 2.3: Boundary bounding box calculation
  // Use drawn boundaries instead of viewport for tile generation
  getBoundaryBounds() {
    // If no boundaries drawn, fall back to viewport bounds
    if (!this.boundaries || this.boundaries.length === 0) {
      console.log('📍 No boundaries drawn, using viewport bounds');
      return this.getBounds();
    }

    console.log(`📐 Calculating bounding box for ${this.boundaries.length} boundary/boundaries`);

    // Calculate bounding box from all boundaries
    let minLng = Infinity, maxLng = -Infinity;
    let minLat = Infinity, maxLat = -Infinity;

    for (let boundary of this.boundaries) {
      if (!boundary.points || boundary.points.length === 0) {
        console.warn('⚠️ Boundary has no points, skipping');
        continue;
      }

      for (let point of boundary.points) {
        const [lng, lat] = point;
        minLng = Math.min(minLng, lng);
        maxLng = Math.max(maxLng, lng);
        minLat = Math.min(minLat, lat);
        maxLat = Math.max(maxLat, lat);
      }
    }

    // Verify we got valid bounds
    if (!isFinite(minLng) || !isFinite(maxLng) || !isFinite(minLat) || !isFinite(maxLat)) {
      console.warn('⚠️ Invalid boundary bounds calculated, falling back to viewport');
      return this.getBounds();
    }

    const bounds = [minLng, maxLat, maxLng, minLat]; // [west, north, east, south]
    console.log('✅ Boundary bounding box:', {
      west: minLng.toFixed(6),
      north: maxLat.toFixed(6),
      east: maxLng.toFixed(6),
      south: minLat.toFixed(6)
    });

    return bounds;
  }

  getBoundaryBoundsUrl() {
    let b = this.getBoundaryBounds();
    return [b[3], b[0], b[1], b[2]].join(","); // assemble in google format w, s, e, n
  }

  // Memory Management: Abstract cleanup method - must be implemented by subclasses
  cleanup() {
    throw new Error("cleanup() must be implemented by subclass")
  }

  setCenter() {
    throw new Error("not implemented")
  }

  getCenter() {
    let b = this.getBounds();
    return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
  }

  getCenterUrl() {
    let c = this.getCenter();
    return c[0] + "," + c[1];
  }

  getZoom() {
    throw new Error("not implemented")
  }

  setZoom(z) {
    throw new Error("not implemented")
  }
  fitCenter() {
    throw new Error("not implemented")
  }

  search(place) {
    throw new Error("not implemented")
  }

  makeMapRect(o) {
    throw new Error("not implemented")
  }

  updateMapRect(o) {
    throw new Error("not implemented")
  }

  getBoundariesStr() {
    throw new Error("not implemented")
  }
}



//

//
// Azure Maps
//

class AzureMap extends TSMap {
  constructor() {
    super();
    // Check if Azure Maps SDK is available
    if (typeof atlas === 'undefined') {
      throw new Error('Azure Maps SDK not loaded. Please ensure the Azure Maps scripts are loaded before initializing the map.');
    }

    if (typeof atlas.Map === 'undefined') {
      throw new Error('Azure Maps Map class not available. Please check Azure Maps SDK loading.');
    }

    console.log('Azure Maps SDK loaded, initializing with subscription key authentication...');

    this.boundaries = [];
    this.newShapes = [];
    this.drawingManager = null;
    this.searchDataSource = null;
    this.subscriptionKey = null;
    this.map = null; // Will be initialized after getting API key
    this.mapEventListeners = []; // Track map-specific event listeners for cleanup

    // TASK-041 Phase 2 Step 2.1: Track created shapes for explicit cleanup
    this.activeShapes = {
      circles: [],      // Circle boundaries created via circle tool
      polygons: [],     // Polygon boundaries drawn by user
      markers: []       // Future: detection result markers
    };

    this.initializationPromise = this.initializeWithSubscriptionKey();
  }

  async initializeWithSubscriptionKey() {
    try {
      // Fetch Azure Maps subscription key from backend
      console.log('🔑 Fetching Azure Maps subscription key...');
      const response = await fetch('/getazurekey');

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.subscriptionKey) {
        throw new Error('Azure Maps subscription key not available: ' + (data.message || 'Unknown error'));
      }

      this.subscriptionKey = data.subscriptionKey;
      console.log('✅ Azure Maps subscription key loaded, initializing map...');

      // Validate subscription key format
      if (this.subscriptionKey.length < 20 || !this.subscriptionKey.match(/^[A-Za-z0-9\-_]+$/)) {
        console.warn('⚠️ Subscription key format may be invalid:', this.subscriptionKey.substring(0, 8) + '...');
      }

      // Now initialize Azure Maps with proper authentication and error recovery
      this.map = new atlas.Map('azureMap', {
        center: [nyc[0], nyc[1]], // Azure Maps uses [longitude, latitude] order
        zoom: 14,
        maxZoom: 21,
        // Use satellite style for cooling tower detection with fallback
        style: 'satellite',
        authOptions: {
          authType: 'subscriptionKey',
          subscriptionKey: this.subscriptionKey
        },
        // Enable features needed for satellite imagery
        traffic: false,                // Keep traffic disabled for performance
        showBuildingModels: false,     // Disable 3D buildings for performance
        showPointsOfInterest: false,   // Keep POI disabled for cleaner view
        showRoadLabels: false,         // Disable road labels over satellite imagery
        enableAccessibility: false     // Simplify for performance
      });

      // Force resize after map loads to ensure proper container sizing
      this.map.events.addOnce('ready', () => {
        console.log('✅ Azure Maps ready, forcing resize...');

        // Basic container sizing
        const container = document.getElementById('azureMap');
        if (container) {
          container.style.width = '100%';
          container.style.height = '100%';
          container.style.position = 'relative';
        }

        this.map.resize();
        console.log('✅ Azure Maps container resized');

        // Validate style loaded correctly
        this.validateStyleLoading();
      });

      // Add style error recovery
      this.map.events.add('styleimagemissing', (e) => {
        console.warn('⚠️ Azure Maps style image missing:', e);
      });

      console.log('✅ Azure Maps instance created with subscription key authentication');
      return this.setupMapEvents();
    } catch (error) {
      console.error('❌ Azure Maps initialization failed:', error);
      console.error('Azure provider available:', !!aak); // aak is boolean flag

      // Enhanced error reporting
      if (error.message && error.message.includes('401')) {
        console.error('🔑 Authentication Error: Subscription key may be invalid or expired');
      } else if (error.message && error.message.includes('fetch')) {
        console.error('🌐 Network Error: Unable to fetch subscription key from backend');
      }

      throw new Error('Failed to create Azure Maps instance: ' + error.message);
    }
  }

  validateStyleLoading() {
    try {
      // Check if satellite style loaded correctly
      const currentStyle = this.map.getStyle();
      console.log('🗺️ Azure Maps current style:', currentStyle ? currentStyle.name || 'unknown' : 'none');

      if (!currentStyle || currentStyle.name !== 'satellite') {
        console.warn('⚠️ Satellite style may not have loaded correctly, attempting fallback...');

        // Try to switch back to satellite style
        setTimeout(() => {
          try {
            this.map.setStyle('satellite');
            console.log('🔄 Attempted to reload satellite style');
            // TASK-041 Phase 1: Mark style loaded after successful reload
            providerManager.markInitialized('azure', 'styleLoaded');
          } catch (styleError) {
            console.error('❌ Failed to reload satellite style:', styleError);
            console.log('📍 Using default style as fallback');
            // Mark as loaded anyway to not block other operations
            providerManager.markInitialized('azure', 'styleLoaded');
          }
        }, 1000);
      } else {
        console.log('✅ Satellite style loaded successfully');
        // TASK-041 Phase 1: Mark style loaded
        providerManager.markInitialized('azure', 'styleLoaded');
      }
    } catch (validationError) {
      console.warn('⚠️ Style validation error (non-critical):', validationError);
      // Mark as loaded anyway to not block other operations
      providerManager.markInitialized('azure', 'styleLoaded');
    }
  }

  setupMapEvents() {
    // Add error event handling
    this.map.events.add('error', (e) => {
      // Improved error logging to show actual error details
      let errorMsg = 'Unknown error';
      if (e && e.error) {
        if (typeof e.error === 'string') {
          errorMsg = e.error;
        } else if (e.error.message) {
          errorMsg = e.error.message;
        } else {
          try {
            errorMsg = JSON.stringify(e.error, null, 2);
          } catch (jsonError) {
            errorMsg = e.error.toString();
          }
        }
      } else if (e && e.message) {
        errorMsg = e.message;
      }

      console.error('Azure Maps error:', errorMsg);
      console.error('Full error object:', e);

      // Provide helpful error messages for common issues
      if (errorMsg.includes('401') || errorMsg.includes('Unauthorized')) {
        console.error('Authentication Error: Invalid or missing Azure Maps subscription key');
        console.error('Azure provider available:', !!aak); // aak is boolean flag
      } else if (errorMsg.includes('403') || errorMsg.includes('Forbidden')) {
        console.error('Permission Error: Subscription key may not have access to requested service');
      } else if (errorMsg.includes('traffic') || errorMsg.includes('tileset')) {
        console.warn('Service Access Error: Trying fallback configuration...');
        // Could implement fallback logic here
      }
    });

    // Wait for Azure Maps to be ready before initializing drawing tools
    this.map.events.add('ready', () => {
      console.log('Azure Maps ready event fired');

      // Azure Maps already initialized with satellite style
      console.log('Azure Maps initialized with satellite style for optimal detection performance');

      this.initializeDrawingTools();
      this.initializeSearchBox();
      this.initializeAzureSearch();
    });

    // Add view change event for Azure-specific functionality
    this.map.events.add('moveend', () => {
      // Azure Maps doesn't need to bias Google's search box
      // Azure Maps uses native search that auto-biases to current viewport
      console.log('Azure Maps view changed - native search automatically biased');
    });

    return this.map;
  }

  initializeDrawingTools(retryCount = 0) {
    // Check if drawing SDK is available
    if (typeof atlas.drawing === 'undefined') {
      if (retryCount >= CONFIG.DRAWING_TOOLS_MAX_RETRIES) {
        console.error('❌ Azure Maps Drawing SDK failed to load after maximum retries');
        return;
      }
      console.warn(`Azure Maps Drawing SDK not loaded yet, retrying in ${CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS}ms... (attempt ${retryCount + 1}/${CONFIG.DRAWING_TOOLS_MAX_RETRIES})`);
      timerManager.setTimeout(() => this.initializeDrawingTools(retryCount + 1), CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS);
      return;
    }

    if (typeof atlas.drawing.DrawingManager === 'undefined' || typeof atlas.control.DrawingToolbar === 'undefined') {
      if (retryCount >= CONFIG.DRAWING_TOOLS_MAX_RETRIES) {
        console.error('❌ Azure Maps DrawingManager or DrawingToolbar failed to load after maximum retries');
        return;
      }
      console.warn(`Azure Maps DrawingManager or DrawingToolbar not available, retrying in ${CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS}ms... (attempt ${retryCount + 1}/${CONFIG.DRAWING_TOOLS_MAX_RETRIES})`);
      timerManager.setTimeout(() => this.initializeDrawingTools(retryCount + 1), CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS);
      return;
    }

    console.log('Initializing Azure Maps drawing tools...');

    // Create drawing manager with polygon, rectangle, and edit tools
    // TASK-041 Phase 1: Added edit controls for better polygon completion UX
    this.drawingManager = new atlas.drawing.DrawingManager(this.map, {
      toolbar: new atlas.control.DrawingToolbar({
        position: 'top-right',
        style: 'light',
        buttons: ['draw-polygon', 'draw-rectangle', 'edit-geometry'],
        numColumns: 3
      })
    });

    // Listen for drawing completion events
    this.map.events.add('drawingcomplete', this.drawingManager, (drawingCompleteEvent) => {
      console.log('🎨 Azure Maps drawingcomplete event fired');
      let shape = drawingCompleteEvent.data;

      // TASK-041 Phase 1: Defensive check - Azure SDK may pass incomplete shapes during mode changes
      if (!shape || typeof shape.getType !== 'function') {
        console.warn('⚠️ Received incomplete shape from drawing event, ignoring');
        return;
      }

      this.newShapes.push(shape);
      console.log('✅ New Azure Maps shape drawn:', shape.getType());
      console.log('  - Total shapes in newShapes array:', this.newShapes.length);
    });

    // TASK-041 Phase 1: Mark drawing manager ready
    providerManager.markInitialized('azure', 'drawingManagerReady');
    console.log('✅ Azure Maps drawing tools initialized');
  }

  initializeSearchBox() {
    // Create data source for search results
    this.searchDataSource = new atlas.source.DataSource();
    this.map.sources.add(this.searchDataSource);

    // Create data source for detection rectangles
    this.detectionDataSource = new atlas.source.DataSource();
    this.map.sources.add(this.detectionDataSource);

    // TASK-041 Phase 1: Mark data source ready
    providerManager.markInitialized('azure', 'dataSourceReady');
    console.log('✅ Azure Maps data sources initialized');

    // Add layer for search result markers (only for point features, not boundaries)
    this.map.layers.add(new atlas.layer.BubbleLayer(this.searchDataSource, null, {
      strokeColor: 'blue',
      strokeWidth: 2,
      fillColor: 'transparent',
      filter: ['==', ['geometry-type'], 'Point']
    }));

    // Add polygon layer for boundary visualization (transparent fill for clean map view)
    this.map.layers.add(new atlas.layer.PolygonLayer(this.searchDataSource, null, {
      fillColor: 'transparent',
      fillOpacity: 0,
      filter: ['==', ['get', 'type'], 'boundary']
    }));

    // Add line layer for boundary outlines (blue to match Google Maps styling)
    this.map.layers.add(new atlas.layer.LineLayer(this.searchDataSource, null, {
      strokeColor: 'blue',
      strokeWidth: 2,
      filter: ['==', ['get', 'type'], 'boundary']
    }));

    // Add polygon layer for detection rectangles with dynamic styling
    this.detectionPolygonLayer = new atlas.layer.PolygonLayer(this.detectionDataSource, null, {
      fillColor: [
        'case',
        ['has', 'fillColor'], ['get', 'fillColor'],
        'rgba(255, 0, 0, 0.2)' // default
      ],
      fillOpacity: [
        'case',
        ['has', 'opacity'], ['get', 'opacity'],
        0.2 // default
      ]
    });
    this.map.layers.add(this.detectionPolygonLayer);

    // Add line layer for detection rectangle outlines with dynamic styling
    this.detectionLineLayer = new atlas.layer.LineLayer(this.detectionDataSource, null, {
      strokeColor: [
        'case',
        ['has', 'strokeColor'], ['get', 'strokeColor'],
        'rgba(255, 0, 0, 1.0)' // default
      ],
      strokeWidth: 1
    });
    this.map.layers.add(this.detectionLineLayer);

    console.log('✅ Azure Maps: Detection DataSource and layers initialized');

    // Initialize Azure-native search for this provider
    this.initializeAzureSearch();
  }

  initializeAzureSearch() {
    // Prevent duplicate initialization
    if (this.searchInitialized) {
      console.log('⚠️ Azure search already initialized, skipping...');
      return;
    }

    console.log('Initializing Azure-native search system');
    this.searchInitialized = true;

    // Store reference to search input for Azure-specific handling
    this.searchInput = document.getElementById("search");

    // Use already-loaded subscription key from initialization
    if (this.subscriptionKey) {
      console.log('Using pre-loaded Azure Maps subscription key for search');

      // Initialize Azure Maps search with proper authentication
      if (typeof atlas.service !== 'undefined' && typeof atlas.service.SearchURL !== 'undefined') {
        this.searchURL = new atlas.service.SearchURL(atlas.service.MapsURL.newPipeline(
          new atlas.service.SubscriptionKeyCredential(this.subscriptionKey)
        ));
        console.log('Azure Maps Search service initialized with authentication');
      }
    } else {
      console.warn('Azure Maps subscription key not available for search initialization');
    }

    // Disable Google Places autocomplete when Azure is active
    this.disableGooglePlacesWhenActive();
  }

  updateMapAuthentication() {
    // Update map authentication from anonymous to subscription key
    if (this.map && this.subscriptionKey) {
      console.log('Updating Azure Maps authentication to use subscription key');

      // Set authentication for the map instance
      this.map.setAuthenticationOptions({
        authType: 'subscriptionKey',
        subscriptionKey: this.subscriptionKey
      });
    }
  }

  disableGooglePlacesWhenActive() {
    // Critical fix: Disable Google Places SearchBox when Azure is active
    const searchInput = document.getElementById('search');

    // Remove Google Places classes and listeners when Azure is selected
    if (currentProvider === 'azure') {
      console.log('🔧 Completely disabling Google Places for Azure Maps');

      // Remove Google Places autocomplete classes
      searchInput.classList.remove('pac-target-input');

      // Remove Google Places autocomplete attribute
      searchInput.removeAttribute('autocomplete');
      searchInput.setAttribute('autocomplete', 'off');

      // Hide Google Places autocomplete dropdown
      const pacContainer = document.querySelector('.pac-container');
      if (pacContainer) {
        pacContainer.style.display = 'none';
        pacContainer.style.visibility = 'hidden';
      }

      // Clear any existing Google Places listeners
      const newInput = searchInput.cloneNode(true);
      searchInput.parentNode.replaceChild(newInput, searchInput);

      // CRITICAL: Update global input reference to new element
      input = document.getElementById('search');

      // Re-add the Azure Maps event listener to the new input
      eventManager.addEventListener(input, 'keypress', function (e) {
        if (e.key === 'Enter') {
          handleGlobalSearch();
        }
      });

      // Set Azure Maps placeholder
      input.setAttribute('placeholder', 'Search with Azure Maps...');

      console.log('✅ Google Places completely disabled, Azure Maps search active');
    }
  }

  addSearchResultMarker(result) {
    // Add a marker for search results with proper Azure coordinates
    const lng = result.position.lon;
    const lat = result.position.lat;

    // Clear previous search markers
    this.searchDataSource.clear();

    // Create marker using Azure Maps Point with [lng, lat] format
    const searchMarker = new atlas.data.Feature(
      new atlas.data.Point([lng, lat]),
      {
        title: result.address.freeformAddress || 'Search Result',
        description: `${result.address.municipality || ''} ${result.address.countrySubdivision || ''}`.trim(),
        searchResult: true,
        confidence: result.score || 1.0
      }
    );

    this.searchDataSource.add(searchMarker);

    // Log search result details instead of showing popup
    const address = result.address || {};
    console.log('🎯 Search Result Details:', {
      location: address.freeformAddress || 'Search Result',
      municipality: address.municipality || '',
      region: address.countrySubdivision || '',
      confidence: Math.round((result.score || 0) * 100) + '%',
      coordinates: [lng, lat]
    });

    console.log(`Added Azure Maps search marker at [${lng}, ${lat}]`);
    return searchMarker;
  }

  getBounds() {
    // Force map to update camera state before retrieving bounds
    this.map.resize();
    let bounds = this.map.getCamera().bounds;
    return [
      bounds[0], // west
      bounds[3], // north  
      bounds[2], // east
      bounds[1]  // south
    ];
  }

  getCenter() {
    // Get current map center from Azure Maps camera
    const camera = this.map.getCamera();
    const center = camera.center;

    // Ensure we have valid coordinates
    if (!center || !Array.isArray(center) || center.length < 2) {
      console.warn('⚠️ Invalid camera center, using default');
      return [0, 0];
    }

    const result = [center[0], center[1]]; // [lng, lat]
    console.log('🎯 Azure Maps getCenter() - camera center:', center, '→ result:', result);
    return result;
  }

  fitBounds(b) {
    // Convert bounds to Azure Maps format [west, south, east, north]
    this.map.setCamera({
      bounds: [b[0], b[3], b[2], b[1]],
      padding: 50
    });
  }

  setCenter(c) {
    this.map.setCamera({
      center: [c[0], c[1]] // Azure Maps uses [lng, lat]
    });
  }

  getZoom() {
    return this.map.getCamera().zoom;
  }

  setZoom(z) {
    this.map.setCamera({
      zoom: z
    });
  }

  fitCenter() {
    this.fitBounds(this.getBounds());
  }

  async search(place) {
    console.log('Azure Maps search for:', place);

    if (!this.searchURL) {
      console.error('Azure Maps Search service not initialized');
      return;
    }

    try {
      console.log('Performing Azure Maps search...');
      const results = await this.searchURL.searchAddressReverse(
        atlas.service.Aborter.none,
        [0, 0], // This will be replaced with proper query
        {
          query: place,
          limit: 1,
          language: 'en-US'
        }
      );

      if (results && results.results && results.results.length > 0) {
        const result = results.results[0];
        console.log('Azure Maps search result:', result);

        // Add search marker and center map
        this.addSearchResultMarker(result);

        // Center and zoom map to result
        const position = [result.position.lon, result.position.lat];
        this.map.setCamera({
          center: position,
          zoom: 18,
          duration: 1000
        });

        return result;
      } else {
        console.warn('No Azure Maps search results found for:', place);
      }
    } catch (error) {
      console.error('Azure Maps search error:', error);
      throw error;
    }
  }

  biasSearchBox() {
    // Azure Maps does not need to bias Google's SearchBox
    // Azure Maps uses native search that is automatically biased to current viewport
    console.log('Azure Maps search bias not needed - using native Azure search');

    // Optional: Could add Azure-specific search viewport biasing here if needed
    // For now, Azure Maps native search provides proper geographic relevance
  }

  makeMapRect(o, listener) {
    // Create a rectangle overlay for detection results
    // CRITICAL: Azure Maps Polygon expects [longitude, latitude] order
    // TowerScout uses x=longitude, y=latitude, so [o.x1, o.y1] is correct
    let rectangle = new atlas.data.Polygon([[
      [o.x1, o.y1], // top-left: [lng, lat]
      [o.x1, o.y2], // bottom-left: [lng, lat]
      [o.x2, o.y2], // bottom-right: [lng, lat]
      [o.x2, o.y1], // top-right: [lng, lat]
      [o.x1, o.y1]  // close polygon
    ]]);

    // Handle detection ID - may be undefined if called before ID assignment
    const detectionId = (o.id !== undefined) ? o.id : 'pending';

    let feature = new atlas.data.Feature(rectangle, {
      type: 'detection',
      confidence: o.confidence || 0,
      strokeColor: o.color || '#FF0000',
      fillColor: o.fillColor || '#FF0000',
      opacity: o.opacity || 0.2,
      detectionId: detectionId
    });

    // Store reference for later updates
    o.azureFeature = feature;

    // Skip rendering for tiles - they're data objects only, not visual elements
    const isTile = o.classname === 'tile';

    // Add feature to detection data source for rendering (skip tiles)
    if (this.detectionDataSource && !isTile) {
      this.detectionDataSource.add(feature);

      // Calculate box dimensions for debugging coordinate precision
      const widthDeg = Math.abs(o.x2 - o.x1);
      const heightDeg = Math.abs(o.y1 - o.y2);
      const widthMeters = widthDeg * 111320 * Math.cos(o.y1 * Math.PI / 180); // approximate meters
      const heightMeters = heightDeg * 110540; // approximate meters

      console.log(`Added detection ${detectionId} to Azure Maps:`);
      console.log(`  Coordinates: [${o.x1.toFixed(6)}, ${o.y1.toFixed(6)}] to [${o.x2.toFixed(6)}, ${o.y2.toFixed(6)}]`);
      console.log(`  Box size: ${widthMeters.toFixed(1)}m x ${heightMeters.toFixed(1)}m`);

      // Warn if detection is suspiciously small (< 10m)
      if (widthMeters < 10 || heightMeters < 10) {
        console.warn(`⚠️ Detection ${detectionId} is very small (${widthMeters.toFixed(1)}m x ${heightMeters.toFixed(1)}m) - possible coordinate transformation issue`);
      }
    } else if (isTile) {
      console.log(`Tile ${detectionId} created for metadata (not rendered on map)`);
    }

    // Handle click listener if provided
    if (listener) {
      // Azure Maps requires event handling through layer events
      // Store listener reference for future implementation
      feature.properties.clickListener = listener;
    }

    return feature;
  }

  updateMapRect(o, onoff) {
    // Show or hide detection rectangle
    if (!o.azureFeature) return;

    // Skip tiles - they're metadata only, not visual elements
    const isTile = o.classname === 'tile';
    if (isTile) return;

    // Handle detection ID - may be undefined if called before ID assignment
    const detectionId = (o.id !== undefined) ? o.id : 'pending';

    if (onoff) {
      // Add feature to data source if not already present
      if (this.detectionDataSource) {
        const shapes = this.detectionDataSource.getShapes();
        const exists = shapes && shapes.some(s =>
          s.properties && s.properties.detectionId === detectionId
        );
        if (!exists) {
          this.detectionDataSource.add(o.azureFeature);
          console.log(`Showing detection ${detectionId} on Azure Maps`);
        }
      }
    } else {
      // Remove feature from data source
      if (this.detectionDataSource) {
        this.detectionDataSource.remove(o.azureFeature);
        console.log(`Hiding detection ${detectionId} from Azure Maps`);
      }
    }
  }

  colorMapRect(o, color) {
    // Update rectangle color
    if (o.azureFeature && this.detectionDataSource) {
      // Handle detection ID - may be undefined if called before ID assignment
      const detectionId = (o.id !== undefined) ? o.id : 'pending';

      // Determine if detection is selected (green) or unselected (red)
      const isSelected = (color === 'green' ||
        color === '#00FF00' ||
        color.toLowerCase().includes('0, 255, 0') ||
        color.toLowerCase().includes('0,255,0'));

      // Update feature properties with appropriate opacity
      o.azureFeature.properties.strokeColor = color;

      // Selected detections: Higher opacity (0.3) for better visibility
      // Unselected detections: Standard opacity (0.15) - matches constructor
      if (isSelected) {
        o.azureFeature.properties.fillColor = 'rgba(0, 255, 0, 0.3)';
      } else {
        // For unselected, maintain the transparent red fill
        o.azureFeature.properties.fillColor = 'rgba(255, 0, 0, 0.15)';
      }

      // Remove and re-add feature to trigger visual update
      this.detectionDataSource.remove(o.azureFeature);
      this.detectionDataSource.add(o.azureFeature);

      console.log(`Updated detection ${detectionId} color to ${color} (opacity: ${isSelected ? '0.3' : '0.15'})`);
    }
  }

  resetBoundaries() {
    console.log('🧹 Azure Maps: Resetting boundaries...');

    // Use clear-and-rebuild pattern (proven reliable in Step 2.2)
    if (this.searchDataSource) {
      try {
        // Get all shapes from searchDataSource
        const allShapes = this.searchDataSource.getShapes();

        // Filter to keep only non-boundary shapes (like markers)
        const nonBoundaryShapes = allShapes.filter(feature => {
          const props = feature.getProperties();  // Use getProperties() method
          return !(props && props.type === 'boundary');
        });

        const boundaryCount = allShapes.length - nonBoundaryShapes.length;
        console.log(`✅ Removing ${boundaryCount} boundary shapes`);

        // Clear all shapes and re-add non-boundary shapes
        this.searchDataSource.clear();
        if (nonBoundaryShapes.length > 0) {
          this.searchDataSource.add(nonBoundaryShapes);
        }

      } catch (e) {
        console.warn('⚠️ Boundary removal failed, clearing all:', e.message);
        this.searchDataSource.clear();
      }
    }

    // Clear drawing manager's data source (polygons being drawn)
    if (this.drawingManager && this.drawingManager.getSource()) {
      this.drawingManager.getSource().clear();
    }

    // Clear activeShapes tracking
    this.activeShapes.circles = [];
    this.activeShapes.polygons = [];

    // Clear boundary tracking and release references
    if (this.boundaries && this.boundaries.length > 0) {
      const boundaryCount = this.boundaries.length;
      this.boundaries.forEach(b => {
        if (b) {
          b.azureObject = null; // Release reference to enable garbage collection
        }
      });
      console.log(`✅ Cleared ${boundaryCount} boundary references`);
    }
    this.boundaries = [];
    console.log('✅ Azure Maps boundaries reset complete');
  }

  clearCircles() {
    console.log(`🔄 Clearing ${this.activeShapes.circles.length} circle(s) from Azure Maps...`);

    if (this.activeShapes.circles.length === 0) {
      console.log('✅ No circles to clear');
      return;
    }

    // Step 1: Remove circle features from searchDataSource
    if (this.searchDataSource) {
      try {
        // Get all shapes from data source
        const allShapes = this.searchDataSource.getShapes();
        console.log(`  - searchDataSource BEFORE cleanup: ${allShapes.length} total shapes`);

        // Filter to separate circles from other shapes using PROPERTIES (not object references)
        // Object reference matching with .includes() doesn't work reliably with Azure Maps
        const circleShapes = [];
        const nonCircleShapes = [];

        allShapes.forEach(shape => {
          const props = shape.getProperties();
          // Check if this is a circle by looking at properties
          if (props && props.type === 'boundary' && props.isCircle === true) {
            circleShapes.push(shape);
          } else {
            nonCircleShapes.push(shape);
          }
        });

        console.log(`  - Circle shapes found: ${circleShapes.length}`);
        console.log(`  - Non-circle shapes to preserve: ${nonCircleShapes.length}`);

        // Clear entire data source
        this.searchDataSource.clear();
        console.log('  - Cleared all shapes from searchDataSource');

        // Re-add only non-circle shapes
        if (nonCircleShapes.length > 0) {
          this.searchDataSource.add(nonCircleShapes);
          console.log(`  - Re-added ${nonCircleShapes.length} non-circle shape(s)`);
        }

        // Verify final state
        const afterShapes = this.searchDataSource.getShapes();
        console.log(`  - searchDataSource AFTER cleanup: ${afterShapes.length} total shapes`);
        console.log('  - ✅ Circle removal complete');

      } catch (e) {
        console.warn('  - Failed to clear circles:', e.message);
        console.error('  - Error details:', e);
      }
    }

    // Step 2: Also clear from drawing manager's data source (Azure Maps keeps separate sources)
    if (this.drawingManager) {
      try {
        const drawingSource = this.drawingManager.getSource();
        console.log('  - Drawing manager source exists:', !!drawingSource);

        if (drawingSource) {
          // Get all shapes from drawing source and remove circles
          const allShapes = drawingSource.getShapes();
          console.log(`  - Total shapes in drawing source: ${allShapes.length}`);

          const circleShapes = allShapes.filter(shape => {
            const props = shape.getProperties();
            console.log('  - Shape properties:', props);
            return props && props.type === 'boundary' && props.isCircle;
          });

          console.log(`  - Circle shapes found in drawing source: ${circleShapes.length}`);

          if (circleShapes.length > 0) {
            drawingSource.remove(circleShapes);
            console.log(`  - Removed ${circleShapes.length} circle(s) from drawing manager source`);
          } else {
            // If no circles found by properties, try removing ALL shapes and re-add non-circles
            console.log('  - No circles found with properties, trying comprehensive clear...');
            const nonCircleBoundaries = this.boundaries.filter(b => !b.isCircle);

            // Clear everything from drawing source
            drawingSource.clear();
            console.log('  - Cleared all shapes from drawing manager source');

            // Re-add non-circle boundaries if any
            if (nonCircleBoundaries.length > 0) {
              console.log(`  - Re-adding ${nonCircleBoundaries.length} non-circle boundaries`);
            }
          }
        }
      } catch (e) {
        console.warn('  - Failed to clear circles from drawing manager:', e.message);
        console.error('  - Full error:', e);
      }
    }

    // Step 3: Filter circles from boundaries array
    const beforeCount = this.boundaries.length;
    this.boundaries = this.boundaries.filter(b => !b.isCircle);
    const removedCount = beforeCount - this.boundaries.length;
    console.log(`  - Removed ${removedCount} circle boundary reference(s)`);

    // Step 4: Clear tracking array
    const clearedCount = this.activeShapes.circles.length;
    this.activeShapes.circles = [];

    console.log(`✅ Cleared ${clearedCount} circle(s)`);
  }

  addBoundary(b) {
    // Safety check: Ensure searchDataSource is initialized
    if (!this.searchDataSource) {
      console.warn('⚠️ Azure Maps searchDataSource not initialized yet, initializing now');
      // Initialize if not ready (fallback)
      this.searchDataSource = new atlas.source.DataSource();
      this.map.sources.add(this.searchDataSource);

      // Add all the necessary layers since initializeSearchBox wasn't called
      console.log('Adding missing layers for boundary display');

      // Add layer for search result markers (only for point features, not boundaries)
      this.map.layers.add(new atlas.layer.BubbleLayer(this.searchDataSource, null, {
        strokeColor: 'blue',
        strokeWidth: 2,
        fillColor: 'transparent',
        filter: ['==', ['geometry-type'], 'Point']
      }));

      // Add polygon layer for boundary visualization (transparent fill for clean map view)
      this.map.layers.add(new atlas.layer.PolygonLayer(this.searchDataSource, null, {
        fillColor: 'transparent',
        fillOpacity: 0,
        filter: ['==', ['get', 'type'], 'boundary']
      }));

      // Add line layer for boundary outlines (blue to match Google Maps styling)
      this.map.layers.add(new atlas.layer.LineLayer(this.searchDataSource, null, {
        strokeColor: 'blue',
        strokeWidth: 2,
        filter: ['==', ['get', 'type'], 'boundary']
      }));
    }

    // Add boundary polygon to the map
    let coordinates;

    if (b.type === 'simple') {
      // Rectangle boundary: [x1, y1, x2, y2]
      coordinates = [[[b.x1, b.y1], [b.x1, b.y2], [b.x2, b.y2], [b.x2, b.y1], [b.x1, b.y1]]];
    } else {
      // Polygon boundary: array of [lng, lat] pairs
      coordinates = [b.points.concat([b.points[0]])]; // Close the polygon
    }

    let polygon = new atlas.data.Polygon(coordinates);
    let feature = new atlas.data.Feature(polygon, {
      type: 'boundary',
      isCircle: b.isCircle || false  // TASK-041: Mark circles for property-based filtering
    });

    b.azureObject = feature;
    this.searchDataSource.add(feature);
    this.boundaries.push(b);

    // TASK-041 Phase 2 Step 2.2: Track circle boundaries for cleanup
    if (b.isCircle) {
      this.activeShapes.circles.push(feature);
      console.log('  - Tracked circle in activeShapes (total:', this.activeShapes.circles.length + ')');
    }
  }

  hasNonCircleBoundaries() {
    return this.boundaries.some(boundary => !boundary.isCircle);
  }

  showBoundaries() {
    // Fit map to show all boundaries
    if (this.boundaries.length > 0) {
      let allCoordinates = [];
      for (let b of this.boundaries) {
        if (b.azureObject && b.azureObject.geometry) {
          let coords = b.azureObject.geometry.coordinates[0];
          allCoordinates = allCoordinates.concat(coords);
        }
      }

      if (allCoordinates.length > 0) {
        let bounds = atlas.data.BoundingBox.fromData(allCoordinates);
        this.map.setCamera({
          bounds: bounds,
          padding: 100
        });
      }
    }
  }

  retrieveDrawnBoundaries() {
    console.log('🔍 Retrieving drawn boundaries from Azure Maps...');
    console.log('  - newShapes array length:', this.newShapes.length);
    console.log('  - drawingManager exists:', !!this.drawingManager);

    let polys = [];

    // TASK-041 Debug: Check if drawing manager has shapes we didn't capture
    if (this.drawingManager) {
      const source = this.drawingManager.getSource();
      const allShapes = source.getShapes();
      console.log('  - Drawing manager source shapes:', allShapes.length);

      // If we have shapes in drawing manager but not in newShapes, use those
      if (allShapes.length > 0 && this.newShapes.length === 0) {
        console.log('  ⚠️ Found shapes in drawing manager that were not captured in event');
        this.newShapes = allShapes;
      }
    }

    for (let shape of this.newShapes) {
      console.log('  - Processing shape:', shape.getType());
      let geometry = shape.toJson().geometry;

      if (geometry.type === 'Polygon') {
        let coordinates = geometry.coordinates[0];
        let poly = [];
        for (let coord of coordinates) {
          poly.push([coord[0], coord[1]]); // [lng, lat]
        }
        console.log('  ✅ Created PolygonBoundary with', poly.length, 'points');
        polys.push(new PolygonBoundary(poly));
      } else if (geometry.type === 'Rectangle') {
        // Handle rectangle if Azure Maps provides this type
        let coords = geometry.coordinates[0];
        let minLng = Math.min(...coords.map(c => c[0]));
        let maxLng = Math.max(...coords.map(c => c[0]));
        let minLat = Math.min(...coords.map(c => c[1]));
        let maxLat = Math.max(...coords.map(c => c[1]));
        console.log('  ✅ Created SimpleBoundary (rectangle)');
        polys.push(new SimpleBoundary([minLng, maxLat, maxLng, minLat]));
      }
    }

    console.log('📊 Total boundaries retrieved:', polys.length);
    this.clearShapes();
    return polys;
  }

  hasShapes() {
    return this.newShapes.length !== 0;
  }

  addShapes() {
    // Process drawn shapes and add as detections
    let bounds;

    for (let shape of this.newShapes) {
      let geometry = shape.toJson().geometry;

      // Calculate bounds for the shape
      let coordinates = geometry.coordinates[0];
      let lngs = coordinates.map(c => c[0]);
      let lats = coordinates.map(c => c[1]);

      let x1 = Math.min(...lngs);
      let x2 = Math.max(...lngs);
      let y1 = Math.max(...lats);
      let y2 = Math.min(...lats);

      let tileIds = Tile.getTileIds(x1, y1, x2, y2);
      for (let tileId of tileIds) {
        let tile = Tile_tiles[tileId];
        x1 = Math.max(x1, tile.x1);
        x1 = Math.min(x1, tile.x2);
        x2 = Math.max(x2, tile.x1);
        x2 = Math.min(x2, tile.x2);
        y1 = Math.max(y1, tile.y2);
        y1 = Math.min(y1, tile.y1);
        y2 = Math.max(y2, tile.y2);
        y2 = Math.min(y2, tile.y1);

        let det = new Detection(x1, y1, x2, y2,
          'added', 1.0, tileId, -1 /*id_in_tile*/, true, true);
        det.update();
      }
    }

    this.newShapes = [];

    // Turn off drawing mode
    if (this.drawingManager) {
      this.drawingManager.setOptions({ mode: 'idle' });
    }

    Detection.generateList();
    adjustConfidence();
  }

  clearShapes() {
    // Clear all drawn shapes
    for (let shape of this.newShapes) {
      this.drawingManager.getSource().remove(shape);
    }
    this.newShapes = [];

    // Turn off drawing mode
    if (this.drawingManager) {
      this.drawingManager.setOptions({ mode: 'idle' });
    }
  }

  clearAll() {
    this.clearShapes();
    // Remove manually added detections (confidence = 1.0)
    let dets = [];
    for (let det of Detection_detections) {
      if (det.conf !== 1.0) {
        det.id = dets.length;
        dets.push(det);
      }
    }
    Detection_detections = dets;
    Detection.generateList();
  }

  getBoundsPolygon(query, place) {
    // Azure Maps native search integration - NO Google dependency
    this.resetBoundaries();

    console.log("Azure Maps native search for: " + query);

    // Use Azure Maps Search API directly with proper coordinate handling
    this.searchAddress(query).then(searchResults => {
      if (searchResults && searchResults.length > 0) {
        const result = searchResults[0]; // Use the first/best result

        // CRITICAL: Use native Azure Maps coordinates [lng, lat] directly
        const lng = result.position.lon;
        const lat = result.position.lat;

        console.log(`Azure Maps result: ${result.address.freeformAddress} at [${lng}, ${lat}]`);

        // Set map view to the search result using correct Azure coordinates
        console.log('🎯 Centering Azure Maps on search result:', [lng, lat]);
        console.log('🗺️ Map instance available:', !!this.map);

        // Use correct Azure Maps API methods
        if (this.map) {
          // Azure Maps proper centering method
          this.map.setCamera({
            center: [lng, lat],
            zoom: 17,
            type: 'fly',
            duration: 1500
          });

          console.log('🎯 Azure Maps setCamera called with fly animation');
        } else {
          console.error('❌ Azure Maps instance not available for centering');
        }

        // Clear any existing search markers and add new result marker
        const searchMarker = this.addSearchResultMarker(result);

        // USER JOURNEY FIX: Do NOT auto-create boundary on search
        // User should manually define search area using Circle or Polygon tools
        // This matches Google Maps behavior (center only, no auto-boundary)
        console.log('✅ Azure Maps search complete - map centered, no auto-boundary');
        console.log('💡 User can now define search area using Circle or Polygon tools');

        // Final verification of map center using proper Azure Maps methods
        setTimeout(() => {
          if (this.map) {
            try {
              const camera = this.map.getCamera();
              console.log('🔍 Final map state - Center:', camera.center, 'Zoom:', camera.zoom);
              console.log('🎯 Expected center:', [lng, lat]);

              // Verify the centering worked
              const actualCenter = camera.center;
              const expectedLng = lng;
              const expectedLat = lat;

              if (actualCenter && Math.abs(actualCenter[0] - expectedLng) < 0.01 && Math.abs(actualCenter[1] - expectedLat) < 0.01) {
                console.log('✅ Map successfully centered on search result!');
              } else {
                console.log('⚠️ Map centering may not have worked as expected');
              }
            } catch (error) {
              console.error('❌ Error checking map state:', error);
            }
          }
        }, 2000);

        // Note: Google Maps synchronization disabled when Azure is primary provider
        console.log('✅ Azure Maps search completed successfully');
      } else {
        console.warn("Azure Maps search returned no results for: " + query);
        // Show user-friendly message instead of silent fallback
        console.log('🔍 No results found for:', query);
        // Could add a non-intrusive notification here instead of alert
      }
    }).catch(error => {
      console.error("🐛 Azure Maps search error:", error.message || error);
      // Log error instead of showing alert popup
      console.warn('⚠️ Search request failed - this may be a temporary network issue');
    });
  }

  async searchAddress(query) {
    // Azure Maps Search API integration with enhanced error handling
    try {
      console.log('🔍 Azure Maps search request:', query);

      // Clean and prepare query for Azure Maps Search
      const cleanQuery = query.trim();

      // Use server-side proxy for Azure Maps search to protect API keys
      const url = `/api/maps/azure/search?query=${encodeURIComponent(cleanQuery)}&limit=5&countrySet=US`;

      const response = await fetch(url);

      console.log('🌐 Azure search proxy response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Azure search proxy error:', response.status, errorText);

        if (response.status === 401) {
          throw new Error('Azure Maps authentication failed: Invalid subscription key');
        } else if (response.status === 403) {
          throw new Error('Azure Maps access denied: Subscription key lacks search permissions');
        } else if (response.status === 429) {
          throw new Error('Azure Maps rate limit exceeded');
        } else {
          throw new Error(`Azure Maps search failed: ${response.status} - ${errorText}`);
        }
      }

      const data = await response.json();
      console.log('✅ Azure Maps search results:', data.results ? data.results.length : 0, 'results found');

      if (data.results && data.results.length > 0) {
        console.log('📍 First result:', data.results[0].address?.freeformAddress || 'No address');
      }

      return data.results || [];
    } catch (error) {
      console.error('❌ Azure Maps search API error:', error.message || error);
      throw new Error(`Azure Maps search failed: ${error.message || error}`);
    }
  }

  // Memory Management: Cleanup Methods

  cleanupDrawingManager() {
    if (this.drawingManager) {
      console.log('🧹 Cleaning up Azure DrawingManager...');

      // Remove event listeners
      if (this.map && this.map.events) {
        this.map.events.remove('drawingcomplete', this.drawingManager);
      }

      // Clear drawn shapes
      try {
        const source = this.drawingManager.getSource();
        if (source) {
          source.clear();
        }
      } catch (e) {
        console.warn('⚠️ Error clearing drawing source:', e.message);
      }

      // Dispose drawing manager if method exists
      if (typeof this.drawingManager.dispose === 'function') {
        try {
          this.drawingManager.dispose();
        } catch (e) {
          console.warn('⚠️ Error disposing drawing manager:', e.message);
        }
      }

      this.drawingManager = null;
      console.log('✅ Azure DrawingManager cleaned up');
    }
  }

  cleanupMapListeners() {
    if (this.map && this.map.events && this.mapEventListeners.length > 0) {
      console.log(`🧹 Cleaning up ${this.mapEventListeners.length} Azure map listeners...`);

      for (const listener of this.mapEventListeners) {
        try {
          this.map.events.remove(listener.eventType, listener.handler);
        } catch (e) {
          console.warn(`⚠️ Error removing listener ${listener.eventType}:`, e.message);
        }
      }

      this.mapEventListeners = [];
      console.log('✅ Azure map listeners cleaned up');
    }
  }

  cleanupSearch() {
    console.log('🧹 Cleaning up Azure search infrastructure...');

    // Remove search result markers and boundaries
    if (this.searchDataSource) {
      try {
        this.searchDataSource.clear();

        // Remove layers that reference this data source
        if (this.map && this.map.layers) {
          const layers = this.map.layers.getLayers();
          if (layers && Array.isArray(layers)) {
            layers.forEach(layer => {
              try {
                if (layer && typeof layer.getSource === 'function') {
                  const layerSource = layer.getSource();
                  if (layerSource === this.searchDataSource) {
                    this.map.layers.remove(layer);
                  }
                }
              } catch (e) {
                console.warn('⚠️ Error removing layer:', e.message);
              }
            });
          }
        }

        // Remove data source
        if (this.map && this.map.sources) {
          try {
            this.map.sources.remove(this.searchDataSource);
          } catch (e) {
            console.warn('⚠️ Error removing search data source:', e.message);
          }
        }

        this.searchDataSource = null;
      } catch (e) {
        console.warn('⚠️ Error during search cleanup:', e.message);
      }
    }

    // Clear SearchURL and reset initialization flag
    this.searchURL = null;
    this.searchInitialized = false;

    console.log('✅ Azure search infrastructure cleaned up');
  }

  cleanup() {
    console.log('🧹 Starting Azure Maps cleanup...');

    try {
      // 1. Cleanup drawing manager
      this.cleanupDrawingManager();

      // 2. Cleanup map event listeners
      this.cleanupMapListeners();

      // 3. Cleanup search infrastructure
      this.cleanupSearch();

      // 4. Reset boundaries
      this.resetBoundaries();

      // 5. Clear drawn shapes
      if (this.newShapes && this.newShapes.length > 0) {
        this.clearShapes();
      }

      console.log('✅ Azure Maps cleanup complete');
    } catch (error) {
      console.error('❌ Error during Azure Maps cleanup:', error);
      // Don't throw - allow cleanup to complete partially
    }
  }

  getBoundariesStr() {
    let result = [];
    for (let b of this.boundaries) {
      result.push(b.toString());
    }
    return "[" + result.join(",") + "]";
  }
}

//
// Google Maps
//


class GoogleMap extends TSMap {
  constructor() {
    super();
    // make the map 
    this.map = new google.maps.Map(document.getElementById("googleMap"), {
      zoom: 19,
      //center: nyc,
      mapTypeId: google.maps.MapTypeId.SATELLITE, // Start with satellite imagery for detection
      fullscreenControl: false,
      streetViewControl: false,
      scaleControl: true,
      mapTypeControl: false, // Disable map type control to prevent switching away from satellite
      maxZoom: 21,
      tilt: 0,
      styles: [
        {
          featureType: 'poi', // Points of interest
          stylers: [{ visibility: 'off' }]
        },
        {
          featureType: 'transit', // Transit stations
          stylers: [{ visibility: 'off' }]
        },
        {
          featureType: 'administrative.locality', // City labels
          elementType: 'labels',
          stylers: [{ visibility: 'off' }]
        },
        {
          featureType: 'road', // Road labels and lines
          elementType: 'labels',
          stylers: [{ visibility: 'off' }]
        }
      ]
    });
    this.boundaries = [];
    this.mapEventListeners = []; // Track map-specific event listeners for cleanup
    this.drawingManager = new google.maps.drawing.DrawingManager({
      drawingMode: null
    });
    this.newShapes = [];

    // TASK-041 Phase 2 Step 2.1: Track created shapes for explicit cleanup
    this.activeShapes = {
      circles: [],      // Circle boundaries created via circle tool
      polygons: [],     // Polygon boundaries drawn by user
      markers: []       // Future: detection result markers
    };

    // Create the search box and link it to the UI element ONLY if Google is the provider
    if (!this.searchBox) {  // Prevent multiple initializations
      this.searchBox = new google.maps.places.SearchBox(input);
    }

    // Bias the SearchBox results towards current map's viewport.
    this.map.addListener("bounds_changed", () => {
      if (currentProvider === 'google' && this.searchBox) {
        this.searchBox.setBounds(this.map.getBounds());
      }
    });

    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    this.searchBox.addListener("places_changed", () => {
      // Only handle if Google Maps is the current provider
      if (currentProvider !== 'google') {
        console.log('Ignoring Google Places search - not current provider');
        return;
      }

      let i = 0;
      if (input.value !== '"') {
        this.places = this.searchBox.getPlaces();

        if (this.places.length == 0) {
          console.log("No places found.");
          return;
        }
      }

      let p = input.value;
      if ((p.length === 5 && !isNaN(p)) ||
        (p.length === 7 && p[0] == '"' && p[6] == '"' && !isNaN(p.substring(1, 6))) ||
        (p.startsWith("zipcode "))) {
        // special case: zipcode
        getZipcodePolygon(p);
        return;
      }

      // Google Maps handles its own search
      console.log('Google Maps handling search through Places API');
      this.getBoundsPolygon(input.value, this.places[0]);
    });

    this.drawingManager.setOptions({
      drawingMode: null,
      drawingControl: true,
      drawingControlOptions: {
        position: google.maps.ControlPosition.TOP_CENTER,
        drawingModes: [google.maps.drawing.OverlayType.RECTANGLE,
        google.maps.drawing.OverlayType.POLYGON]
      },
      rectangleOptions: {
        strokeColor: 'green',
        strokeWeight: 2,
        fillColor: 'green',
        fillOpacity: 0.1,
        editable: true,
        draggable: true
      }
    });
    this.drawingManager.setMap(this.map);

    google.maps.event.addListener(this.drawingManager, 'rectanglecomplete', function (rect) {
      googleMap.newShapes.push(rect);
      console.log("new rectangle: " + rect.bounds.toString());
    });

    google.maps.event.addListener(this.drawingManager, 'polygoncomplete', function (poly) {
      googleMap.newShapes.push(poly);
      console.log("new polygon:");
      // let path = poly.getPath();
      // path.forEach((e,i)=>{console.log(" "+e.lng()+","+e.lat())})
    });

    // TASK-041 Phase 1: Initialization milestones marked in initGoogleMap()
    // after constructor completes (styleLoaded, drawingManagerReady)

  }

  retrieveDrawnBoundaries() {
    let polys = [];

    for (let s of this.newShapes) {
      if (typeof s.bounds !== "undefined") {
        // rectangles have bounds
        let ne = s.bounds.getNorthEast();
        let sw = s.bounds.getSouthWest();
        polys.push(new SimpleBoundary([sw.lng(), ne.lat(), ne.lng(), sw.lat()]));
      } else {
        // polygons do not
        let poly = [];
        s.getPath().forEach((e, i) => { poly.push([e.lng(), e.lat()]); });
        polys.push(new PolygonBoundary(poly));
      }
    }
    this.clearShapes()
    return polys;
  }

  hasShapes() {
    return this.newShapes.length !== 0;
  }

  addShapes() {
    let bounds;

    for (let s of this.newShapes) {
      if (typeof s.bounds === "undefined") {
        bounds = new google.maps.LatLngBounds();
        s.getPath().forEach((e) => {
          bounds = bounds.extend(e);
        });
      } else {
        bounds = s.bounds;
      }
      s.setMap(null);

      let x1 = bounds.getSouthWest().lng();
      let y1 = bounds.getNorthEast().lat();
      let x2 = bounds.getNorthEast().lng();
      let y2 = bounds.getSouthWest().lat();

      let tileIds = Tile.getTileIds(x1, y1, x2, y2);
      for (let tileId of tileIds) {
        let tile = Tile_tiles[tileId]
        x1 = Math.max(x1, tile.x1);
        x1 = Math.min(x1, tile.x2);
        x2 = Math.max(x2, tile.x1);
        x2 = Math.min(x2, tile.x2);
        y1 = Math.max(y1, tile.y2);
        y1 = Math.min(y1, tile.y1);
        y2 = Math.max(y2, tile.y2);
        y2 = Math.min(y2, tile.y1);
        let det = new Detection(x1, y1, x2, y2,
          'added', 1.0, tileId, -1 /*id_in_tile*/, true, true);
        det.update();
      }
    }
    this.newShapes = [];
    this.drawingManager.setDrawingMode(null);

    Detection.generateList();
    adjustConfidence();
  }

  clearShapes() {
    for (let rect of this.newShapes) {
      rect.setMap(null);
    }
    this.newShapes = [];
    this.drawingManager.setDrawingMode(null);
  }

  clearAll() {
    this.clearShapes();
    // now, also go through Detection_detections and take out the blue ones
    let dets = [];
    for (let det of Detection_detections) {
      if (det.conf !== 1.0) {
        det.id = dets.length;
        dets.push(det);
      }
    }
    Detection_detections = dets;
    Detection.generateList();
  }



  getBoundsPolygon(query, place) {
    googleMap.resetBoundaries();
    // Google Maps provider-specific search - only affects Google Maps

    // Handle null/undefined place for Enter-to-search fallback
    const hasPlace = place && place.geometry && place.formatted_address;
    console.log("Querying place outline for: " + query + (hasPlace ? (" (" + place.name + ")") : " (no Place)"));
    if (query[0] === '"' && query.endsWith('"')) {
      // hand this to openstreetmap "as is"
      query = query.substring(1, query.length - 1);
    } else if (hasPlace) {
      // take the google idea of what this is instead
      query = place.formatted_address;
    } // else use the raw query string

    // Fit bounds using place viewport when available, otherwise keep current view
    const viewport = hasPlace ? place.geometry.viewport : googleMap.map.getBounds();
    if (viewport) {
      googleMap.map.fitBounds(viewport);
    }

    $.ajax({
      url: "https://nominatim.openstreetmap.org/search.php",
      data: {
        q: query,
        polygon_geojson: "1",
        format: "json",
      },
      success: function (result) {
        let x = result[0];
        if (typeof x === 'undefined') {
          //googleMap.map.setCenter(place.geometry.location);
          // Fit to place viewport if present; otherwise keep current bounds
          if (hasPlace && place.geometry && place.geometry.viewport) {
            googleMap.map.fitBounds(place.geometry.viewport);
          }
          //googleMap.map.setZoom(19);
          // No Azure Maps dependency - Google provider handles Google Maps only
          return;
        }
        console.log(" Display name: " + x['display_name'] + ": " + x['boundingbox']);
        if (x["geojson"]["type"] == "Polygon" || x["geojson"]["type"] == "MultiPolygon") {
          let bounds = null;
          let ps = x["geojson"]["coordinates"];
          for (let p of ps) {
            if (x["geojson"]["type"] == "MultiPolygon") {
              p = p[0];
            }
            //console.log(" Polygon: " + p);
            //let polyData = parseLatLngArray(p);
            googleMap.addBoundary(new PolygonBoundary(p));
            // Only update Google Maps when Google is the provider
          }
          //console.log(bounds.toUrlValue());
        } else if (x["geojson"]["type"] == "LineString" || x["geojson"]["type"] == "Point") {
          googleMap.map.fitBounds(place.geometry.viewport, 0)
        }
        if (googleMap.boundaries.length > 0) {
          googleMap.showBoundaries();
          // Only show Google Maps boundaries when Google is the provider
        }
      }
    });
  }


  // will always synchronize with the Google map,
  // which should in turn be in sync with the Azure map.
  biasSearchBox() {
    this.searchBox.setBounds(this.map.getBounds());
  }

  getBounds() {
    let bounds = this.map.getBounds();
    let ne = bounds.getNorthEast();
    let sw = bounds.getSouthWest();
    return [sw.lng(), ne.lat(), ne.lng(), sw.lat()];
  }

  fitBounds(x1, y1, x2, y2) {
    let bounds = google.maps.LatLngBounds({
      north: y1,
      south: y2,
      east: x2,
      west: x1
    });
    this.map.fitBounds(bounds);
  }

  setCenter(c) {
    this.map.setCenter({ lat: c[1], lng: c[0] });
    //this.map.setZoom(19);
  }

  getZoom() {
    return this.map.getZoom();
  }

  setZoom(z) {
    this.map.setZoom(z);
  }

  makeMapRect(o, listener) {
    const rectangle = new google.maps.Rectangle({
      strokeColor: o.color,
      strokeOpacity: 1.0,
      strokeWeight: 1,
      fillColor: o.fillColor,
      fillOpacity: o.opacity,
      clickable: true,
      bounds: {
        north: o.y1,
        south: o.y2,
        east: o.x2,
        west: o.x1,
      },
    });
    if (typeof listener !== 'undefined') {
      rectangle.addListener("click", listener);
      rectangle.setOptions({ zIndex: 1000 });
    } else {
      rectangle.setOptions({ zIndex: 0 });
    }
    return rectangle;
  }

  colorMapRect(o, color) {
    o.mapRect.setOptions({ strokeColor: color, fillColor: color, fillOpacity: o.opacity });
  }

  updateMapRect(o, onoff) {
    let r = o.mapRect;
    r.setMap(onoff ? this.map : null)
  }

  resetBoundaries() {
    console.log('🧹 Google Maps: Resetting boundaries...');
    const boundaryCount = this.boundaries.length;

    for (let b of this.boundaries) {
      if (b && b.object) {
        b.object.setMap(null); // Remove from map visually
        b.object = null; // Release reference
      }
    }
    this.boundaries = [];

    // Clear activeShapes tracking
    this.activeShapes.circles = [];
    this.activeShapes.polygons = [];

    console.log(`✅ Google Maps: Removed ${boundaryCount} boundaries from map`);
  }

  clearCircles() {
    console.log(`🔄 Clearing ${this.activeShapes.circles.length} circle(s) from Google Maps...`);

    if (this.activeShapes.circles.length === 0) {
      console.log('✅ No circles to clear');
      return;
    }

    // Step 1: Remove circle polygons from map
    for (let circle of this.activeShapes.circles) {
      if (circle) {
        circle.setMap(null);
      }
    }
    console.log('  - Removed circle polygons from map');

    // Step 2: Filter circles from boundaries array
    const beforeCount = this.boundaries.length;
    this.boundaries = this.boundaries.filter(b => !b.isCircle);
    const removedCount = beforeCount - this.boundaries.length;
    console.log(`  - Removed ${removedCount} circle boundary reference(s)`);

    // Step 3: Clear tracking array
    const clearedCount = this.activeShapes.circles.length;
    this.activeShapes.circles = [];

    console.log(`✅ Cleared ${clearedCount} circle(s)`);
  }

  addBoundary(b) {
    // add to active bounds
    b.index = this.boundaries.length;

    // now make GoogleMap objects and link to them
    let points = b.points.map(p => ({ lng: p[0], lat: p[1] }));
    const poly = new google.maps.Polygon({
      paths: points,
      strokeColor: "#0000FF",
      strokeOpacity: 1,
      strokeWeight: 2,
      fillColor: "#00FF00",
      fillOpacity: 0,
    });
    poly.setMap(googleMap.map);
    b.object = poly;
    b.objectBounds = new google.maps.LatLngBounds();
    for (let p of points) {
      b.objectBounds.extend(p);
    }

    this.boundaries.push(b);

    // TASK-041 Phase 2 Step 2.2: Track circle boundaries for cleanup
    if (b.isCircle) {
      this.activeShapes.circles.push(poly);
      console.log('  - Tracked circle in activeShapes (total:', this.activeShapes.circles.length + ')');
    }


  }

  hasNonCircleBoundaries() {
    return this.boundaries.some(boundary => !boundary.isCircle);
  }

  showBoundaries() {
    // set map bounds to fit union of all active boundaries
    let bounds = new google.maps.LatLngBounds();
    for (let b of this.boundaries) {
      bounds = bounds.union(b.objectBounds);
    }
    this.map.fitBounds(bounds, 0);
  }

  getBoundaryBoundsUrl() {
    // set map bounds to fit union of all active boundaries
    let bounds = new google.maps.LatLngBounds();
    for (let b of this.boundaries) {
      bounds = bounds.union(b.objectBounds);
    }
    return bounds.toUrlValue();
  }

  getBoundariesStr() {
    let result = [];
    for (let b of this.boundaries) {
      result.push(b.toString())
    }
    return "[" + result.join(",") + "]";
  }

  // Memory Management: Cleanup Methods

  cleanupDrawingManager() {
    if (this.drawingManager) {
      console.log('🧹 Cleaning up Google DrawingManager...');

      // Remove all event listeners from drawing manager
      try {
        if (typeof google !== 'undefined' && google.maps && google.maps.event) {
          google.maps.event.clearInstanceListeners(this.drawingManager);
        }
      } catch (e) {
        console.warn('⚠️ Error clearing drawing manager listeners:', e.message);
      }

      // Remove from map
      try {
        this.drawingManager.setMap(null);
      } catch (e) {
        console.warn('⚠️ Error removing drawing manager from map:', e.message);
      }

      this.drawingManager = null;
      console.log('✅ Google DrawingManager cleaned up');
    }
  }

  cleanupMapListeners() {
    if (this.mapEventListeners.length > 0) {
      console.log(`🧹 Cleaning up ${this.mapEventListeners.length} Google map listeners...`);

      for (const listener of this.mapEventListeners) {
        try {
          if (listener.listener && typeof google !== 'undefined' && google.maps && google.maps.event) {
            google.maps.event.removeListener(listener.listener);
          }
        } catch (e) {
          console.warn(`⚠️ Error removing listener ${listener.eventType}:`, e.message);
        }
      }

      this.mapEventListeners = [];
      console.log('✅ Google map listeners cleaned up');
    }
  }

  cleanupSearch() {
    console.log('🧹 Cleaning up Google search infrastructure...');

    // Remove SearchBox listeners
    if (this.searchBox) {
      try {
        if (typeof google !== 'undefined' && google.maps && google.maps.event) {
          google.maps.event.clearInstanceListeners(this.searchBox);
        }
        this.searchBox = null;
      } catch (e) {
        console.warn('⚠️ Error cleaning up search box:', e.message);
      }
    }

    // Clear places cache
    this.places = null;

    console.log('✅ Google search infrastructure cleaned up');
  }

  cleanup() {
    console.log('🧹 Starting Google Maps cleanup...');

    try {
      // 1. Cleanup drawing manager
      this.cleanupDrawingManager();

      // 2. Cleanup map event listeners
      this.cleanupMapListeners();

      // 3. Cleanup search infrastructure
      this.cleanupSearch();

      // 4. Reset boundaries (already correct implementation)
      this.resetBoundaries();

      // 5. Clear drawn shapes
      if (this.newShapes && this.newShapes.length > 0) {
        this.clearShapes();
      }

      console.log('✅ Google Maps cleanup complete');
    } catch (error) {
      console.error('❌ Error during Google Maps cleanup:', error);
      // Don't throw - allow cleanup to complete partially
    }
  }

}


//
// boundaries: simple, circle, polygon
//

class Boundary {
  constructor(kind) {
    this.kind = kind;
  }

  toString() {
    throw new Error("not implemented");
  }
}

class PolygonBoundary extends Boundary {
  constructor(points) {
    super("polygon");
    this.points = points;
  }

  toString() {
    return JSON.stringify(this.points);
  }
}

class SimpleBoundary extends PolygonBoundary {
  constructor(bounds) {
    super("simple:" + bounds);
    this.points = [[bounds[0], bounds[1]],
    [bounds[2], bounds[1]],
    [bounds[2], bounds[3]],
    [bounds[0], bounds[3]],
    [bounds[0], bounds[1]]
    ];
  }
}

class CircleBoundary extends PolygonBoundary {
  constructor(center, radius) {
    super("circle: " + center + ", " + radius + " m");
    this.isCircle = true; // Flag to identify circle boundaries

    // Use Azure Maps compatible circle generation
    console.log('Generating circle with center:', center, 'radius:', radius);
    this.points = this.generateCircle(center, radius, 64); // Use 64 segments for smooth circle
    console.log('Generated circle with', this.points.length, 'points');
  }

  // Generate circle using proper geographic calculations
  generateCircle(center, radiusMeters, segments = 64) {
    const points = [];
    const earthRadius = 6378137; // Earth radius in meters
    const centerLat = center[1];
    const centerLng = center[0];
    const latRad = centerLat * Math.PI / 180;

    for (let i = 0; i < segments; i++) {
      const angle = (i * 2 * Math.PI) / segments;

      // Calculate offset in degrees
      const latOffset = (radiusMeters * Math.cos(angle)) / earthRadius * (180 / Math.PI);
      const lngOffset = (radiusMeters * Math.sin(angle)) / (earthRadius * Math.cos(latRad)) * (180 / Math.PI);

      const lat = centerLat + latOffset;
      const lng = centerLng + lngOffset;
      points.push([lng, lat]);
    }

    // Close the polygon by adding the first point at the end
    if (points.length > 0) {
      points.push([points[0][0], points[0][1]]);
    }

    return points;
  }
}



//
// PlaceRects - rectangles on the map (results, tiles, bounding boxes)
//

class PlaceRect {

  constructor(x1, y1, x2, y2, color, fillColor, opacity, classname, listener) {
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;
    this.color = color;
    this.fillColor = fillColor;
    this.opacity = opacity;
    this.classname = classname;
    this.address = "<unknown address>";
    this.map = currentMap
    this.mapRect = this.map.makeMapRect(this, listener);
    this.update();
    this.listener = listener;
  }

  centerInMap() {
    // this.map.setCenter([(this.x1 + this.x2) / 2, (this.y1 + this.y2) / 2]);
    // currentMap.setZoom(19);
    const targetMap = currentMap || this.map || googleMap;
    if (targetMap && typeof targetMap.setCenter === 'function') {
      targetMap.setCenter([(this.x1 + this.x2) / 2, (this.y1 + this.y2) / 2]);
      if (typeof targetMap.setZoom === 'function') {
        targetMap.setZoom(19);
      }
    }
  }

  getCenter() {
    return [(this.x1 + this.x2) / 2, (this.y1 + this.y2) / 2];
  }

  getCenterUrl() {
    let c = this.getCenter();
    return c[1] + "," + c[0];
  }

  augment(addr) {
    this.addrSpan.innerText = addr;
    this.address = addr;
    //console.log("tower " + i + ": " + addr)
  }

  highlight(color) {
    currentMap.colorMapRect(this, color);
    setTimeout(() => {
      currentMap.colorMapRect(this, this.color);
    }, 5000);
  }

  update(newMap) {
    if (typeof newMap !== 'undefined') {
      this.map.updateMapRect(this, false);
      this.mapRect = newMap.makeMapRect(this, this.listener);
      this.map = newMap;
    }
    this.map.updateMapRect(this, true);
  }
}

let Tile_tiles = [];
class Tile extends PlaceRect {
  static resetAll() {
    for (let tile of Tile_tiles) {
      currentMap.updateMapRect(tile, false);
    }
    Tile_tiles = [];
  }

  constructor(x1, y1, x2, y2, metadata, url) {
    super(x1, y1, x2, y2, "#0000FF", "#0000FF", 0.0, "tile")
    this.metadata = metadata; // for map metadata
    this.url = url

    Tile_tiles.push(this);
  }

  // find the ids for all tiles that the center of this box belongs to
  static getTileIds(x1, y1, x2, y2) {
    let result = [];
    for (let i = 0; i < Tile_tiles.length; i++) {
      let t = Tile_tiles[i]
      // compute center
      let cx = (x1 + x2) / 2;
      let cy = (y1 + y2) / 2;

      // check if center in tile
      if (cx >= t.x1 && cx <= t.x2 && cy <= t.y1 && cy >= t.y2) {
        result.push(i);
      }
    }
    return result;
  }

  // tile navigation for review pane
  static number() {
    let index = document.getElementById("tile").value;
    if (index === "") {
      index = "0";
    } else {
      index = Number(index) % Tile_tiles.length;
    }
    document.getElementById("tile").value = String(index);
    Tile_tiles[index].centerInMap();
  }

  static prev() {
    let index = document.getElementById("tile").value;
    if (index === "") {
      index = "0";
    } else {
      index = (((Number(index) - 1) % Tile_tiles.length) + Tile_tiles.length) % Tile_tiles.length; // don't ask
    }
    document.getElementById("tile").value = String(index);
    Tile_tiles[index].centerInMap();
  }

  static next() {
    let index = document.getElementById("tile").value;
    if (index === "") {
      index = "0";
    } else {
      index = (Number(index) + 1) % Tile_tiles.length;
    }
    document.getElementById("tile").value = String(index);
    Tile_tiles[index].centerInMap();
  }
}


let Detection_detections = []
let Detection_detectionsAugmented = 0;
let Detection_minConfidence = DEFAULT_CONFIDENCE;
let Detection_current = null;

class Detection extends PlaceRect {
  static resetAll() {
    for (let det of Detection_detections) {
      det.select(false);
    }
    Detection_detections = [];
    Detection_detectionsAugmented = 0;
    detectionsList.innerHTML = "";
  }

  constructor(x1, y1, x2, y2, classname, conf, tile, idInTile, inside, selected, secondary, address, addressConfidence, addressProvider) {
    super(x1, y1, x2, y2, conf === 1.0 ? "blue" : "#FF0000", conf === 1.0 ? "blue" : "#FF0000", 0.15, classname, () => {
      this.highlight(true, true);
    })
    this.conf = conf;
    this.inside = inside;
    this.idInTile = idInTile;
    this.selected = selected;
    this.address = address || "";
    this.addressConfidence = addressConfidence || 0.0;
    this.addressProvider = addressProvider || "none";
    this.maxConf = conf; // maximum confidence across same address towers, only recorded in first
    this.maxSecondary = secondary; // maximum secondary confidence across same address towers, only recorded in first
    this.firstDet = null; // first of block of same address towers
    this.tile = tile; // id of detection tile
    this.secondary = secondary;

    this.id = Detection_detections.length;
    this.originalId = this.id;
    // console.log("Detection #" + this.id + " is " + (this.selected ? "" : "not ") + "selected");
    Detection_detections.push(this);
  }

  static sort() {
    Detection_detections.sort((a, b) => {
      if (a.address < b.address) {
        return -1;
      } else if (a.address > b.address) {
        return 1;
      } else {
        return b.conf - a.conf;
      }
    });

    // fix ids
    for (let i = 0; i < Detection_detections.length; i++) {
      let det = Detection_detections[i];
      det.id = i;
    }
  }

  static generateList() {
    let currentAddr = "";
    let firstDet = null;
    let boxes = "<ul>";
    let count = 0;
    for (let det of Detection_detections) {
      if (det.address !== currentAddr) {
        if (currentAddr !== "") {
          boxes += "</ul></li>";
        }
        boxes += "<li id='addrli" + det.id + "'>";
        boxes += "<span class='caret' onclick='";
        boxes += "this.parentElement.querySelector(\".nested\").classList.toggle(\"active\"),";
        boxes += "this.classList.toggle(\"caret-down\")';"
        boxes += "'></span>";
        boxes += "<input type='checkbox' id='addrcb" + det.id + "' name='addrcb" + det.id;
        boxes + "' value='";
        boxes += det.id + "' checked style='display:inline;vertical-align:-10%;'"
        boxes += " onclick='Detection_detections[" + det.id + "].selectAddr(this.checked)'>";
        boxes += "<span class='address' id='addrlabel" + det.id + "'";
        boxes += " onclick='Detection.showDetection(" + det.id + ", true)'>"
        boxes += det.address + "</span><br>";
        boxes += "<ul class='nested' id='towerslist" + det.id;
        boxes += "' style='text-indent:-25px; padding-left: 60px;'>";
        currentAddr = det.address;
        firstDet = det;
      }
      boxes += det.generateCheckBox();
      firstDet.maxConf = Math.max(det.conf, firstDet.maxConf); // record max conf in block header
      firstDet.maxSecondary = Math.max(det.secondary, firstDet.maxSecondary || 0)
      det.firstDet = firstDet; // record block header
      det.indexInList = count;
      det.update();
      count++;
    }
    boxes += "</li></ul>";
    detectionsList.innerHTML = boxes;
  }

  generateCheckBox() {
    // Defensive check for tile existence (prevents crash if tiles not loaded)
    let meta = "";
    if (Tile_tiles[this.tile] && Tile_tiles[this.tile].metadata) {
      meta = Tile_tiles[this.tile].metadata;
    }
    let p2 = (this.secondary > 0 && this.secondary < 1.0 ? ",&nbsp;P2(" + this.secondary.toFixed(2) + ")" : "")
    let box = "<li><div style='display:block' id='detdiv" + this.id + "'>";
    box += "<input type='checkbox' id='detcb" + this.id + "' name='detcb" + this.id + "'";
    box += " value='" + this.id + "' " + (this.selected ? "checked" : "");
    box += " style='display:inline;vertical-align:-10%;'"
    box += " onclick='Detection_detections[" + this.id + "].select(undefined)'>";
    box += "&nbsp;";
    box += "<span class='address' onclick='Detection.showDetection(" + this.id + ", true)' ";
    box += "id='plabel" + this.id + "'>";
    box += "P(" + this.conf.toFixed(2) + ")" + p2 + (meta !== "" ? ",&nbsp" + meta : "") + "</span></li>";
    box += "</div>";

    this.checkBoxId = 'detdiv' + this.id;
    this.labelId = 'plabel' + this.id;
    return box;
  }



  select(onoff) {
    if (typeof onoff === 'undefined') {
      onoff = !this.selected;
    }
    this.selected = onoff;
    document.getElementById("detcb" + this.id).checked = onoff;
    this.update();
  }

  selectAddr(onoff) {
    if (typeof onoff === 'undefined') {
      onoff = !this.selected;
    }
    for (let det of Detection_detections) {
      if (det.address === this.address) {
        det.selected = onoff;
        document.getElementById("detcb" + det.id).checked = onoff;
        det.update();
      }
    }
  }

  show(onoff) {
    document.getElementById("detdiv" + this.id).style.display = onoff ? "block" : "none";
  }

  isShown() {
    return document.getElementById("detdiv" + this.id).style.display === "block";
  }

  showAddr(onoff) {
    document.getElementById("addrli" + this.id).style.display = onoff ? "block" : "none";
  }

  static showDetection(id, center) {
    Detection_detections[id].highlight(center, false);
  }

  highlight(center, scroll) {
    let firstDet = this.firstDet;

    if (currentAddrElement !== null) {
      currentAddrElement.style.fontWeight = "normal";
      currentAddrElement.style.textDecoration = "";
      currentElement.style.fontWeight = "normal";
      currentElement.style.textDecoration = "";
    }

    // highlight the address
    let element = document.getElementById('addrlabel' + firstDet.id);
    element.style.fontWeight = "bolder";
    element.style.textDecoration = "underline";
    currentAddrElement = element;

    // make sure parent element is open
    element.parentNode.firstChild.classList.add('caret-down');
    // and list displayed
    element.parentNode.lastChild.classList.add('active');

    // highlight the individual detection
    element = document.getElementById(this.labelId);
    if (scroll) {
      currentAddrElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    element.style.fontWeight = "bolder";
    element.style.textDecoration = "underline";
    currentElement = element;
    document.getElementById("detection").value = this.indexInList;


    if (center) {
      this.centerInMap();
    }

    if (Detection_current !== null) {
      Detection_current.resetHighlight();
    }
    super.highlight("green");
    Detection_current = this;
  }

  resetHighlight() {
    super.highlight(this.color);
  }


  augment(addr) {
    // this.addrSpan.innerText = addr;
    this.address = addr;
    Detection_detectionsAugmented++;
    //console.log("tower " + i + ": " + addr)
  }

  update(newMap) {
    // first, process any map UI change
    super.update(newMap)

    let meetsInside = reviewCheckBox.checked || this.inside;

    // FIX: Use secondary classifier threshold for visibility instead of primary confidence
    // Backend selects detections based on secondary >= 0.35, so frontend should too
    let meetsConfidence = this.conf >= Detection_minConfidence || this.secondary >= 0.35;

    // then update by confidence - show if selected and meets either confidence threshold
    this.map.updateMapRect(this, this.selected && meetsConfidence && meetsInside);
  }

  // navigation for review pane
  static number() {
    let index = document.getElementById("detection").value;
    if (index === "") {
      index = "0";
    } else {
      index = Number(index);
    }
    document.getElementById("detection").value = String(this.navigateTo(index));
  }

  // navigation for review pane
  static prev() {
    let index = document.getElementById("detection").value;
    if (index === "") {
      index = "0";
    } else {
      index = Number(index) - 1;
    }
    document.getElementById("detection").value = String(this.navigateTo(index));
  }

  static next() {
    let index = document.getElementById("detection").value;
    if (index === "") {
      index = "0";
    } else {
      index = Number(index) + 1;
    }
    document.getElementById("detection").value = String(this.navigateTo(index));
  }

  static navigateTo(index) {
    // first, count shown detections
    let count = 0;
    for (let det of Detection_detections) {
      if (det.isShown() && det.selected) {
        count++;
      }
    }
    // limit index to count
    index = ((index % count) + count) % count;

    // now find and center
    let j = 0;
    for (let det of Detection_detections) {
      if (det.isShown() && det.selected) {
        if (j == index) {
          det.highlight(true, true);
          return index;
        }
        j++;
      }
    }
    return index;
  }
}


function createElementFromHTML(htmlString) {
  let div = document.createElement('div');
  div.innerHTML = htmlString.trim();
  return div.firstChild;
}

// retrieve satellite image and detect objects
function getObjects(estimate) {
  //let center = currentMap.getCenterUrl();

  if (!currentMap) {
    const fallbackMap = providerManager.getMap();
    if (fallbackMap) {
      currentMap = fallbackMap;
    }
  }
  if (!currentMap) {
    TowerScoutErrorHandler.showUserNotification(
      'Map is still initializing. Please wait a moment and try again.',
      'warning'
    );
    return;
  }

  if (Detection_detections.length > 0) {
    if (!window.confirm("This will erase current detections. Proceed?")) {
      return;
    }
  }

  let engine = $('input[name=model]:checked', '#engines').val()
  let provider = $('input[name=provider]:checked', '#providers').val()
  console.log('🎯 Detection provider value:', provider, '| Type:', typeof provider);
  console.log('🎯 Provider validation - Azure:', provider === 'azure', '| Google:', provider === 'google');
  // let boundaries = googleMap.getBoundariesStr();
  // if (boundaries === "[]" && radius == "") {
  //   console.log("No boundary selected, instead using viewport: " + googleMap.getBounds())
  //   googleMap.addBoundary(new SimpleBoundary(googleMap.getBounds()));
  // }


  // TASK-041 Phase 2 Step 2.6: Use boundary bounding box instead of viewport bounds
  // This ensures tiles are generated only for the drawn search area, not the entire viewport
  let bounds = currentMap.getBoundaryBoundsUrl();
  console.log('🗺️ Using bounds for tile generation:', bounds);

  if (currentMap && currentMap.boundaries && currentMap.boundaries.length === 0) {
    if (currentMap.hasShapes && currentMap.hasShapes()) {
      drawnBoundary();
    }
  }

  let boundaries = currentMap.getBoundariesStr();

  // Auto-create viewport boundary if no polygons are drawn
  if (boundaries === "[]") {
    console.log("No boundary selected, automatically using current viewport as detection area");
    const bounds = currentMap.getBounds();
    currentMap.addBoundary(new SimpleBoundary(bounds));
    // TASK-041 Phase 1: Sync boundaries to initialized providers only
    if (currentMap === googleMap && azureMap) {
      azureMap.addBoundary(new SimpleBoundary(bounds));
    } else if (currentMap === azureMap && googleMap) {
      googleMap.addBoundary(new SimpleBoundary(bounds));
    }
    boundaries = currentMap.getBoundariesStr();
  }
  let kinds = ["None", "Polygon", "Multiple polygons"]
  if (estimate) {
    console.log("Estimate request in progress");
  } else {
    console.log("Detection request in progress");
  }

  // erase the previous set of towers and tiles
  Detection.resetAll();
  Tile.resetAll();

  // first, play the request, but get an estimate of the number of tiles
  const formData = new FormData();
  formData.append('bounds', bounds);
  formData.append('engine', engine);
  formData.append('provider', provider);
  formData.append('polygons', boundaries);
  formData.append('estimate', "yes");

  fetch("/getobjects", { method: "POST", body: formData, })
    .then(result => {
      if (!result.ok) {
        throw new Error(`HTTP ${result.status}: ${result.statusText}`);
      }

      // Check if result is JSON error instead of tile count
      const contentType = result.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return result.json().then(errorData => {
          throw new Error(errorData.error || 'Server error');
        });
      }
      return result.text();
    })
    .then(result => {
      // Validate result is a number
      const tileCount = Number(result);
      if (isNaN(tileCount)) {
        throw new Error(`Invalid tile count response: ${result}`);
      }

      if (tileCount === -1) {
        fatalError("Tile limit for this session exceeded. Please close browser to continue.")
        return;
      }
      console.log("Number of tiles: " + tileCount + ", estimated time: "
        + (Math.round(tileCount * secsPerTile * 10) / 10) + " s");
      // let nt = estimateNumTiles(currentMap.getZoom());
      // console.log("  Estimated tiles:" + nt);
      if (estimate) {
        return;
      }

      // actual retrieval process starts here
      let nt = tileCount;
      enableProgress(nt);
      setProgress(0);
      let startTime = performance.now();

      // now, the actual request

      Detection.resetAll();
      formData.delete("estimate");

      const detectionCall = TowerScoutErrorHandler.wrapNetworkCall(
        async () => {
          const response = await fetch("/getobjects", { method: "POST", body: formData });
          if (!response.ok) {
            throw new Error(`Detection failed: HTTP ${response.status} - ${response.statusText}`);
          }
          return await response.json();
        },
        'Cooling Tower Detection'
      );

      detectionCall()
        .then(result => {
          if (!result || !Array.isArray(result)) {
            throw new Error('Invalid detection response format');
          }
          processObjects(result, startTime);
        })
        .catch(error => {
          console.error('❌ Detection pipeline error:', error);
          TowerScoutErrorHandler.handleNetworkError(error, 'Cooling Tower Detection');
          disableProgress(0, 0);

          // Provide helpful error message to user
          const errorMsg = error.message || 'Detection failed';
          if (errorMsg.includes('timeout')) {
            TowerScoutErrorHandler.showUserNotification(
              'Detection timed out. Try a smaller area or check your internet connection.',
              'warning'
            );
          } else if (errorMsg.includes('rate') || errorMsg.includes('429')) {
            TowerScoutErrorHandler.showUserNotification(
              'Too many requests. Please wait a moment before trying again.',
              'warning'
            );
          } else {
            TowerScoutErrorHandler.showUserNotification(
              `Detection failed: ${errorMsg}. Please try again or refresh the page.`,
              'error'
            );
          }
        });
    })
    .catch(error => {
      console.error("Validation error:", error.message);
      fatalError("Error: " + error.message);
    });
}

function processObjects(result, startTime) {
  try {
    console.log(`📊 Processing detection results: ${result?.length || 0} objects...`);

    // Validate input
    if (!Array.isArray(result)) {
      throw new Error(`Invalid result data: expected array, got ${typeof result}`);
    }

    // Safe DOM element access
    const confElement = document.getElementById("conf");
    if (!confElement) {
      console.warn('⚠️ Confidence slider not found, using default value');
    }
    const conf = confElement ? Number(confElement.value) : Detection_minConfidence;

    if (result.length === 0) {
      console.log('📊 Area too big or no detections found. Please ' + (radius !== '' ? 'enter a smaller radius.' : 'zoom in.'));
      disableProgress(0, 0);
      TowerScoutErrorHandler.showUserNotification(
        'No cooling towers found. Try a smaller search area or different location.',
        'info'
      );
      return;
    }

    console.log(`🔍 Processing ${result.length} detection results...`);

    // Process detection objects with error handling
    let processedDetections = 0;
    let processedTiles = 0;

    for (let r of result) {
      try {
        if (r['class'] === 0) {
          // Create detection with server-provided address data
          let det = new Detection(r['x1'], r['y1'], r['x2'], r['y2'],
            r['class_name'], r['conf'], r['tile'], r['id_in_tile'], r['inside'], r['selected'], r['secondary'],
            r['address'], r['address_confidence'], r['address_provider']);
          processedDetections++;
        } else if (r['class'] === 1) {
          let tile = new Tile(r['x1'], r['y1'], r['x2'], r['y2'], r['metadata'], r['url']);
          processedTiles++;
        }
      } catch (objectError) {
        console.error('❌ Error processing individual object:', objectError);
        // Continue processing other objects
      }
    }

    console.log(`✅ Processed ${processedDetections} detections and ${processedTiles} tiles`);
    console.log(`📊 ${Detection_detections.length} total detections with server-provided addresses.`);

    // Update API usage display if geocoding usage data is available
    try {
      updateApiUsageDisplay();
    } catch (displayError) {
      console.warn('⚠️ Failed to update API usage display:', displayError);
    }

    // Calculate and display processing time
    if (startTime) {
      const processingTime = ((performance.now() - startTime) / 1000).toFixed(1);
      console.log(`⏱️ Processing completed in ${processingTime} seconds`);
      disableProgress(processingTime, Tile_tiles.length);
    } else {
      disableProgress(0, Tile_tiles.length);
    }

    // Process detections immediately since addresses are already available
    try {
      Detection.sort();
      Detection.generateList();
      adjustConfidence();
    } catch (sortError) {
      console.error('❌ Error in detection post-processing:', sortError);
      TowerScoutErrorHandler.handleCriticalError(sortError, 'Detection Post-Processing');
    }

    // Show success notification
    if (processedDetections > 0) {
      TowerScoutErrorHandler.showUserNotification(
        `Successfully found ${processedDetections} cooling towers!`,
        'success'
      );
    }

  } catch (error) {
    console.error('❌ Critical error in processObjects:', error);

    // Ensure UI is in a safe state
    try {
      disableProgress(0, 0);
    } catch (progressError) {
      console.error('❌ Failed to reset progress indicator:', progressError);
    }

    // Handle specific error types
    if (error.message.includes('Invalid result data')) {
      TowerScoutErrorHandler.showUserNotification(
        'Received invalid data from detection service. Please try again.',
        'error'
      );
    } else {
      TowerScoutErrorHandler.handleCriticalError(error, 'Detection Processing');
    }

    // Re-throw for caller if needed
    throw error;
  }
}

function cancelRequest() {
  // Removed unsafe abort of undefined xhr; rely on server-side abort
  disableProgress(0, 0);
  fetch('/abort', { method: "GET" })
    .then(response => {
      response.text();
    })
    .then(response => {
      console.log("aborted.");
    })
    .catch(error => {
      console.log("abort error: " + error);
    });
}

function circleBoundary() {
  // TASK-041 Phase 1: Get map via provider manager
  const map = providerManager.getMap();
  const provider = providerManager.getCurrentProvider();

  // TASK-041 Phase 1: Check comprehensive initialization
  if (!providerManager.isFullyInitialized()) {
    console.warn(`⏳ ${provider} is still initializing, please wait...`);
    TowerScoutErrorHandler.showUserNotification(
      'Map is still loading. Please wait a moment and try again.',
      'warning'
    );
    return;
  }

  // Defensive null checks (fallback)
  if (!map) {
    console.error('❌ Map is not available from provider manager');
    TowerScoutErrorHandler.showUserNotification(
      'Map is not available. Please refresh the page.',
      'error'
    );
    return;
  }

  // radius? construct a circle
  let radius = document.getElementById("radius").value;
  if (radius !== "") {
    console.log('🔵 Creating circle with radius:', radius, 'meters');

    // convert to m
    radius = Number(radius);

    if (isNaN(radius) || radius <= 0) {
      console.warn('Invalid radius value:', radius);
      TowerScoutErrorHandler.showUserNotification(
        'Please enter a valid radius (positive number).',
        'warning'
      );
      return;
    }

    // TASK-041 Phase 1: Use map from provider manager
    // make circle - use current map center
    let centerCoords = map.getCenter();
    console.log('🎯 Circle center coordinates:', centerCoords);

    // TASK-041 Phase 2 Step 2.2: Clear previous circles (surgical removal, preserves polygons)
    console.log('🔄 Clearing previous circles before creating new one...');

    // Clear circles from both providers (only if initialized)
    if (googleMap && typeof googleMap.clearCircles === 'function') {
      googleMap.clearCircles();
    }
    if (azureMap && typeof azureMap.clearCircles === 'function') {
      azureMap.clearCircles();
    }

    // Show user feedback
    TowerScoutErrorHandler.showUserNotification('Updating search area...', 'info', 1500);

    // Add new circle
    let circleBoundary = new CircleBoundary(centerCoords, radius);
    console.log('Circle boundary points:', circleBoundary.points.length);
    console.log('Circle boundary sample points:', circleBoundary.points.slice(0, 5));
    console.log('Circle boundary isCircle flag:', circleBoundary.isCircle);

    // Add boundary to initialized providers only
    if (googleMap) {
      googleMap.addBoundary(circleBoundary);
      console.log('After add - Google boundaries:', googleMap.boundaries.length);
    }
    if (azureMap) {
      azureMap.addBoundary(circleBoundary);
      console.log('After add - Azure boundaries:', azureMap.boundaries.length);
      console.log('Azure searchDataSource exists:', !!azureMap.searchDataSource);

      // Check if boundary was actually added to data source
      if (azureMap.searchDataSource) {
        let shapes = azureMap.searchDataSource.getShapes();
        console.log('Total shapes in data source:', shapes.length);
        let boundaryShapes = shapes.filter(s => s.getProperties().type === 'boundary');
        console.log('Boundary shapes in data source:', boundaryShapes.length);
      }
    }

    // DON'T call showBoundaries() to avoid map reset - boundary should render automatically
    console.log('✅ Circle boundary created (should render automatically)');
  } else {
    console.warn('⚠️ No radius value entered');
  }
}

function drawnBoundary() {
  // Defensive null checks
  if (!currentMap) {
    console.error('❌ currentMap is not initialized');
    TowerScoutErrorHandler.showUserNotification(
      'Map is still initializing. Please wait a moment and try again.',
      'warning'
    );
    return;
  }

  // TASK-041 Phase 1: Don't require both providers, just work with initialized ones
  console.log("using custom boundary polygon(s)");
  let boundaries = currentMap.retrieveDrawnBoundaries();

  if (!boundaries || boundaries.length === 0) {
    console.warn('⚠️ No drawn boundaries found');
    TowerScoutErrorHandler.showUserNotification(
      'No custom shapes drawn. Please use the polygon tool to draw a boundary first.',
      'info'
    );
    return;
  }

  // TASK-041 Phase 1: Add boundaries to initialized providers only
  for (let b of boundaries) {
    if (googleMap && typeof googleMap.addBoundary === 'function') {
      googleMap.addBoundary(b);
    }
    if (azureMap && typeof azureMap.addBoundary === 'function') {
      azureMap.addBoundary(b);
    }
  }

  console.log(`✅ Added ${boundaries.length} custom boundary/boundaries`);
}

function clearBoundaries() {
  // Get current map via provider manager (align with Phase 1 pattern)
  const currentMap = providerManager.getMap();

  // Only require current provider to be initialized (not both)
  if (!currentMap) {
    console.error('❌ Current map provider not initialized');
    TowerScoutErrorHandler.showUserNotification(
      'Map provider is still initializing. Please wait a moment.',
      'warning'
    );
    return;
  }

  console.log('🧹 Clearing all boundaries');

  // Clear boundaries on initialized providers only (both if available)
  if (googleMap && typeof googleMap.resetBoundaries === 'function') {
    googleMap.resetBoundaries();
  }

  if (azureMap && typeof azureMap.resetBoundaries === 'function') {
    azureMap.resetBoundaries();
  }

  console.log('✅ Boundaries cleared');
}


function parseLatLngArray(a) {
  let result = [];  // CRITICAL FIX: Add missing let declaration
  for (let p of a) {
    result.push({ lat: p[1], lng: p[0] });
  }
  return result;
}

function polyBounds(ps) {
  let bounds = new google.maps.LatLngBounds();  // CRITICAL FIX: Add missing let declaration

  for (let p of ps) {
    bounds.extend(p);
  }
  return bounds;
}

function fillEngines() {
  $.ajax({
    url: "/getengines",
    success: function (result) {
      let html = "";
      //console.log(result);
      let es = JSON.parse(result);
      engines = {};
      //console.log(engines);
      for (let i = 0; i < es.length; i++) {
        html += "<input type='radio' id='" + es[i]['id']
        html += "' name='model' value='" + es[i]['id'] + "'"
        html += i == 0 ? " checked>" : ">"
        html += "<label for='" + es[i]['id'] + "'>" + es[i]['name'] + "</label><br>";
        engines[es[i]['id']] = es[i]['name'];
      }
      $("#engines").html(html);
    }
  });
}

async function fillProviders() {
  // retrieve the backend providers
  $.ajax({
    url: "/getproviders",
    success: async function (result) {
      let html = "";
      //console.log(result);
      let ps = JSON.parse(result);
      providers = {};
      //console.log(engines);
      for (let i = 0; i < ps.length; i++) {
        const isDefault = (i === 0); // First provider from backend is default
        html += "<input type='radio' id='" + ps[i]['id']
        html += "_provider' name='provider' value='" + ps[i]['id'] + "'"
        html += isDefault ? " checked>" : ">"
        html += "<label for='" + ps[i]['id'] + "_provider'>" + ps[i]['name'] + "</label><br>";
        providers[ps[i]['id']] = ps[i]['name'];

        if (isDefault) {
          console.log('🎨 Setting UI default provider to:', ps[i]['id']);
        }
      }
      $("#providers").html(html);

      // add change listeners for the backend provider radio box
      let rad = document.providers.provider;

      // Set initial provider using proper provider manager
      for (let r of rad) {
        if (r.checked) {
          console.log('🔧 Setting initial provider to:', r.value);

          // Store initial provider selection (don't switch yet)
          console.log('📌 Storing initial provider:', r.value);
          providerManager.currentProvider = r.value;
          console.log('✅ Initial provider stored via providerManager:', r.value);

          // CRITICAL: Actually initialize the map instance for the selected provider
          console.log('🚀 Initializing map for provider:', r.value);

          // Provider manager will handle currentProvider setting
          console.log('🔗 Provider manager will handle currentProvider setting');

          if (r.value === 'azure') {
            console.log('🗺️ Initializing Azure Maps...');
            await initAzureMap();

            // Set as current map and make visible
            currentMap = azureMap;
            providerManager.currentMap = azureMap;
            console.log('✅ Azure Maps set as current map');

            // Update UI to show Azure Maps div
            document.getElementById("googleMap").style.display = "none";
            document.getElementById("azureMap").style.display = "block";
            console.log('👁️ Azure Maps div set to visible');

          } else if (r.value === 'google') {
            console.log('🌍 Initializing Google Maps...');
            await initGoogleMap();

            // Set as current map and make visible  
            currentMap = googleMap;
            providerManager.currentMap = googleMap;
            console.log('✅ Google Maps set as current map');

            // Update UI to show Google Maps div
            document.getElementById("azureMap").style.display = "none";
            document.getElementById("googleMap").style.display = "block";
            console.log('👁️ Google Maps div set to visible');
          }

          // Set currentUI to the corresponding radio button
          const uiRadio = document.querySelector(`input[name="uis"][value="${r.value}"]`);
          if (uiRadio) {
            uiRadio.checked = true;
            currentUI = uiRadio;
            console.log('🔘 UI radio button set to:', r.value);
          }

          console.log('✅ Provider validation - currentProvider === "azure":', currentProvider === 'azure');
          console.log('✅ Provider validation - currentProvider === "google":', currentProvider === 'google');
          break;
        }
      }

      for (let r of rad) {
        eventManager.addEventListener(r, 'change', async function () {
          if (this.checked) {
            const oldProvider = providerManager.getProvider();
            console.log('🔄 Provider change requested from:', oldProvider, 'to:', this.value);

            try {
              // Use provider manager for coordinated switching
              await providerManager.switchProvider(this.value);
              console.log('✅ Provider successfully changed to:', this.value);
            } catch (error) {
              console.error('❌ Provider change failed:', error);
              // Revert radio button selection on failure
              if (oldProvider) {
                const oldRadio = document.querySelector(`input[value="${oldProvider}"]`);
                if (oldRadio) {
                  oldRadio.checked = true;
                  this.checked = false;
                }
              }
            }
          }
        });
      }

      // and one for the file input box
      let fileBox = document.getElementById("upload_file");
      if (fileBox) {
        eventManager.addEventListener(fileBox, 'change', () => {
          uploadImage();
        });
      }

      // and one for the model upload box
      let modelBox = document.getElementById("upload_model");
      if (modelBox) {
        eventManager.addEventListener(modelBox, 'change', () => {
          uploadModel();
        });
      }

      // and one for the dataset upload box
      let datasetBox = document.getElementById("upload_dataset");
      if (datasetBox) {
        eventManager.addEventListener(datasetBox, 'change', () => {
          uploadDataset();
        });
      }

    }
  });

  // also add change listeners for the UI providers
  // add change listeners for radio buttons
  let rads = document.uis.uis;
  // Use the checked radio button instead of just the first one
  currentUI = document.querySelector('input[name="uis"]:checked') || rads[0];
  setMap(currentUI);

  for (let rad of rads) {
    rad.addEventListener('change', function () {
      setMap(this);
    });
  }
}

async function setMap(newMap) {
  // Gracefully handle missing argument by using the currently checked radio
  if (!newMap) {
    const checked = document.querySelector('input[name="uis"]:checked');
    if (checked) {
      newMap = checked;
    } else if (currentUI) {
      newMap = currentUI;
    } else if (document.uis && document.uis.uis && document.uis.uis[0]) {
      newMap = document.uis.uis[0];
    } else {
      console.warn('setMap called without UI element and no radios found');
      return;
    }
  }

  // Check if switching is already in progress
  if (providerManager.isSwitching()) {
    console.log('⏳ Provider switch in progress, waiting...');
    return;
  }

  if (currentUI !== null) {
    document.getElementById(currentUI.value + "Map").style.display = "none";
  }
  currentUI = newMap;
  const handle = document.getElementById(currentUI.value + "Map");
  handle.style.display = "block";
  handle.style.width = "100%";
  handle.style.height = "100%";

  let lastMap = providerManager.getMap();  // Use provider manager
  let zoom;
  let center;
  if (typeof lastMap !== 'undefined' && lastMap) {
    zoom = lastMap.getZoom();
    center = lastMap.getCenter();
  }

  if (currentUI.value === "upload") {
    document.getElementById("uploadsearchui").style.display = "block";
    document.getElementById("mapsearchui").style.display = "none";
    document.getElementById("fdetect").style.display = "none";
    document.getElementById("ftowers").style.display = "none";
    document.getElementById("fsave").style.display = "none";
    document.getElementById("freview").style.display = "none";
    // document.getElementById("ffilter").style.display = "none";
    document.getElementById("fadd").style.display = "none";

  } else if (currentUI.value === "google") {
    document.getElementById("uploadsearchui").style.display = "none";
    document.getElementById("mapsearchui").style.display = null;
    document.getElementById("fdetect").style.display = null;
    document.getElementById("ftowers").style.display = null;
    document.getElementById("fsave").style.display = null;
    document.getElementById("freview").style.display = null;
    // document.getElementById("ffilter").style.display = null;
    document.getElementById("fadd").style.display = null;

    // Defer provider switching until after initialization is complete
    if (!isInitializing) {
      // Ensure Google Maps is initialized before switching
      if (!googleMap) {
        console.log('🌍 Google Maps not initialized, loading Google Maps API...');
        try {
          await loadGoogleMaps();
          console.log('✅ Google Maps loaded and initialized successfully');
        } catch (initError) {
          console.error('❌ Failed to load Google Maps:', initError);
          return;
        }
      }

      // Use provider manager for coordinated switching
      try {
        console.log(`🔄 Attempting to switch to Google Maps (isInitializing: ${isInitializing})`);
        await providerManager.switchProvider('google', googleMap);
        currentMap = googleMap;  // ✅ FIX: Sync global currentMap with providerManager
        console.log('🌍 Switched to Google Maps');
      } catch (error) {
        console.error('❌ Failed to switch to Google Maps:', error);
        console.error('❌ Google Maps state:', {
          exists: !!googleMap,
          hasMap: googleMap && !!googleMap.map,
          hasBounds: googleMap && typeof googleMap.getBounds === 'function'
        });
        return;
      }
    } else {
      console.log('📝 Storing Google Maps preference for post-initialization');
      // Just store the UI preference during initialization
      localStorage.setItem('preferredMapProvider', 'google');
    }

  } else if (currentUI.value === "azure") {
    document.getElementById("uploadsearchui").style.display = "none";
    document.getElementById("mapsearchui").style.display = null;
    document.getElementById("fdetect").style.display = null;
    document.getElementById("ftowers").style.display = null;
    document.getElementById("fsave").style.display = null;
    document.getElementById("freview").style.display = null;
    document.getElementById("fadd").style.display = null;

    // Defer provider switching until after initialization is complete
    if (!isInitializing) {
      // Ensure Azure Maps is initialized before switching
      if (!azureMap) {
        console.log('🗺️ Azure Maps not initialized, initializing now...');
        try {
          await initAzureMap();
          console.log('✅ Azure Maps initialized successfully');
        } catch (initError) {
          console.error('❌ Failed to initialize Azure Maps:', initError);
          return;
        }
      }

      // Use provider manager for coordinated switching
      try {
        console.log(`🔄 Attempting to switch to Azure Maps (isInitializing: ${isInitializing})`);
        await providerManager.switchProvider('azure');
        currentMap = azureMap;  // ✅ FIX: Sync global currentMap with providerManager
        console.log('🗺️ Switched to Azure Maps');

        // Disable Google Places when switching to Azure
        if (azureMap && azureMap.disableGooglePlacesWhenActive) {
          azureMap.disableGooglePlacesWhenActive();
        }

        console.log('Current map set to Azure Maps');
        let azBs = azureMap ? azureMap.boundaries : [];
        if (azureMap) {
          azureMap.resetBoundaries();
          azBs.map(b => azureMap.addBoundary(b));
        }
      } catch (error) {
        console.error('❌ Failed to switch to Azure Maps:', error);
        console.error('❌ Azure Maps state:', {
          exists: !!azureMap,
          hasMap: azureMap && !!azureMap.map,
          hasBounds: azureMap && typeof azureMap.getBounds === 'function',
          hasSubscriptionKey: azureMap && !!azureMap.subscriptionKey
        });
        return;
      }
    } else {
      console.log('📝 Storing Azure Maps preference for post-initialization');
      // Just store the UI preference during initialization
      localStorage.setItem('preferredMapProvider', 'azure');
    }
  }

  // set center and zoom
  const currentMapInstance = providerManager.getMap();
  if (typeof lastMap !== 'undefined' && lastMap && currentMapInstance) {
    if (currentMapInstance.boundaries && currentMapInstance.boundaries.length > 0) {
      currentMapInstance.showBoundaries();
    }
    if (zoom) currentMapInstance.setZoom(zoom);
    if (center) currentMapInstance.setCenter(center);
  }

  // move all rectangles over to the new map
  if (currentMapInstance) {
    Tile_tiles.forEach(t => t.update(currentMapInstance));
    Detection_detections.forEach(d => d.update(currentMapInstance));
  }
}

function adjustConfidence() {
  // Validate DOM elements are available
  if (!confSlider || !reviewCheckBox) {
    console.error('❌ Required DOM elements not initialized for adjustConfidence');
    return;
  }

  Detection_minConfidence = confSlider.value / 100;
  for (let det of Detection_detections) {
    let meetsInside = reviewCheckBox.checked || det.inside;
    let meetsConf = det.conf >= Detection_minConfidence || det.secondary >= 0.35;
    let meetsAddrConf = det.firstDet.maxConf >= Detection_minConfidence || det.firstDet.maxSecondary >= 0.35;
    det.firstDet.showAddr(meetsAddrConf && meetsInside);
    det.show(meetsConf && meetsInside);
    det.update();
  }

  const confPercentElement = document.getElementById('confpercent');
  if (confPercentElement) {
    confPercentElement.innerText = confSlider.value;
  }
}

function changeReviewMode() {
  // Validate DOM elements are available
  if (!reviewCheckBox || !confSlider) {
    console.error('❌ Required DOM elements not initialized for changeReviewMode');
    return;
  }

  if (reviewCheckBox.checked) {
    confSlider.value = 0;
  } else {
    confSlider.value = Math.round(DEFAULT_CONFIDENCE * 100);
  }
  adjustConfidence();
}

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

function afterAugment() {
  // Legacy function maintained for compatibility - addresses now come from server
  // This ensures existing calling code doesn't break
  Detection.sort();
  Detection.generateList();
  adjustConfidence();
}




function rad(x) {
  return x * Math.PI / 180;
};

// returns the Haversine distance between two points, in meters
function getDistance(p1, p2) {
  let R = 6378137; // Earth’s mean radius in meters
  let dLat = rad(p2[1] - p1[1]);
  let dLong = rad(p2[0] - p1[0]);
  let a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(rad(p1[1])) * Math.cos(rad(p2[1])) *
    Math.sin(dLong / 2) * Math.sin(dLong / 2);
  let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  let d = R * c;
  return d;
};


function download(filename, data) {
  // create blob object with our data
  let blob = new Blob([data], { type: 'text/csv' });

  // create a temp anchor element
  let elem = window.document.createElement('a');

  // direct it to the blob and filename
  elem.href = window.URL.createObjectURL(blob);
  elem.download = filename;

  // briefly insert it into the document, click it, remove it
  document.body.appendChild(elem);
  elem.click();
  document.body.removeChild(elem);
}



function download_dataset() {
  console.log("downloading dataset ...")
  let include = [];  // CRITICAL FIX: Add missing let declaration
  let additions = [];  // CRITICAL FIX: Add missing let declaration
  for (let det of Detection_detections) {
    if (det.idInTile !== -1 && det.conf >= Detection_minConfidence && det.selected) {
      include.push({ 'tile': det.tile, 'detection': det.idInTile, 'id': det.originalId });
      //console.log(" including detection #" + (det.originalId));
    }
    if (det.idInTile === -1) {
      const tile = Tile_tiles[det.tile];
      additions.push({
        'tile': det.tile,
        'centerx': (((det.x1 + det.x2) / 2) - tile.x1) / (tile.x2 - tile.x1),
        'centery': (((det.y1 + det.y2) / 2) - tile.y1) / (tile.y2 - tile.y1),
        'w': (det.x2 - det.x1) / (tile.x2 - tile.x1),
        'h': (det.y1 - det.y2) / (tile.y1 - tile.y2)
      })
    }
  }

  // package all this up for the request
  let formData = new FormData();
  formData.append("include", JSON.stringify(include));
  formData.append("additions", JSON.stringify(additions));

  // post the arguments, get the dataset
  fetch("getdataset", { method: 'POST', body: formData })
    .then(response => response.blob())
    .then(blob => {
      // create a temp anchor element
      let elem = window.document.createElement('a');

      // direct it to the blob and filename
      elem.href = window.URL.createObjectURL(blob);
      elem.download = "dataset.zip";

      // briefly insert it into the document, click it, remove it
      document.body.appendChild(elem);
      elem.click();
      document.body.removeChild(elem);
    })
    .catch(error => {
      console.log("error in download: " + error);
    });
}

function download_csv() {
  let text = "id,selected,inside_boundary,meets threshold,latitude (deg),longitude (deg),distance from center (m),address,confidence\n";  // CRITICAL FIX: Add missing let declaration
  for (let i = 0; i < Detection_detections.length; i++) {
    let det = Detection_detections[i];
    text += [
      i,
      det['selected'],
      reviewCheckBox.checked || det.inside,
      det['conf'] >= confSlider.value / 100,
      det.getCenter()[1].toFixed(8),
      det.getCenter()[0].toFixed(8),
      getDistance(det.getCenter(), currentMap.getCenter()).toFixed(1),
      ("\"" + det['address'] + "\""),
      det['conf'].toFixed(2)
    ].join(",") + "\n";
  }
  download("detections.csv", text);
}

function download_kml() {
  let text = '<?xml version="1.0" encoding="UTF-8"?>\n';  // CRITICAL FIX: Add missing let declaration
  text += '<kml xmlns="http://www.opengis.net/kml/2.2">\n';
  text += "  <Document>\n";
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

  for (let det of Detection_detections) {
    let inside = reviewCheckBox.checked || det.inside;
    if (det.conf >= Detection_minConfidence && det.selected && inside) {
      text += "    <Placemark>\n";
      text += '      <name>' + det.address + '</name>\n'
      // Defensive check for tile metadata in KML export
      let tileMeta = (Tile_tiles[det.tile] && Tile_tiles[det.tile].metadata) ? Tile_tiles[det.tile].metadata : '';
      text += '      <description>P(' + det.conf.toFixed(2) + ') at ' + det.address + ' ' + tileMeta + '</description>\n';
      text += "      <styleUrl>#icon-1736-0F9D58</styleUrl>\n"
      text += '      <Point>\n';
      text += '        <altitudeMode>relativeToGround</altitudeMode>\n';
      text += '        <extrude>1</extrude>\n'
      text += '        <coordinates>' + det.getCenter()[0] + ',' + det.getCenter()[1] + ',300</coordinates>\n'
      text += '      </Point>\n';
      text += "    </Placemark>\n";
    }
  }
  text += "  </Document>\n";
  text += '</kml>\n';
  download("detections.kml", text);
}

//
// model upload functionality
// 

function uploadModel() {
  let model = document.getElementById("upload_model").files[0];
  let formData = new FormData();

  Detection.resetAll();
  console.log("Model upload request in progress ...")

  formData.append("model", model);
  fetch('/uploadmodel', { method: "POST", body: formData })
    .then(response => {
      console.log("installed model " + model);
      fillEngines();
    })
    .catch(error => {
      console.log(error);
    });
}


//
// file upload functionality
//

function uploadImage() {
  let image = document.getElementById("upload_file").files[0];
  let engine = $('input[name=model]:checked', '#engines').val()
  let formData = new FormData();

  Detection.resetAll();
  console.log("Custome image detection request in progress ...")

  formData.append("image", image);
  formData.append("engine", engine)
  fetch('/getobjectscustom', { method: "POST", body: formData })
    .then(response => response.json())
    .then(response => {
      response = response[0];
      console.log(response.length + " object" + (response.length == 1 ? "" : "s") + " detected");
      console.log("loading file " + image.name);
      drawCustomImage("/uploads/" + image.name);
    })
    .catch(error => {
      console.log(error);
    });
}

function drawCustomImage(url) {
  let img = document.getElementById('canvas');
  img.src = url;
  if (img.complete) {
    removeCustomImage(url)
  } else {
    img.addEventListener('load', () => { removeCustomImage(url); }, { once: true });
  }
}

function removeCustomImage(url) {
  fetch('/rm' + url, { method: "GET" });
}




//
// upload dataset functionality
// 

function uploadDataset() {
  if (Detection_detections.length > 0) {
    if (!window.confirm("This will erase current detections. Proceed?")) {
      return;
    }
  }

  let dataset = document.getElementById("upload_dataset").files[0];
  let formData = new FormData();

  Detection.resetAll();
  console.log("Dataset upload request in progress ...")
  let startTime = performance.now();


  formData.append("dataset", dataset);
  fetch('/uploaddataset', { method: "POST", body: formData })
    .then(response => response.json())
    .then(response => {
      processObjects(response, startTime);
    })
    .catch(error => {
      console.log(error);
    });
}

//
// estimate number of tiles
//

function estimateNumTiles(zoom, bounds) {
  // cop-out: do it from zoom, does not take window size into account
  let num = Math.pow(2, (19 - zoom) * 2 + 1);
  return Math.ceil(num);
}

//
// progress bar
//

let progressTimer = null;
let totalSecsEstimated = 0;
let secsElapsed = 0;
let numTiles = 0;
let secsPerTile = CONFIG.SECS_PER_TILE_DEFAULT;
let dataPoints = 0;

function enableProgress(tiles) {
  document.getElementById("progress_div").style.display = "flex";

  // Clear any existing progress timer to prevent memory leaks
  if (progressTimer !== null) {
    clearInterval(progressTimer);
  }
  progressTimer = setInterval(progressFunction, CONFIG.PROGRESS_UPDATE_INTERVAL_MS);
  numTiles = tiles;
  totalSecsEstimated = secsPerTile * numTiles;
  secsElapsed = 0;
}
function fatalError(msg) {
  const div = document.getElementById("fatal_div");
  div.style.display = "flex";
  div.innerHTML = `
    <div style="background: white; padding: 30px; border-radius: 8px; 
                max-width: 500px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
      <p style="color: #d32f2f; font-weight: bold; font-size: 18px; margin-bottom: 15px;">
        ⚠️ Error
      </p>
      <p style="color: #333; margin-bottom: 20px;">${msg}</p>
      <button onclick="this.closest('#fatal_div').style.display='none'; location.reload();" 
              style="background: #1976d2; color: white; border: none; padding: 10px 20px; 
                     border-radius: 4px; cursor: pointer; margin-right: 10px;">
        Refresh Application
      </button>
      <button onclick="this.closest('#fatal_div').style.display='none'" 
              style="background: #757575; color: white; border: none; padding: 10px 20px; 
                     border-radius: 4px; cursor: pointer;">
        Dismiss
      </button>
    </div>
  `;
}

function disableProgress(time, actualTiles) {
  document.getElementById("progress_div").style.display = "none";

  clearInterval(progressTimer);
  if (time !== 0) {
    let secsPerTileLast = time / actualTiles;
    secsPerTile = (secsPerTile * dataPoints + secsPerTileLast) / (dataPoints + 1);
    dataPoints++;
  }
}
function progressFunction() {
  secsElapsed += 0.1;
  setProgress(secsElapsed / totalSecsEstimated * 100);
}

function setProgress(val) {
  document.getElementById("progress").value = String(val);
}


// debug helper: rerouting console.log into the window

class myConsole {
  constructor() {
    this.textArea = document.getElementById("output");
    this.console = console;
    // console.log("output area: " + this.textArea);
  }

  print(text) {
    this.textArea.innerText += text;
  }

  warn(text) {
    this.console.warn(text);
  }

  error(text) {
    this.console.error(text);
  }

  newLine() {
    this.textArea.innerHTML += "<br>";
    this.textArea.scrollTop = 99999;
  }

  log(text) {
    this.print(text);
    this.newLine();
  }
}

//
// initial position
//

function setMyLocation() {
  if (location.protocol === 'https:' && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    googleMap.setCenter(nyc);
  }
}

function showPosition(position) {
  googleMap.setCenter([position.coords.longitude, position.coords.latitude]);
}


//
// zipcode lookup
//

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

// Provider detection and UI management
function detectAvailableProviders() {
  console.log("Detecting available providers...");

  const availableProviders = [];

  // Check Google Maps availability (API key and global variable)
  if (typeof gak !== 'undefined' && gak) {
    availableProviders.push('google');
    console.log("Google Maps provider available");
  } else {
    console.warn("Google Maps provider unavailable - missing API key");
  }

  // Check Azure Maps availability (API key and global variable)
  if (typeof aak !== 'undefined' && aak) {
    availableProviders.push('azure');
    console.log("Azure Maps provider available");
  } else {
    console.warn("Azure Maps provider unavailable - missing API key");
  }

  return availableProviders;
}

function updateProviderUI(availableProviders) {
  console.log("Updating provider UI for available providers:", availableProviders);

  // Get radio button elements
  const googleRadio = document.getElementById('google');
  const azureRadio = document.getElementById('azure');
  const googleLabel = document.querySelector('label[for="google"]');
  const azureLabel = document.querySelector('label[for="azure"]');

  // Update Google Maps UI
  if (availableProviders.includes('google')) {
    googleRadio.disabled = false;
    googleLabel.style.color = '';
    googleLabel.title = 'Google Maps provider available';
  } else {
    googleRadio.disabled = true;
    googleLabel.style.color = '#999';
    googleLabel.title = 'Google Maps API key not configured';
  }

  // Update Azure Maps UI  
  if (availableProviders.includes('azure')) {
    azureRadio.disabled = false;
    azureLabel.style.color = '';
    azureLabel.title = 'Azure Maps provider available';
  } else {
    azureRadio.disabled = true;
    azureLabel.style.color = '#999';
    azureLabel.title = 'Azure Maps API key not configured';
  }

  // Auto-select first available provider
  if (availableProviders.length > 0) {
    if (!googleRadio.checked && !azureRadio.checked) {
      // No provider selected, select first available
      const firstProvider = availableProviders[0];
      if (firstProvider === 'google') {
        googleRadio.checked = true;
      } else if (firstProvider === 'azure') {
        azureRadio.checked = true;
      }

      // Trigger setMap to initialize the selected provider
      timerManager.setTimeout(() => setMap(), CONFIG.PROVIDER_SWITCH_DELAY_MS);
    } else if (googleRadio.checked && !availableProviders.includes('google')) {
      // Google selected but not available, switch to Azure if available
      if (availableProviders.includes('azure')) {
        azureRadio.checked = true;
        googleRadio.checked = false;
        timerManager.setTimeout(() => setMap(), CONFIG.PROVIDER_SWITCH_DELAY_MS);
      }
    } else if (azureRadio.checked && !availableProviders.includes('azure')) {
      // Azure selected but not available, switch to Google if available  
      if (availableProviders.includes('google')) {
        googleRadio.checked = true;
        azureRadio.checked = false;
        timerManager.setTimeout(() => setMap(), CONFIG.PROVIDER_SWITCH_DELAY_MS);
      }
    }
  } else {
    // No providers available - show configuration guidance
    showProviderConfigurationGuidance();
  }
}

function showProviderConfigurationGuidance() {
  console.warn("No map providers available");

  // Create or update guidance message
  let guidanceDiv = document.getElementById('provider-guidance');
  if (!guidanceDiv) {
    guidanceDiv = document.createElement('div');
    guidanceDiv.id = 'provider-guidance';
    guidanceDiv.style.cssText = 'background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 4px; font-size: 12px;';

    // Insert after the provider form
    const providerForm = document.getElementById('uis');
    providerForm.parentNode.insertBefore(guidanceDiv, providerForm.nextSibling);
  }

  guidanceDiv.innerHTML = `
    <strong>⚠️ Configuration Required</strong><br>
    No map providers are configured. Please set environment variables:<br>
    • <code>GOOGLE_API_KEY</code> for Google Maps<br>
    • <code>AZURE_MAPS_SUBSCRIPTION_KEY</code> for Azure Maps<br>
    <small>At least one provider is required for map functionality.</small>
  `;
}

function initializeProviderManagement() {
  const availableProviders = detectAvailableProviders();
  updateProviderUI(availableProviders);

  // Enhanced error handling for map provider initialization
  try {
    // The existing initialization code will run after this
    console.log("Provider management initialized successfully");
  } catch (error) {
    console.error("Provider management initialization failed:", error);
    showProviderConfigurationGuidance();
  }
}

// init actions
console = new myConsole();

// Initialize application after DOM is ready
document.addEventListener('DOMContentLoaded', function () {
  console.log('🚀 DOM ready - initializing TowerScout...');

  try {
    // Initialize global error handling first
    TowerScoutErrorHandler.setupGlobalErrorHandling();

    // Initialize DOM references first
    initializeDOMReferences();

    // Initialize provider management first (needed for backend sync)
    initializeProviderManagement();

    // Show about screen immediately while initialization proceeds
    console.log('📺 Showing about screen...');
    if (typeof dev !== 'undefined' && dev === 0) {
      about(6);
    } else {
      about(0); // Skip in dev mode
    }

    // Sync UI with backend provider defaults (Phase 2 improvement)
    syncUIWithBackendProviders()
      .then(async () => {

        // Initialize provider-aware search
        initializeProviderAwareSearch();

        // Setup UI components
        fillEngines();
        await fillProviders();
        confSlider.value = Math.round(Detection_minConfidence * 100);

        // Initialization complete - enable provider switching
        isInitializing = false;
        console.log('🎉 Initialization complete - provider switching enabled');

        // Apply stored provider preference if any
        const preferredProvider = localStorage.getItem('preferredMapProvider');
        if (preferredProvider && currentUI && currentUI.value !== preferredProvider) {
          console.log(`🔄 Applying stored provider preference: ${preferredProvider}`);
          const targetRadio = document.querySelector(`input[name="uis"][value="${preferredProvider}"]`);
          if (targetRadio) {
            targetRadio.checked = true;
            currentUI = targetRadio;
            // Now provider switching will work since isInitializing = false
            await setMap(targetRadio);
          }
        }

        console.log("✅ TowerScout initialized successfully.");

        // Show initialization success
        TowerScoutErrorHandler.showUserNotification(
          'TowerScout loaded successfully',
          'info',
          3000
        );

        // Validate map integrity after initialization
        timerManager.setTimeout(() => {
          validateMapIntegrity();
        }, CONFIG.MAP_VALIDATION_DELAY_MS);
      })
      .catch(async error => {
        console.error('❌ Backend provider sync failed:', error);

        // Fallback to local initialization with better error handling
        console.log('🔄 Falling back to local provider initialization...');

        try {
          initializeProviderManagement();
          initializeProviderAwareSearch();
          fillEngines();
          await fillProviders();

          // Set defaults
          if (confSlider) {
            confSlider.value = Math.round(Detection_minConfidence * 100);
          }

          // Show about screen in dev mode
          if (typeof dev !== 'undefined') {
            if (dev === 0) {
              about(6);
            } else {
              about(0);
            }
          }

          console.log("✅ TowerScout initialized successfully (fallback mode).");

          TowerScoutErrorHandler.showUserNotification(
            'TowerScout loaded (using default settings)',
            'warning',
            5000
          );
        } catch (fallbackError) {
          console.error('❌ Fallback initialization also failed:', fallbackError);
          TowerScoutErrorHandler.showUserNotification(
            'TowerScout initialization failed: ' + fallbackError.message,
            'error',
            10000
          );
        }
      });

  } catch (error) {
    console.error('💥 Critical initialization error:', error);
    TowerScoutErrorHandler.showUserNotification(
      'TowerScout initialization failed: ' + error.message,
      'error',
      10000
    );
  }
});

// New function to sync UI with backend provider defaults (Phase 2)
async function syncUIWithBackendProviders() {
  console.log('🔄 Syncing UI with backend provider defaults...');

  try {
    // Check if getBackendProviders function is available
    if (typeof window.getBackendProviders !== 'function') {
      console.warn('⚠️ getBackendProviders function not available, using fallback provider detection');

      // Fallback: Use direct API call instead of template function
      try {
        const response = await fetch('/getproviders');
        const providers = await response.json();

        if (providers && providers.length > 0) {
          const defaultProvider = providers[0];
          console.log('🎯 Backend default provider (via fallback):', defaultProvider.id);

          // Store backend default provider for initialization (don't switch yet)
          console.log('📌 Storing backend default provider:', defaultProvider.id);
          providerManager.currentProvider = defaultProvider.id;

          // Update UI radio button to match
          const googleRadio = document.getElementById('providers-google');
          const azureRadio = document.getElementById('providers-azure');

          if (googleRadio && azureRadio) {
            if (defaultProvider.id === 'google') {
              googleRadio.checked = true;
              azureRadio.checked = false;
            } else if (defaultProvider.id === 'azure') {
              azureRadio.checked = true;
              googleRadio.checked = false;
            }

            console.log('✅ UI provider selection synced with backend default (fallback method)');
          }

          return providers;
        } else {
          console.warn('⚠️ No providers returned from backend');
          return [];
        }
      } catch (fallbackError) {
        console.error('❌ Fallback provider sync also failed:', fallbackError);
        throw new Error('Unable to sync with backend providers: ' + fallbackError.message);
      }
    }

    // Original implementation when getBackendProviders is available
    const providers = await window.getBackendProviders();

    if (providers && providers.length > 0) {
      const defaultProvider = providers[0];
      console.log('🎯 Backend default provider:', defaultProvider.id);

      // Store backend default provider for initialization (don't switch yet)
      console.log('📌 Storing backend default provider:', defaultProvider.id);
      providerManager.currentProvider = defaultProvider.id;

      // Update UI radio button to match
      const googleRadio = document.getElementById('providers-google');
      const azureRadio = document.getElementById('providers-azure');

      if (googleRadio && azureRadio) {
        if (defaultProvider.id === 'google') {
          googleRadio.checked = true;
          azureRadio.checked = false;
        } else if (defaultProvider.id === 'azure') {
          azureRadio.checked = true;
          googleRadio.checked = false;
        }

        console.log('✅ UI provider selection synced with backend default');
      }

      return providers;
    } else {
      console.warn('⚠️ No providers returned from backend');
      return [];
    }
  } catch (error) {
    console.error('❌ Failed to sync with backend providers:', error);
    throw error;
  }
}

// Map validation function to ensure integrity after sizing changes

// Map validation function to ensure integrity after sizing changes
function validateMapIntegrity() {
  console.log('🔍 Validating map integrity after sizing changes...');

  // Test center coordinates
  if (currentMap && typeof currentMap.getCenter === 'function') {
    let center = currentMap.getCenter();
    console.log('Current map center:', center);

    if (!center || !Array.isArray(center) || center.length !== 2) {
      console.error('❌ Invalid map center after resize');
      return false;
    }
  }

  // Test map bounds
  if (currentMap && typeof currentMap.getBounds === 'function') {
    let bounds = currentMap.getBounds();
    console.log('Current map bounds:', bounds);
  }

  console.log('✅ Map integrity validated');
  return true;
}

// Fallback initialization for older browsers
if (document.readyState === 'loading') {
  // DOM is still loading
  console.log('📝 DOM loading - event listener registered');
} else {
  // DOM already loaded - run initialization immediately
  console.log('📝 DOM already loaded - initializing immediately');
  timerManager.setTimeout(() => {
    const event = new Event('DOMContentLoaded');
    document.dispatchEvent(event);
  }, 0);
}

