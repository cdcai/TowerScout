'use strict';

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const sourcePath = path.resolve(
  __dirname,
  '..',
  '..',
  'webapp',
  'js',
  'src',
  'managers',
  'ProviderStateManager.js'
);
const source = fs.readFileSync(sourcePath, 'utf8');

function makeMap(provider) {
  return {
    provider,
    subscriptionKey: provider === 'azure' ? 'test-key' : undefined,
    map: {
      getCenter: () => ({ lat: 0, lng: 0 })
    },
    getBounds: () => [0, 0, 1, 1],
    restoreCount: 0,
    cleanupCount: 0,
    restore() {
      this.restoreCount += 1;
    },
    cleanup() {
      this.cleanupCount += 1;
    }
  };
}

function loadProviderManagerContext() {
  const context = {
    console,
    setTimeout(callback) {
      callback();
      return 0;
    },
    clearTimeout() {},
    setInterval,
    clearInterval,
    window: {
      TowerScoutLogger: {
        debug() {},
        info() {},
        warn() {},
        error() {}
      },
      TowerScoutErrorHandler: {
        handleProviderError() {}
      },
      timerManager: {
        setTimeout() {
          return 0;
        },
        clearTimeout() {},
        setInterval,
        clearInterval
      },
      googleMap: makeMap('google'),
      azureMap: makeMap('azure')
    }
  };

  context.global = context;
  vm.createContext(context);
  vm.runInContext(source, context, { filename: sourcePath });
  return context;
}

function loadProviderManager() {
  return loadProviderManagerContext().window.providerManager;
}

async function testQueuedSwitchesReplayTargetProvider() {
  const manager = loadProviderManager();

  await Promise.all([
    manager.switchProvider('google'),
    manager.switchProvider('azure'),
    manager.switchProvider('google')
  ]);

  assert.equal(manager.getProvider(), 'google');
  assert.equal(manager.getMap().provider, 'google');
  assert.equal(manager.isSwitching(), false);
}

async function testProviderSwitchQueueRecoversAfterFailure() {
  const context = loadProviderManagerContext();
  const manager = context.window.providerManager;

  context.window.azureMap.getBounds = () => {
    throw new Error('forced Azure bounds failure');
  };

  const failedSwitch = manager.switchProvider('azure');
  const recoveredSwitch = manager.switchProvider('google');

  await assert.rejects(
    failedSwitch,
    /azure map bounds not available: forced Azure bounds failure/
  );
  assert.equal(await recoveredSwitch, true);
  assert.equal(manager.getProvider(), 'google');
  assert.equal(manager.getMap().provider, 'google');
  assert.equal(manager.isSwitching(), false);
  assert.equal(context.window.googleMap.restoreCount, 1);
}

function testLockedMutationsFailFastInsteadOfSpinning() {
  const manager = loadProviderManager();

  manager.detectionLock = true;
  assert.throws(
    () => manager.addDetection({ id: 1 }),
    /Add detection already in progress/
  );
  assert.equal(manager.detectionLock, true);

  manager.detectionLock = false;
  manager.addDetection({ id: 1 });
  manager.addDetection({ id: 2 });
  manager.sortDetections((a, b) => b.id - a.id);
  assert.deepEqual(manager.getDetections().map(item => item.id), [2, 1]);

  manager.progressLock = true;
  assert.throws(
    () => manager.startProgressTimer(() => {}, 1000),
    /Start progress timer already in progress/
  );
  assert.equal(manager.progressLock, true);

  manager.tileLock = true;
  assert.throws(
    () => manager.addTile({ id: 1 }),
    /Add tile already in progress/
  );
  assert.equal(manager.tileLock, true);
}

function testSourceHasNoProviderStateSpinLoops() {
  assert.equal(/while\s*\(\s*this\.[a-zA-Z]+Lock\s*\)/.test(source), false);
}

(async () => {
  await testQueuedSwitchesReplayTargetProvider();
  await testProviderSwitchQueueRecoversAfterFailure();
  testLockedMutationsFailFastInsteadOfSpinning();
  testSourceHasNoProviderStateSpinLoops();
  console.log('TASK-064 ProviderStateManager tests passed');
})().catch(error => {
  console.error(error);
  process.exit(1);
});
