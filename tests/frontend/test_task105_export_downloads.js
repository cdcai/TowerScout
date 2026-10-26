#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.join(__dirname, '../..');
const source = fs.readFileSync(path.join(root, 'webapp/js/src/ui/export.js'), 'utf8');
const template = fs.readFileSync(path.join(root, 'webapp/templates/towerscout.html'), 'utf8');

assert.match(template, /onclick="download_csv\(\)"/);
assert.match(template, /onclick="download_kml\(\)"/);
assert.doesNotMatch(template, /onclick="download_csv\(\),download_kml\(\)"/);

const clicks = [];
const revoked = [];
const notifications = [];
const blobs = [];
const detection = {
  selected: true, inside: true, conf: 0.9, address: 'Test address', tile: 0,
  idInTile: 0,
  getCenter() { return [-75, 40]; }
};
const document = {
  body: {
    appendChild(elem) { elem.parentNode = this; },
    removeChild(elem) { elem.parentNode = null; }
  },
  createElement() {
    return {
      click() { clicks.push({ filename: this.download, url: this.href }); }
    };
  }
};
const context = {
  Blob: class {
    constructor(parts, options) { this.parts = parts; this.type = options.type; blobs.push(this); }
  },
  Detection_detections: [detection],
  Detection_minConfidence: 0.5,
  Tile_tiles: [],
  reviewCheckBox: { checked: false },
  confSlider: { value: 50 },
  getDistance() { return 0; },
  currentMap: { getCenter() { return [-75, 40]; } },
  providerManager: {
    getDetectionsArrayDirect() { return [detection]; },
    getTilesArrayDirect() { return []; }
  },
  document,
  alert(message) { notifications.push(message); },
  setTimeout(callback) { callback(); },
  console,
  window: {
    document,
    URL: {
      createObjectURL() { return `blob:test-${blobs.length}`; },
      revokeObjectURL(url) { revoked.push(url); }
    },
    TowerScoutLogger: { debug() {} },
    Detection_detections: [detection]
  }
};
vm.createContext(context);
vm.runInContext(source, context);

context.window.download_csv();
assert.deepStrictEqual(clicks.map(click => click.filename), ['detections.csv']);
assert.strictEqual(blobs[0].type, 'text/csv;charset=utf-8');
assert.deepStrictEqual(revoked, ['blob:test-1']);

context.window.download_kml();
assert.deepStrictEqual(clicks.map(click => click.filename), ['detections.csv', 'detections.kml']);
assert.strictEqual(blobs[1].type, 'application/vnd.google-earth.kml+xml');
assert.deepStrictEqual(revoked, ['blob:test-1', 'blob:test-2']);
assert.strictEqual(notifications.length, 2);
// Exercise the real download handlers; Python's standard parsers independently
// verify the emitted files when --serialization-fixture is requested.
if (process.argv.includes('--serialization-fixture')) {
  const special = 'A & B "Annex", <North> \'West\'\r\nMontréal ]]> &amp;';
  const metadata = 'Satellite & aerial <imagery> "2026"\r\nProvider';
  const detections = [
    { ...detection, address: special },
    { ...detection, idInTile: -1, address: 'Manual "tower", café' },
    { ...detection, address: '' },
    { ...detection, address: 'Unselected', selected: false },
    { ...detection, address: 'Below threshold', conf: 0.1 },
    { ...detection, address: 'Outside boundary', inside: false }
  ];
  context.Detection_detections = detections;
  context.window.Detection_detections = detections;
  context.providerManager.getDetectionsArrayDirect = () => detections;
  context.providerManager.getTilesArrayDirect = () => [{ metadata }];
  context.window.download_csv();
  context.window.download_kml();
  assert.strictEqual(clicks.length, 4);
  assert.strictEqual(notifications.length, 4);
  assert.strictEqual(revoked.length, 4);
  console.log(JSON.stringify({
    special, metadata,
    csv: blobs[2].parts.join(''), kml: blobs[3].parts.join('')
  }));
} else {
  console.log('Task-105 explicit export downloads passed');
}
