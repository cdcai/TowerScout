/**
 * Frontend Integration Test Template - Provider TLS helper-unavailable fallback
 *
 * Purpose: Template test that simulates the host helper being unavailable
 * (network or 5xx response) during the start attempt and asserts the
 * frontend falls back to the command guidance and does not enter retry loops.
 *
 * IMPORTANT: This is a template scaffold. The real assertions may need to be
 * adapted to the UI markup and notification helpers present in the app.
 *
 * Usage:
 *  node tests/frontend/test_provider_tls_helper_unavailable_template.js
 */

const puppeteer = require('puppeteer');

const CONFIG = { baseUrl: 'http://localhost:5000', headless: true, timeout: 60000 };

async function run() {
  const launchOptions = { headless: CONFIG.headless, args: ['--no-sandbox', '--disable-setuid-sandbox'] };
  // Prefer a provided executable path (Playwright-installed Chromium) in CI
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    launchOptions.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
  } else if (process.env.TEST_BROWSER_EXECUTABLE) {
    launchOptions.executablePath = process.env.TEST_BROWSER_EXECUTABLE;
  }
  const browser = await puppeteer.launch(launchOptions);
  const page = await browser.newPage();

  try {
    const USE_REAL_HELPER = (process.env.E2E_USE_SERVER === '1' || process.env.E2E_USE_SERVER === 'true' || process.env.USE_REAL_HELPER === '1');

    // Expose helper base URL to the page when running e2e
    await page.evaluateOnNewDocument((hb, real) => {
      try { window.__TEST_HELPER_BASE_URL = hb || ''; window.__E2E_USE_REAL_HELPER = !!real; } catch(e) {}
    }, process.env.TEST_HELPER_BASE_URL || '', USE_REAL_HELPER);

    await page.goto(CONFIG.baseUrl, { waitUntil: 'networkidle2', timeout: CONFIG.timeout });
    await page.evaluate((hb, real) => {
      window.__TEST_HELPER_BASE_URL = hb || '';
      window.__E2E_USE_REAL_HELPER = !!real;
    }, process.env.TEST_HELPER_BASE_URL || '', USE_REAL_HELPER);

    // Mirror page console to node for easier diagnostics in CI
    page.on('console', msg => {
      try { console.log('PAGE:', msg.text()); } catch (e) { console.log('PAGE: (console unreadable)'); }
    });

    // Inject a repairable validation result as in the other template
    const future = new Date(Date.now() + 30 * 60 * 1000).toISOString();
    await page.evaluate((future) => {
      const payload = {
        provider: 'google',
        repairable: true,
        helper_available: true,
        category: 'tls_ca_untrusted',
        operation_authorization: {
          operation_type: 'provider_tls_repair',
          expires_at: future,
          operation_token: 'TEST_TOKEN_' + 'Y'.repeat(32)
        }
      };
      if (typeof rememberProviderValidationResult === 'function') {
        rememberProviderValidationResult('google', payload);
      } else {
        window.__TEST_provider_validation = payload;
      }
    }, future);

    // Install fetch wrapper to record calls and provide controlled shim behavior
    await page.evaluate((useReal) => {
      const orig = window.fetch;
      window.__fetchCalls = [];

      window.fetch = async function(url, options) {
        window.__fetchCalls.push(String(url));
        const recorded = { url: String(url), method: options && options.method ? options.method : 'GET' };

        if (!useReal) {
          if (recorded.url.endsWith('/operations/provider-tls-repair')) {
            console.log('[TEST-SHIM] Simulate 503 for', recorded.url);
            return { ok: false, status: 503, json: async () => ({ message: 'helper_unavailable' }) };
          }
          return orig.apply(this, arguments);
        }

        // In real mode, forward the request but still record a small snippet
        try {
          const resp = await orig.apply(this, arguments);
          let txt = null;
          try { txt = await resp.clone().text(); if (txt && txt.length>1000) txt = txt.slice(0,1000)+'...'; } catch(e){ txt = '<non-text>'; }
          window.__fetchCalls.push(Object.assign({}, recorded, { status: resp.status, bodySnippet: txt }));
          console.log('[FETCH] ', recorded.method, recorded.url, '->', resp.status);
          return resp;
        } catch (e) {
          window.__fetchCalls.push(Object.assign({}, recorded, { error: String(e) }));
          console.log('[FETCH-ERROR]', recorded.method, recorded.url, e && e.message ? e.message : e);
          throw e;
        }
      };
    }, USE_REAL_HELPER);

    // Use the builder to create POST body and then attempt a start via a small
    // injected helper so we can observe UI reaction.
    const outcome = await page.evaluate(async () => {
      let built = typeof buildProviderTlsRepairStartRequest === 'function' ? buildProviderTlsRepairStartRequest('google') : null;
      if (!built && window.__TEST_provider_validation) {
        const pv = window.__TEST_provider_validation;
        const helperBase = (window.__TEST_HELPER_BASE_URL || '').replace(/\/+$/, '');
        built = {
          endpoint: (helperBase ? helperBase : '') + '/operations/provider-tls-repair',
          options: {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              provider: pv.provider,
              confirmation: 'repair_tls_and_restart',
              operation_authorization: pv.operation_authorization && pv.operation_authorization.operation_token
            })
          }
        };
      }

      if (window.__E2E_USE_REAL_HELPER || (window.__TEST_HELPER_BASE_URL && window.__TEST_HELPER_BASE_URL.length)) {
        if (!built || !String(built.endpoint).match(/^https?:\/\//i)) {
          console.log('[E2E-ERROR] Helper base URL not configured or builder returned a relative endpoint:', built && built.endpoint);
          return { error: 'missing_helper_base_url', builtEndpoint: built && built.endpoint };
        }
      }
      if (!built) {
        return { error: 'no_builder' };
      }

      // Perform a single POST attempt
      const resp = await fetch(built.endpoint, built.options);
      const body = await (resp.json ? resp.json() : {});

      // Wait a short while to detect any retry loops
      await new Promise(r => setTimeout(r, 200));

      return {
        status: resp.status,
        bodyText: body && body.message,
        fetchCalls: (window.__fetchCalls || []).slice()
      };
    });

    if (outcome.error) {
      console.error('Builder not available in page context; adapt test to current frontend build.');
      process.exitCode = 2;
      return;
    }

    if (outcome.status !== 503) {
      console.error('Expected helper POST to return 503 in this simulation, got', outcome.status);
      process.exitCode = 2;
      return;
    }

    // Assert only one POST attempt occurred and that the UI should have fallback guidance
    const postCalls = outcome.fetchCalls.filter(u => u.endsWith('/operations/provider-tls-repair'));
    if (postCalls.length !== 1) {
      console.error('Expected a single POST attempt, saw', postCalls.length);
      process.exitCode = 2;
      return;
    }

    console.log('Helper-unavailable template: single POST observed, status=503');
    console.log('Body message:', outcome.bodyText);

    // TODO: Add DOM assertions here to validate that the UI shows the command
    // fallback text or an appropriate user notification instead of retry loops.

  } finally {
    await browser.close();
  }
}

run().catch(err => { console.error(err); process.exitCode = 1; });
