#!/usr/bin/env node
/**
 * Puppeteer coverage for the production SetupWizard helper-unavailable path.
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
).replace(
  'const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false;',
  'const PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = true;'
);
const HELPER_BASE_URL = 'http://127.0.0.1:5001';
const WEB_URL = (
  process.env.TEST_WEB_URL || 'http://localhost:5000'
).replace(/\/+$/, '');

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
    await page.goto(WEB_URL, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });
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
    await page.evaluate(helperBaseUrl => {
      const response = (ok, status, payload) => ({
        ok,
        status,
        async json() {
          return payload;
        }
      });
      window.needsSetup = true;
      window.__fetchCalls = [];
      window.__notifications = [];
      window.TowerScoutLogger = { info() {}, debug() {} };
      window.TowerScoutErrorHandler = {
        showUserNotification(message, type) {
          window.__notifications.push({ message, type });
        }
      };
      window.fetch = async (url, options = {}) => {
        const target = String(url);
        window.__fetchCalls.push({
          url: target,
          method: options.method || 'GET'
        });
        if (target === '/api/config/validate-key') {
          const body = JSON.parse(options.body);
          if (body.provider === 'azure') {
            return response(true, 200, {
              valid: true,
              provider: 'azure',
              category: 'tls_ok',
              repairable: false
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
              support_action: 'Use the command fallback while the helper is unavailable.',
              repair_command: '.\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off',
              helper_bridge: {
                base_url: helperBaseUrl,
                probe: {
                  path: '/health',
                  scope: 'helper_probe',
                  expires_at: '2999-01-01T00:00:00Z',
                  authorization: 'unavailable-probe-authorization'
                },
                operation_authorization: {
                  operation_type: 'provider_tls_repair',
                  expires_at: '2999-01-01T00:00:00Z',
                  operation_token: 'unavailable-operation-authorization'
                },
                provider_tls_repair_capability: true,
                expected_runtime: {
                  engine: 'docker',
                  gpu: 'off',
                  app_port: 5000
                }
              }
            }
          });
        }
        if (target === `${helperBaseUrl}/health`) {
          return response(false, 503, { state: 'helper_unavailable' });
        }
        if (target === '/api/config/performance') {
          return response(true, 200, { session_count: 0 });
        }
        throw new Error(`Unexpected fetch target: ${target}`);
      };
    }, HELPER_BASE_URL);

    await page.addScriptTag({ content: API_HELPERS });
    await page.addScriptTag({ content: SETUP_WIZARD });
    const result = await page.evaluate(async () => {
      if (!window.SetupWizard) {
        throw new Error('Production SetupWizard controller was not loaded.');
      }
      window.SetupWizard.showStep(2);
      await window.SetupWizard.validateAndNext();
      document.getElementById('wizard_provider_tls_repair_confirm').checked = true;
      window.SetupWizard.updateProviderTlsRepairControls();
      const startResult = window.SetupWizard.startProviderTlsRepair();
      return {
        viewModel: window.SetupWizard.getProviderTlsRepairViewModel('google'),
        startResult,
        fetchCalls: window.__fetchCalls,
        notifications: window.__notifications,
        command: document.getElementById('wizard_provider_tls_repair_command').textContent,
        status: document.getElementById('wizard_provider_tls_repair_status').textContent
      };
    });

    assert.strictEqual(result.viewModel.visible, true);
    assert.strictEqual(result.viewModel.helper_available, false);
    assert.strictEqual(result.viewModel.enabled, false);
    assert.strictEqual(result.viewModel.blocked_reason, 'helper_unavailable');
    assert.strictEqual(result.startResult, false);
    assert.ok(result.command.includes('repair-provider-tls.cmd'));
    assert.ok(result.status.includes('helper is unavailable'));
    assert.strictEqual(
      result.fetchCalls.some(
        call => call.url === `${HELPER_BASE_URL}/operations/provider-tls-repair`
      ),
      false
    );
    assert.strictEqual(
      JSON.stringify({ notifications: result.notifications, status: result.status })
        .includes('unavailable-operation-authorization'),
      false
    );
    console.log('Production SetupWizard helper-unavailable Puppeteer test PASSED');
  } finally {
    await browser.close();
  }
}

run().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
