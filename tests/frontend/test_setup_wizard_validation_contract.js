#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '../..');
const API_HELPERS_PATH = path.join(ROOT, 'webapp/js/src/utils/apiHelpers.js');
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
  let savePayload = null;
  const notifications = [];
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
  const context = {
    console: testConsole,
    consoleMessages,
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

function loadSetupWizard(context) {
  const apiHelpersSource = fs.readFileSync(API_HELPERS_PATH, 'utf8');
  vm.runInContext(apiHelpersSource, context, { filename: API_HELPERS_PATH });
  const source = fs.readFileSync(SETUP_WIZARD_PATH, 'utf8');
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
  assert.strictEqual(context.window.SetupWizard.shouldShowProviderTlsRepair('google'), false);
  assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'none');

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

async function testRepairPredicateRequiresRepairableTlsAndHelperAvailability() {
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
        helper_available: true
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
  assert.strictEqual(viewModel.authorization_ready, false);
  assert.strictEqual(viewModel.enabled, false);
  assert.strictEqual(viewModel.blocked_reason, 'operation_authorization_unavailable');
  assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'block');
  assert.strictEqual(elements.wizard_provider_tls_repair_button.disabled, true);
  assert.strictEqual(elements.wizard_provider_tls_repair_button.textContent, 'Repair unavailable');
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('authorization is not available'));
}

async function testRepairPanelRejectsNonTlsHelperUnavailableAndPodmanStates() {
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

    assert.strictEqual(
      context.window.SetupWizard.shouldShowProviderTlsRepair('google'),
      false,
      scenario.category
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairViewModel('google').visible,
      false,
      scenario.category
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairStartContract('google').ready,
      false,
      scenario.category
    );
    assert.strictEqual(
      context.window.SetupWizard.getProviderTlsRepairStartContract('google').blocked_reason,
      'not_repairable_or_helper_unavailable',
      scenario.category
    );
    assert.strictEqual(elements.wizard_provider_tls_repair_panel.style.display, 'none', scenario.category);
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
        helper_available: true,
        operation_authorization: {
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: operationToken
        }
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
  assert.strictEqual(startContract.endpoint, '/operations/provider-tls-repair');
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
        helper_available: true,
        operation_authorization: {
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: operationToken
        }
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
  assert.ok(elements.wizard_provider_tls_repair_status.textContent.includes('already active'));

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
        helper_available: true,
        operation_authorization: {
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'google-token-12345678901234567890123456789012'
        }
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
        helper_available: true,
        operation_authorization: {
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: 'azure-token-123456789012345678901234567890123'
        }
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
          helper_available: true,
          operation_authorization: scenario.authorization
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

testSecondProviderStillValidatesAfterFirstProviderNetworkFailure()
  .then(testInvalidProviderKeyDoesNotExposeRepairPredicate)
  .then(testRepairPredicateRequiresRepairableTlsAndHelperAvailability)
  .then(testRepairPanelRejectsNonTlsHelperUnavailableAndPodmanStates)
  .then(testShortLivedAuthorizationDoesNotStartRepairWhileMutationGateIsClosed)
  .then(testRepairStartContractHandlesActiveOperationAndRedaction)
  .then(testRepairPanelSignalsAdditionalRepairableProviders)
  .then(testInvalidOperationAuthorizationLeavesRepairDisabled)
  .then(() => {
    console.log('Setup wizard validation contract PASSED');
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
