#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(__dirname, '../../webapp/js/src/ui/search.js'),
  'utf8'
);

function load(fetchImplementation) {
  const elements = {
    progress_div: { style: { display: 'flex' } },
    progress: {
      value: '25',
      setAttribute(name, value) { this[name] = value; },
      removeAttribute(name) { delete this[name]; }
    },
    progress_status_title: { textContent: 'Detection in progress' },
    progress_status_detail: { textContent: 'Processing tiles...' }
  };
  const loggerMessages = [];
  const notifications = [];
  const context = {
    AbortController,
    CONFIG: {
      SECS_PER_TILE_DEFAULT: 1,
      DETECTION_PROGRESS_POLL_INTERVAL_MS: 1000,
      PROGRESS_UPDATE_INTERVAL_MS: 1000
    },
    Date,
    Error,
    Math,
    Number,
    Set,
    console,
    document: {
      getElementById(id) { return elements[id] || null; }
    },
    fetch: fetchImplementation,
    performance,
    providerManager: {
      isProgressActive() { return true; },
      stopProgressTimer() {},
      startProgressTimer() {},
      getMap() { return null; }
    },
    TowerScoutErrorHandler: {
      showUserNotification(message, type) { notifications.push({ message, type }); }
    },
    window: {
      TowerScoutLogger: {
        debug() {},
        info(message) { loggerMessages.push(message); }
      }
    }
  };
  context.window.window = context.window;
  vm.createContext(context);
  vm.runInContext(source, context);
  return {
    cancelRequest: context.window.cancelRequest,
    getObjects: context.window.getObjects,
    elements,
    loggerMessages,
    notifications
  };
}

function response(status, payload) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async json() { return payload; }
  };
}

async function testReadyCancellationUnlocksProgressUi() {
  const harness = load(async () => response(200, {
    status: 'cancelled',
    retryReady: true
  }));

  await harness.cancelRequest();

  assert.strictEqual(harness.elements.progress_div.style.display, 'none');
  assert.ok(harness.loggerMessages.includes('Detection request cancelled.'));
}

async function testPendingCancellationKeepsProgressUiBlocked() {
  const harness = load(async () => response(202, {
    status: 'cancel_requested',
    retryReady: false
  }));

  await harness.cancelRequest();

  assert.strictEqual(harness.elements.progress_div.style.display, 'flex');
  assert.strictEqual(harness.elements.progress_status_title.textContent, 'Cancellation still pending');
  assert.ok(harness.elements.progress_status_detail.textContent.includes('current model step'));

  await harness.getObjects(false);
  assert.strictEqual(harness.notifications.length, 1);
  assert.ok(harness.notifications[0].message.includes('Cancellation is still pending'));
}

testReadyCancellationUnlocksProgressUi()
  .then(testPendingCancellationKeepsProgressUiBlocked)
  .then(() => {
    console.log('Detection cancellation recovery contract PASSED');
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
