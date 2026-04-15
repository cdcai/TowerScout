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

  async function syncUIWithBackendProviders() {
    window.TowerScoutLogger.info('Syncing configured providers from current UI state...');

    if (window.needsSetup) {
      window.TowerScoutLogger.info('Setup is required before provider sync can continue.');
      return [];
    }

    const providerRadios = Array.from(document.querySelectorAll('#providers input[name="provider"]'));
    if (providerRadios.length === 0) {
      window.TowerScoutLogger.debug('Provider radios are not ready yet; skipping sync.');
      return [];
    }

    const checkedProvider = providerRadios.find(radio => radio.checked) || providerRadios[0];
    if (checkedProvider) {
      providerManager.currentProvider = checkedProvider.value;
      window.TowerScoutLogger.info('Current detection provider:', checkedProvider.value);
    }

    return providerRadios.map(radio => ({
      id: radio.value,
      name: radio.nextElementSibling ? radio.nextElementSibling.textContent : radio.value
    }));
  }

  function validateMapIntegrity() {
    if (window.needsSetup) {
      window.TowerScoutLogger.debug('Setup-required mode active - skipping map integrity validation');
      return true;
    }

    window.TowerScoutLogger.debug('Validating map integrity after sizing changes...');

    if (currentMap && typeof currentMap.getCenter === 'function') {
      const center = currentMap.getCenter();
      window.TowerScoutLogger.debug('Current map center:', center);

      if (!center || !Array.isArray(center) || center.length !== 2) {
        console.error('Invalid map center after resize');
        return false;
      }
    }

    if (currentMap && typeof currentMap.getBounds === 'function') {
      const bounds = currentMap.getBounds();
      window.TowerScoutLogger.debug('Current map bounds:', bounds);
    }

    window.TowerScoutLogger.debug('Map integrity validated');
    return true;
  }

  window.syncUIWithBackendProviders = syncUIWithBackendProviders;
  window.validateMapIntegrity = validateMapIntegrity;

  window.TowerScoutLogger.debug('API Helpers module loaded (backend sync, map validation)');
})();
