const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { performance } = require('perf_hooks');

const repoRoot = path.resolve(__dirname, '..', '..');

function loadScript(relPath) {
  const fullPath = path.join(repoRoot, relPath);
  const source = fs.readFileSync(fullPath, 'utf8');
  vm.runInThisContext(source, { filename: fullPath });
}

function createElement(id) {
  return {
    id,
    style: { display: 'block' },
    value: '',
    checked: false,
    innerHTML: '',
    innerText: '',
    textContent: '',
    onclick: null,
    onchange: null,
    oninput: null,
    disabled: false,
    title: '',
    parentNode: {
      firstChild: { classList: { add() {}, remove() {}, toggle() {} } },
      lastChild: { classList: { add() {}, remove() {}, toggle() {} } }
    },
    classList: { add() {}, remove() {}, toggle() {} },
    querySelector() {
      return { classList: { add() {}, remove() {}, toggle() {} } };
    },
    scrollIntoView() {}
  };
}

function setupEnvironment() {
  global.window = global;
  global.performance = performance;

  const consoleCounters = {
    log: 0,
    warn: 0,
    error: 0
  };

  global.console = {
    log() {
      consoleCounters.log += 1;
    },
    warn() {
      consoleCounters.warn += 1;
    },
    error() {
      consoleCounters.error += 1;
    }
  };

  const elements = new Map();
  const document = {
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, createElement(id));
      }
      return elements.get(id);
    },
    querySelectorAll() {
      return [];
    }
  };

  global.document = document;
  global.fetch = async () => {
    throw new Error('fetch is not available in ISSUE-003 benchmark harness');
  };

  global.DEFAULT_CONFIDENCE = 0.15;
  global.setTimeout = setTimeout;
  global.clearTimeout = clearTimeout;
  global.setInterval = setInterval;
  global.clearInterval = clearInterval;

  const requiredIds = ['checkBoxes', 'conf', 'review', 'confpercent', 'detection'];
  requiredIds.forEach((id) => document.getElementById(id));

  loadScript('webapp/js/src/store.js');
  loadScript('webapp/js/src/managers/ProviderStateManager.js');
  loadScript('webapp/js/src/globals.js');

  global.detectionsList = document.getElementById('checkBoxes');
  global.confSlider = document.getElementById('conf');
  global.reviewCheckBox = document.getElementById('review');
  global.confSlider.value = '15';
  global.reviewCheckBox.checked = false;
  global.document.getElementById('detection').value = '0';

  loadScript('webapp/js/src/detection/PlaceRect.js');
  loadScript('webapp/js/src/detection/Detection.js');
  loadScript('webapp/js/src/detection/DetectionList.js');

  return { consoleCounters };
}

function createGoogleLikeMap() {
  const stats = {
    updateCalls: 0,
    makeCalls: 0
  };

  return {
    stats,
    makeMapRect() {
      stats.makeCalls += 1;
      return {
        setMap() {},
        setOptions() {}
      };
    },
    updateMapRect() {
      stats.updateCalls += 1;
    },
    colorMapRect() {},
    setCenter() {},
    setZoom() {}
  };
}

function createAzureLikeMap() {
  const shapes = [];
  const stats = {
    updateCalls: 0,
    shapeLookups: 0,
    shapesAdded: 0,
    maxShapeCount: 0,
    makeCalls: 0
  };

  const detectionDataSource = {
    getShapes() {
      return shapes;
    },
    add(shape) {
      shapes.push(shape);
      stats.shapesAdded += 1;
      stats.maxShapeCount = Math.max(stats.maxShapeCount, shapes.length);
    }
  };

  return {
    stats,
    detectionDataSource,
    makeMapRect(obj) {
      stats.makeCalls += 1;
      const feature = {
        properties: {
          detectionId: 'pending'
        }
      };
      obj.azureFeature = feature;
      return feature;
    },
    updateMapRect(obj, onoff) {
      stats.updateCalls += 1;

      const detectionId = (obj.id !== undefined) ? obj.id : 'pending';
      const allShapes = detectionDataSource.getShapes();
      stats.shapeLookups += allShapes.length;

      const existingShapes = allShapes.filter((shape) => shape.properties && shape.properties.detectionId === detectionId);

      if (existingShapes.length > 0) {
        const shape = existingShapes[0];
        if (!onoff) {
          shape.setProperties({
            detectionId,
            fillOpacity: 0.0,
            strokeColor: 'transparent',
            strokeWidth: 0
          });
        } else {
          shape.setProperties({
            detectionId,
            fillColor: obj.fillColor,
            strokeColor: obj.color,
            fillOpacity: 0.5,
            strokeWidth: 2
          });
        }
        return;
      }

      if (onoff) {
        const shape = {
          properties: {
            detectionId,
            fillColor: obj.fillColor,
            strokeColor: obj.color,
            fillOpacity: 0.5,
            strokeWidth: 2
          },
          setProperties(next) {
            this.properties = { ...this.properties, ...next };
          },
          getProperties() {
            return this.properties;
          }
        };

        detectionDataSource.add(shape);
        obj.azureShape = shape;
      }
    },
    colorMapRect() {},
    setCenter() {},
    setZoom() {}
  };
}

function resetState(map) {
  providerManager.setDetections([]);
  providerManager.currentMap = map;
  global.currentMap = map;
  global.Detection_detectionsAugmented = 0;
  global.Detection_current = null;
  global.detectionsList.innerHTML = '';
  global.confSlider.value = '15';
  global.reviewCheckBox.checked = false;
  global.document.getElementById('confpercent').innerText = '15';
}

function timed(fn) {
  const start = performance.now();
  fn();
  return Number((performance.now() - start).toFixed(3));
}

function populateDetections(count, map) {
  for (let i = 0; i < count; i += 1) {
    const x1 = -74.0 + (i * 0.00001);
    const y1 = 40.7 + (i * 0.00001);
    const x2 = x1 + 0.000005;
    const y2 = y1 - 0.000005;
    const confidence = 0.92;
    const secondary = 0.95;
    const inside = true;
    const addressGroup = Math.floor(i / 5);
    const address = `Address ${addressGroup.toString().padStart(4, '0')}`;

    global.currentMap = map;
    providerManager.currentMap = map;

    new Detection(
      x1,
      y1,
      x2,
      y2,
      'tower',
      confidence,
      0,
      i,
      inside,
      true,
      secondary,
      address,
      0.9,
      'benchmark'
    );
  }
}

function remountAllDetections(mapFactory) {
  const nextMap = mapFactory();
  const detections = providerManager.getDetectionsArrayDirect();

  providerManager.currentMap = nextMap;
  global.currentMap = nextMap;

  for (const det of detections) {
    det._lastVisibilityState = undefined;
    det.update(nextMap);
    det.update();
  }

  return nextMap.stats;
}

function benchmarkScenario(label, count, mapFactory, consoleCounters) {
  const consoleStart = { ...consoleCounters };
  const map = mapFactory();
  resetState(map);

  const createMs = timed(() => populateDetections(count, map));
  const sortMs = timed(() => Detection.sort());
  const listMs = timed(() => Detection.generateList());
  const confidenceMs = timed(() => adjustConfidence());
  let remountStats;
  const remountMs = timed(() => {
    remountStats = remountAllDetections(mapFactory);
  });

  const consoleDelta = {
    log: consoleCounters.log - consoleStart.log,
    warn: consoleCounters.warn - consoleStart.warn,
    error: consoleCounters.error - consoleStart.error
  };

  return {
    provider: label,
    detections: count,
    timingsMs: {
      create: createMs,
      sort: sortMs,
      generateList: listMs,
      adjustConfidence: confidenceMs,
      remountOnFreshMap: remountMs
    },
    mapStats: {
      initial: map.stats,
      remount: remountStats
    },
    consoleCalls: consoleDelta
  };
}

function main() {
  const { consoleCounters } = setupEnvironment();
  const sizes = [100, 500, 1000];
  const results = [];

  for (const size of sizes) {
    results.push(benchmarkScenario('google-like', size, createGoogleLikeMap, consoleCounters));
    results.push(benchmarkScenario('azure-like', size, createAzureLikeMap, consoleCounters));
  }

  process.stdout.write(`${JSON.stringify({ generatedAt: new Date().toISOString(), results }, null, 2)}\n`);
}

main();
