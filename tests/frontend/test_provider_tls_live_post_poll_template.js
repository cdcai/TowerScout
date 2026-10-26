#!/usr/bin/env node
/**
 * Puppeteer coverage for the production SetupWizard TLS-repair controller.
 *
 * The browser loads the repository's real apiHelpers.js and setup-wizard.js
 * sources into a minimal DOM. Only the two closed activation constants and
 * the poll interval are changed in-memory for this isolated test harness.
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const ROOT = path.join(__dirname, '../..');
const API_HELPERS = fs.readFileSync(
  path.join(ROOT, 'webapp/js/src/utils/apiHelpers.js'),
  'utf8'
);
const SETUP_WIZARD = fs.readFileSync(
  path.join(ROOT, 'webapp/js/src/setup-wizard.js'),
  'utf8'
)
  .replace(
    'const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false;',
    'const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = true;'
  )
  .replace(
    'const PROVIDER_TLS_REPAIR_POLL_INTERVAL_MS = 1000;',
    'const PROVIDER_TLS_REPAIR_POLL_INTERVAL_MS = 10;'
  );

const WEB_URL = (
  process.env.TEST_WEB_URL || 'http://localhost:5000'
).replace(/\/+$/, '');
const HELPER_BASE_URL = (
  process.env.TEST_HELPER_BASE_URL || 'http://127.0.0.1:5001'
).replace(/\/+$/, '');
const WEB_APP_PORT = Number(new URL(WEB_URL).port || 80);
const USE_REAL_HELPER = ['1', 'true'].includes(
  String(process.env.E2E_USE_SERVER || '').toLowerCase()
);
const OPERATION_TOKEN = WEB_URL.includes('127.0.0.1')
  ? `TEST_LOOPBACK_${'R'.repeat(32)}`
  : `TEST_LOCALHOST_${'L'.repeat(32)}`;
const PROBE_TOKEN = `PROBE_${'Y'.repeat(40)}`;
const STATUS_TOKEN = `STATUS_${'Z'.repeat(40)}`;
const OPERATION_ID = '0123456789abcdef0123456789abcdef';

async function installHarness(page) {
  await page.goto(WEB_URL, { waitUntil: 'networkidle2', timeout: 60000 });
  await page.setContent(`
    <div id="setup_wizard_div">
      <div class="wizard-progress">
        ${[1, 2, 3, 4, 5].map(step => `<span class="step" data-step="${step}"></span>`).join('')}
      </div>
      ${[1, 2, 3, 4, 5].map(step => `<section class="wizard-step" data-step="${step}"></section>`).join('')}
    </div>
    <input id="wizard_google_key" value="google-key">
    <input id="wizard_azure_key" value="azure-key">
    <span id="google_key_status"></span>
    <span id="azure_key_status"></span>
    <div id="wizard_validation_message"></div>
    <button id="wizard_validate_button"></button>
    <button id="wizard_save_button"></button>
    <div id="wizard_performance_stats"></div>
    <label id="wizard_google_provider_option"><input name="default_provider" value="google"></label>
    <label id="wizard_azure_provider_option"><input name="default_provider" value="azure"></label>
    <div id="wizard_provider_tls_repair_panel">
      <div id="wizard_provider_tls_repair_title"></div>
      <div id="wizard_provider_tls_repair_message"></div>
      <div id="wizard_provider_tls_repair_support"></div>
      <div id="wizard_provider_tls_repair_command"></div>
      <div id="wizard_provider_tls_repair_confirmation"></div>
      <input id="wizard_provider_tls_repair_confirm" type="checkbox">
      <button id="wizard_provider_tls_repair_button"></button>
      <div id="wizard_provider_tls_repair_status"></div>
    </div>
  `);

  await page.evaluate(
    ({
      helperBaseUrl,
      useRealHelper,
      operationToken,
      probeToken,
      statusToken,
      operationId,
      webAppPort
    }) => {
      const response = (ok, status, payload) => ({
        ok,
        status,
        async json() {
          return payload;
        }
      });
      window.needsSetup = true;
      window.__notifications = [];
      window.__fetchCalls = [];
      window.__googleValidationCount = 0;
      window.TowerScoutLogger = { info() {}, debug() {} };
      window.TowerScoutErrorHandler = {
        showUserNotification(message, type) {
          window.__notifications.push({ message, type });
        }
      };
      const nativeFetch = window.fetch.bind(window);
      const helperBridge = {
        base_url: helperBaseUrl,
        probe: {
          path: '/health',
          scope: 'helper_probe',
          expires_at: '2999-01-01T00:00:00Z',
          authorization: probeToken
        },
        operation_authorization: {
          operation_type: 'provider_tls_repair',
          expires_at: '2999-01-01T00:00:00Z',
          operation_token: operationToken
        },
        provider_tls_repair_capability: true,
        expected_runtime: {
          engine: 'docker',
          gpu: 'off',
          app_port: webAppPort
        }
      };

      window.fetch = async (url, options = {}) => {
        const target = String(url);
        window.__fetchCalls.push({
          url: target,
          method: options.method || 'GET',
          body: options.body || null,
          headers: options.headers || {}
        });

        if (target === '/api/config/validate-key') {
          const requestBody = JSON.parse(options.body);
          if (requestBody.provider === 'azure') {
            return response(true, 200, {
              valid: true,
              provider: 'azure',
              category: 'tls_ok',
              repairable: false
            });
          }
          window.__googleValidationCount += 1;
          if (window.__googleValidationCount > 1) {
            return response(true, 200, {
              valid: true,
              provider: 'google',
              category: 'tls_ok',
              repairable: false,
              message: 'Google Maps key validated successfully.'
            });
          }
          return response(false, 502, {
            error: true,
            message: 'Google Maps TLS verification failed.',
            details: {
              provider: 'google',
              category: 'tls_ca_untrusted',
              repairable: true,
              helper_available: false,
              support_action: 'Use guided TLS repair.',
              repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
              helper_bridge: helperBridge
            }
          });
        }
        if (target === '/api/readiness') {
          return response(true, 200, { state: 'ready' });
        }
        if (target === '/api/config/performance') {
          return response(true, 200, { session_count: 0 });
        }
        if (target === '/api/config/status') {
          return response(true, 200, { needs_setup: true });
        }
        if (target === '/api/config/provider-tls-repair-status-authorization') {
          const requestBody = JSON.parse(options.body);
          return response(true, 200, {
            base_url: helperBaseUrl,
            operation_id: requestBody.operation_id,
            status_authorization: {
              operation_type: 'provider_tls_repair',
              scope: 'operation_status',
              expires_at: '2999-01-01T00:00:00Z',
              authorization: statusToken
            }
          });
        }

        if (target.startsWith(helperBaseUrl) && useRealHelper) {
          return nativeFetch(target, options);
        }
        if (target === `${helperBaseUrl}/health`) {
          return response(true, 200, {
            state: 'ready',
            runtime: { engine: 'docker', gpu: 'off', app_port: webAppPort },
            capabilities: {
              provider_tls_repair: true,
              podman_provider_repair: false,
              max_active_operations: 1
            }
          });
        }
        if (target === `${helperBaseUrl}/operations/provider-tls-repair`) {
          return response(true, 202, {
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
            next_action: 'await_controlled_execution',
            status_authorization: {
              operation_type: 'provider_tls_repair',
              scope: 'operation_status',
              expires_at: '2999-01-01T00:00:00Z',
              authorization: statusToken
            }
          });
        }
        if (target === `${helperBaseUrl}/operations/${operationId}`) {
          window.__pollCount = (window.__pollCount || 0) + 1;
          if (window.__pollCount === 1) {
            return response(true, 200, {
              state: 'runtime_starting',
              operation_id: operationId,
              operation_type: 'provider_tls_repair',
              provider: 'google',
              accepted: true,
              existing_operation: false,
              execution_enabled: true,
              current_step: 'runtime_starting',
              classification: 'active',
              terminal: false,
              next_action: 'poll_existing_operation'
            });
          }
          return response(true, 200, {
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
          });
        }
        throw new Error(`Unexpected fetch target: ${target}`);
      };
    },
    {
      helperBaseUrl: HELPER_BASE_URL,
      useRealHelper: USE_REAL_HELPER,
      operationToken: OPERATION_TOKEN,
      probeToken: PROBE_TOKEN,
      statusToken: STATUS_TOKEN,
      operationId: OPERATION_ID,
      webAppPort: WEB_APP_PORT
    }
  );

  await page.addScriptTag({ content: API_HELPERS });
  await page.addScriptTag({ content: SETUP_WIZARD });
}

async function run() {
  const launchOptions = {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  };
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    launchOptions.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
  } else if (process.env.TEST_BROWSER_EXECUTABLE) {
    launchOptions.executablePath = process.env.TEST_BROWSER_EXECUTABLE;
  }
  const browser = await puppeteer.launch(launchOptions);
  const page = await browser.newPage();
  try {
    await installHarness(page);
    if (USE_REAL_HELPER) {
      const rejectedProbe = await page.evaluate(
        async helperBaseUrl => {
          const response = await fetch(`${helperBaseUrl}/health`, {
            method: 'GET'
          });
          return { status: response.status, payload: await response.json() };
        },
        HELPER_BASE_URL
      );
      assert.strictEqual(rejectedProbe.status, 401);
      assert.strictEqual(
        rejectedProbe.payload.state,
        'rejected_operation_authorization'
      );

      const rejectedStart = await page.evaluate(
        async helperBaseUrl => {
          const response = await fetch(`${helperBaseUrl}/operations/provider-tls-repair`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              provider: 'google',
              confirmation: 'repair_tls_and_restart',
              operation_authorization: 'invalid-start-authorization'
            })
          });
          return { status: response.status, payload: await response.json() };
        },
        HELPER_BASE_URL
      );
      assert.strictEqual(rejectedStart.status, 401);
      assert.strictEqual(
        rejectedStart.payload.state,
        'rejected_operation_authorization'
      );
    }
    const result = await page.evaluate(async () => {
      if (!window.SetupWizard || typeof window.SetupWizard.startProviderTlsRepair !== 'function') {
        throw new Error('Production SetupWizard controller was not loaded.');
      }
      window.SetupWizard.showStep(2);
      await window.SetupWizard.validateAndNext();
      const viewModel = window.SetupWizard.getProviderTlsRepairViewModel('google');
      document.getElementById('wizard_provider_tls_repair_confirm').checked = true;
      window.SetupWizard.updateProviderTlsRepairControls();
      const status = await window.SetupWizard.startProviderTlsRepair();
      return {
        viewModel,
        status,
        fetchCalls: window.__fetchCalls,
        notifications: window.__notifications,
        renderedStatus: document.getElementById('wizard_provider_tls_repair_status').textContent,
        storage: sessionStorage.getItem('towerscout.providerTlsRepair.activeOperation'),
        googleValidationCount: window.__googleValidationCount
      };
    });

    assert.strictEqual(result.viewModel.enabled, true);
    assert.strictEqual(result.status.state, 'ready');
    assert.strictEqual(result.status.terminal, true);
    assert.strictEqual(result.googleValidationCount, 2);
    assert.strictEqual(result.storage, null);

    const startCalls = result.fetchCalls.filter(
      call => call.url === `${HELPER_BASE_URL}/operations/provider-tls-repair`
    );
    const validStartCalls = startCalls.filter(call => {
      try {
        return (
          JSON.parse(call.body || '{}').operation_authorization ===
          OPERATION_TOKEN
        );
      } catch (_error) {
        return false;
      }
    });
    const pollCalls = result.fetchCalls.filter(
      call => /^https?:\/\/.+\/operations\/[a-f0-9]{32}$/i.test(call.url)
    );
    assert.strictEqual(validStartCalls.length, 1);
    assert.ok(pollCalls.length >= 1);
    if (USE_REAL_HELPER) {
      const rejectedStatus = await page.evaluate(
        async ({ helperBaseUrl, operationId }) => {
          const response = await fetch(`${helperBaseUrl}/operations/${operationId}`, {
            method: 'GET',
            headers: {
              'X-TowerScout-Operation-Authorization': 'invalid-status-authorization'
            }
          });
          return { status: response.status, payload: await response.json() };
        },
        {
          helperBaseUrl: HELPER_BASE_URL,
          operationId: result.status.operation_id
        }
      );
      assert.strictEqual(rejectedStatus.status, 401);
      assert.strictEqual(
        rejectedStatus.payload.state,
        'rejected_operation_authorization'
      );
    }
    const startBody = JSON.parse(validStartCalls[0].body);
    assert.deepStrictEqual(Object.keys(startBody).sort(), [
      'confirmation',
      'operation_authorization',
      'provider'
    ]);
    assert.deepStrictEqual(startBody, {
      provider: 'google',
      confirmation: 'repair_tls_and_restart',
      operation_authorization: OPERATION_TOKEN
    });
    assert.ok(
      result.fetchCalls.some(call => call.url === '/api/readiness'),
      'terminal success must trigger readiness recovery'
    );
    const publicOutput = JSON.stringify({
      notifications: result.notifications,
      renderedStatus: result.renderedStatus,
      storage: result.storage
    });
    for (const credential of [OPERATION_TOKEN, PROBE_TOKEN, STATUS_TOKEN]) {
      assert.strictEqual(publicOutput.includes(credential), false);
    }
    console.log(
      `Production SetupWizard POST/poll Puppeteer test PASSED (${USE_REAL_HELPER ? 'simulated-helper e2e' : 'in-page transport shim'})`
    );
  } finally {
    await browser.close();
  }
}

run().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
