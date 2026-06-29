(function () {
  'use strict';

  let isDirty = false;
  let originalState = {
    google: '',
    azure: '',
    defaultProvider: 'azure'
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

  function updateIndicatorsFromValidation(validationResults = {}) {
    if (validationResults.google) {
      updateIndicator('settings_google_status', validationResults.google.valid === true);
    }
    if (validationResults.azure) {
      updateIndicator('settings_azure_status', validationResults.azure.valid === true);
    }
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

  function getSettingsElement() {
    return document.getElementById('settings_div');
  }

  function updateIndicator(elementId, isValid) {
    const indicator = document.getElementById(elementId);
    if (!indicator) {
      return;
    }

    if (isValid === null) {
      indicator.textContent = '';
      indicator.classList.remove('valid', 'invalid');
      return;
    }

    indicator.textContent = isValid ? 'OK' : 'X';
    indicator.classList.toggle('valid', isValid);
    indicator.classList.toggle('invalid', !isValid);
  }

  function readCurrentState() {
    return {
      google: document.getElementById('settings_google_key').value.trim(),
      azure: document.getElementById('settings_azure_key').value.trim(),
      defaultProvider: document.getElementById('settings_default_provider').value
    };
  }

  function setDirty(nextDirty) {
    isDirty = nextDirty;
  }

  function isDebugModeEnabled() {
    if (window.TowerScoutLogger && typeof window.TowerScoutLogger.isDebugEnabled === 'function') {
      return window.TowerScoutLogger.isDebugEnabled();
    }

    try {
      return localStorage.getItem('debugMode') === 'true';
    } catch (_error) {
      return false;
    }
  }

  function toggleKeyVisibility(provider) {
    const input = document.getElementById(provider === 'google' ? 'settings_google_key' : 'settings_azure_key');
    if (!input) {
      return;
    }

    input.type = input.type === 'password' ? 'text' : 'password';
  }

  async function loadStatus() {
    const status = await fetchJson('/api/config/status');
    document.getElementById('settings_google_preview').textContent = status.google.preview ? `Current value: ${status.google.preview}` : 'No Google key configured.';
    document.getElementById('settings_azure_preview').textContent = status.azure.preview ? `Current value: ${status.azure.preview}` : 'No Azure key configured.';
    document.getElementById('settings_default_provider').value = status.default_map_provider || 'azure';
    originalState = {
      google: '',
      azure: '',
      defaultProvider: document.getElementById('settings_default_provider').value
    };
    document.getElementById('settings_google_key').value = '';
    document.getElementById('settings_azure_key').value = '';
    updateIndicator('settings_google_status', null);
    updateIndicator('settings_azure_status', null);
    setDirty(false);
  }

  async function loadPerformance() {
    const container = document.getElementById('settings_performance_stats');
    if (!container) {
      return;
    }

    try {
      const stats = await fetchJson('/api/config/performance');
      if (!stats.session_count) {
        container.innerHTML = '<p>No recent performance history available yet.</p>';
        return;
      }

      container.innerHTML = `
        <p>Recent sessions: ${stats.session_count}</p>
        <p>Average: ${stats.avg_tiles_per_second.toFixed(2)} tiles/second</p>
        <p>Last detection: ${stats.last_detection_timestamp || 'Unavailable'}</p>
      `;
    } catch (_error) {
      container.innerHTML = '<p>Unable to load performance data.</p>';
    }
  }

  async function open() {
    const settings = getSettingsElement();
    if (!settings) {
      return;
    }

    await loadStatus();
    await loadPerformance();
    document.getElementById('debug_mode_toggle').checked = isDebugModeEnabled();
    settings.style.display = 'flex';
  }

  function close(force = false) {
    if (!force && isDirty) {
      const shouldClose = window.confirm('Discard unsaved settings changes?');
      if (!shouldClose) {
        return;
      }
    }

    const settings = getSettingsElement();
    if (settings) {
      settings.style.display = 'none';
    }
    setDirty(false);
  }

  async function saveKeys() {
    const state = readCurrentState();

    try {
      const result = await fetchJson('/api/config/save-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          google_api_key: state.google,
          azure_maps_subscription_key: state.azure,
          default_map_provider: state.defaultProvider
        })
      });
      updateIndicatorsFromValidation(result.validation_results);

      originalState = { ...state };
      setDirty(false);
      const failedGoogle = result.validation_results && result.validation_results.google && result.validation_results.google.valid !== true;
      const failedAzure = result.validation_results && result.validation_results.azure && result.validation_results.azure.valid !== true;
      if (failedGoogle || failedAzure) {
        const messages = [];
        if (failedGoogle) {
          messages.push(providerFailureMessage('Google Maps', result.validation_results.google));
        }
        if (failedAzure) {
          messages.push(providerFailureMessage('Azure Maps', result.validation_results.azure));
        }
        TowerScoutErrorHandler.showUserNotification(`Settings saved. ${messages.join(' ')}`, 'info');
      } else {
        TowerScoutErrorHandler.showUserNotification('Settings saved successfully.', 'success');
      }
      await loadStatus();
    } catch (error) {
      updateIndicatorsFromValidation((error.payload && error.payload.validation_results) || {});
      TowerScoutErrorHandler.showUserNotification(saveFailureMessage(error), 'error');
    }
  }

  function toggleDebugMode() {
    const enabled = document.getElementById('debug_mode_toggle').checked;
    if (window.TowerScoutLogger && typeof window.TowerScoutLogger.setDebugMode === 'function') {
      window.TowerScoutLogger.setDebugMode(enabled);
    } else {
      localStorage.setItem('debugMode', String(enabled));
      window.TOWERSCOUT_DEBUG = enabled;
    }

    TowerScoutErrorHandler.showUserNotification(
      enabled ? 'Debug mode enabled. Extra application and browser console detail is now visible.' : 'Debug mode disabled. Extra application and browser console detail is now hidden.',
      enabled ? 'success' : 'info'
    );
  }

  async function clearCache() {
    const confirmed = window.confirm('Clear session data and temporary files?');
    if (!confirmed) {
      return;
    }

    try {
      await fetchJson('/api/config/reset-session', {
        method: 'POST'
      });
      close(true);
      window.location.reload();
    } catch (error) {
      TowerScoutErrorHandler.showUserNotification(error.message, 'error');
    }
  }

  function trackChanges() {
    const trackedIds = ['settings_google_key', 'settings_azure_key', 'settings_default_provider'];
    trackedIds.forEach(id => {
      const element = document.getElementById(id);
      if (!element || element.dataset.settingsTracked === 'true') {
        return;
      }

      element.addEventListener('input', () => setDirty(true));
      element.addEventListener('change', () => setDirty(true));
      element.dataset.settingsTracked = 'true';
    });
  }

  function init() {
    trackChanges();
  }

  window.Settings = {
    init,
    open,
    close,
    saveKeys,
    toggleKeyVisibility,
    toggleDebugMode,
    clearCache
  };

  document.addEventListener('DOMContentLoaded', init);
})();
