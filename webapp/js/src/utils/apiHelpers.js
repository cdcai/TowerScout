/**
 * STAGE 5 - UI & Final Integration
 * Module: apiHelpers.js
 * Purpose: Backend API communication and synchronization utilities
 * 
 * Functions:
 * - syncUIWithBackendProviders(): Synchronize UI provider selection with backend defaults
 * - validateMapIntegrity(): Validate map state after sizing or initialization changes
 * 
 * Dependencies:
 * - providers/ProviderManager.js (providerManager)
 * - window.getBackendProviders (template function, optional)
 * 
 * Exposed to window: syncUIWithBackendProviders, validateMapIntegrity
 */

(function () {
  'use strict';

  // ===== Backend API Synchronization =====

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

  // ===== Map Validation =====

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

  // ===== Expose to window for global access =====
  window.syncUIWithBackendProviders = syncUIWithBackendProviders;
  window.validateMapIntegrity = validateMapIntegrity;

  console.log('✅ API Helpers module loaded (backend sync, map validation)');

})();
