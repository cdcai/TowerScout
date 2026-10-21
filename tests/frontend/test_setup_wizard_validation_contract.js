#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '../..');
const API_HELPERS_PATH = path.join(ROOT, 'webapp/js/src/utils/apiHelpers.js');
const SETUP_WIZARD_PATH = path.join(ROOT, 'webapp/js/src/setup-wizard.js');
const HELPER_BASE_URL = 'http://127.0.0.1:49152';
const HELPER_PROBE_TOKEN = 'probe-authorization-should-not-render';

function createHelperBridge(
  operationAuthorization = {},
  providerTlsRepairCapability = true
) {
  return {
    base_url: HELPER_BASE_URL,
    probe: {
      path: '/health',
      scope: 'helper_probe',
      expires_at: '2999-01-01T00:00:00Z',
      authorization: HELPER_PROBE_TOKEN
    },
    operation_authorization: operationAuthorization,
    provider_tls_repair_capability: providerTlsRepairCapability,
    expected_runtime: {
      engine: 'docker',
      gpu: 'off',
      app_port: 5000
    }
  };
}

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

function createJsonResponse(ok, status, payload) {
  return {
    ok,
    status,
    async json() {
      return payload;
    }
  };
}

function createContext(options = {}) {
  const elements = {
    setup_wizard_div: createElement('setup_wizard_div'),
    wizard_google_key: createElement('wizard_google_key', 'bad-google-key'),
    wizard_azure_key: createElement('wizard_azure_key', 'valid-azure-key'),
    wizard_validation_message: createElement('wizard_validation_message'),
    google_key_status: createElement('google_key_status'),
    azure_key_status: createElement('azure_key_status'),
    wizard_validate_button: createElement('wizard_validate_button'),
    wizard_save_button: createElement('wizard_save_button'),
    wizard_performance_stats: createElement('wizard_performance_stats'),
    wizard_provider_tls_repair_panel: createElement('wizard_provider_tls_repair_panel'),
    wizard_provider_tls_repair_title: createElement('wizard_provider_tls_repair_title'),
    wizard_provider_tls_repair_message: createElement('wizard_provider_tls_repair_message'),
    wizard_provider_tls_repair_support: createElement('wizard_provider_tls_repair_support'),
    wizard_provider_tls_repair_command: createElement('wizard_provider_tls_repair_command'),
    wizard_provider_tls_repair_confirmation: createElement('wizard_provider_tls_repair_confirmation'),
    wizard_provider_tls_repair_confirm: createElement('wizard_provider_tls_repair_confirm'),
    wizard_provider_tls_repair_button: createElement('wizard_provider_tls_repair_button'),
    wizard_provider_tls_repair_status: createElement('wizard_provider_tls_repair_status')
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
  const fetchRequests = [];
  const sessionValues = new Map();
  const storageWrites = [];
  let savePayload = null;
  const notifications = [];
  const timerDelays = [];
  const consoleMessages = [];
  const testConsole = {
    log(...args) {
      consoleMessages.push(args.join(' '));
    },
    info(...args) {
      consoleMessages.push(args.join(' '));
    },
    warn(...args) {
      consoleMessages.push(args.join(' '));
    },
    error(...args) {
      consoleMessages.push(args.join(' '));
    }
  };
  const googleValidationPayload = options.googleValidationPayload || {
    error: true,
    message: 'TowerScout could not verify the Google Maps TLS certificate.',
    details: {
      provider: 'google',
      category: 'tls_ca_untrusted',
      repairable: true,
      support_action: 'Import the trusted organization/root TLS CA into the container trust store, then retry Google Maps.',
      repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
      helper_available: false
    }
  };
  const googleValidationOk = options.googleValidationOk === true;
  const googleValidationStatus = options.googleValidationStatus || (googleValidationOk ? 200 : 502);
  const azureValidationPayload = options.azureValidationPayload || {
    valid: true,
    provider: 'azure',
    category: 'tls_ok',
    repairable: false,
    helper_available: false,
    message: 'Azure Maps subscription key validated successfully.'
  };
  const configuredHelperBridge = (
    (googleValidationPayload.details || {}).helper_bridge ||
    googleValidationPayload.helper_bridge ||
    null
  );
  const context = {
    console: testConsole,
    consoleMessages,
    document,
    fetchCalls,
    fetchRequests,
    sessionValues,
    storageWrites,
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
      fetchRequests.push({ url, options });
      if (url === '/api/config/validate-key') {
        const body = JSON.parse(options.body);
        fetchCalls.push(body.provider);
        if (body.provider === 'google') {
          return createJsonResponse(googleValidationOk, googleValidationStatus, googleValidationPayload);
        }
        return createJsonResponse(true, 200, azureValidationPayload);
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

      if (url === `${HELPER_BASE_URL}/health`) {
        const helperHealthOk = Boolean(
          createContextHelperHealthEnabled &&
          options &&
          options.method === 'GET' &&
          options.cache === 'no-store' &&
          (options.headers || {})['X-TowerScout-Operation-Authorization'] === HELPER_PROBE_TOKEN
        );
        return createJsonResponse(
          helperHealthOk,
          helperHealthOk ? 200 : 503,
          helperHealthOk
            ? {
                state: 'ready',
                runtime: { engine: 'docker', gpu: 'off', app_port: 5000 },
                capabilities: {
                  provider_tls_repair: Boolean(
                    configuredHelperBridge &&
                    configuredHelperBridge.provider_tls_repair_capability === true
                  ),
                  max_active_operations: 1
                }
              }
            : { state: 'unavailable' }
        );
      }

      if (url === '/api/config/provider-tls-repair-status-authorization') {
        const operation = JSON.parse(options.body);
        const statusToken = optionsForContext.statusAuthorizationToken || 'status-authorization-should-not-render';
        const configuredResponses = optionsForContext.statusAuthorizationResponses;
        if (configuredResponses && configuredResponses.length > 0) {
          const configuredResponse = configuredResponses.shift();
          if (configuredResponse.throwError) {
            throw new Error(configuredResponse.throwError);
          }
          if (configuredResponse.status) {
            return createJsonResponse(
              configuredResponse.status < 400,
              configuredResponse.status,
              configuredResponse.payload || {}
            );
          }
        }
        return createJsonResponse(true, 200, {
          base_url: optionsForContext.statusAuthorizationBaseUrl || HELPER_BASE_URL,
          operation_id: operation.operation_id,
          status_authorization: {
            operation_type: 'provider_tls_repair',
            scope: 'operation_status',
            expires_at: '2999-01-01T00:00:00Z',
            authorization: statusToken
          }
        });
      }

      if (url === `${HELPER_BASE_URL}/operations/provider-tls-repair`) {
        const statusToken = optionsForContext.statusAuthorizationToken || 'status-authorization-should-not-render';
        const response = optionsForContext.startResponse || {
          state: 'planned',
          operation_id: '0123456789abcdef0123456789abcdef',
          operation_type: 'provider_tls_repair',
          provider: 'google',
          accepted: true,
          existing_operation: false,
          execution_enabled: false,
          current_step: 'planned',
          classification: 'pending',
          terminal: false,
          next_action: 'await_controlled_execution',
          status_authorization: {
            operation_type: 'provider_tls_repair',
            scope: 'operation_status',
            expires_at: '2999-01-01T00:00:00Z',
            authorization: statusToken
          }
        };
        return createJsonResponse(
          optionsForContext.startStatus ? optionsForContext.startStatus < 400 : true,
          optionsForContext.startStatus || 202,
          response
        );
      }

      if (String(url).startsWith(`${HELPER_BASE_URL}/operations/`)) {
        const statusResponses = optionsForContext.statusResponses || [{
          state: 'ready',
          operation_id: '0123456789abcdef0123456789abcdef',
          operation_type: 'provider_tls_repair',
          provider: 'google',
          accepted: true,
          existing_operation: false,
          execution_enabled: false,
          current_step: 'readiness_wait',
          classification: 'terminal_success',
          terminal: true,
          next_action: 'retry_provider_validation'
        }];
        const response = statusResponses.shift();
        if (response && response.throwError) {
          throw new Error(response.throwError);
        }
        return createJsonResponse(
          response.status ? response.status < 400 : true,
          response.status || 200,
          response.payload || response
        );
      }

      if (url === '/api/readiness') {
        const readinessResponses = optionsForContext.readinessResponses;
        if (readinessResponses && readinessResponses.length > 0) {
          const readinessResponse = readinessResponses.shift();
          if (readinessResponse.throwError) {
            throw new Error(readinessResponse.throwError);
          }
          return createJsonResponse(
            readinessResponse.status ? readinessResponse.status < 400 : true,
            readinessResponse.status || 200,
            readinessResponse.payload || readinessResponse
          );
        }
        return createJsonResponse(true, 200, {
          state: 'ready'
        });
      }

      throw new Error(`Unexpected fetch URL: ${url}`);
    }
  };
  const optionsForContext = options;
  const createContextHelperHealthEnabled = options.helperHealthOk !== false;
  const sessionStorage = {
    getItem(key) {
      return sessionValues.has(key) ? sessionValues.get(key) : null;
    },
    setItem(key, value) {
      sessionValues.set(key, String(value));
      storageWrites.push({ key, value: String(value) });
    },
    removeItem(key) {
      sessionValues.delete(key);
    }
  };
  context.window = {
    window: null,
    needsSetup: true,
    SetupWizard: null,
    TowerScoutErrorHandler: context.TowerScoutErrorHandler,
    sessionStorage,
    setTimeout(callback, delay = 0) {
      timerDelays.push(delay);
      callback();
      return 1;
    },
    clearTimeout() {
    }
  };
  context.window.window = context.window;

  return {
    context,
    elements,
    steps,
    providerOptions,
    notifications,
    timerDelays
  };
}

function loadSetupWizard(context, options = {}) {
  const apiHelpersSource = fs.readFileSync(API_HELPERS_PATH, 'utf8');
  vm.runInContext(apiHelpersSource, context, { filename: API_HELPERS_PATH });
  let source = fs.readFileSync(SETUP_WIZARD_PATH, 'utf8');
  if (options.enableBrowserMutation === true) {
    source = source.replace(
      'const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false;',
      'const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = true;'
    );
  }
  vm.runInContext(source, context, { filename: SETUP_WIZARD_PATH });
}

async function testSecondProviderStillValidatesAfterFirstProviderNetworkFailure() {
  const { context, elements, steps, providerOptions } = createContext();
  vm.createContext(context);
  loadSetupWizard(context);

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
  const googleValidation = context.window.SetupWizard.getProviderValidationState('google');
  assert.strictEqual(googleValidation.lastFailure.provider, 'google');
  assert.strictEqual(googleValidation.lastFailure.category, 'tls_ca_untrusted');
  assert.strictEqual(googleValidation.lastFailure.repairable, true);
  assert.strictEqual(googleValidation.lastFailure.helper_available, false);
  assert.strictEqual(
    googleValidation.lastFailure.repair_command,
    '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off'
  );
  assert.strictEqual(context.window.SetupWizard.shouldShowProviderTlsRepair('google'), true);
  assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'block');
  assert.strictEqual(elements.wizard_provider_tls_repair_button.style.display, 'none');
  assert.ok(elements.wizard_provider_tls_repair_command.textContent.includes('repair-provider-tls.cmd'));
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('helper is unavailable'));

  await context.window.SetupWizard.saveAndReview();
  assert.deepStrictEqual(context.savePayload, {
    google_api_key: '',
    azure_maps_subscription_key: 'valid-azure-key',
    default_map_provider: 'azure'
  });
}

async function testInvalidProviderKeyDoesNotExposeRepairPredicate() {
  const { context, elements } = createContext({
    googleValidationOk: true,
    googleValidationPayload: {
      valid: false,
      provider: 'google',
      category: 'invalid_provider_key',
      repairable: false,
      helper_available: false,
      repair_command: null,
      message: 'Google Maps key reached Google but was rejected.'
    }
  });
  vm.createContext(context);
  loadSetupWizard(context);

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  const googleValidation = context.window.SetupWizard.getProviderValidationState('google');
  assert.strictEqual(googleValidation.lastFailure.category, 'invalid_provider_key');
  assert.strictEqual(googleValidation.lastFailure.repairable, false);
  assert.strictEqual(googleValidation.lastFailure.helper_available, false);
  assert.strictEqual(context.window.SetupWizard.shouldShowProviderTlsRepair('google'), false);
  assert.strictEqual(context.window.SetupWizard.getProviderTlsRepairViewModel('google').visible, false);
  assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'none');
}

async function testRepairPredicateUsesAuthenticatedHelperProbe() {
  const operationToken = 'probe-backed-operation-token-should-not-render';
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Import the trusted organization/root TLS CA into the container trust store, then retry Google Maps.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: operationToken
        })
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context);

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  assert.strictEqual(context.window.SetupWizard.shouldShowProviderTlsRepair('google'), true);
  assert.strictEqual(context.window.SetupWizard.shouldShowProviderTlsRepair('azure'), false);
  const viewModel = context.window.SetupWizard.getProviderTlsRepairViewModel('google');
  assert.strictEqual(viewModel.visible, true);
  assert.strictEqual(viewModel.helper_available, true);
  assert.strictEqual(viewModel.authorization_ready, true);
  assert.strictEqual(viewModel.enabled, false);
  assert.strictEqual(viewModel.blocked_reason, 'browser_mutation_disabled');
  assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'block');
  assert.strictEqual(elements.wizard_provider_tls_repair_button.disabled, true);
  assert.strictEqual(elements.wizard_provider_tls_repair_button.textContent, 'Repair unavailable');
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('browser-triggered repair remains disabled'));
  const publicFailure = context.window.SetupWizard.getProviderValidationState('google').lastFailure;
  assert.strictEqual(publicFailure.helper_bridge.configured, true);
  assert.strictEqual(publicFailure.helper_bridge.probe, undefined);
  assert.strictEqual(JSON.stringify(publicFailure).includes(operationToken), false);
  assert.strictEqual(JSON.stringify(publicFailure).includes(HELPER_PROBE_TOKEN), false);
  assert.strictEqual(
    context.fetchRequests.some(request => request.url === `${HELPER_BASE_URL}/health`),
    true
  );
}

async function testRepairPanelPreservesTlsFallbackAndRejectsNonTlsStates() {
  const blockedScenarios = [
    {
      category: 'invalid_provider_key',
      repairable: false,
      helper_available: true
    },
    {
      category: 'provider_api_not_authorized',
      repairable: false,
      helper_available: true
    },
    {
      category: 'provider_http_error',
      repairable: false,
      helper_available: true
    },
    {
      category: 'provider_network_blocked',
      repairable: false,
      helper_available: true
    },
    {
      category: 'tls_ca_untrusted',
      repairable: true,
      helper_available: false
    },
    {
      category: 'unsupported_runtime',
      repairable: true,
      helper_available: true
    },
    {
      category: 'podman_compose_provider_unapproved',
      repairable: true,
      helper_available: true
    }
  ];

  for (const scenario of blockedScenarios) {
    const { context, elements } = createContext({
      googleValidationPayload: {
        error: true,
        message: `Google Maps validation failed with ${scenario.category}.`,
        details: {
          provider: 'google',
          category: scenario.category,
          repairable: scenario.repairable,
          support_action: 'Use provider-specific fallback guidance.',
          repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
          helper_available: scenario.helper_available
        }
      }
    });
    vm.createContext(context);
    loadSetupWizard(context);

    context.window.SetupWizard.showStep(2);
    await context.window.SetupWizard.validateAndNext();

    const showsManualTlsFallback = scenario.category === 'tls_ca_untrusted';
    assert.strictEqual(
      context.window.SetupWizard.shouldShowProviderTlsRepair('google'),
      showsManualTlsFallback,
      scenario.category
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairViewModel('google').visible,
      showsManualTlsFallback,
      scenario.category
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairStartContract('google').ready,
      false,
      scenario.category
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairStartContract('google').blocked_reason,
      showsManualTlsFallback ? 'helper_unavailable' : 'not_repairable',
      scenario.category
    );
    assert.strictEqual(
      elements.wizard_provider_tls_repair_panel.style.display,
      showsManualTlsFallback ? 'block' : 'none',
      scenario.category
    );
    if (showsManualTlsFallback) {
      assert.strictEqual(elements.wizard_provider_tls_repair_button.style.display, 'none');
      assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('helper is unavailable'));
    }
  }
}

async function testShortLivedAuthorizationDoesNotStartRepairWhileMutationGateIsClosed() {
  const operationToken = 'short-lived-operation-token-should-not-render';
  const { context, elements, notifications } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Import the trusted organization/root TLS CA into the container trust store.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: operationToken
        })
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context);

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  let viewModel = context.window.SetupWizard.getProviderTlsRepairViewModel('google');
  const publicFailure = context.window.SetupWizard.getProviderValidationState('google').lastFailure;
  assert.strictEqual(viewModel.visible, true);
  assert.strictEqual(viewModel.authorization_ready, true);
  assert.strictEqual(viewModel.enabled, false);
  assert.strictEqual(viewModel.blocked_reason, 'browser_mutation_disabled');
  assert.strictEqual(Object.values(viewModel).includes(operationToken), false);
  assert.strictEqual(publicFailure.operation_authorization.operation_type, 'provider_tls_repair');
  assert.strictEqual(publicFailure.operation_authorization.expires_at, '2999-01-01T00:00:00Z');
  assert.strictEqual(publicFailure.operation_authorization.operation_token, undefined);

  const startContract = context.window.SetupWizard.getProviderTlsRepairStartContract('google');
  assert.strictEqual(startContract.endpoint, `${HELPER_BASE_URL}/operations/provider-tls-repair`);
  assert.strictEqual(startContract.method, 'POST');
  assert.strictEqual(startContract.content_type, 'application/json');
  assert.strictEqual(startContract.provider, 'google');
  assert.strictEqual(startContract.confirmation, 'repair_tls_and_restart');
  assert.strictEqual(startContract.ready, true);
  assert.strictEqual(startContract.enabled, false);
  assert.strictEqual(startContract.blocked_reason, 'browser_mutation_disabled');
  assert.deepStrictEqual(Array.from(startContract.allowed_body_fields), [
    'provider',
    'confirmation',
    'operation_authorization'
  ]);
  assert.strictEqual(startContract.request_body_schema.provider, 'google');
  assert.strictEqual(startContract.request_body_schema.confirmation, 'repair_tls_and_restart');
  assert.strictEqual(
    startContract.request_body_schema.operation_authorization,
    'short_lived_operation_authorization'
  );
  assert.strictEqual(startContract.operation_authorization.operation_type, 'provider_tls_repair');
  assert.strictEqual(startContract.operation_authorization.expires_at, '2999-01-01T00:00:00Z');
  assert.strictEqual(startContract.operation_authorization.credential, 'short_lived_operation_authorization');
  assert.strictEqual(JSON.stringify(startContract).includes(operationToken), false);
  for (const forbiddenField of [
    'command',
    'repair_command',
    'script_path',
    'engine',
    'gpu',
    'port',
    'app_port',
    'restart_mode',
    'podman_provider',
    'provider_path',
    'install_dir',
    'python_path',
    'arguments',
    'helper_token',
    'durable_token'
  ]) {
    assert.strictEqual(startContract.allowed_body_fields.includes(forbiddenField), false, forbiddenField);
  }

  elements.wizard_provider_tls_repair_confirm.checked = true;
  viewModel = context.window.SetupWizard.updateProviderTlsRepairControls();
  assert.strictEqual(viewModel.enabled, false);
  assert.strictEqual(elements.wizard_provider_tls_repair_button.disabled, true);
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('browser-triggered repair remains disabled'));

  const renderedText = [
    elements.wizard_provider_tls_repair_title.textContent,
    elements.wizard_provider_tls_repair_message.textContent,
    elements.wizard_provider_tls_repair_support.textContent,
    elements.wizard_provider_tls_repair_command.textContent,
    elements.wizard_provider_tls_repair_status.textContent
  ].join(' ');
  assert.strictEqual(renderedText.includes(operationToken), false);
  assert.strictEqual(context.window.SetupWizard.startProviderTlsRepair(), false);
  assert.strictEqual(context.window.SetupWizard.startProviderTlsRepair(), false);
  assert.strictEqual(notifications[0].type, 'info');
  assert.strictEqual(JSON.stringify(notifications).includes(operationToken), false);
  assert.strictEqual(context.consoleMessages.join(' ').includes(operationToken), false);
  assert.deepStrictEqual(
    context.fetchCalls,
    ['google', 'azure']
  );
}

async function testRepairStartContractHandlesActiveOperationAndRedaction() {
  const operationToken = 'active-operation-token-should-not-render';
  const durableHelperToken = 'durable-helper-token-should-not-render';
  const commandPath = 'C:\\private\\repair-provider-tls.cmd';
  const { context, elements, notifications } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Import the trusted organization/root TLS CA into the container trust store.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: operationToken
        })
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context);

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  const remembered = context.window.SetupWizard.rememberProviderTlsRepairOperationStatus({
    state: 'operation_busy',
    operation_id: '0123456789abcdef0123456789abcdef',
    operation_type: 'provider_tls_repair',
    provider: 'google',
    accepted: true,
    existing_operation: true,
    execution_enabled: false,
    current_step: 'planned',
    classification: 'active',
    terminal: false,
    next_action: 'poll_existing_operation',
    helper_token: durableHelperToken,
    command: commandPath,
    runtime: {
      engine: 'docker',
      gpu: 'off',
      app_port: 5000
    }
  });

  assert.deepStrictEqual(JSON.parse(JSON.stringify(remembered)), {
    state: 'operation_busy',
    operation_id: '0123456789abcdef0123456789abcdef',
    operation_type: 'provider_tls_repair',
    provider: 'google',
    accepted: true,
    existing_operation: true,
    execution_enabled: false,
    current_step: 'planned',
    classification: 'active',
    terminal: false,
    next_action: 'poll_existing_operation'
  });
  assert.strictEqual(JSON.stringify(remembered).includes(durableHelperToken), false);
  assert.strictEqual(JSON.stringify(remembered).includes(commandPath), false);

  const activeOperation = context.window.SetupWizard.getProviderTlsRepairActiveOperation();
  assert.strictEqual(activeOperation.state, 'operation_busy');
  assert.strictEqual(activeOperation.next_action, 'poll_existing_operation');

  const startContract = context.window.SetupWizard.getProviderTlsRepairStartContract('google');
  assert.strictEqual(startContract.ready, false);
  assert.strictEqual(startContract.enabled, false);
  assert.strictEqual(startContract.blocked_reason, 'operation_active');
  assert.strictEqual(startContract.active_operation.state, 'operation_busy');
  assert.strictEqual(JSON.stringify(startContract).includes(operationToken), false);
  assert.strictEqual(JSON.stringify(startContract).includes(durableHelperToken), false);
  assert.strictEqual(JSON.stringify(startContract).includes(commandPath), false);
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('is active'));

  assert.strictEqual(context.window.SetupWizard.startProviderTlsRepair(), false);
  assert.ok(notifications[0].message.includes('already active'));
  assert.strictEqual(JSON.stringify(notifications).includes(operationToken), false);
  assert.strictEqual(JSON.stringify(notifications).includes(durableHelperToken), false);
  assert.strictEqual(context.consoleMessages.join(' ').includes(operationToken), false);
  assert.deepStrictEqual(context.fetchCalls, ['google', 'azure']);

  context.window.SetupWizard.rememberProviderTlsRepairOperationStatus({
    state: 'ready',
    operation_id: '0123456789abcdef0123456789abcdef',
    operation_type: 'provider_tls_repair',
    provider: 'google',
    accepted: true,
    existing_operation: false,
    execution_enabled: false,
    current_step: 'readiness_wait',
    classification: 'terminal_success',
    terminal: true,
    next_action: 'retry_provider_validation'
  });

  assert.strictEqual(context.window.SetupWizard.getProviderTlsRepairActiveOperation(), null);
  const postTerminalContract = context.window.SetupWizard.getProviderTlsRepairStartContract('google');
  assert.strictEqual(postTerminalContract.ready, true);
  assert.strictEqual(postTerminalContract.blocked_reason, 'browser_mutation_disabled');
  assert.deepStrictEqual(context.fetchCalls, ['google', 'azure']);
}

async function testRepairPanelSignalsAdditionalRepairableProviders() {
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Import the trusted organization/root TLS CA into the container trust store.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'google-token-12345678901234567890123456789012'
        })
      }
    },
    azureValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Azure Maps TLS certificate.',
      details: {
        provider: 'azure',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Import the trusted organization/root TLS CA into the container trust store.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider azure -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'azure-token-123456789012345678901234567890123'
        })
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context);

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'block');
  assert.strictEqual(elements.wizard_provider_tls_repair_title.textContent, 'Google Maps TLS repair');
  assert.ok(elements.wizard_provider_tls_repair_message.textContent.includes('1 additional provider also needs repair.'));
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('Another provider also needs repair.'));
}

async function testInvalidOperationAuthorizationLeavesRepairDisabled() {
  const scenarios = [
    {
      name: 'expired',
      authorization: {
        operation_type: 'provider_tls_repair',
        expires_at: '2000-01-01T00:00:00Z',
        operation_token: 'expired-token-should-not-render'
      }
    },
    {
      name: 'malformed_expiry',
      authorization: {
        operation_type: 'provider_tls_repair',
        expires_at: 'not-a-date',
        operation_token: 'malformed-expiry-token-should-not-render'
      }
    },
    {
      name: 'missing_token',
      authorization: {
        operation_type: 'provider_tls_repair',
        expires_at: '2999-01-01T00:00:00Z'
      }
    },
    {
      name: 'wrong_type',
      authorization: {
        operation_type: 'podman_provider_repair',
        expires_at: '2999-01-01T00:00:00Z',
        operation_token: 'wrong-type-token-should-not-render'
      }
    },
    {
      name: 'non_object',
      authorization: 'not-an-authorization-object'
    }
  ];

  for (const scenario of scenarios) {
    const tokenText = typeof scenario.authorization === 'object'
      ? scenario.authorization.operation_token
      : '';
    const { context, elements, notifications } = createContext({
      googleValidationPayload: {
        error: true,
        message: 'TowerScout could not verify the Google Maps TLS certificate.',
        details: {
          provider: 'google',
          category: 'tls_ca_untrusted',
          repairable: true,
          support_action: 'Import the trusted organization/root TLS CA into the container trust store.',
          repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
          helper_available: false,
          helper_bridge: createHelperBridge(scenario.authorization)
        }
      }
    });
    vm.createContext(context);
    loadSetupWizard(context);

    context.window.SetupWizard.showStep(2);
    await context.window.SetupWizard.validateAndNext();

    const viewModel = context.window.SetupWizard.getProviderTlsRepairViewModel('google');
    const publicFailure = context.window.SetupWizard.getProviderValidationState('google').lastFailure;
    assert.strictEqual(viewModel.visible, true, scenario.name);
    assert.strictEqual(viewModel.authorization_ready, false, scenario.name);
    assert.strictEqual(viewModel.enabled, false, scenario.name);
    assert.strictEqual(viewModel.blocked_reason, 'operation_authorization_unavailable', scenario.name);
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairStartContract('google').blocked_reason,
      'operation_authorization_unavailable',
      scenario.name
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairStartContract('google').ready,
      false,
      scenario.name
    );
    assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'block', scenario.name);
    assert.strictEqual(elements.wizard_provider_tls_repair_button.disabled, true, scenario.name);
    assert.strictEqual(elements.wizard_provider_tls_repair_button.textContent, 'Repair unavailable', scenario.name);
    assert.ok(
      elements.wizard_provider_tls_repair_status.textContent.includes('authorization is not available'),
      scenario.name
    );

    if (tokenText) {
      const publicAuthorization = publicFailure.operation_authorization || {};
      assert.strictEqual(publicAuthorization.operation_token, undefined, scenario.name);
      assert.strictEqual(JSON.stringify(viewModel).includes(tokenText), false, scenario.name);
      const renderedText = [
        elements.wizard_provider_tls_repair_title.textContent,
        elements.wizard_provider_tls_repair_message.textContent,
        elements.wizard_provider_tls_repair_support.textContent,
        elements.wizard_provider_tls_repair_command.textContent,
        elements.wizard_provider_tls_repair_status.textContent
      ].join(' ');
      assert.strictEqual(renderedText.includes(tokenText), false, scenario.name);
    }

    assert.strictEqual(context.window.SetupWizard.startProviderTlsRepair(), false, scenario.name);
    assert.strictEqual(notifications[0].type, 'info', scenario.name);
    assert.deepStrictEqual(context.fetchCalls, ['google', 'azure'], scenario.name);
  }
}

async function testBrowserGateAloneDoesNotBypassDisabledHelperCapability() {
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Use the manual command if guided repair is unavailable.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge(
          {
            operation_type: 'provider_tls_repair',
            expires_at: '2999-01-01T00:00:00Z',
            operation_token: 'capability-gate-operation-authorization'
          },
          false
        )
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const viewModel = context.window.SetupWizard.updateProviderTlsRepairControls();

  assert.strictEqual(viewModel.helper_available, false);
  assert.strictEqual(viewModel.capability_enabled, false);
  assert.strictEqual(viewModel.enabled, false);
  assert.strictEqual(viewModel.blocked_reason, 'helper_unavailable');
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('helper is unavailable'));
  assert.strictEqual(context.window.SetupWizard.startProviderTlsRepair(), false);
  assert.strictEqual(
    context.fetchRequests.some(
      request => request.url === `${HELPER_BASE_URL}/operations/provider-tls-repair`
    ),
    false
  );
}

async function testEnabledReviewHarnessPostsExactBodyAndPollsWithoutPersistingCredentials() {
  const operationToken = 'live-operation-authorization-should-not-render';
  const statusToken = 'live-status-authorization-should-not-render';
  const operationId = '0123456789abcdef0123456789abcdef';
  const {
    context,
    elements,
    notifications
  } = createContext({
    statusAuthorizationToken: statusToken,
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Import the trusted organization/root TLS CA into the container trust store.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge(
          {
            operation_type: 'provider_tls_repair',
            expires_at: '2999-01-01T00:00:00Z',
            operation_token: operationToken
          },
          true
        )
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  context.window.SetupWizard.updateProviderTlsRepairControls();

  const startPromise = context.window.SetupWizard.startProviderTlsRepair();
  assert.ok(startPromise && typeof startPromise.then === 'function');
  assert.strictEqual(context.window.SetupWizard.startProviderTlsRepair(), false);
  const terminalStatus = await startPromise;

  assert.strictEqual(terminalStatus.state, 'ready');
  assert.strictEqual(terminalStatus.terminal, true);
  assert.strictEqual(context.window.SetupWizard.getProviderTlsRepairActiveOperation(), null);

  const startRequest = context.fetchRequests.find(
    request => request.url === `${HELPER_BASE_URL}/operations/provider-tls-repair`
  );
  assert.ok(startRequest);
  assert.deepStrictEqual(
    Object.keys(JSON.parse(startRequest.options.body)).sort(),
    ['confirmation', 'operation_authorization', 'provider']
  );
  assert.deepStrictEqual(JSON.parse(startRequest.options.body), {
    provider: 'google',
    confirmation: 'repair_tls_and_restart',
    operation_authorization: operationToken
  });
  assert.strictEqual(startRequest.options.headers['X-TowerScout-Helper-Token'], undefined);

  const statusAuthorizationRequest = context.fetchRequests.find(
    request => request.url === '/api/config/provider-tls-repair-status-authorization'
  );
  assert.strictEqual(statusAuthorizationRequest, undefined);
  const statusRequest = context.fetchRequests.find(
    request => request.url === `${HELPER_BASE_URL}/operations/${operationId}`
  );
  assert.strictEqual(
    statusRequest.options.headers['X-TowerScout-Operation-Authorization'],
    statusToken
  );

  assert.strictEqual(context.sessionValues.size, 0);
  assert.deepStrictEqual(
    JSON.parse(context.storageWrites[0].value),
    {
      operation_id: operationId,
      provider: 'google',
      helper_base_url: HELPER_BASE_URL
    }
  );
  const publicText = JSON.stringify({
    validation: context.window.SetupWizard.getProviderValidationState('google'),
    notifications,
    console: context.consoleMessages,
    storageWrites: context.storageWrites,
    rendered: [
      elements.wizard_provider_tls_repair_title.textContent,
      elements.wizard_provider_tls_repair_message.textContent,
      elements.wizard_provider_tls_repair_support.textContent,
      elements.wizard_provider_tls_repair_command.textContent,
      elements.wizard_provider_tls_repair_status.textContent
    ]
  });
  assert.strictEqual(publicText.includes(operationToken), false);
  assert.strictEqual(publicText.includes(statusToken), false);
  assert.strictEqual(publicText.includes(HELPER_PROBE_TOKEN), false);
}

async function testExpiredStatusAuthorizationRefreshesOnceBeforeTerminalStatus() {
  const operationId = '0123456789abcdef0123456789abcdef';
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'TowerScout could not verify the Google Maps TLS certificate.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Use the manual command if guided repair is unavailable.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge(
          {
            operation_type: 'provider_tls_repair',
            expires_at: '2999-01-01T00:00:00Z',
            operation_token: 'refresh-test-operation-authorization'
          },
          true
        )
      }
    },
    statusResponses: [
      {
        status: 401,
        payload: { state: 'rejected_expired_authorization' }
      },
      {
        state: 'ready',
        operation_id: operationId,
        operation_type: 'provider_tls_repair',
        provider: 'google',
        accepted: true,
        existing_operation: false,
        execution_enabled: false,
        current_step: 'readiness_wait',
        classification: 'terminal_success',
        terminal: true,
        next_action: 'retry_provider_validation'
      }
    ]
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const status = await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(status.state, 'ready');
  assert.strictEqual(
    context.fetchRequests.filter(
      request => request.url === '/api/config/provider-tls-repair-status-authorization'
    ).length,
    1
  );
  assert.strictEqual(
    context.fetchRequests.filter(
      request => request.url === `${HELPER_BASE_URL}/operations/${operationId}`
    ).length,
    2
  );
  assert.strictEqual(context.sessionValues.size, 0);
}

async function testTransientPollingFailuresRetryWithoutManualFallback() {
  const operationId = '0123456789abcdef0123456789abcdef';
  const statusToken = 'transient-status-authorization-should-not-render';
  const { context, elements, notifications, timerDelays } = createContext({
    statusAuthorizationToken: statusToken,
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Wait for guided repair status.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'transient-start-authorization'
        })
      }
    },
    statusResponses: [
      { status: 500, payload: { state: 'temporary_error' } },
      { status: 429, payload: { state: 'rate_limited' } },
      { throwError: 'temporary network interruption' },
      {
        state: 'ready',
        operation_id: operationId,
        operation_type: 'provider_tls_repair',
        provider: 'google',
        accepted: true,
        existing_operation: false,
        execution_enabled: true,
        current_step: 'readiness_wait',
        classification: 'terminal_success',
        terminal: true,
        next_action: 'retry_provider_validation'
      }
    ]
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const status = await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(status.state, 'ready');
  assert.strictEqual(
    context.fetchRequests.filter(
      request => request.url === `${HELPER_BASE_URL}/operations/${operationId}`
    ).length,
    4
  );
  assert.ok(
    notifications.some(notification => notification.message.includes('temporarily unavailable'))
  );
  assert.strictEqual(
    notifications.some(notification => notification.message.includes('Use the suggested command fallback')),
    false
  );
  assert.strictEqual(context.sessionValues.size, 0);
  assert.strictEqual(JSON.stringify(notifications).includes(statusToken), false);
  assert.deepStrictEqual(timerDelays.slice(0, 3), [1000, 2000, 4000]);
}

async function testMalformedStatusRetriesWithoutClearingActiveOperation() {
  const operationId = '0123456789abcdef0123456789abcdef';
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'malformed-status-start-authorization'
        })
      }
    },
    statusResponses: [
      { state: 'ready', operation_id: '../invalid', provider: 'google' },
      {
        state: 'ready',
        operation_id: operationId,
        operation_type: 'provider_tls_repair',
        provider: 'google',
        accepted: true,
        existing_operation: false,
        execution_enabled: true,
        current_step: 'readiness_wait',
        classification: 'terminal_success',
        terminal: true,
        next_action: 'retry_provider_validation'
      }
    ]
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const status = await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(status.state, 'ready');
  assert.strictEqual(
    context.fetchRequests.filter(
      request => request.url === `${HELPER_BASE_URL}/operations/${operationId}`
    ).length,
    2
  );
  assert.strictEqual(
    context.fetchRequests.filter(
      request => request.url === `${HELPER_BASE_URL}/operations/provider-tls-repair`
    ).length,
    1
  );
}

async function testReadinessRecoveryRetriesBeforeProviderValidation() {
  const operationId = '0123456789abcdef0123456789abcdef';
  const { context, elements, timerDelays } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'readiness-retry-start-authorization'
        })
      }
    },
    readinessResponses: [
      { status: 503, payload: { state: 'starting' } },
      { throwError: 'temporary restart disconnect' },
      { state: 'ready' }
    ],
    statusResponses: [{
      state: 'ready',
      operation_id: operationId,
      operation_type: 'provider_tls_repair',
      provider: 'google',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'readiness_wait',
      classification: 'terminal_success',
      terminal: true,
      next_action: 'retry_provider_validation'
    }]
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(
    context.fetchRequests.filter(request => request.url === '/api/readiness').length,
    3
  );
  assert.deepStrictEqual(timerDelays.slice(-2), [1000, 2000]);
}

async function testFreshValidationClearsSameProviderTerminalRepairState() {
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'fresh-validation-start-authorization'
        })
      }
    }
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  context.window.SetupWizard.rememberProviderTlsRepairOperationStatus({
    state: 'runtime_start_failed',
    operation_id: '0123456789abcdef0123456789abcdef',
    operation_type: 'provider_tls_repair',
    provider: 'google',
    accepted: true,
    existing_operation: false,
    execution_enabled: true,
    current_step: 'worker_exit',
    classification: 'terminal_failure',
    terminal: true,
    next_action: 'use_startup_fallback_guidance'
  });
  context.window.SetupWizard.updateProviderTlsRepairControls();
  assert.strictEqual(elements.wizard_provider_tls_repair_button.disabled, true);

  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  context.window.SetupWizard.updateProviderTlsRepairControls();

  assert.strictEqual(elements.wizard_provider_tls_repair_button.disabled, false);
  assert.strictEqual(
    elements.wizard_provider_tls_repair_status.textContent.includes(
      'did not restart cleanly'
    ),
    false
  );
}

async function testStatusAuthorization404RetriesWithoutDeclaringOperationGone() {
  const operationId = '0123456789abcdef0123456789abcdef';
  const { context, elements, notifications } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Wait for guided repair status.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'authorization-retry-start-token'
        })
      }
    },
    startResponse: {
      state: 'planned',
      operation_id: operationId,
      operation_type: 'provider_tls_repair',
      provider: 'google',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'worker_start',
      classification: 'pending',
      terminal: false,
      next_action: 'await_controlled_execution'
    },
    statusAuthorizationResponses: [
      { status: 404, payload: { state: 'helper_unavailable' } }
    ],
    statusResponses: [{
      state: 'ready',
      operation_id: operationId,
      operation_type: 'provider_tls_repair',
      provider: 'google',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'readiness_wait',
      classification: 'terminal_success',
      terminal: true,
      next_action: 'retry_provider_validation'
    }]
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const status = await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(status.state, 'ready');
  assert.strictEqual(
    context.fetchRequests.filter(
      request => request.url === '/api/config/provider-tls-repair-status-authorization'
    ).length,
    2
  );
  assert.strictEqual(
    notifications.some(notification => notification.message.includes('temporarily unavailable')),
    true
  );
  assert.strictEqual(
    notifications.some(notification => notification.message.includes('status expired')),
    false
  );
  assert.strictEqual(context.sessionValues.size, 0);
}

async function testChangedHelperSessionRequiresNewAuthorizationWithoutManualFallback() {
  const operationId = '0123456789abcdef0123456789abcdef';
  const { context, elements, notifications } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Wait for guided repair status.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'changed-session-start-authorization'
        })
      }
    },
    startResponse: {
      state: 'planned',
      operation_id: operationId,
      operation_type: 'provider_tls_repair',
      provider: 'google',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'worker_start',
      classification: 'pending',
      terminal: false,
      next_action: 'await_controlled_execution'
    },
    statusAuthorizationBaseUrl: 'http://127.0.0.1:5099'
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const status = await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(status.state, 'helper_session_changed');
  assert.strictEqual(status.terminal, true);
  assert.strictEqual(status.next_action, 'new_authorization_required');
  assert.strictEqual(context.sessionValues.size, 0);
  assert.ok(
    notifications.some(notification => notification.message.includes('session changed'))
  );
  assert.strictEqual(
    notifications.some(notification => notification.message.includes('manual repair')),
    false
  );
}

async function testCrossProviderConflictUsesReturnedOperationIdentity() {
  const operationId = 'fedcba9876543210fedcba9876543210';
  const { context, elements } = createContext({
    googleValidationPayload: {
      error: true,
      message: 'Google Maps TLS verification failed.',
      details: {
        provider: 'google',
        category: 'tls_ca_untrusted',
        repairable: true,
        support_action: 'Wait for guided repair status.',
        repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
        helper_available: false,
        helper_bridge: createHelperBridge({
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'cross-provider-start-authorization'
        })
      }
    },
    startStatus: 409,
    startResponse: {
      state: 'operation_busy',
      operation_id: operationId,
      operation_type: 'provider_tls_repair',
      provider: 'azure',
      accepted: true,
      existing_operation: true,
      execution_enabled: true,
      current_step: 'runtime_starting',
      classification: 'active',
      terminal: false,
      next_action: 'poll_existing_operation',
      status_authorization: {
        operation_type: 'provider_tls_repair',
        scope: 'operation_status',
        expires_at: '2999-01-01T00:00:00Z',
        authorization: 'cross-provider-status-authorization'
      }
    },
    statusResponses: [{
      state: 'ready',
      operation_id: operationId,
      operation_type: 'provider_tls_repair',
      provider: 'azure',
      accepted: true,
      existing_operation: true,
      execution_enabled: true,
      current_step: 'readiness_wait',
      classification: 'terminal_success',
      terminal: true,
      next_action: 'retry_provider_validation'
    }]
  });
  vm.createContext(context);
  loadSetupWizard(context, { enableBrowserMutation: true });

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();
  elements.wizard_provider_tls_repair_confirm.checked = true;
  const status = await context.window.SetupWizard.startProviderTlsRepair();

  assert.strictEqual(status.provider, 'azure');
  assert.deepStrictEqual(
    JSON.parse(context.storageWrites[0].value),
    {
      operation_id: operationId,
      provider: 'azure',
      helper_base_url: HELPER_BASE_URL
    }
  );
  assert.strictEqual(
    context.fetchRequests.some(
      request => request.url === `${HELPER_BASE_URL}/operations/${operationId}`
    ),
    true
  );
  assert.strictEqual(
    context.fetchRequests.some(request => request.url === '/api/readiness'),
    true
  );
}

async function testTerminalFailuresRenderStableRecoveryGuidance() {
  const { context, elements } = createContext();
  vm.createContext(context);
  loadSetupWizard(context);

  context.window.SetupWizard.showStep(2);
  await context.window.SetupWizard.validateAndNext();

  const cases = [
    ['review_runtime_state_before_retry', 'runtime status'],
    ['use_startup_fallback_guidance', 'did not restart cleanly'],
    ['clear_or_reauthorize_after_timeout', 'reload setup'],
    ['use_manual_dry_run_support_selection', 'manual dry run'],
    ['use_manual_tls_repair_fallback', 'manual repair command'],
    ['use_status_and_log_guidance', 'sanitized logs'],
    ['support_review_required', 'Support review']
  ];
  for (const [nextAction, expectedText] of cases) {
    context.window.SetupWizard.rememberProviderTlsRepairOperationStatus({
      state: 'terminal_failure',
      operation_id: '00112233445566778899aabbccddeeff',
      operation_type: 'provider_tls_repair',
      provider: 'google',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'repair',
      classification: 'terminal_support_escalation',
      terminal: true,
      next_action: nextAction
    });
    assert.ok(
      elements.wizard_provider_tls_repair_status.textContent.includes(expectedText),
      `${nextAction} should render stable recovery guidance`
    );
  }
}

async function testValidationResetPreservesActiveOperation() {
  const { context } = createContext();
  vm.createContext(context);
  loadSetupWizard(context);
  context.window.SetupWizard.rememberProviderTlsRepairOperationStatus({
    state: 'runtime_starting',
    operation_id: '00112233445566778899aabbccddeeff',
    operation_type: 'provider_tls_repair',
    provider: 'azure',
    accepted: true,
    existing_operation: true,
    execution_enabled: true,
    current_step: 'runtime_starting',
    classification: 'active',
    terminal: false,
    next_action: 'poll_existing_operation'
  });

  await context.window.SetupWizard.validateAndNext();

  const active = context.window.SetupWizard.getProviderTlsRepairActiveOperation();
  assert.strictEqual(active.operation_id, '00112233445566778899aabbccddeeff');
  assert.strictEqual(active.provider, 'azure');
}

testSecondProviderStillValidatesAfterFirstProviderNetworkFailure()
  .then(testInvalidProviderKeyDoesNotExposeRepairPredicate)
  .then(testRepairPredicateUsesAuthenticatedHelperProbe)
  .then(testRepairPanelPreservesTlsFallbackAndRejectsNonTlsStates)
  .then(testShortLivedAuthorizationDoesNotStartRepairWhileMutationGateIsClosed)
  .then(testRepairStartContractHandlesActiveOperationAndRedaction)
  .then(testRepairPanelSignalsAdditionalRepairableProviders)
  .then(testInvalidOperationAuthorizationLeavesRepairDisabled)
  .then(testBrowserGateAloneDoesNotBypassDisabledHelperCapability)
  .then(testEnabledReviewHarnessPostsExactBodyAndPollsWithoutPersistingCredentials)
  .then(testExpiredStatusAuthorizationRefreshesOnceBeforeTerminalStatus)
  .then(testTransientPollingFailuresRetryWithoutManualFallback)
  .then(testMalformedStatusRetriesWithoutClearingActiveOperation)
  .then(testReadinessRecoveryRetriesBeforeProviderValidation)
  .then(testFreshValidationClearsSameProviderTerminalRepairState)
  .then(testStatusAuthorization404RetriesWithoutDeclaringOperationGone)
  .then(testChangedHelperSessionRequiresNewAuthorizationWithoutManualFallback)
  .then(testCrossProviderConflictUsesReturnedOperationIdentity)
  .then(testTerminalFailuresRenderStableRecoveryGuidance)
  .then(testValidationResetPreservesActiveOperation)
  .then(() => {
    console.log('Setup wizard validation contract PASSED');
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
