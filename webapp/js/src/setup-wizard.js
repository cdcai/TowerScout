(function () {
  'use strict';

  let currentStep = 1;
  let validatedKeys = {
    google: false,
    azure: false
  };
  let validationInFlight = false;
  let saveInFlight = false;
  const TLS_REPAIR_CATEGORIES = new Set([
    'tls_ca_untrusted',
    'tls_bundle_missing',
    'tls_bundle_unusable'
  ]);
  const PROVIDER_TLS_REPAIR_CONFIRMATION = 'repair_tls_and_restart';
  const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false;
  const PROVIDER_TLS_REPAIR_OPERATION_ENDPOINT = '/operations/provider-tls-repair';
  const PROVIDER_TLS_REPAIR_STATUS_AUTHORIZATION_ENDPOINT = '/api/config/provider-tls-repair-status-authorization';
  const PROVIDER_TLS_REPAIR_ACTIVE_OPERATION_STORAGE_KEY = 'towerscout.providerTlsRepair.activeOperation';
  const PROVIDER_TLS_REPAIR_POLL_INTERVAL_MS = 1000;
  const PROVIDER_TLS_REPAIR_POLL_TIMEOUT_MS = 15 * 60 * 1000;
  const PROVIDER_TLS_REPAIR_REQUEST_TIMEOUT_MS = 5000;
  const PROVIDER_TLS_REPAIR_MAX_RETRY_DELAY_MS = 10000;
  const PROVIDER_TLS_REPAIR_AUTHORIZATION_CLOCK_SKEW_MS = 5 * 60 * 1000;
  const PROVIDER_TLS_REPAIR_READINESS_MAX_ATTEMPTS = 6;
  const PROVIDER_TLS_REPAIR_READINESS_MAX_RETRY_DELAY_MS = 5000;
  const PROVIDER_TLS_REPAIR_ALLOWED_START_BODY_FIELDS = Object.freeze([
    'provider',
    'confirmation',
    'operation_authorization'
  ]);
  const PROVIDER_TLS_REPAIR_DISALLOWED_START_BODY_FIELDS = Object.freeze([
    'command',
    'repair_command',
    'script',
    'script_path',
    'engine',
    'gpu',
    'port',
    'app_port',
    'runtime',
    'restart_mode',
    'podman_provider',
    'provider_path',
    'install_dir',
    'python_path',
    'arguments',
    'helper_token',
    'durable_token'
  ]);
  const PROVIDER_TLS_REPAIR_STATUS_CLASSIFICATIONS = new Set([
    'pending',
    'active',
    'intermediate_success',
    'terminal_success',
    'terminal_timeout',
    'terminal_support_escalation',
    'retryable_failure_with_support_review',
    'rejected',
    'unknown'
  ]);
  const PROVIDER_TLS_REPAIR_NEXT_ACTIONS = new Set([
    'await_controlled_execution',
    'poll_existing_operation',
    'continue_to_runtime_stop',
    'continue_to_runtime_start',
    'retry_provider_validation',
    'review_runtime_state_before_retry',
    'use_startup_fallback_guidance',
    'clear_or_reauthorize_after_timeout',
    'use_manual_dry_run_support_selection',
    'use_manual_tls_repair_fallback',
    'use_manual_start_fallback',
    'use_status_and_log_guidance',
    'new_authorization_required',
    'support_review_required'
  ]);
  const providerNames = ['google', 'azure'];
  let providerValidationState = createEmptyProviderValidationState();
  let activeProviderTlsRepairProvider = null;
  let providerTlsRepairStartInFlight = false;
  let providerTlsRepairOperationStatus = null;
  let providerTlsRepairPollingPromise = null;
  const fetchJson = window.TowerScoutConfigApi.fetchJson;
  const providerFailureMessage = window.TowerScoutConfigApi.providerFailureMessage;
  const saveFailureMessage = window.TowerScoutConfigApi.saveFailureMessage;

  function createEmptyProviderValidationState() {
    return {
      google: {
        lastResult: null,
        lastFailure: null
      },
      azure: {
        lastResult: null,
        lastFailure: null
      }
    };
  }

  function getWizardElement() {
    return document.getElementById('setup_wizard_div');
  }

  function getSelectedDefaultProvider() {
    const selected = document.querySelector('input[name="default_provider"]:checked');
    return selected ? selected.value : 'azure';
  }

  function normalizeProviderTlsRepairBaseUrl(value) {
    const text = String(value || '').trim();
    const match = text.match(/^http:\/\/(?:127\.0\.0\.1|localhost):(\d{1,5})$/i);
    if (!match) {
      return '';
    }
    const port = Number(match[1]);
    return Number.isInteger(port) && port >= 1 && port <= 65535 ? text.replace(/\/+$/, '') : '';
  }

  function normalizeProviderTlsRepairCredential(rawCredential, expectedScope) {
    if (!rawCredential || typeof rawCredential !== 'object') {
      return null;
    }
    const scope = String(rawCredential.scope || '').trim();
    const expiresAt = String(rawCredential.expires_at || rawCredential.expiresAt || '').trim();
    const authorization = String(
      rawCredential.authorization ||
      rawCredential.operation_token ||
      rawCredential.token ||
      ''
    ).trim();
    if (scope !== expectedScope || !expiresAt || !authorization) {
      return null;
    }
    return {
      scope,
      expires_at: expiresAt,
      authorization
    };
  }

  function normalizeProviderTlsRepairBridge(payload, details) {
    const rawBridge = payload.helper_bridge || details.helper_bridge || null;
    if (!rawBridge || typeof rawBridge !== 'object') {
      return null;
    }
    const baseUrl = normalizeProviderTlsRepairBaseUrl(rawBridge.base_url);
    const rawProbe = rawBridge.probe || {};
    const probe = normalizeProviderTlsRepairCredential(rawProbe, 'helper_probe');
    const operationAuthorization = normalizeProviderTlsRepairAuthorization(
      { operation_authorization: rawBridge.operation_authorization },
      {}
    );
    if (
      !baseUrl ||
      !probe ||
      rawProbe.path !== '/health'
    ) {
      return null;
    }
    return {
      base_url: baseUrl,
      probe: {
        ...probe,
        path: '/health'
      },
      operation_authorization: operationAuthorization,
      provider_tls_repair_capability: rawBridge.provider_tls_repair_capability === true,
      expected_runtime: normalizeProviderTlsRepairRuntime(rawBridge.expected_runtime)
    };
  }

  function normalizeProviderTlsRepairRuntime(runtime) {
    if (!runtime || typeof runtime !== 'object') {
      return null;
    }
    const engine = String(runtime.engine || '').trim().toLowerCase();
    const gpu = String(runtime.gpu || '').trim().toLowerCase();
    const appPort = Number(runtime.app_port);
    if (
      !['docker', 'podman'].includes(engine) ||
      !['off', 'auto', 'on'].includes(gpu) ||
      !Number.isInteger(appPort) ||
      appPort < 1 ||
      appPort > 65535
    ) {
      return null;
    }
    return { engine, gpu, app_port: appPort };
  }

  function normalizeProviderValidationResult(provider, payload = {}) {
    const details = payload.details || {};
    const category = payload.category || details.category || null;
    const repairable = (
      payload.repairable === true ||
      details.repairable === true ||
      (category !== null && TLS_REPAIR_CATEGORIES.has(category))
    );
    const helperAvailable = payload.helper_available === true || details.helper_available === true;
    const helperBridge = repairable ? normalizeProviderTlsRepairBridge(payload, details) : null;
    const operationAuthorization = normalizeProviderTlsRepairAuthorization(payload, details);

    return {
      provider: payload.provider || details.provider || provider,
      valid: payload.valid === true,
      message: payload.message || payload.technical_message || payload.error || 'Validation failed.',
      category,
      repairable,
      support_action: payload.support_action || details.support_action || null,
      repair_command: payload.repair_command || details.repair_command || null,
      helper_available: repairable && helperAvailable,
      operation_authorization: repairable && helperAvailable ? operationAuthorization : null,
      helper_bridge: repairable ? helperBridge : null,
      status_code: payload.status_code || details.status_code || payload.status || null
    };
  }

  function normalizeProviderTlsRepairAuthorization(payload, details) {
    const rawAuthorization = payload.operation_authorization || details.operation_authorization || null;
    if (!rawAuthorization || typeof rawAuthorization !== 'object') {
      return null;
    }

    const operationType = rawAuthorization.operation_type || rawAuthorization.operationType || '';
    const expiresAt = rawAuthorization.expires_at || rawAuthorization.expiresAt || '';
    const token = rawAuthorization.operation_token || rawAuthorization.token || rawAuthorization.authorization || '';

    if (operationType !== 'provider_tls_repair' || !expiresAt || !token) {
      return null;
    }

    return {
      operation_type: 'provider_tls_repair',
      expires_at: String(expiresAt),
      operation_token: String(token)
    };
  }

  function cloneValidationRecord(record) {
    if (!record) {
      return null;
    }

    const cloned = { ...record };
    if (cloned.operation_authorization) {
      cloned.operation_authorization = {
        operation_type: cloned.operation_authorization.operation_type,
        expires_at: cloned.operation_authorization.expires_at
      };
    }
    if (cloned.helper_bridge) {
      cloned.helper_bridge = {
        base_url: cloned.helper_bridge.base_url,
        configured: true,
        provider_tls_repair_capability: (
          cloned.helper_bridge.provider_tls_repair_capability === true
        )
      };
    }
    return cloned;
  }

  function rememberProviderValidationResult(provider, payload) {
    if (!providerNames.includes(provider)) {
      return normalizeProviderValidationResult(provider, payload);
    }

    const normalized = normalizeProviderValidationResult(provider, payload);
    providerValidationState[provider] = {
      lastResult: normalized,
      lastFailure: normalized.valid ? null : normalized
    };
    if (
      providerTlsRepairOperationStatus &&
      providerTlsRepairOperationStatus.terminal === true &&
      providerTlsRepairOperationStatus.provider === provider
    ) {
      providerTlsRepairOperationStatus = null;
    }
    renderProviderTlsRepairState();
    return normalized;
  }

  function rememberProviderValidationResults(validationResults = {}) {
    providerNames.forEach(provider => {
      if (validationResults[provider]) {
        rememberProviderValidationResult(provider, validationResults[provider]);
      }
    });
  }

  function clearProviderValidationState(provider) {
    if (providerNames.includes(provider)) {
      providerValidationState[provider] = {
        lastResult: null,
        lastFailure: null
      };
      if (
        providerTlsRepairOperationStatus &&
        providerTlsRepairOperationStatus.terminal === true &&
        providerTlsRepairOperationStatus.provider === provider
      ) {
        providerTlsRepairOperationStatus = null;
      }
      renderProviderTlsRepairState();
    }
  }

  function resetProviderValidationState() {
    providerValidationState = createEmptyProviderValidationState();
    if (!isProviderTlsRepairOperationActive(providerTlsRepairOperationStatus)) {
      providerTlsRepairOperationStatus = null;
    }
    renderProviderTlsRepairState();
  }

  function getProviderValidationState(provider) {
    const state = providerValidationState[provider] || {
      lastResult: null,
      lastFailure: null
    };
    return {
      lastResult: cloneValidationRecord(state.lastResult),
      lastFailure: cloneValidationRecord(state.lastFailure)
    };
  }

  function getProviderValidationFailure(provider) {
    const state = providerValidationState[provider] || {};
    return state.lastFailure || null;
  }

  function shouldShowProviderTlsRepair(provider) {
    const failure = getProviderValidationFailure(provider);
    return Boolean(
      failure &&
      failure.repairable === true &&
      TLS_REPAIR_CATEGORIES.has(failure.category)
    );
  }

  function providerDisplayName(provider) {
    if (provider === 'google') {
      return 'Google Maps';
    }
    if (provider === 'azure') {
      return 'Azure Maps';
    }
    return provider || 'provider';
  }

  function hasCurrentProviderTlsRepairAuthorization(record, now = Date.now()) {
    const authorization = record && record.operation_authorization;
    if (!authorization || authorization.operation_type !== 'provider_tls_repair') {
      return false;
    }
    if (!authorization.operation_token) {
      return false;
    }

    const expiresAtMs = Date.parse(authorization.expires_at);
    if (!Number.isFinite(expiresAtMs)) {
      return false;
    }

    return expiresAtMs + PROVIDER_TLS_REPAIR_AUTHORIZATION_CLOCK_SKEW_MS > now;
  }

  function hasCurrentProviderTlsRepairCredential(credential, now = Date.now()) {
    if (!credential || !credential.authorization) {
      return false;
    }
    const expiresAtMs = Date.parse(credential.expires_at);
    return (
      Number.isFinite(expiresAtMs) &&
      expiresAtMs + PROVIDER_TLS_REPAIR_AUTHORIZATION_CLOCK_SKEW_MS > now
    );
  }

  function getPrivateProviderTlsRepairBridge(provider) {
    const failure = getProviderValidationFailure(provider);
    return failure && failure.helper_bridge ? failure.helper_bridge : null;
  }

  function getProviderTlsRepairHelperUrl(baseUrl, path) {
    const normalizedBaseUrl = normalizeProviderTlsRepairBaseUrl(baseUrl);
    const normalizedPath = String(path || '');
    if (!normalizedBaseUrl || !/^\/[a-z0-9/-]+$/i.test(normalizedPath)) {
      return '';
    }
    return `${normalizedBaseUrl}${normalizedPath}`;
  }

  async function refreshProviderTlsRepairHelperAvailability(provider) {
    const failure = getProviderValidationFailure(provider);
    const bridge = getPrivateProviderTlsRepairBridge(provider);
    if (
      !failure ||
      !bridge ||
      !hasCurrentProviderTlsRepairCredential(bridge.probe)
    ) {
      if (failure) {
        failure.helper_available = false;
        failure.operation_authorization = null;
      }
      renderProviderTlsRepairState();
      return false;
    }

    const healthUrl = getProviderTlsRepairHelperUrl(bridge.base_url, bridge.probe.path);
    if (!healthUrl) {
      failure.helper_available = false;
      failure.operation_authorization = null;
      renderProviderTlsRepairState();
      return false;
    }

    try {
      const health = await fetchJson(healthUrl, {
        method: 'GET',
        headers: {
          'X-TowerScout-Operation-Authorization': bridge.probe.authorization
        },
        cache: 'no-store',
        timeoutMs: PROVIDER_TLS_REPAIR_REQUEST_TIMEOUT_MS
      });
      const liveRuntime = normalizeProviderTlsRepairRuntime(health && health.runtime);
      const expectedRuntime = bridge.expected_runtime;
      const ready = Boolean(
        health &&
        health.state === 'ready' &&
        health.capabilities &&
        health.capabilities.max_active_operations === 1 &&
        health.capabilities.provider_tls_repair === true &&
        bridge.provider_tls_repair_capability === true &&
        liveRuntime &&
        expectedRuntime &&
        liveRuntime.engine === expectedRuntime.engine &&
        liveRuntime.gpu === expectedRuntime.gpu &&
        liveRuntime.app_port === expectedRuntime.app_port
      );
      failure.helper_available = ready;
      failure.operation_authorization = ready
        ? bridge.operation_authorization
        : null;
      renderProviderTlsRepairState();
      return ready;
    } catch (_error) {
      failure.helper_available = false;
      failure.operation_authorization = null;
      renderProviderTlsRepairState();
      return false;
    }
  }

  async function refreshProviderTlsRepairHelperAvailabilityForResults(validationResults = {}) {
    for (const provider of providerNames) {
      if (validationResults[provider]) {
        await refreshProviderTlsRepairHelperAvailability(provider);
      }
    }
  }

  function sanitizeProviderTlsRepairSymbol(value, allowedValues, fallback = '') {
    const text = String(value || '').trim().toLowerCase();
    if (!/^[a-z0-9_]{1,80}$/.test(text)) {
      return fallback;
    }
    return allowedValues && !allowedValues.has(text) ? fallback : text;
  }

  function sanitizeProviderTlsRepairProvider(provider) {
    const normalized = String(provider || '').trim().toLowerCase();
    return providerNames.includes(normalized) ? normalized : '';
  }

  function sanitizeProviderTlsRepairOperationId(value) {
    const text = String(value || '').trim().toLowerCase();
    return /^[a-f0-9]{32}$/.test(text) ? text : '';
  }

  function cloneProviderTlsRepairOperationStatus(status) {
    if (!status) {
      return null;
    }
    return { ...status };
  }

  function normalizeProviderTlsRepairOperationStatus(payload = {}) {
    if (!payload || typeof payload !== 'object') {
      return null;
    }

    const provider = sanitizeProviderTlsRepairProvider(payload.provider);
    const operationType = payload.operation_type === 'provider_tls_repair' ? 'provider_tls_repair' : '';
    if (!provider || operationType !== 'provider_tls_repair') {
      return null;
    }

    const classification = sanitizeProviderTlsRepairSymbol(
      payload.classification,
      PROVIDER_TLS_REPAIR_STATUS_CLASSIFICATIONS,
      'unknown'
    );

    return {
      state: sanitizeProviderTlsRepairSymbol(payload.state, null, 'unknown'),
      operation_id: sanitizeProviderTlsRepairOperationId(payload.operation_id),
      operation_type: operationType,
      provider,
      accepted: payload.accepted === true,
      existing_operation: payload.existing_operation === true,
      execution_enabled: payload.execution_enabled === true,
      current_step: sanitizeProviderTlsRepairSymbol(payload.current_step, null, ''),
      classification,
      terminal: payload.terminal === true,
      next_action: sanitizeProviderTlsRepairSymbol(
        payload.next_action,
        PROVIDER_TLS_REPAIR_NEXT_ACTIONS,
        'support_review_required'
      )
    };
  }

  function isProviderTlsRepairOperationActive(status) {
    return Boolean(
      status &&
      status.terminal !== true &&
      ['pending', 'active', 'intermediate_success'].includes(status.classification)
    );
  }

  function rememberProviderTlsRepairOperationStatus(payload) {
    const status = normalizeProviderTlsRepairOperationStatus(payload);
    providerTlsRepairOperationStatus = status;
    if (!isProviderTlsRepairOperationActive(status)) {
      providerTlsRepairStartInFlight = false;
    }
    renderProviderTlsRepairState();
    return cloneProviderTlsRepairOperationStatus(status);
  }

  function getProviderTlsRepairActiveOperation() {
    if (!isProviderTlsRepairOperationActive(providerTlsRepairOperationStatus)) {
      return null;
    }
    return cloneProviderTlsRepairOperationStatus(providerTlsRepairOperationStatus);
  }

  function summarizeProviderTlsRepairAuthorization(record) {
    const authorization = record && record.operation_authorization;
    if (!hasCurrentProviderTlsRepairAuthorization(record)) {
      return null;
    }
    return {
      operation_type: 'provider_tls_repair',
      expires_at: authorization.expires_at,
      credential: 'short_lived_operation_authorization'
    };
  }

  function getProviderTlsRepairViewModel(provider) {
    const failure = getProviderValidationFailure(provider);
    if (!shouldShowProviderTlsRepair(provider)) {
      return {
        visible: false,
        enabled: false,
        provider,
        helper_available: false,
        blocked_reason: 'not_repairable'
      };
    }

    const helperAvailable = failure.helper_available === true;
    const authorizationReady = helperAvailable && hasCurrentProviderTlsRepairAuthorization(failure);
    const bridge = getPrivateProviderTlsRepairBridge(provider);
    const capabilityEnabled = Boolean(
      bridge && bridge.provider_tls_repair_capability === true
    );
    const enabled = (
      helperAvailable &&
      authorizationReady &&
      capabilityEnabled &&
      PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED
    );
    let blockedReason = null;
    if (!helperAvailable) {
      blockedReason = 'helper_unavailable';
    } else if (!authorizationReady) {
      blockedReason = 'operation_authorization_unavailable';
    } else if (!PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED) {
      blockedReason = 'browser_mutation_disabled';
    } else if (!capabilityEnabled) {
      blockedReason = 'helper_capability_disabled';
    }

    return {
      visible: true,
      enabled,
      provider,
      display_name: providerDisplayName(provider),
      category: failure.category,
      message: failure.message,
      support_action: failure.support_action,
      repair_command: failure.repair_command,
      confirmation: PROVIDER_TLS_REPAIR_CONFIRMATION,
      helper_available: helperAvailable,
      capability_enabled: capabilityEnabled,
      authorization_ready: authorizationReady,
      blocked_reason: blockedReason
    };
  }

  function getProviderTlsRepairStartContract(provider) {
    const selectedProvider = sanitizeProviderTlsRepairProvider(provider) || activeProviderTlsRepairProvider;
    const baseContract = {
      endpoint: '',
      method: 'POST',
      content_type: 'application/json',
      provider: selectedProvider || '',
      confirmation: PROVIDER_TLS_REPAIR_CONFIRMATION,
      allowed_body_fields: [...PROVIDER_TLS_REPAIR_ALLOWED_START_BODY_FIELDS],
      disallowed_body_fields: [...PROVIDER_TLS_REPAIR_DISALLOWED_START_BODY_FIELDS],
      ready: false,
      enabled: false,
      blocked_reason: 'not_repairable'
    };

    const viewModel = getProviderTlsRepairViewModel(selectedProvider);
    if (!viewModel.visible) {
      return baseContract;
    }

    const activeOperation = getProviderTlsRepairActiveOperation();
    if (activeOperation) {
      return {
        ...baseContract,
        provider: viewModel.provider,
        blocked_reason: 'operation_active',
        active_operation: activeOperation
      };
    }

    const failure = getProviderValidationFailure(viewModel.provider);
    const bridge = getPrivateProviderTlsRepairBridge(viewModel.provider);
    const endpoint = bridge
      ? getProviderTlsRepairHelperUrl(bridge.base_url, PROVIDER_TLS_REPAIR_OPERATION_ENDPOINT)
      : '';
    if (!viewModel.helper_available || !endpoint) {
      return {
        ...baseContract,
        provider: viewModel.provider,
        blocked_reason: 'helper_unavailable'
      };
    }
    const authorization = summarizeProviderTlsRepairAuthorization(failure);
    if (!authorization) {
      return {
        ...baseContract,
        endpoint,
        provider: viewModel.provider,
        blocked_reason: 'operation_authorization_unavailable'
      };
    }

    return {
      ...baseContract,
      endpoint,
      provider: viewModel.provider,
      operation_authorization: authorization,
      request_body_schema: {
        provider: viewModel.provider,
        confirmation: PROVIDER_TLS_REPAIR_CONFIRMATION,
        operation_authorization: 'short_lived_operation_authorization'
      },
      ready: true,
      enabled: viewModel.enabled,
      blocked_reason: viewModel.blocked_reason
    };
  }

  function buildProviderTlsRepairStartRequest(provider) {
    const contract = getProviderTlsRepairStartContract(provider);
    const failure = getProviderValidationFailure(contract.provider);
    const authorization = failure && failure.operation_authorization;
    if (!contract.ready || !authorization || !authorization.operation_token) {
      return null;
    }

    return {
      endpoint: contract.endpoint,
      options: {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: contract.provider,
          confirmation: PROVIDER_TLS_REPAIR_CONFIRMATION,
          operation_authorization: authorization.operation_token
        })
      }
    };
  }

  function clearStoredProviderTlsRepairOperation(operationId = '') {
    try {
      const stored = window.sessionStorage && window.sessionStorage.getItem(
        PROVIDER_TLS_REPAIR_ACTIVE_OPERATION_STORAGE_KEY
      );
      if (!stored) {
        return;
      }
      if (operationId) {
        const parsed = JSON.parse(stored);
        if (sanitizeProviderTlsRepairOperationId(parsed.operation_id) !== operationId) {
          return;
        }
      }
      window.sessionStorage.removeItem(PROVIDER_TLS_REPAIR_ACTIVE_OPERATION_STORAGE_KEY);
    } catch (_error) {
      // Storage is optional. Operation status remains available in memory.
    }
  }

  function persistProviderTlsRepairOperation(descriptor) {
    const operationId = sanitizeProviderTlsRepairOperationId(descriptor && descriptor.operation_id);
    const provider = sanitizeProviderTlsRepairProvider(descriptor && descriptor.provider);
    const helperBaseUrl = normalizeProviderTlsRepairBaseUrl(
      descriptor && descriptor.helper_base_url
    );
    if (!operationId || !provider || !helperBaseUrl) {
      return false;
    }
    try {
      window.sessionStorage.setItem(
        PROVIDER_TLS_REPAIR_ACTIVE_OPERATION_STORAGE_KEY,
        JSON.stringify({
          operation_id: operationId,
          provider,
          helper_base_url: helperBaseUrl
        })
      );
      return true;
    } catch (_error) {
      return false;
    }
  }

  function restoreProviderTlsRepairOperation() {
    try {
      const rawValue = window.sessionStorage && window.sessionStorage.getItem(
        PROVIDER_TLS_REPAIR_ACTIVE_OPERATION_STORAGE_KEY
      );
      if (!rawValue) {
        return null;
      }
      const parsed = JSON.parse(rawValue);
      const descriptor = {
        operation_id: sanitizeProviderTlsRepairOperationId(parsed.operation_id),
        provider: sanitizeProviderTlsRepairProvider(parsed.provider),
        helper_base_url: normalizeProviderTlsRepairBaseUrl(parsed.helper_base_url)
      };
      if (!descriptor.operation_id || !descriptor.provider || !descriptor.helper_base_url) {
        clearStoredProviderTlsRepairOperation();
        return null;
      }
      return descriptor;
    } catch (_error) {
      clearStoredProviderTlsRepairOperation();
      return null;
    }
  }

  function normalizeProviderTlsRepairStatusAuthorization(payload, descriptor) {
    const statusAuthorization = payload && payload.status_authorization;
    const baseUrl = normalizeProviderTlsRepairBaseUrl(payload && payload.base_url);
    const operationId = sanitizeProviderTlsRepairOperationId(payload && payload.operation_id);
    const credential = normalizeProviderTlsRepairCredential(
      statusAuthorization,
      'operation_status'
    );
    if (
      !credential ||
      !baseUrl ||
      operationId !== descriptor.operation_id ||
      baseUrl !== descriptor.helper_base_url ||
      !statusAuthorization ||
      statusAuthorization.operation_type !== 'provider_tls_repair'
    ) {
      return null;
    }
    return credential;
  }

  async function requestProviderTlsRepairStatusAuthorization(descriptor) {
    let payload;
    try {
      payload = await fetchJson(PROVIDER_TLS_REPAIR_STATUS_AUTHORIZATION_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: descriptor.provider,
          operation_id: descriptor.operation_id
        }),
        cache: 'no-store',
        timeoutMs: PROVIDER_TLS_REPAIR_REQUEST_TIMEOUT_MS
      });
    } catch (error) {
      if (error && typeof error === 'object') {
        error.request_stage = 'status_authorization';
      }
      throw error;
    }
    const currentBaseUrl = normalizeProviderTlsRepairBaseUrl(payload && payload.base_url);
    if (currentBaseUrl && currentBaseUrl !== descriptor.helper_base_url) {
      const error = new Error('The TowerScout host-helper session changed.');
      error.category = 'helper_session_changed';
      throw error;
    }
    const credential = normalizeProviderTlsRepairStatusAuthorization(payload, descriptor);
    if (!credential) {
      const error = new Error('Host repair status authorization was rejected.');
      error.request_stage = 'status_authorization';
      throw error;
    }
    return credential;
  }

  function normalizeProviderTlsRepairInlineStatusAuthorization(payload) {
    const authorization = payload && payload.status_authorization;
    if (!authorization || authorization.operation_type !== 'provider_tls_repair') {
      return null;
    }
    return normalizeProviderTlsRepairCredential(authorization, 'operation_status');
  }

  function createProviderTlsRepairTerminalStatus(descriptor, state, classification, nextAction) {
    return {
      state,
      operation_id: descriptor.operation_id,
      operation_type: 'provider_tls_repair',
      provider: descriptor.provider,
      accepted: false,
      existing_operation: false,
      execution_enabled: false,
      current_step: '',
      classification,
      terminal: true,
      next_action: nextAction
    };
  }

  async function fetchProviderTlsRepairOperationStatus(descriptor, credential) {
    const statusUrl = getProviderTlsRepairHelperUrl(
      descriptor.helper_base_url,
      `/operations/${descriptor.operation_id}`
    );
    if (!statusUrl || !hasCurrentProviderTlsRepairCredential(credential)) {
      const error = new Error('Host repair status authorization is unavailable.');
      error.status = 401;
      error.request_stage = 'operation_status';
      throw error;
    }
    try {
      return await fetchJson(statusUrl, {
        method: 'GET',
        headers: {
          'X-TowerScout-Operation-Authorization': credential.authorization
        },
        cache: 'no-store',
        timeoutMs: PROVIDER_TLS_REPAIR_REQUEST_TIMEOUT_MS
      });
    } catch (error) {
      if (error && typeof error === 'object') {
        error.request_stage = 'operation_status';
      }
      throw error;
    }
  }

  async function runProviderTlsRepairPolling(descriptor) {
    const deadline = Date.now() + PROVIDER_TLS_REPAIR_POLL_TIMEOUT_MS;
    let statusAuthorization = descriptor.status_authorization || null;
    let transientFailures = 0;
    let unresolvedNotified = false;

    while (true) {
      try {
        if (!hasCurrentProviderTlsRepairCredential(statusAuthorization)) {
          statusAuthorization = await requestProviderTlsRepairStatusAuthorization(descriptor);
        }

        let payload;
        try {
          payload = await fetchProviderTlsRepairOperationStatus(descriptor, statusAuthorization);
        } catch (error) {
          if (error && error.status === 401) {
            statusAuthorization = await requestProviderTlsRepairStatusAuthorization(descriptor);
            if (!statusAuthorization) {
              throw error;
            }
            payload = await fetchProviderTlsRepairOperationStatus(descriptor, statusAuthorization);
          } else {
            throw error;
          }
        }

        const status = normalizeProviderTlsRepairOperationStatus(payload);
        if (
          !status ||
          status.operation_id !== descriptor.operation_id ||
          status.provider !== descriptor.provider
        ) {
          throw new Error('Host repair returned an invalid status.');
        }
        rememberProviderTlsRepairOperationStatus(status);
        if (status.terminal) {
          clearStoredProviderTlsRepairOperation(descriptor.operation_id);
          return status;
        }
        transientFailures = 0;
      } catch (error) {
        if (error && error.category === 'helper_session_changed') {
          const changed = createProviderTlsRepairTerminalStatus(
            descriptor,
            'helper_session_changed',
            'terminal_timeout',
            'new_authorization_required'
          );
          rememberProviderTlsRepairOperationStatus(changed);
          clearStoredProviderTlsRepairOperation(descriptor.operation_id);
          TowerScoutErrorHandler.showUserNotification(
            'The TowerScout host-helper session changed. The previous recovery record was cleared; reload setup to obtain a new authorization before retrying.',
            'info'
          );
          return changed;
        }
        if (
          error &&
          error.request_stage === 'operation_status' &&
          (error.status === 404 || error.status === 410)
        ) {
          const expired = createProviderTlsRepairTerminalStatus(
            descriptor,
            'operation_expired',
            'terminal_timeout',
            'clear_or_reauthorize_after_timeout'
          );
          rememberProviderTlsRepairOperationStatus(expired);
          clearStoredProviderTlsRepairOperation(descriptor.operation_id);
          return expired;
        }

        transientFailures += 1;
        if (transientFailures === 1) {
          TowerScoutErrorHandler.showUserNotification(
            'Host TLS repair status is temporarily unavailable. TowerScout will keep retrying; do not run the command fallback while the outcome is unknown.',
            'info'
          );
        }
      }

      if (Date.now() >= deadline && !unresolvedNotified) {
        unresolvedNotified = true;
        const uncertain = {
          state: 'status_unavailable',
          operation_id: descriptor.operation_id,
          operation_type: 'provider_tls_repair',
          provider: descriptor.provider,
          accepted: true,
          existing_operation: true,
          execution_enabled: true,
          current_step: 'awaiting_status',
          classification: 'active',
          terminal: false,
          next_action: 'poll_existing_operation'
        };
        rememberProviderTlsRepairOperationStatus(uncertain);
        TowerScoutErrorHandler.showUserNotification(
          'Host TLS repair is still unresolved. TowerScout will continue low-frequency authenticated status checks; do not run the command fallback until the helper reports a terminal result or the operation is confirmed gone.',
          'info'
        );
      }

      const retryDelay = transientFailures > 0
        ? Math.min(
          PROVIDER_TLS_REPAIR_POLL_INTERVAL_MS * (2 ** Math.min(transientFailures - 1, 4)),
          PROVIDER_TLS_REPAIR_MAX_RETRY_DELAY_MS
        )
        : PROVIDER_TLS_REPAIR_POLL_INTERVAL_MS;
      await new Promise(resolve => window.setTimeout(
        resolve,
        unresolvedNotified
          ? Math.max(retryDelay, PROVIDER_TLS_REPAIR_MAX_RETRY_DELAY_MS)
          : retryDelay
      ));
    }
  }

  function pollProviderTlsRepairOperation(descriptor) {
    if (
      providerTlsRepairPollingPromise &&
      providerTlsRepairPollingPromise.operation_id === descriptor.operation_id
    ) {
      return providerTlsRepairPollingPromise;
    }
    const pollingPromise = runProviderTlsRepairPolling(descriptor)
      .finally(() => {
        if (
          providerTlsRepairPollingPromise &&
          providerTlsRepairPollingPromise.operation_id === descriptor.operation_id
        ) {
          providerTlsRepairPollingPromise = null;
        }
        providerTlsRepairStartInFlight = false;
        renderProviderTlsRepairState();
      });
    pollingPromise.operation_id = descriptor.operation_id;
    providerTlsRepairPollingPromise = pollingPromise;
    return providerTlsRepairPollingPromise;
  }

  function getVisibleProviderTlsRepairViewModels() {
    const visibleViewModels = [];
    for (const provider of providerNames) {
      const viewModel = getProviderTlsRepairViewModel(provider);
      if (viewModel.visible) {
        visibleViewModels.push(viewModel);
      }
    }
    return visibleViewModels;
  }

  function setText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
      element.textContent = text || '';
    }
  }

  function renderProviderTlsRepairState() {
    const panel = document.getElementById('wizard_provider_tls_repair_panel');
    if (!panel) {
      return null;
    }

    const visibleViewModels = getVisibleProviderTlsRepairViewModels();
    const viewModel = visibleViewModels[0] || null;
    const additionalVisibleCount = Math.max(visibleViewModels.length - 1, 0);
    const checkbox = document.getElementById('wizard_provider_tls_repair_confirm');
    const confirmation = document.getElementById('wizard_provider_tls_repair_confirmation');
    const button = document.getElementById('wizard_provider_tls_repair_button');

    if (!viewModel) {
      activeProviderTlsRepairProvider = null;
      panel.style.display = 'none';
      if (checkbox) {
        checkbox.checked = false;
      }
      if (confirmation) {
        confirmation.style.display = 'none';
      }
      if (button) {
        button.disabled = true;
        button.style.display = 'none';
      }
      setText('wizard_provider_tls_repair_title', '');
      setText('wizard_provider_tls_repair_message', '');
      setText('wizard_provider_tls_repair_support', '');
      setText('wizard_provider_tls_repair_command', '');
      setText('wizard_provider_tls_repair_status', '');
      return null;
    }

    activeProviderTlsRepairProvider = viewModel.provider;
    panel.style.display = 'block';
    setText('wizard_provider_tls_repair_title', `${viewModel.display_name} TLS repair`);
    const additionalRepairNotice = additionalVisibleCount === 1
      ? ' 1 additional provider also needs repair.'
      : additionalVisibleCount > 1
        ? ` ${additionalVisibleCount} additional providers also need repair.`
        : '';
    setText(
      'wizard_provider_tls_repair_message',
      `${viewModel.display_name} failed with a repairable TLS trust error.${additionalRepairNotice}`
    );
    setText('wizard_provider_tls_repair_support', viewModel.support_action || '');
    setText(
      'wizard_provider_tls_repair_command',
      viewModel.repair_command ? `Command fallback: ${viewModel.repair_command}` : ''
    );

    const confirmed = checkbox && checkbox.checked === true;
    const activeOperation = getProviderTlsRepairActiveOperation();
    const operationActive = Boolean(activeOperation);
    const terminalStatus = (
      providerTlsRepairOperationStatus &&
      providerTlsRepairOperationStatus.terminal === true
    ) ? providerTlsRepairOperationStatus : null;
    if (confirmation) {
      confirmation.style.display = viewModel.helper_available ? '' : 'none';
    }
    if (button) {
      button.style.display = viewModel.helper_available ? '' : 'none';
      button.disabled = Boolean(
        operationActive ||
        terminalStatus ||
        providerTlsRepairStartInFlight ||
        !(viewModel.enabled && confirmed)
      );
      button.textContent = viewModel.enabled ? 'Repair and restart TowerScout' : 'Repair unavailable';
    }

    let statusMessage;
    if (operationActive) {
      statusMessage = `A ${providerDisplayName(activeOperation.provider)} host repair operation is active. Wait for its authenticated terminal result before starting another repair.`;
    } else if (terminalStatus && terminalStatus.classification === 'terminal_success') {
      statusMessage = `${providerDisplayName(terminalStatus.provider)} TLS repair completed. TowerScout is rechecking readiness and provider validation.`;
    } else if (terminalStatus) {
      statusMessage = getProviderTlsRepairTerminalGuidance(terminalStatus);
    } else if (!viewModel.helper_available) {
      statusMessage = 'The host helper is unavailable. Use the command fallback for this package.';
    } else if (!viewModel.authorization_ready) {
      statusMessage = 'Host repair authorization is not available yet. Use the command fallback for this package.';
    } else if (!PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED) {
      statusMessage = 'Host repair is prepared for review but browser-triggered repair remains disabled in this gate.';
    } else if (!viewModel.capability_enabled) {
      statusMessage = 'The helper repair capability remains disabled pending review. Use the command fallback.';
    } else if (!confirmed) {
      statusMessage = 'Confirm the restart behavior before running repair.';
    } else {
      statusMessage = 'Ready to start the authorized repair operation.';
    }

    if (additionalVisibleCount > 0) {
      statusMessage += additionalVisibleCount === 1
        ? ' Another provider also needs repair.'
        : ` ${additionalVisibleCount} additional providers also need repair.`;
    }
    setText('wizard_provider_tls_repair_status', statusMessage);

    return viewModel;
  }

  function updateProviderTlsRepairControls() {
    return renderProviderTlsRepairState();
  }

  function getProviderTlsRepairTerminalGuidance(status) {
    const providerName = providerDisplayName(status && status.provider);
    switch (status && status.next_action) {
      case 'review_runtime_state_before_retry':
        return `${providerName} repair could not stop the runtime cleanly. Review TowerScout runtime status before retrying.`;
      case 'use_startup_fallback_guidance':
      case 'use_manual_start_fallback':
        return `${providerName} TLS repair finished, but TowerScout did not restart cleanly. Use the documented startup troubleshooting guidance.`;
      case 'clear_or_reauthorize_after_timeout':
      case 'new_authorization_required':
        return `${providerName} repair authorization or status expired. Confirm that no host operation is active, then reload setup before retrying.`;
      case 'use_manual_dry_run_support_selection':
        return `${providerName} repair needs support review. Run the documented manual dry run to select the trusted certificate safely.`;
      case 'use_manual_tls_repair_fallback':
        return `${providerName} guided TLS repair failed definitively. Use the displayed manual repair command before retrying setup.`;
      case 'use_status_and_log_guidance':
        return `${providerName} repair ended without a healthy TowerScout readiness result. Review status and sanitized logs.`;
      default:
        return `${providerName} host repair ended with ${status && status.state ? status.state : 'an unknown result'}. Support review is required before retrying.`;
    }
  }

  function getProviderTlsRepairStartErrorMessage(error) {
    if (error && error.category === 'request_timeout') {
      return 'Host TLS repair start timed out before TowerScout could confirm acceptance. TowerScout retained the recovery guard; wait for authenticated status before using the command fallback.';
    }
    if (error && error.status === 401) {
      return 'Host TLS repair authorization was rejected or expired. Revalidate the provider to obtain a new authorization before retrying.';
    }
    if (error && error.status === 403) {
      return 'The host TLS repair capability is not enabled for this runtime. Use the reviewed command fallback.';
    }
    if (error && error.status === 429) {
      return 'Host TLS repair start is rate limited. Wait before revalidating and retrying; do not repeatedly submit the operation.';
    }
    if (error && error.message === 'Host repair did not return a valid operation.') {
      return 'The host helper returned an invalid operation descriptor. TowerScout did not clear any active-operation guard; review helper status before retrying.';
    }
    return 'Host TLS repair start could not be confirmed after a bounded retry. Do not run the command fallback until the helper outcome is confirmed.';
  }

  async function executeProviderTlsRepairStart(viewModel, request) {
    const bridge = getPrivateProviderTlsRepairBridge(viewModel.provider);
    const descriptorBase = {
      provider: viewModel.provider,
      helper_base_url: bridge && bridge.base_url
    };

    providerTlsRepairStartInFlight = true;
    renderProviderTlsRepairState();
    try {
      let payload = null;
      let lastError = null;
      for (let attempt = 0; attempt < 2 && !payload; attempt += 1) {
        try {
          payload = await fetchJson(request.endpoint, {
            ...request.options,
            cache: 'no-store',
            timeoutMs: PROVIDER_TLS_REPAIR_REQUEST_TIMEOUT_MS
          });
        } catch (error) {
          const conflictStatus = error && error.status === 409
            ? normalizeProviderTlsRepairOperationStatus(error.payload)
            : null;
          if (conflictStatus && conflictStatus.operation_id) {
            payload = error.payload;
            break;
          }
          lastError = error;
          const retryable = !error || !error.status || error.status === 429 || error.status >= 500;
          if (!retryable || attempt === 1) {
            throw error;
          }
          await new Promise(resolve => window.setTimeout(resolve, 500));
        }
      }
      if (!payload) {
        throw lastError || new Error('Host repair start outcome is unknown.');
      }

      const status = normalizeProviderTlsRepairOperationStatus(payload);
      if (!status || !status.operation_id) {
        throw new Error('Host repair did not return a valid operation.');
      }
      if (!status.existing_operation && status.provider !== descriptorBase.provider) {
        throw new Error('Host repair returned an inconsistent provider descriptor.');
      }
      rememberProviderTlsRepairOperationStatus(status);

      const descriptor = {
        ...descriptorBase,
        operation_id: status.operation_id,
        provider: status.provider,
        status_authorization: normalizeProviderTlsRepairInlineStatusAuthorization(payload)
      };
      persistProviderTlsRepairOperation(descriptor);
      TowerScoutErrorHandler.showUserNotification(
        status.existing_operation
          ? 'The existing host TLS repair operation is being monitored.'
          : 'The authorized host TLS repair operation was accepted.',
        'info'
      );
      const terminalStatus = await pollProviderTlsRepairOperation(descriptor);
      await handleProviderTlsRepairTerminalStatus(terminalStatus);
      return terminalStatus;
    } catch (error) {
      providerTlsRepairStartInFlight = false;
      renderProviderTlsRepairState();
      TowerScoutErrorHandler.showUserNotification(
        getProviderTlsRepairStartErrorMessage(error),
        'info'
      );
      return false;
    }
  }

  async function handleProviderTlsRepairTerminalStatus(status) {
    if (!status || status.terminal !== true) {
      return false;
    }
    if (
      status.classification !== 'terminal_success' ||
      status.next_action !== 'retry_provider_validation'
    ) {
      TowerScoutErrorHandler.showUserNotification(
        getProviderTlsRepairTerminalGuidance(status),
        'info'
      );
      renderProviderTlsRepairState();
      return false;
    }

    try {
      let readiness = null;
      let readinessError = null;
      for (
        let attempt = 0;
        attempt < PROVIDER_TLS_REPAIR_READINESS_MAX_ATTEMPTS;
        attempt += 1
      ) {
        try {
          readiness = await fetchJson('/api/readiness', {
            cache: 'no-store',
            timeoutMs: PROVIDER_TLS_REPAIR_REQUEST_TIMEOUT_MS
          });
          if (
            readiness &&
            ['setup_required', 'degraded', 'ready'].includes(readiness.state)
          ) {
            break;
          }
          readinessError = new Error('TowerScout readiness has not recovered yet.');
        } catch (error) {
          readinessError = error;
        }
        readiness = null;
        if (attempt < PROVIDER_TLS_REPAIR_READINESS_MAX_ATTEMPTS - 1) {
          const retryDelay = Math.min(
            1000 * (2 ** attempt),
            PROVIDER_TLS_REPAIR_READINESS_MAX_RETRY_DELAY_MS
          );
          await new Promise(resolve => window.setTimeout(resolve, retryDelay));
        }
      }
      if (!readiness) {
        throw readinessError || new Error('TowerScout readiness has not recovered yet.');
      }
      const provider = status.provider;
      const keyElement = document.getElementById(`wizard_${provider}_key`);
      const indicatorId = `${provider}_key_status`;
      const validationMessages = [];
      const isValid = await validateProviderInput(
        provider,
        keyElement ? keyElement.value.trim() : '',
        indicatorId,
        providerDisplayName(provider),
        validationMessages
      );
      validatedKeys[provider] = isValid;
      updateProviderOptions();
      if (isValid) {
        providerTlsRepairOperationStatus = null;
        if (currentStep === 2) {
          nextStep();
        }
        TowerScoutErrorHandler.showUserNotification(
          `${providerDisplayName(provider)} TLS repair and provider validation succeeded.`,
          'success'
        );
      } else {
        providerTlsRepairOperationStatus = {
          ...status,
          state: 'provider_revalidation_failed',
          classification: 'terminal_support_escalation',
          next_action: 'use_manual_tls_repair_fallback'
        };
        TowerScoutErrorHandler.showUserNotification(
          validationMessages.join(' ') || `${providerDisplayName(provider)} still requires review after host repair.`,
          'info'
        );
      }
    } catch (error) {
      providerTlsRepairOperationStatus = {
        ...status,
        state: 'readiness_revalidation_pending',
        classification: 'terminal_timeout',
        next_action: 'use_status_and_log_guidance'
      };
      TowerScoutErrorHandler.showUserNotification(
        error.message || 'TowerScout restarted, but readiness revalidation is not complete yet.',
        'info'
      );
    }
    renderProviderTlsRepairState();
    return true;
  }

  function startProviderTlsRepair() {
    const viewModel = getProviderTlsRepairViewModel(activeProviderTlsRepairProvider);
    if (!viewModel.visible) {
      return false;
    }

    const startContract = getProviderTlsRepairStartContract(viewModel.provider);
    if (startContract.blocked_reason === 'operation_active') {
      TowerScoutErrorHandler.showUserNotification(
        'A host TLS repair operation is already active. Wait for it to finish before starting another repair.',
        'info'
      );
      renderProviderTlsRepairState();
      return false;
    }

    if (!PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED || !viewModel.enabled) {
      TowerScoutErrorHandler.showUserNotification(
        'Host TLS repair is not enabled for this package yet. Use the suggested command fallback.',
        'info'
      );
      renderProviderTlsRepairState();
      return false;
    }

    if (providerTlsRepairStartInFlight) {
      TowerScoutErrorHandler.showUserNotification(
        'Host TLS repair is already starting. Wait for the current operation status.',
        'info'
      );
      renderProviderTlsRepairState();
      return false;
    }

    const confirmation = document.getElementById('wizard_provider_tls_repair_confirm');
    if (!confirmation || confirmation.checked !== true) {
      TowerScoutErrorHandler.showUserNotification(
        'Confirm the restart behavior before running host TLS repair.',
        'info'
      );
      renderProviderTlsRepairState();
      return false;
    }

    const request = buildProviderTlsRepairStartRequest(viewModel.provider);
    if (!request) {
      TowerScoutErrorHandler.showUserNotification(
        'Host TLS repair authorization is no longer current. Use the command fallback or revalidate the key.',
        'info'
      );
      renderProviderTlsRepairState();
      return false;
    }

    return executeProviderTlsRepairStart(viewModel, request);
  }

  function resumeStoredProviderTlsRepairOperation() {
    if (!PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED) {
      return false;
    }
    const descriptor = restoreProviderTlsRepairOperation();
    if (!descriptor) {
      return false;
    }
    rememberProviderTlsRepairOperationStatus({
      state: 'planned',
      operation_id: descriptor.operation_id,
      operation_type: 'provider_tls_repair',
      provider: descriptor.provider,
      accepted: true,
      existing_operation: true,
      execution_enabled: false,
      current_step: 'awaiting_status',
      classification: 'pending',
      terminal: false,
      next_action: 'poll_existing_operation'
    });
    return pollProviderTlsRepairOperation(descriptor)
      .then(status => handleProviderTlsRepairTerminalStatus(status));
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
    renderProviderTlsRepairState();
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

    if (validatedKeys.google && googleOption) {
      googleOption.checked = true;
    } else if (validatedKeys.azure && azureOption) {
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

  async function validateProviderInput(provider, key, indicatorId, displayName, validationMessages) {
    if (!key) {
      clearProviderValidationState(provider);
      return false;
    }

    try {
      const result = await validateKey(provider, key);
      const validation = rememberProviderValidationResult(provider, result);
      await refreshProviderTlsRepairHelperAvailability(provider);
      const isValid = validation.valid === true;
      updateIndicator(indicatorId, isValid);
      if (!isValid && validation.message) {
        validationMessages.push(providerFailureMessage(displayName, validation));
      }
      return isValid;
    } catch (error) {
      const validation = rememberProviderValidationResult(provider, error.payload || error);
      await refreshProviderTlsRepairHelperAvailability(provider);
      updateIndicator(indicatorId, false);
      validationMessages.push(providerFailureMessage(displayName, validation));
      return false;
    }
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
    resetProviderValidationState();
    updateIndicator('google_key_status', null);
    updateIndicator('azure_key_status', null);
    validationInFlight = true;
    setButtonBusy('wizard_validate_button', true, 'Validate Keys', 'Validating...');

    try {
      const validationMessages = [];

      validatedKeys.google = await validateProviderInput(
        'google',
        googleKey,
        'google_key_status',
        'Google Maps',
        validationMessages
      );
      validatedKeys.azure = await validateProviderInput(
        'azure',
        azureKey,
        'azure_key_status',
        'Azure Maps',
        validationMessages
      );

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
      google_api_key: validatedKeys.google ? document.getElementById('wizard_google_key').value.trim() : '',
      azure_maps_subscription_key: validatedKeys.azure ? document.getElementById('wizard_azure_key').value.trim() : '',
      default_map_provider: getSelectedDefaultProvider()
    };

    saveInFlight = true;
    setButtonBusy('wizard_save_button', true, 'Save Configuration', 'Saving...');

    try {
      const result = await fetchJson('/api/config/save-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      rememberProviderValidationResults(result.validation_results);
      await refreshProviderTlsRepairHelperAvailabilityForResults(result.validation_results);

      window.needsSetup = false;
      nextStep();
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
        TowerScoutErrorHandler.showUserNotification(`Configuration saved. ${messages.join(' ')}`, 'info');
      } else {
        TowerScoutErrorHandler.showUserNotification('Configuration saved successfully.', 'success');
      }
    } catch (error) {
      const validationResults = (error.payload && error.payload.validation_results) || {};
      rememberProviderValidationResults(validationResults);
      await refreshProviderTlsRepairHelperAvailabilityForResults(validationResults);
      TowerScoutErrorHandler.showUserNotification(saveFailureMessage(error), 'error');
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
      const resumedOperation = resumeStoredProviderTlsRepairOperation();
      if (resumedOperation && typeof resumedOperation.catch === 'function') {
        resumedOperation.catch(error => {
          console.error('SetupWizard host repair resume failed:', error);
          TowerScoutErrorHandler.showUserNotification(
            'TowerScout could not resume host repair status automatically. Reload setup to retry authenticated status recovery.',
            'info'
          );
        });
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
    complete,
    getProviderValidationState,
    refreshProviderTlsRepairHelperAvailability,
    shouldShowProviderTlsRepair,
    getProviderTlsRepairViewModel,
    getProviderTlsRepairStartContract,
    rememberProviderTlsRepairOperationStatus,
    getProviderTlsRepairActiveOperation,
    renderProviderTlsRepairState,
    updateProviderTlsRepairControls,
    startProviderTlsRepair
  };

  document.addEventListener('DOMContentLoaded', init);
})();
