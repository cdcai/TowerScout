#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(
  path.join(__dirname, '../../webapp/js/src/utils/apiHelpers.js'),
  'utf8'
);

function load(fetchImplementation) {
  const context = {
    AbortController,
    Error,
    console,
    fetch: fetchImplementation,
    setTimeout,
    clearTimeout,
    window: {
      TowerScoutLogger: { info() {}, debug() {} },
      setTimeout,
      clearTimeout
    }
  };
  context.window.window = context.window;
  vm.createContext(context);
  vm.runInContext(source, context);
  return context.window.TowerScoutConfigApi.fetchJson;
}

function rejectWhenAborted(signal) {
  return new Promise((_resolve, reject) => {
    const rejectAbort = () => {
      const error = new Error('aborted');
      error.name = 'AbortError';
      reject(error);
    };
    if (signal.aborted) {
      rejectAbort();
    } else {
      signal.addEventListener('abort', rejectAbort, { once: true });
    }
  });
}

async function testTimeoutCoversResponseBodyConsumption() {
  const fetchJson = load(async (_url, options) => ({
    ok: true,
    status: 200,
    json() {
      return rejectWhenAborted(options.signal);
    }
  }));

  await assert.rejects(
    fetchJson('/slow-body', { timeoutMs: 10 }),
    error => error.category === 'request_timeout'
  );
}

async function testCallerAbortIsComposedWithTimeoutSignal() {
  const callerController = new AbortController();
  const fetchJson = load(async (_url, options) => ({
    ok: true,
    status: 200,
    json() {
      return rejectWhenAborted(options.signal);
    }
  }));

  const request = fetchJson('/caller-cancelled', {
    timeoutMs: 1000,
    signal: callerController.signal
  });
  callerController.abort();

  await assert.rejects(
    request,
    error => error.name === 'AbortError' && error.category !== 'request_timeout'
  );
}

testTimeoutCoversResponseBodyConsumption()
  .then(testCallerAbortIsComposedWithTimeoutSignal)
  .then(() => {
    console.log('API helper timeout contract PASSED');
  })
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
