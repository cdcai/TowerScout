#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '../..');
const SETUP_WIZARD_PATH = path.join(ROOT, 'webapp/js/src/setup-wizard.js');

function createClassList() {
  const values = new Set();
  return {
    toggle(name, enabled) {
      if (enabled) {
        values.add(name);
      } else {
        values.delete(name);
      }
    },
    remove(...names) {
      names.forEach(name => values.delete(name));
    },
    contains(name) {
      return values.has(name);
    }
  };
}

function createElement(id, value = '') {
  return {
    id,
    value,
    textContent: '',
    disabled: false,
    checked: false,
    style: { display: 'none' },
    classList: createClassList(),
    dataset: {}
  };
}

function createContext() {
  const elements = {
    setup_wizard_div: createElement('setup_wizard_div'),
    wizard_google_key: createElement('wizard_google_key', 'bad-google-key'),
    wizard_azure_key: createElement('wizard_azure_key', 'valid-azure-key'),
    wizard_validation_message: createElement('wizard_validation_message'),
    google_key_status: createElement('google_key_status'),
    azure_key_status: createElement('azure_key_status'),
    wizard_validate_button: createElement('wizard_validate_button'),
    wizard_save_button: createElement('wizard_save_button'),
    wizard_performance_stats: createElement('wizard_performance_stats')
  };
  const steps = [1, 2, 3, 4, 5].map(stepNumber => ({
    dataset: { step: String(stepNumber) },
    style: { display: 'none' },
    classList: createClassList()
  }));
  const indicators = [1, 2, 3, 4, 5].map(stepNumber => ({
    dataset: { step: String(stepNumber) },
    classList: createClassList()
  }));
  const providerOptions = {
    google: createElement('default_provider_google'),
    azure: createElement('default_provider_azure')
  };
  providerOptions.google.value = 'google';
  providerOptions.azure.value = 'azure';

  const document = {
    body: { classList: createClassList() },
    getElementById(id) {
      return elements[id] || null;
    },
    querySelector(selector) {
      if (selector === '#wizard_google_provider_option input') {
        return providerOptions.google;
      }
      if (selector === '#wizard_azure_provider_option input') {
        return providerOptions.azure;
      }
      if (selector === 'input[name="default_provider"]:checked') {
        return Object.values(providerOptions).find(option => option.checked) || null;
      }
      return null;
    },
    querySelectorAll(selector) {
      if (selector === '#setup_wizard_div .wizard-step') {
        return steps;
      }
      if (selector === '#setup_wizard_div .wizard-progress .step') {
        return indicators;
      }
      return [];
    },
    addEventListener() {}
  };

  const fetchCalls = [];
  let savePayload = null;
  const notifications = [];
  const context = {
    console,
    document,
    fetchCalls,
    get savePayload() {
      return savePayload;
    },
    window: {},
    TowerScoutErrorHandler: {
      showUserNotification(message, type) {
        notifications.push({ message, type });
      }
    },
    async fetch(url, options = {}) {
      if (url === '/api/config/validate-key') {
        const body = JSON.parse(options.body);
        fetchCalls.push(body.provider);
        if (body.provider === 'google') {
          return {
            ok: false,
            status: 502,
            async json() {
              return { message: 'TowerScout could not reach Google Maps from the local server.' };
            }
          };
        }
        return {
          ok: true,
          status: 200,
          async json() {
            return { valid: true, message: 'Azure Maps subscription key validated successfully.' };
          }
        };
      }

      if (url === '/api/config/save-keys') {
        savePayload = JSON.parse(options.body);
        return {
          ok: true,
          status: 200,
          async json() {
            return { success: true };
          }
        };
      }

      if (url === '/api/config/performance') {
        return {
          ok: true,
          status: 200,
          async json() {
            return { session_count: 0 };
          }
        };
      }

      throw new Error(`Unexpected fetch URL: ${url}`);
    }
  };
  context.window = {
    window: null,
    needsSetup: true,
    SetupWizard: null,
    TowerScoutErrorHandler: context.TowerScoutErrorHandler
  };
  context.window.window = context.window;

  return { context, elements, steps, providerOptions, notifications };
}

async function testSecondProviderStillValidatesAfterFirstProviderNetworkFailure() {
  const { context, elements, steps, providerOptions } = createContext();
  vm.createContext(context);
  const source = fs.readFileSync(SETUP_WIZARD_PATH, 'utf8');
  vm.runInContext(source, context, { filename: SETUP_WIZARD_PATH });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  assert.deepStrictEqual(context.fetchCalls, ['google', 'azure']);
  assert.strictEqual(elements.google_key_status.textContent, 'X');
  assert.strictEqual(elements.azure_key_status.textContent, 'OK');
  assert.strictEqual(providerOptions.google.disabled, true);
  assert.strictEqual(providerOptions.azure.disabled, false);
  assert.strictEqual(providerOptions.azure.checked, true);
  assert.strictEqual(elements.wizard_validation_message.textContent, 'Validation succeeded.');
  assert.strictEqual(steps[2].style.display, 'block');

  await context.window.SetupWizard.saveAndReview();
  assert.deepStrictEqual(context.savePayload, {
    google_api_key: '',
    azure_maps_subscription_key: 'valid-azure-key',
    default_map_provider: 'azure'
  });
}

testSecondProviderStillValidatesAfterFirstProviderNetworkFailure()
  .then(() => {
    console.log('Setup wizard validation contract PASSED');
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
