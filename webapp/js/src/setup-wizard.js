(function () {
  'use strict';

  let currentStep = 1;
  let validatedKeys = {
    google: false,
    azure: false
  };
  let validationInFlight = false;
  let saveInFlight = false;

  function getWizardElement() {
    return document.getElementById('setup_wizard_div');
  }

  function getSelectedDefaultProvider() {
    const selected = document.querySelector('input[name="default_provider"]:checked');
    return selected ? selected.value : 'azure';
  }

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.message || data.error || `Request failed with status ${response.status}`);
    }

    return data;
  }

  function setSetupBlocked(isBlocked) {
    document.body.classList.toggle('setup-required-active', isBlocked);
  }

  function showStep(stepNumber) {
    const steps = document.querySelectorAll('#setup_wizard_div .wizard-step');
    const indicators = document.querySelectorAll('#setup_wizard_div .wizard-progress .step');

    steps.forEach(step => {
      step.style.display = Number(step.dataset.step) === stepNumber ? 'block' : 'none';
    });

    indicators.forEach(step => {
      const indicatorStep = Number(step.dataset.step);
      step.classList.toggle('active', indicatorStep === stepNumber);
      step.classList.toggle('complete', indicatorStep < stepNumber);
    });

    currentStep = stepNumber;
  }

  function show() {
    const wizard = getWizardElement();
    if (!wizard) {
      return;
    }

    wizard.style.display = 'flex';
    setSetupBlocked(true);
    showStep(currentStep);
    loadPerformanceStats();
  }

  function hide() {
    const wizard = getWizardElement();
    if (!wizard) {
      return;
    }

    wizard.style.display = 'none';
    setSetupBlocked(false);
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

  function updateProviderOptions() {
    const googleOption = document.querySelector('#wizard_google_provider_option input');
    const azureOption = document.querySelector('#wizard_azure_provider_option input');

    if (googleOption) {
      googleOption.disabled = !validatedKeys.google;
    }
    if (azureOption) {
      azureOption.disabled = !validatedKeys.azure;
    }

    if (validatedKeys.google) {
      googleOption.checked = true;
    } else if (validatedKeys.azure) {
      azureOption.checked = true;
    }
  }

  async function validateKey(provider, key) {
    return fetchJson('/api/config/validate-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, key })
    });
  }

  function setButtonBusy(buttonId, isBusy, idleText, busyText) {
    const button = document.getElementById(buttonId);
    if (!button) {
      return;
    }

    button.disabled = isBusy;
    button.textContent = isBusy ? busyText : idleText;
  }

  async function validateAndNext() {
    if (validationInFlight) {
      return;
    }

    const googleKey = document.getElementById('wizard_google_key').value.trim();
    const azureKey = document.getElementById('wizard_azure_key').value.trim();
    const message = document.getElementById('wizard_validation_message');

    validatedKeys = { google: false, azure: false };
    updateIndicator('google_key_status', null);
    updateIndicator('azure_key_status', null);
    validationInFlight = true;
    setButtonBusy('wizard_validate_button', true, 'Validate Keys', 'Validating...');

    try {
      const validationMessages = [];

      if (googleKey) {
        const googleResult = await validateKey('google', googleKey);
        validatedKeys.google = googleResult.valid === true;
        updateIndicator('google_key_status', validatedKeys.google);
        if (!validatedKeys.google && googleResult.message) {
          validationMessages.push(`Google Maps: ${googleResult.message}`);
        }
      }

      if (azureKey) {
        const azureResult = await validateKey('azure', azureKey);
        validatedKeys.azure = azureResult.valid === true;
        updateIndicator('azure_key_status', validatedKeys.azure);
        if (!validatedKeys.azure && azureResult.message) {
          validationMessages.push(`Azure Maps: ${azureResult.message}`);
        }
      }

      if (!validatedKeys.google && !validatedKeys.azure) {
        throw new Error(validationMessages.join(' ') || 'Provide at least one valid API key before continuing.');
      }

      updateProviderOptions();
      if (message) {
        message.textContent = 'Validation succeeded.';
      }
      nextStep();
    } catch (error) {
      if (message) {
        message.textContent = error.message;
      }
      TowerScoutErrorHandler.showUserNotification(error.message, 'error');
    } finally {
      validationInFlight = false;
      setButtonBusy('wizard_validate_button', false, 'Validate Keys', 'Validating...');
    }
  }

  async function saveAndReview() {
    if (saveInFlight) {
      return;
    }

    const payload = {
      google_api_key: document.getElementById('wizard_google_key').value.trim(),
      azure_maps_subscription_key: document.getElementById('wizard_azure_key').value.trim(),
      default_map_provider: getSelectedDefaultProvider()
    };

    saveInFlight = true;
    setButtonBusy('wizard_save_button', true, 'Save Configuration', 'Saving...');

    try {
      await fetchJson('/api/config/save-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      window.needsSetup = false;
      nextStep();
      TowerScoutErrorHandler.showUserNotification('Configuration saved successfully.', 'success');
    } catch (error) {
      TowerScoutErrorHandler.showUserNotification(error.message, 'error');
    } finally {
      saveInFlight = false;
      setButtonBusy('wizard_save_button', false, 'Save Configuration', 'Saving...');
    }
  }

  async function loadPerformanceStats() {
    const container = document.getElementById('wizard_performance_stats');
    if (!container) {
      return;
    }

    try {
      const stats = await fetchJson('/api/config/performance');
      if (!stats.session_count) {
        container.innerHTML = '<p>No recent detection runs found yet.</p>';
        return;
      }

      container.innerHTML = `
        <p>Recent sessions: ${stats.session_count}</p>
        <p>Average throughput: ${stats.avg_tiles_per_second.toFixed(2)} tiles/second</p>
        <p>Last detection: ${stats.last_detection_timestamp || 'Unavailable'}</p>
      `;
    } catch (_error) {
      container.innerHTML = '<p>Performance metrics are not available yet.</p>';
    }
  }

  function nextStep() {
    if (currentStep < 5) {
      showStep(currentStep + 1);
    }
  }

  function prevStep() {
    if (currentStep > 1) {
      showStep(currentStep - 1);
    }
  }

  function complete() {
    hide();
    window.location.reload();
  }

  async function init() {
    try {
      const status = await fetchJson('/api/config/status');
      window.needsSetup = Boolean(status.needs_setup);
      if (window.needsSetup) {
        show();
      }
    } catch (error) {
      console.error('SetupWizard init failed:', error);
    }
  }

  window.SetupWizard = {
    init,
    show,
    hide,
    showStep,
    nextStep,
    prevStep,
    validateAndNext,
    saveAndReview,
    complete
  };

  document.addEventListener('DOMContentLoaded', init);
})();
