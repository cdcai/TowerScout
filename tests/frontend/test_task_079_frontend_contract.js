#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '../..');

function loadScript(relativePath, context) {
  const source = fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
  vm.runInContext(source, context, { filename: relativePath });
}

function createContext() {
  const context = {
    console,
    window: {
      TowerScoutLogger: {
        debug() {},
        info() {},
        warn() {},
        error() {}
      }
    },
    TowerScoutErrorHandler: {
      showUserNotification() {}
    },
    PlaceRect: class PlaceRect {},
    TSMap: class TSMap {}
  };
  context.window.window = context.window;
  context.window.TowerScoutErrorHandler = context.TowerScoutErrorHandler;
  vm.createContext(context);
  return context;
}

function makeShape(points, type = 'Polygon') {
  return {
    toJson() {
      return {
        geometry: {
          type,
          coordinates: [points]
        }
      };
    }
  };
}

function testPolygonValidationContext() {
  const context = createContext();
  loadScript('webapp/js/src/utils/polygonValidation.js', context);

  assert.strictEqual(
    context.window.PolygonValidation.validatePolygonCollection([]).valid,
    true,
    'empty polygon collection remains valid by default'
  );

  const emptyRequired = context.window.PolygonValidation.validatePolygonCollection([], { requireNonEmpty: true });
  assert.strictEqual(emptyRequired.valid, false);
  assert.strictEqual(emptyRequired.reason, 'empty_collection');
}

function testAzureShapeValidationAndFallbackSource() {
  const context = createContext();
  loadScript('webapp/js/src/utils/polygonValidation.js', context);
  loadScript('webapp/js/src/providers/AzureMap.js', context);

  const map = Object.create(context.window.AzureMap.prototype);
  const sourceShape = makeShape([
    [-122.0, 47.0],
    [-122.0, 47.1],
    [-121.9, 47.1],
    [-122.0, 47.0]
  ]);
  map.newShapes = [];
  map.drawingManager = {
    getSource() {
      return {
        getShapes() {
          return [sourceShape];
        }
      };
    }
  };

  assert.deepStrictEqual(map.getPendingBoundaryShapes(), [sourceShape]);

  const valid = map.validateDrawnShapes({
    shapes: [sourceShape],
    requireNonEmpty: true
  });
  assert.strictEqual(valid.valid, true);

  const unsupported = map.validateDrawnShapes({
    shapes: [makeShape([[0, 0]], 'Point')],
    requireNonEmpty: true
  });
  assert.strictEqual(unsupported.valid, false);
  assert.strictEqual(unsupported.reason, 'unsupported_geometry');

  const empty = map.validateDrawnShapes({
    shapes: [],
    requireNonEmpty: true
  });
  assert.strictEqual(empty.valid, false);
  assert.strictEqual(empty.reason, 'empty_collection');
}

function testDetectionAddressEscaping() {
  const context = createContext();
  context.Detection_detections = [{
    id: 0,
    address: '<img src=x onerror=alert(1)>',
    conf: 0.95,
    secondary: 0.9,
    generateCheckBox() {
      return '<li>tower</li>';
    }
  }];
  context.Detection_detectionsAugmented = 0;
  context.detectionsList = { innerHTML: '' };
  context.adjustConfidence = function adjustConfidence() {};
  loadScript('webapp/js/src/detection/Detection.js', context);

  context.window.Detection.generateList();
  assert(
    context.detectionsList.innerHTML.includes('&lt;img src=x onerror=alert(1)&gt;'),
    'address text should be escaped before insertion'
  );
  assert(
    !context.detectionsList.innerHTML.includes('<img src=x'),
    'raw address HTML should not be inserted'
  );
}

testPolygonValidationContext();
testAzureShapeValidationAndFallbackSource();
testDetectionAddressEscaping();
console.log('TASK-079 frontend contract PASSED');
