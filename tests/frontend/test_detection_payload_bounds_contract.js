#!/usr/bin/env node

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '../..');
const SEARCH_PATH = path.join(ROOT, 'webapp/js/src/ui/search.js');

class TestFormData {
  constructor() {
    this.values = new Map();
  }

  append(name, value) {
    this.values.set(name, value);
  }

  get(name) {
    return this.values.get(name);
  }
}

class TestBoundary {
  constructor(bounds) {
    this.bounds = bounds;
  }
}

function createMap(provider, options = {}) {
  const map = {
    provider,
    boundaries: options.boundaries ? [...options.boundaries] : [],
    addCount: 0,
    hasShapes() {
      return false;
    },
    getBounds() {
      return { north: 38, south: 37, east: -122, west: -123 };
    },
    addBoundary(boundary) {
      this.addCount += 1;
      this.boundaries.push(boundary);
    },
    getBoundariesStr() {
      return this.boundaries.length === 0 ? '[]' : JSON.stringify([{ type: 'viewport' }]);
    },
    getBoundaryBoundsUrl() {
      if (this.boundaries.length > 0) {
        return options.explicitBounds || '38,-123,37,-122';
      }
      if (provider === 'azure') {
        return '38,-123,37,-122';
      }
      return '';
    }
  };
  return map;
}

function createContext(provider, map) {
  const fetchCalls = [];
  const inactiveMap = createMap(provider === 'google' ? 'azure' : 'google');
  const logger = { debug() {}, info() {}, warn() {}, error() {} };
  const context = {
    console,
    CONFIG: {
      SECS_PER_TILE_DEFAULT: 1,
      DETECTION_PROGRESS_POLL_INTERVAL_MS: 1000,
      PROGRESS_UPDATE_INTERVAL_MS: 1000
    },
    currentMap: map,
    Detection_detections: [],
    Detection: { resetAll() {} },
    Tile: { resetAll() {} },
    SimpleBoundary: TestBoundary,
    FormData: TestFormData,
    providerManager: {
      getMap() {
        return map;
      },
      stopProgressTimer() {},
      startProgressTimer() {}
    },
    TowerScoutErrorHandler: {
      showUserNotification() {},
      handleNetworkError(error) {
        throw error;
      },
      wrapNetworkCall(callback) {
        return callback;
      }
    },
    document: {
      querySelector() {
        return null;
      },
      getElementById() {
        return null;
      }
    },
    $: (selector) => ({
      val() {
        return selector.includes('model') ? 'newest' : provider;
      }
    }),
    async fetch(url, options) {
      assert.strictEqual(url, '/api/detection/estimate');
      fetchCalls.push({
        bounds: options.body.get('bounds'),
        polygons: options.body.get('polygons'),
        provider: options.body.get('provider')
      });
      return {
        ok: true,
        status: 200,
        async json() {
          return { tileCount: 1, estimatedSeconds: 1 };
        }
      };
    },
    performance: { now: () => 0 },
    setInterval() {},
    clearInterval() {},
    setTimeout,
    clearTimeout
  };
  context.window = {
    TowerScoutLogger: logger,
    confirm: () => true,
    googleMap: provider === 'google' ? map : inactiveMap,
    azureMap: provider === 'azure' ? map : inactiveMap
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(SEARCH_PATH, 'utf8'), context, { filename: SEARCH_PATH });
  return { context, fetchCalls };
}

async function testGoogleFirstUseCreatesBoundaryBeforeReadingBounds() {
  const googleMap = createMap('google');
  const { context, fetchCalls } = createContext('google', googleMap);

  await context.window.getObjects(true);
  await context.window.getObjects(true);

  assert.strictEqual(fetchCalls[0].bounds, '38,-123,37,-122');
  assert.notStrictEqual(fetchCalls[0].polygons, '[]');
  assert.strictEqual(fetchCalls[0].provider, 'google');
  assert.strictEqual(fetchCalls[1].bounds, '38,-123,37,-122');
  assert.strictEqual(googleMap.addCount, 1, 'repeat estimate must not add a duplicate boundary');
}

async function testExplicitGooglePolygonIsPreserved() {
  const polygon = new TestBoundary({ polygon: true });
  const googleMap = createMap('google', {
    boundaries: [polygon],
    explicitBounds: '37.9,-122.9,37.1,-122.1'
  });
  const { context, fetchCalls } = createContext('google', googleMap);

  await context.window.getObjects(true);

  assert.strictEqual(fetchCalls[0].bounds, '37.9,-122.9,37.1,-122.1');
  assert.strictEqual(googleMap.addCount, 0);
  assert.strictEqual(googleMap.boundaries[0], polygon);
}

async function testAzureViewportBehaviorRemainsValid() {
  const azureMap = createMap('azure');
  const { context, fetchCalls } = createContext('azure', azureMap);

  await context.window.getObjects(true);

  assert.strictEqual(fetchCalls[0].bounds, '38,-123,37,-122');
  assert.notStrictEqual(fetchCalls[0].polygons, '[]');
  assert.strictEqual(fetchCalls[0].provider, 'azure');
}

async function main() {
  await testGoogleFirstUseCreatesBoundaryBeforeReadingBounds();
  await testExplicitGooglePolygonIsPreserved();
  await testAzureViewportBehaviorRemainsValid();
  console.log('Detection payload bounds contract passed.');
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});