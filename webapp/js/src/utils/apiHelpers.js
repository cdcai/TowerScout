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

  const logger = window.TowerScoutLogger || {
    info() {},
    debug() {}
  };

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const error = new Error(data.message || data.error || `Request failed with status ${response.status}`);
      error.status = response.status;
      error.payload = data;
      error.details = data.details || {};
      error.category = data.category || (data.details && data.details.category);
      throw error;
    }

    return data;
  }

  function providerFailureMessage(displayName, payload) {
    if (!payload) {
      return '';
    }

    const details = payload.details || {};
    const message = payload.message || payload.technical_message || payload.error || 'Validation failed.';
    const category = payload.category || details.category;
    const supportAction = payload.support_action || details.support_action;
    const repairCommand = payload.repair_command || details.repair_command;
    const parts = [`${displayName}: ${message}`];
    if (category) {
      parts.push(`Category: ${category}.`);
    }
    if (supportAction) {
      parts.push(supportAction);
    }
    if (repairCommand && (!supportAction || !supportAction.includes(repairCommand))) {
      parts.push(`Suggested command: ${repairCommand}`);
    }
    return parts.join(' ');
  }

  function saveFailureMessage(error) {
    const payload = error.payload || {};
    const validationResults = payload.validation_results || {};
    const messages = [];

    if (validationResults.google && validationResults.google.valid !== true) {
      messages.push(providerFailureMessage('Google Maps', validationResults.google));
    }
    if (validationResults.azure && validationResults.azure.valid !== true) {
      messages.push(providerFailureMessage('Azure Maps', validationResults.azure));
    }

    return [payload.message || error.message, ...messages].filter(Boolean).join(' ');
  }

  async function syncUIWithBackendProviders() {
    logger.info('Syncing configured providers from current UI state...');

    if (window.needsSetup) {
      logger.info('Setup is required before provider sync can continue.');
      return [];
    }

    const providerRadios = Array.from(document.querySelectorAll('#providers input[name="provider"]'));
    if (providerRadios.length === 0) {
      logger.debug('Provider radios are not ready yet; skipping sync.');
      return [];
    }

    const checkedProvider = providerRadios.find(radio => radio.checked) || providerRadios[0];
    if (checkedProvider) {
      providerManager.currentProvider = checkedProvider.value;
      logger.info('Current detection provider:', checkedProvider.value);
    }

    return providerRadios.map(radio => ({
      id: radio.value,
      name: radio.nextElementSibling ? radio.nextElementSibling.textContent : radio.value
    }));
  }

  function validateMapIntegrity() {
    if (window.needsSetup) {
      logger.debug('Setup-required mode active - skipping map integrity validation');
      return true;
    }

    logger.debug('Validating map integrity after sizing changes...');

    if (currentMap && typeof currentMap.getCenter === 'function') {
      const center = currentMap.getCenter();
      logger.debug('Current map center:', center);

      if (!center || !Array.isArray(center) || center.length !== 2) {
        console.error('Invalid map center after resize');
        return false;
      }
    }

    if (currentMap && typeof currentMap.getBounds === 'function') {
      const bounds = currentMap.getBounds();
      logger.debug('Current map bounds:', bounds);
    }

    logger.debug('Map integrity validated');
    return true;
  }

  window.TowerScoutConfigApi = {
    fetchJson,
    providerFailureMessage,
    saveFailureMessage
  };
  window.syncUIWithBackendProviders = syncUIWithBackendProviders;
  window.validateMapIntegrity = validateMapIntegrity;

  logger.debug('API Helpers module loaded (backend sync, map validation)');
})();
