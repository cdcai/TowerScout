#!/usr/bin/env node

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.TOWERSCOUT_BASE_URL || '';
const ALT_BASE_URL = process.env.TOWERSCOUT_ALT_BASE_URL || '';
const EXECUTABLE_PATH = process.env.TOWERSCOUT_EXECUTABLE_PATH || '';
const READY_SIGNAL_PATH = process.env.TOWERSCOUT_BROWSER_READY_SIGNAL || '';
const BROWSER_PID_SIGNAL_PATH =
  process.env.TOWERSCOUT_BROWSER_PID_SIGNAL || '';
const BROWSER_PROFILE_DIR = process.env.TOWERSCOUT_BROWSER_PROFILE_DIR || '';
const TRANSITION_TIMEOUT_MS = Number(
  process.env.TOWERSCOUT_RESTART_TRANSITION_TIMEOUT_MS || 120000
);
const READINESS_REQUEST_TIMEOUT_MS = Number(
  process.env.TOWERSCOUT_READINESS_REQUEST_TIMEOUT_MS || 3000
);
const EXPECTED_READINESS_STATE =
  process.env.TOWERSCOUT_EXPECTED_READINESS_STATE || 'setup_required';
const ALLOWED_READINESS_STATES = new Set(['setup_required', 'degraded', 'ready']);

function normalizeLoopbackUrl(rawValue, name) {
  if (!rawValue) {
    throw new Error(`${name} is required.`);
  }
  let parsed;
  try {
    parsed = new URL(rawValue);
  } catch (_error) {
    throw new Error(`${name} must be a valid absolute URL.`);
  }
  if (
    parsed.protocol !== 'http:' ||
    !['localhost', '127.0.0.1'].includes(parsed.hostname) ||
    !parsed.port ||
    parsed.pathname !== '/' ||
    parsed.username ||
    parsed.password ||
    parsed.search ||
    parsed.hash
  ) {
    throw new Error(
      `${name} must be an explicit http://localhost:<port> or http://127.0.0.1:<port> origin.`
    );
  }
  return parsed.origin;
}

function validateLoopbackPair(baseUrl, alternateUrl) {
  const base = new URL(normalizeLoopbackUrl(baseUrl, 'TOWERSCOUT_BASE_URL'));
  const alternate = new URL(
    normalizeLoopbackUrl(alternateUrl, 'TOWERSCOUT_ALT_BASE_URL')
  );
  assert.notStrictEqual(
    base.hostname,
    alternate.hostname,
    'The two URLs must exercise distinct localhost and 127.0.0.1 origins.'
  );
  assert.deepStrictEqual(
    new Set([base.hostname, alternate.hostname]),
    new Set(['localhost', '127.0.0.1'])
  );
  assert.strictEqual(
    base.port,
    alternate.port,
    'The two loopback origins must target the same explicit port.'
  );
  return {
    baseUrl: base.origin,
    alternateUrl: alternate.origin
  };
}

function requireConfiguration() {
  const urls = validateLoopbackPair(BASE_URL, ALT_BASE_URL);
  for (const [name, value] of [
    ['TOWERSCOUT_EXECUTABLE_PATH', EXECUTABLE_PATH],
    ['TOWERSCOUT_BROWSER_READY_SIGNAL', READY_SIGNAL_PATH],
    ['TOWERSCOUT_BROWSER_PID_SIGNAL', BROWSER_PID_SIGNAL_PATH],
    ['TOWERSCOUT_BROWSER_PROFILE_DIR', BROWSER_PROFILE_DIR]
  ]) {
    if (!value) {
      throw new Error(`${name} is required.`);
    }
  }
  if (!Number.isFinite(TRANSITION_TIMEOUT_MS) || TRANSITION_TIMEOUT_MS < 10000) {
    throw new Error('TOWERSCOUT_RESTART_TRANSITION_TIMEOUT_MS must be at least 10000.');
  }
  if (
    !Number.isFinite(READINESS_REQUEST_TIMEOUT_MS) ||
    READINESS_REQUEST_TIMEOUT_MS < 500 ||
    READINESS_REQUEST_TIMEOUT_MS >= TRANSITION_TIMEOUT_MS
  ) {
    throw new Error(
      'TOWERSCOUT_READINESS_REQUEST_TIMEOUT_MS must be at least 500 and less than the transition timeout.'
    );
  }
  if (!ALLOWED_READINESS_STATES.has(EXPECTED_READINESS_STATE)) {
    throw new Error(
      'TOWERSCOUT_EXPECTED_READINESS_STATE must be setup_required, degraded, or ready.'
    );
  }
  if (
    !fs.existsSync(EXECUTABLE_PATH) ||
    !fs.statSync(EXECUTABLE_PATH).isFile() ||
    path.basename(EXECUTABLE_PATH).toLowerCase() !== 'msedge.exe'
  ) {
    throw new Error('TOWERSCOUT_EXECUTABLE_PATH must identify an existing msedge.exe file.');
  }
  if (!fs.existsSync(path.dirname(path.resolve(READY_SIGNAL_PATH)))) {
    throw new Error('The parent directory for TOWERSCOUT_BROWSER_READY_SIGNAL must exist.');
  }
  if (!fs.existsSync(path.dirname(path.resolve(BROWSER_PID_SIGNAL_PATH)))) {
    throw new Error('The parent directory for TOWERSCOUT_BROWSER_PID_SIGNAL must exist.');
  }
  const resolvedProfileDir = path.resolve(BROWSER_PROFILE_DIR);
  if (
    path.dirname(resolvedProfileDir).toLowerCase() !==
      path.resolve(require('os').tmpdir()).toLowerCase() ||
    !/^towerscout-task087-[a-f0-9]{32}-edge-profile$/i.test(
      path.basename(resolvedProfileDir)
    ) ||
    !fs.existsSync(resolvedProfileDir) ||
    !fs.statSync(resolvedProfileDir).isDirectory()
  ) {
    throw new Error(
      'TOWERSCOUT_BROWSER_PROFILE_DIR must be the dedicated Task-087 directory under the OS temp directory.'
    );
  }
  return urls;
}

async function waitFor(check, description) {
  const deadline = Date.now() + TRANSITION_TIMEOUT_MS;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      if (await check()) {
        return;
      }
    } catch (error) {
      lastError = error;
    }
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  const suffix = lastError ? ` Last error: ${lastError.message}` : '';
  throw new Error(`Timed out waiting for ${description}.${suffix}`);
}

async function readinessFromPage(page) {
  return page.evaluate(async requestTimeoutMs => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), requestTimeoutMs);
    try {
      const response = await fetch('/api/readiness', {
        cache: 'no-store',
        signal: controller.signal
      });
      const payload = await response.json();
      return {
        reachable: true,
        state: String(payload.state || '')
      };
    } catch (_error) {
      return {
        reachable: false,
        state: ''
      };
    } finally {
      clearTimeout(timeout);
    }
  }, READINESS_REQUEST_TIMEOUT_MS);
}

async function assertTowerScoutShell(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  assert.strictEqual(await page.title(), 'TowerScout');
  assert.strictEqual(
    await page.$eval('#setup_wizard_div', element => element.id),
    'setup_wizard_div'
  );
  const readiness = await readinessFromPage(page);
  assert.strictEqual(readiness.reachable, true);
  assert.ok(
    ['setup_required', 'degraded', 'ready'].includes(readiness.state),
    `Unexpected readiness state: ${readiness.state}`
  );
  return readiness.state;
}

async function run() {
  const { baseUrl, alternateUrl } = requireConfiguration();
  const puppeteer = require('puppeteer');
  const browser = await puppeteer.launch({
    executablePath: EXECUTABLE_PATH,
    headless: true,
    userDataDir: BROWSER_PROFILE_DIR
  });
  try {
    const browserProcess = browser.process();
    if (!browserProcess || !Number.isInteger(browserProcess.pid)) {
      throw new Error('Puppeteer did not expose the launched Edge process ID.');
    }
    fs.writeFileSync(BROWSER_PID_SIGNAL_PATH, String(browserProcess.pid), {
      encoding: 'utf8',
      flag: 'wx'
    });
    const page = await browser.newPage();
    const initialState = await assertTowerScoutShell(page, baseUrl);
    assert.strictEqual(initialState, EXPECTED_READINESS_STATE);
    const sessionSentinel = `task087-${Date.now()}-${Math.random()}`;
    await page.evaluate(value => {
      window.sessionStorage.setItem('task087-restart-sentinel', value);
    }, sessionSentinel);
    fs.writeFileSync(READY_SIGNAL_PATH, 'browser_ready', {
      encoding: 'utf8',
      flag: 'wx'
    });

    await waitFor(
      async () => !(await readinessFromPage(page)).reachable,
      'the dedicated TowerScout app to stop'
    );
    await waitFor(
      async () => (await readinessFromPage(page)).reachable,
      'the dedicated TowerScout app to restart'
    );

    const recoveredState = await assertTowerScoutShell(page, baseUrl);
    assert.strictEqual(recoveredState, initialState);
    assert.strictEqual(
      await page.evaluate(() =>
        window.sessionStorage.getItem('task087-restart-sentinel')
      ),
      sessionSentinel
    );
    const alternatePage = await browser.newPage();
    let alternateState;
    try {
      alternateState = await assertTowerScoutShell(alternatePage, alternateUrl);
      assert.strictEqual(alternateState, initialState);
    } finally {
      await alternatePage.close();
    }

    console.log(
      JSON.stringify({
        result: 'passed',
        browser: 'edge',
        initial_state: initialState,
        recovered_state: recoveredState,
        alternate_origin_state: alternateState,
        session_storage_preserved: true,
        observed_stop: true,
        observed_restart: true,
        orchestration: 'external'
      })
    );
  } finally {
    await browser.close();
  }
}

function runConfigurationSelfTest() {
  assert.deepStrictEqual(
    validateLoopbackPair('http://localhost:5006', 'http://127.0.0.1:5006/'),
    {
      baseUrl: 'http://localhost:5006',
      alternateUrl: 'http://127.0.0.1:5006'
    }
  );
  for (const urls of [
    ['https://localhost:5006', 'http://127.0.0.1:5006'],
    ['http://example.com:5006', 'http://127.0.0.1:5006'],
    ['http://localhost:5006/path', 'http://127.0.0.1:5006'],
    ['http://localhost:5006?query=1', 'http://127.0.0.1:5006'],
    ['http://user@localhost:5006', 'http://127.0.0.1:5006'],
    ['http://localhost:5006#fragment', 'http://127.0.0.1:5006'],
    ['http://localhost:5006', 'http://127.0.0.1:5007'],
    ['http://localhost:5006', 'http://localhost:5006']
  ]) {
    assert.throws(() => validateLoopbackPair(...urls));
  }
}

module.exports = {
  normalizeLoopbackUrl,
  validateLoopbackPair,
  runConfigurationSelfTest
};

if (require.main === module) {
  if (process.argv.includes('--self-test')) {
    runConfigurationSelfTest();
    console.log('Task-087 Edge observer configuration self-test passed.');
  } else {
    run().catch(error => {
      console.error(error.stack || error.message);
      process.exitCode = 1;
    });
  }
}
