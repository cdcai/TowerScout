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
  let progressTimerCallback = null;
  const currentMap = {
    boundaries: [],
    hasShapes() { return false; },
    getBoundaryBoundsUrl() { return '40.0,-75.0,40.1,-74.9'; },
    getBoundariesStr() { return '[[[-75,40],[-74.9,40],[-74.9,40.1],[-75,40.1],[-75,40]]]'; }
  };
  const context = {
    AbortController,
    CONFIG: {
      SECS_PER_TILE_DEFAULT: 1,
      DETECTION_PROGRESS_POLL_INTERVAL_MS: 0,
      PROGRESS_UPDATE_INTERVAL_MS: 1000
    },
    Date,
    Error,
    FormData,
    Math,
    Number,
    Set,
    console,
    currentMap,
    Detection_detections: [],
    Detection: {
      resetAll() {}
    },
    Tile: {
      resetAll() {}
    },
    $() {
      return {
        val() { return 'newest'; }
      };
    },
    document: {
      getElementById(id) { return elements[id] || null; },
      querySelector() { return { value: 'azure' }; }
    },
    fetch: fetchImplementation,
    performance,
    providerManager: {
      isProgressActive() { return progressTimerCallback !== null; },
      stopProgressTimer() { progressTimerCallback = null; },
      startProgressTimer(callback) { progressTimerCallback = callback; },
      getMap() { return null; }
    },
    TowerScoutErrorHandler: {
      showUserNotification(message, type) { notifications.push({ message, type }); },
      wrapNetworkCall(operation) { return operation; },
      handleNetworkError() {}
    },
    window: {
      confirm() { return true; },
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
    notifications,
    async runProgressTick() {
      assert.ok(progressTimerCallback, 'progress timer was not active');
      progressTimerCallback();
      await new Promise(resolve => setImmediate(resolve));
      await new Promise(resolve => setImmediate(resolve));
    }
  };
}

function response(status, payload, options = {}) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async json() {
      if (options.invalidJson) {
        throw new SyntaxError('synthetic invalid JSON');
      }
      return payload;
    }
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
  let progressStatus = 'cancel_requested';
  let retryReady = false;
  const harness = load(async url => {
    if (url === '/abort') {
      return response(202, {
        status: 'cancel_requested',
        retryReady: false
      });
    }
    return response(200, {
      status: progressStatus,
      retryReady,
      phase: progressStatus,
      title: progressStatus === 'cancelled' ? 'Detection cancelled' : 'Cancelling detection',
      detail: progressStatus === 'cancelled' ? 'The run stopped.' : 'Waiting for model work.'
    });
  });

  await harness.cancelRequest();
  await new Promise(resolve => setImmediate(resolve));

  assert.strictEqual(harness.elements.progress_div.style.display, 'flex');
  assert.strictEqual(harness.elements.progress_status_title.textContent, 'Cancellation still pending');

  await harness.getObjects(false);
  assert.strictEqual(harness.notifications.length, 1);
  assert.ok(harness.notifications[0].message.includes('Cancellation is still pending'));

  progressStatus = 'cancelled';
  await harness.runProgressTick();
  assert.strictEqual(harness.elements.progress_div.style.display, 'flex');

  retryReady = true;
  await harness.runProgressTick();
  assert.strictEqual(harness.elements.progress_div.style.display, 'none');
}

async function testSuccessfulNonJsonCancellationResponseStaysPending() {
  const harness = load(async () => response(200, null, { invalidJson: true }));

  await harness.cancelRequest();

  assert.strictEqual(harness.elements.progress_div.style.display, 'flex');
  assert.strictEqual(harness.elements.progress_status_title.textContent, 'Cancellation still pending');
}

async function testOlderCancelResponseCannotRestorePendingState() {
  const pendingResponses = [];
  const harness = load(() => new Promise(resolve => pendingResponses.push(resolve)));

  const firstCancel = harness.cancelRequest();
  const secondCancel = harness.cancelRequest();
  assert.strictEqual(pendingResponses.length, 2);

  pendingResponses[1](response(200, {
    status: 'cancelled',
    retryReady: true
  }));
  await secondCancel;
  assert.strictEqual(harness.elements.progress_div.style.display, 'none');

  pendingResponses[0](response(202, {
    status: 'cancel_requested',
    retryReady: false,
    message: 'stale pending response'
  }));
  await firstCancel;

  assert.strictEqual(harness.elements.progress_div.style.display, 'none');
  assert.notStrictEqual(
    harness.elements.progress_status_title.textContent,
    'Cancellation still pending'
  );
}

async function testCancelCorrelatesWithTheActiveDetectionRequest() {
  const calls = [];
  const harness = load(async (url, options = {}) => {
    calls.push({ url, options });
    if (url === '/getobjects') {
      return new Promise(() => {});
    }
    if (url === '/abort') {
      return response(200, {
        status: 'idle',
        retryReady: true
      });
    }
    return response(200, {
      status: 'idle',
      retryReady: true
    });
  });

  void harness.getObjects(false);
  await new Promise(resolve => setImmediate(resolve));

  const detectionCall = calls.find(call => call.url === '/getobjects');
  assert.ok(detectionCall, 'detection request was not started');
  const requestId = detectionCall.options.headers['X-TowerScout-Detection-Request-Id'];
  assert.ok(requestId, 'detection request did not include a correlation ID');

  await harness.cancelRequest();

  const abortCall = calls.find(call => call.url === '/abort');
  assert.ok(abortCall, 'abort request was not sent');
  assert.strictEqual(
    abortCall.options.headers['X-TowerScout-Detection-Request-Id'],
    requestId
  );
}

testReadyCancellationUnlocksProgressUi()
  .then(testPendingCancellationKeepsProgressUiBlocked)
  .then(testSuccessfulNonJsonCancellationResponseStaysPending)
  .then(testOlderCancelResponseCannotRestorePendingState)
  .then(testCancelCorrelatesWithTheActiveDetectionRequest)
  .then(() => {
    console.log('Detection cancellation recovery contract PASSED');
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
