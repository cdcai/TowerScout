'use strict';

const fs = require('node:fs');
const path = require('node:path');
const puppeteer = require('puppeteer');

const DEFAULT_BASE_URL = 'http://localhost:5000';
const DEFAULT_FIXTURE_PATH = path.join(__dirname, 'detection-workflow.local.json');
const EXAMPLE_FIXTURE_PATH = path.join(__dirname, 'detection-workflow.example.json');
const ARTIFACT_ROOT = path.resolve(__dirname, '..', '..', '.agent_work', 'context', 'analysis', 'browser-runs');

function parseArgs(argv) {
  const options = {
    provider: null,
    headed: false,
    cancelSmoke: false,
    fixturePath: process.env.TOWERSCOUT_AOI_FILE || DEFAULT_FIXTURE_PATH,
    baseUrl: process.env.TOWERSCOUT_BASE_URL || null,
    executablePath: process.env.TOWERSCOUT_EXECUTABLE_PATH || null
  };

  for (const arg of argv) {
    if (arg === '--headed') {
      options.headed = true;
    } else if (arg === '--cancel-smoke') {
      options.cancelSmoke = true;
    } else if (arg.startsWith('--provider=')) {
      options.provider = arg.split('=')[1];
    } else if (arg.startsWith('--fixture=')) {
      options.fixturePath = path.resolve(arg.split('=')[1]);
    } else if (arg.startsWith('--base-url=')) {
      options.baseUrl = arg.split('=')[1];
    } else if (arg.startsWith('--browser-path=')) {
      options.executablePath = path.resolve(arg.split('=')[1]);
    } else if (arg === '--help') {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return options;
}

function printHelp() {
  console.log([
    'TowerScout detection workflow smoke harness',
    '',
    'Usage:',
    '  node tests/frontend/test_detection_workflow_smoke.js [--provider=google|azure] [--headed] [--cancel-smoke] [--fixture=path] [--base-url=url] [--browser-path=path]',
    '',
    'Defaults:',
    `  fixture: ${DEFAULT_FIXTURE_PATH}`,
    `  example: ${EXAMPLE_FIXTURE_PATH}`,
    `  base URL: ${DEFAULT_BASE_URL}`
  ].join('\n'));
}

function timestampTag() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  const hh = String(now.getHours()).padStart(2, '0');
  const mi = String(now.getMinutes()).padStart(2, '0');
  const ss = String(now.getSeconds()).padStart(2, '0');
  return `${yyyy}${mm}${dd}-${hh}${mi}${ss}`;
}

function ensureDirectory(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function loadFixture(fixturePath) {
  if (!fs.existsSync(fixturePath)) {
    throw new Error(
      `Fixture not found at ${fixturePath}. Copy ${EXAMPLE_FIXTURE_PATH} to detection-workflow.local.json and replace it with a safe local AOI before running the smoke harness.`
    );
  }

  const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

  if (!Array.isArray(fixture.polygon) || fixture.polygon.length < 4) {
    throw new Error('Fixture must define a polygon array with at least four coordinate points.');
  }

  if (!Array.isArray(fixture.center) || fixture.center.length !== 2) {
    throw new Error('Fixture must define a center array in [lng, lat] order.');
  }

  fixture.expected = fixture.expected || {};
  fixture.expected.minimumDetections = Number.isFinite(fixture.expected.minimumDetections)
    ? fixture.expected.minimumDetections
    : 1;
  fixture.expected.estimateTimeoutMs = Number.isFinite(fixture.expected.estimateTimeoutMs)
    ? fixture.expected.estimateTimeoutMs
    : 30000;
  fixture.expected.detectionTimeoutMs = Number.isFinite(fixture.expected.detectionTimeoutMs)
    ? fixture.expected.detectionTimeoutMs
    : 180000;

  return fixture;
}

function resolveExecutablePath(explicitPath) {
  if (explicitPath) {
    if (!fs.existsSync(explicitPath)) {
      throw new Error(`Browser executable not found: ${explicitPath}`);
    }
    return explicitPath;
  }

  const candidates = process.platform === 'win32'
    ? [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
    ]
    : [];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  throw new Error(
    'No local Chrome or Edge executable was found. Set TOWERSCOUT_EXECUTABLE_PATH or use --browser-path to point the smoke harness at an installed browser.'
  );
}

async function assertServerReachable(baseUrl) {
  let response;

  try {
    response = await fetch(baseUrl, { redirect: 'manual' });
  } catch (error) {
    throw new Error(`TowerScout is not reachable at ${baseUrl}. Start the Flask server first (for example: cd webapp && python towerscout.py dev).`);
  }

  if (!response.ok && response.status !== 302) {
    throw new Error(`TowerScout returned ${response.status} for ${baseUrl}. Expected a reachable local app before running the smoke harness.`);
  }
}

function shouldCaptureUrl(urlString, baseUrl) {
  const base = new URL(baseUrl);
  const url = new URL(urlString);

  if (url.origin === base.origin) {
    return true;
  }

  return (
    url.hostname.includes('atlas.microsoft.com') ||
    url.hostname.includes('googleapis.com') ||
    url.hostname.includes('gstatic.com')
  );
}

function captureConsoleEvent(message) {
  return {
    type: message.type(),
    text: message.text(),
    timestamp: new Date().toISOString()
  };
}

function summarizeOutputTail(outputText) {
  return outputText
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
    .slice(-20);
}

async function waitForAppReady(page) {
  await page.waitForSelector('#output', { timeout: 30000 });

  try {
    await page.waitForFunction(() => {
      const about = document.getElementById('about_div');
      return !about || window.getComputedStyle(about).display === 'none';
    }, { timeout: 15000 });
  } catch (_error) {
    // In non-dev mode the splash can linger briefly; continue with the remaining checks.
  }

  await page.waitForFunction(() => {
    return !!window.TowerScoutLogger && !!window.providerManager;
  }, { timeout: 30000 });

  await page.waitForFunction(() => {
    return window.needsSetup || document.querySelectorAll('#providers input[name="provider"]').length > 0;
  }, { timeout: 30000 });

  const state = await page.evaluate(() => {
    const available = typeof availableProviders !== 'undefined' ? availableProviders : [];
    return {
      needsSetup: window.needsSetup === true,
      availableProviders: Array.isArray(available) ? available : [],
      providerInputs: Array.from(document.querySelectorAll('#providers input[name="provider"]')).map(input => input.value)
    };
  });

  if (state.needsSetup) {
    throw new Error('TowerScout is in setup-required mode. Complete the Setup Wizard before running the smoke harness.');
  }

  return state;
}

async function selectUiAndBackendProvider(page, provider) {
  await page.evaluate(async (targetProvider) => {
    const currentUi = document.querySelector('input[name="uis"]:checked')?.value || null;
    const currentBackend = document.querySelector('#providers input[name="provider"]:checked')?.value || null;

    const uiRadio = document.querySelector(`input[name="uis"][value="${targetProvider}"]`);
    if (!uiRadio) {
      throw new Error(`UI provider radio not found for ${targetProvider}`);
    }

    uiRadio.checked = true;
    if (currentUi !== targetProvider && typeof window.setMap === 'function') {
      await window.setMap(uiRadio);
    }

    const backendRadio = document.querySelector(`#providers input[name="provider"][value="${targetProvider}"]`);
    if (!backendRadio) {
      throw new Error(`Backend provider radio not found for ${targetProvider}`);
    }

    backendRadio.checked = true;
    if (currentBackend !== targetProvider) {
      backendRadio.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }, provider);

  await page.waitForFunction((targetProvider) => {
    const uiRadio = document.querySelector(`input[name="uis"][value="${targetProvider}"]`);
    const backendRadio = document.querySelector(`#providers input[name="provider"][value="${targetProvider}"]`);
    return !!uiRadio?.checked && !!backendRadio?.checked;
  }, { timeout: 30000 }, provider);
}

async function readProgressOverlayState(page) {
  return await page.evaluate(() => {
    const overlay = document.getElementById('progress_div');
    const title = document.getElementById('progress_status_title');
    const detail = document.getElementById('progress_status_detail');
    const progress = document.getElementById('progress');
    const visible = !!overlay && window.getComputedStyle(overlay).display !== 'none';

    return {
      visible,
      title: title?.textContent?.trim() || title?.innerText?.trim() || '',
      detail: detail?.textContent?.trim() || detail?.innerText?.trim() || '',
      progressValue: progress ? progress.value : null,
      progressMax: progress ? progress.max : null
    };
  });
}

async function waitForProgressOverlayText(page, timeoutMs = 3000) {
  try {
    await page.waitForFunction(() => {
      const overlay = document.getElementById('progress_div');
      const title = document.getElementById('progress_status_title');
      const detail = document.getElementById('progress_status_detail');
      const visible = !!overlay && window.getComputedStyle(overlay).display !== 'none';
      const titleText = title?.textContent?.trim() || title?.innerText?.trim() || '';
      const detailText = detail?.textContent?.trim() || detail?.innerText?.trim() || '';
      return visible && !!titleText && !!detailText;
    }, { timeout: timeoutMs });
  } catch (_error) {
    // Fall back to the latest snapshot if the text never appears within the bounded wait.
  }

  return await readProgressOverlayState(page);
}

async function waitForProviderReady(page, provider) {
  await page.waitForFunction((targetProvider) => {
    const manager = window.providerManager;
    if (!manager || typeof manager.isFullyInitialized !== 'function') {
      return false;
    }

    const map = window.currentMap || manager.getMap?.();
    if (!map) {
      return false;
    }

    return manager.isFullyInitialized(targetProvider);
  }, { timeout: 45000 }, provider);
}

async function triggerWorkflowAction(page, selector, fallbackExpression) {
  const state = await page.evaluate((targetSelector) => {
    const element = document.querySelector(targetSelector);
    if (!element) {
      return { exists: false, visible: false };
    }

    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const visible = style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;

    return {
      exists: true,
      visible,
      display: style.display,
      width: rect.width,
      height: rect.height
    };
  }, selector);

  if (!state.exists) {
    throw new Error(`Required workflow control not found: ${selector}`);
  }

  const baseline = await page.evaluate(() => {
    const overlay = document.getElementById('progress_div');
    return {
      output: document.getElementById('output')?.innerText || '',
      overlayVisible: !!overlay && window.getComputedStyle(overlay).display !== 'none'
    };
  });

  const invokeFallback = async (triggerMode) => {
    await page.evaluate((expression) => {
      if (expression === 'estimate') {
        window.getObjects(true);
      } else if (expression === 'find') {
        window.getObjects();
      } else {
        throw new Error(`Unknown workflow fallback expression: ${expression}`);
      }
    }, fallbackExpression);

    return { triggerMode, controlState: state };
  };

  if (state.visible) {
    await page.click(selector);

    try {
      await page.waitForFunction(({ priorOutput, priorOverlayVisible }) => {
        const overlay = document.getElementById('progress_div');
        const overlayVisible = !!overlay && window.getComputedStyle(overlay).display !== 'none';
        const output = document.getElementById('output')?.innerText || '';
        return output !== priorOutput || overlayVisible !== priorOverlayVisible;
      }, { timeout: 1000 }, {
        priorOutput: baseline.output,
        priorOverlayVisible: baseline.overlayVisible
      });
      return { triggerMode: 'click', controlState: state };
    } catch (_error) {
      return invokeFallback('click-fallback');
    }
  }

  return invokeFallback('fallback');
}

async function injectBoundary(page, fixture) {
  return await page.evaluate(({ polygon, center, zoom }) => {
    const map = window.currentMap || window.providerManager?.getMap?.();
    if (!map) {
      throw new Error('Current map is not initialized.');
    }

    if (typeof window.clearBoundaries === 'function') {
      window.clearBoundaries();
    } else if (typeof map.resetBoundaries === 'function') {
      map.resetBoundaries();
    }

    const boundary = new window.PolygonBoundary(polygon);
    map.addBoundary(boundary);

    if (typeof map.showBoundaries === 'function') {
      map.showBoundaries();
    }

    if (typeof map.setCenter === 'function') {
      map.setCenter(center);
    }

    if (Number.isFinite(zoom) && typeof map.setZoom === 'function') {
      map.setZoom(zoom);
    }

    return {
      boundaryCount: Array.isArray(map.boundaries) ? map.boundaries.length : 0,
      boundaryBounds: typeof map.getBoundaryBoundsUrl === 'function' ? map.getBoundaryBoundsUrl() : null
    };
  }, fixture);
}

async function runEstimate(page, summary, timeoutMs) {
  const startedAt = Date.now();
  const responsePromise = page.waitForResponse(response => {
    return response.url().includes('/api/detection/estimate') && response.request().method() === 'POST';
  }, { timeout: timeoutMs });

  const trigger = await triggerWorkflowAction(page, '#estimate', 'estimate');
  const response = await responsePromise;
  const body = await response.json();
  const tileCount = Number(body.tileCount);
  const estimatedSeconds = Number(body.estimatedSeconds);

  summary.estimate = {
    startedAt: new Date(startedAt).toISOString(),
    finishedAt: new Date().toISOString(),
    durationMs: Date.now() - startedAt,
    triggerMode: trigger.triggerMode,
    controlState: trigger.controlState,
    status: response.status(),
    rawBody: body,
    tileCount: Number.isFinite(tileCount) ? tileCount : null,
    estimatedSeconds: Number.isFinite(estimatedSeconds) ? estimatedSeconds : null
  };

  if (!Number.isFinite(tileCount)) {
    throw new Error(`Estimate did not return a numeric tile count. Body: ${JSON.stringify(body)}`);
  }
}

async function runDetection(page, summary, minimumDetections, timeoutMs) {
  const startedAt = Date.now();
  let progressShown = false;
  let progressSnapshot = null;

  const trigger = await triggerWorkflowAction(page, '#find', 'find');

  try {
    await page.waitForFunction(() => {
      const overlay = document.getElementById('progress_div');
      return overlay && window.getComputedStyle(overlay).display !== 'none';
    }, { timeout: 5000 });
    progressShown = true;
    progressSnapshot = await waitForProgressOverlayText(page);
  } catch (_error) {
    // Detection can complete quickly in small AOIs; do not fail only because the overlay was brief.
  }

  await page.waitForFunction(() => {
    const overlay = document.getElementById('progress_div');
    const overlayVisible = overlay && window.getComputedStyle(overlay).display !== 'none';
    const output = document.getElementById('output')?.innerText || '';
    const detectionCount = Array.isArray(window.Detection_detections) ? window.Detection_detections.length : 0;
    const completed = output.includes('Detection request completed');
    const failed = output.includes('Detection failed') || output.includes('Detection pipeline error');
    return (!overlayVisible && completed) || (!overlayVisible && failed) || detectionCount >= 1;
  }, { timeout: timeoutMs });

  const state = await page.evaluate(() => {
    const output = document.getElementById('output')?.innerText || '';
    const detections = Array.isArray(window.Detection_detections) ? window.Detection_detections : [];
    const currentUi = document.querySelector('input[name="uis"]:checked')?.value || null;
    const backendProvider = document.querySelector('#providers input[name="provider"]:checked')?.value || null;
    const outputTail = output
      .split('\n')
      .map(line => line.trim())
      .filter(Boolean)
      .slice(-20);

    const mapVisibleCount = detections.filter(detection => {
      if (currentUi === 'google') {
        return !!detection.mapRect &&
          typeof detection.mapRect.getMap === 'function' &&
          detection.mapRect.getMap() !== null;
      }

      if (currentUi === 'azure') {
        return !!detection.azureShape;
      }

      return !!detection.mapRect;
    }).length;

    return {
      outputTail,
      currentUi,
      backendProvider,
      detectionCount: detections.length,
      selectedCount: detections.filter(detection => detection.selected).length,
      manualCount: detections.filter(detection => detection.idInTile === -1).length,
      withAddressCount: detections.filter(detection => Boolean(detection.address)).length,
      listCount: document.querySelectorAll('#checkBoxes input[id^="detcb"]').length,
      addressGroupCount: document.querySelectorAll('#checkBoxes input[id^="addrcb"]').length,
      mapVisibleCount
    };
  });

  summary.detection = {
    startedAt: new Date(startedAt).toISOString(),
    finishedAt: new Date().toISOString(),
    durationMs: Date.now() - startedAt,
    triggerMode: trigger.triggerMode,
    controlState: trigger.controlState,
    progressShown,
    progressSnapshot,
    ...state
  };

  if (progressShown && (!progressSnapshot?.title || !progressSnapshot?.detail)) {
    throw new Error(`Progress overlay was visible but title/detail text was empty: ${JSON.stringify(progressSnapshot)}`);
  }

  if (state.detectionCount < minimumDetections) {
    throw new Error(`Detection completed with ${state.detectionCount} detections, below the expected minimum of ${minimumDetections}.`);
  }

  if (state.listCount < minimumDetections) {
    throw new Error(`Detection list rendered ${state.listCount} entries, below the expected minimum of ${minimumDetections}.`);
  }

  if (state.mapVisibleCount < minimumDetections) {
    throw new Error(`Map rendered ${state.mapVisibleCount} visible detections, below the expected minimum of ${minimumDetections}.`);
  }
}

async function runCancelSmoke(page, summary, minimumDetections, timeoutMs) {
  const startedAt = Date.now();
  const trigger = await triggerWorkflowAction(page, '#find', 'find');

  await page.waitForFunction(() => {
    const overlay = document.getElementById('progress_div');
    return overlay && window.getComputedStyle(overlay).display !== 'none';
  }, { timeout: 5000 });

  const progressSnapshotBeforeCancel = await waitForProgressOverlayText(page);

  const abortResponsePromise = page.waitForResponse(response => {
    return response.url().includes('/abort') && response.request().method() === 'POST';
  }, { timeout: 10000 });

  await page.evaluate(() => {
    if (typeof window.cancelRequest !== 'function') {
      throw new Error('window.cancelRequest is not available');
    }
    window.cancelRequest();
  });

  const abortResponse = await abortResponsePromise;

  await page.waitForFunction(() => {
    const overlay = document.getElementById('progress_div');
    return !overlay || window.getComputedStyle(overlay).display === 'none';
  }, { timeout: timeoutMs });

  const progressSnapshotAfterCancel = await readProgressOverlayState(page);

  const cancelState = await page.evaluate(() => {
    const output = document.getElementById('output')?.innerText || '';
    return {
      outputTail: output
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean)
        .slice(-20),
      detectionCountAfterCancel: Array.isArray(window.Detection_detections) ? window.Detection_detections.length : 0
    };
  });

  summary.cancel = {
    startedAt: new Date(startedAt).toISOString(),
    finishedAt: new Date().toISOString(),
    durationMs: Date.now() - startedAt,
    triggerMode: trigger.triggerMode,
    controlState: trigger.controlState,
    abortStatus: abortResponse.status(),
    progressSnapshotBeforeCancel,
    progressSnapshotAfterCancel,
    ...cancelState
  };

  if (abortResponse.status() !== 200) {
    throw new Error(`Abort request returned status ${abortResponse.status()}.`);
  }

  if (!progressSnapshotBeforeCancel.title || !progressSnapshotBeforeCancel.detail) {
    throw new Error(
      `Progress overlay text was empty before cancel: ${JSON.stringify(progressSnapshotBeforeCancel)}`
    );
  }

  if (progressSnapshotAfterCancel.visible) {
    throw new Error(
      `Progress overlay remained visible after cancel: ${JSON.stringify(progressSnapshotAfterCancel)}`
    );
  }

  await runDetection(page, summary, minimumDetections, timeoutMs);
}

async function writeArtifacts(artifactDir, summary, page, failed) {
  ensureDirectory(artifactDir);
  fs.writeFileSync(path.join(artifactDir, 'summary.json'), JSON.stringify(summary, null, 2));

  if (failed) {
    await page.screenshot({
      path: path.join(artifactDir, 'failure.png'),
      fullPage: true
    });
  } else {
    await page.screenshot({
      path: path.join(artifactDir, 'final.png'),
      fullPage: true
    });
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const fixture = loadFixture(options.fixturePath);
  const provider = options.provider || fixture.provider || fixture.backendProvider || fixture.uiProvider || 'azure';
  const baseUrl = options.baseUrl || fixture.baseUrl || DEFAULT_BASE_URL;
  const executablePath = resolveExecutablePath(options.executablePath);
  const runId = `${timestampTag()}-${provider}${options.cancelSmoke ? '-cancel' : ''}`;
  const artifactDir = path.join(ARTIFACT_ROOT, runId);

  await assertServerReachable(baseUrl);

  const summary = {
    runId,
    startedAt: new Date().toISOString(),
    baseUrl,
    provider,
    executablePath,
    headed: options.headed,
    fixturePath: path.resolve(options.fixturePath),
    artifactDir,
    browserConsole: [],
    pageErrors: [],
    network: [],
    estimate: null,
    cancel: null,
    detection: null,
    boundary: null,
    status: 'running'
  };

  let browser;
  let page;

  try {
    browser = await puppeteer.launch({
      executablePath,
      headless: options.headed ? false : true,
      slowMo: options.headed ? 60 : 0,
      defaultViewport: { width: 1440, height: 960 },
      args: ['--window-size=1440,960']
    });

    page = await browser.newPage();
    page.setDefaultTimeout(30000);

    page.on('console', message => {
      summary.browserConsole.push(captureConsoleEvent(message));
    });

    page.on('pageerror', error => {
      summary.pageErrors.push({
        message: error.message,
        stack: error.stack || null,
        timestamp: new Date().toISOString()
      });
    });

    page.on('response', async response => {
      const url = response.url();
      if (!shouldCaptureUrl(url, baseUrl)) {
        return;
      }

      const request = response.request();
      let responseBodySnippet = null;
      if ((url.includes('/getobjects') || url.includes('/api/detection/estimate')) && response.status() >= 400) {
        try {
          responseBodySnippet = (await response.text()).trim().slice(0, 1000);
        } catch (_error) {
          responseBodySnippet = '[unavailable]';
        }
      }

      summary.network.push({
        timestamp: new Date().toISOString(),
        method: request.method(),
        url,
        status: response.status(),
        resourceType: request.resourceType(),
        postDataSnippet: request.postData() ? request.postData().slice(0, 500) : null,
        responseBodySnippet
      });
    });

    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const appState = await waitForAppReady(page);

    if (!appState.availableProviders.includes(provider)) {
      throw new Error(`Requested provider "${provider}" is not available. Available providers: ${appState.availableProviders.join(', ') || '(none)'}`);
    }

    await selectUiAndBackendProvider(page, provider);
    await waitForProviderReady(page, provider);
    summary.boundary = await injectBoundary(page, fixture);

    await runEstimate(page, summary, fixture.expected.estimateTimeoutMs);
    if (options.cancelSmoke) {
      await runCancelSmoke(page, summary, fixture.expected.minimumDetections, fixture.expected.detectionTimeoutMs);
    } else {
      await runDetection(page, summary, fixture.expected.minimumDetections, fixture.expected.detectionTimeoutMs);
    }

    const findRunRequests = summary.network.filter(entry =>
      entry.url.includes('/getobjects') &&
      summary.detection &&
      entry.timestamp >= summary.detection.startedAt
    );

    const estimateRequests = summary.network.filter(entry => entry.url.includes('/api/detection/estimate'));

    summary.findRequestSequence = {
      estimateCalls: estimateRequests.length,
      getobjectsCalls: findRunRequests.length,
      hiddenEstimatePreflightObserved: findRunRequests.some(entry => (entry.postDataSnippet || '').includes('name=\"estimate\"'))
    };
    summary.status = 'passed';
  } catch (error) {
    summary.status = 'failed';
    summary.error = {
      message: error.message,
      stack: error.stack || null
    };

    if (page) {
      await writeArtifacts(artifactDir, summary, page, true);
    }

    throw error;
  } finally {
    summary.finishedAt = new Date().toISOString();
    if (page && summary.status !== 'failed') {
      await writeArtifacts(artifactDir, summary, page, false);
    }

    if (browser) {
      await browser.close();
    }
  }

  console.log(`Smoke run passed. Artifact: ${path.join(artifactDir, 'summary.json')}`);
}

main().catch(error => {
  console.error(error.message);
  process.exit(1);
});
