const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '../..');
const warnings = [];
const listeners = {};
const input = { style: {}, value: '' };
const container = {
  style: {}, childNodes: [], appendChild() {},
  querySelectorAll() { return []; }
};
const context = vm.createContext({
  console, input, currentProvider: 'google',
  window: { TowerScoutLogger: { debug() {} } },
  TowerScoutErrorHandler: { showUserNotification: (...args) => warnings.push(args) },
  document: {
    getElementById: id => id === 'search' ? input : container,
    querySelectorAll: () => []
  },
  google: { maps: { places: { PlaceAutocompleteElement: class {
    constructor() { this.style = {}; this.value = ''; }
    addEventListener(name, handler, options) { listeners[name] = { handler, options }; }
  } } } }
});
function load(file) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
}
load('webapp/js/src/utils/coordinates.js');
load('webapp/js/src/providers/TSMap_base.js');
context.TSMap = context.window.TSMap;
load('webapp/js/src/providers/GoogleMap.js');
load('webapp/js/src/providers/AzureMap.js');

const parse = context.window.CoordinateSearch.parse;
for (const text of ['40.7128, -74.0060', '40.7128 -74.0060', '(40.7128, -74.0060)']) {
  assert.strictEqual(JSON.stringify(parse(text)), JSON.stringify({ lat: 40.7128, lng: -74.006 }));
}
for (const text of ['0,0', '-90, -180', '+90 +180', '.5, -.25']) {
  assert.ok(!parse(text).error, text);
}
for (const text of ['91, 0', '0, -181', '40,, -74', '(40, -74', '40, -74, 3']) {
  assert.strictEqual(parse(text).error, true, text);
}
for (const text of ['', '10001', '"10001"', 'zipcode 10001', '1600 Pennsylvania Ave NW', '123 Main St, Washington']) {
  assert.strictEqual(parse(text), null, text);
}

for (const Provider of [context.window.GoogleMap, context.window.AzureMap]) {
  const map = Object.create(Provider.prototype);
  const calls = [];
  map.setCenter = coords => calls.push(['center', ...coords]);
  map.setZoom = zoom => calls.push(['zoom', zoom]);
  map.resetBoundaries = () => { throw new Error('Coordinate search discarded boundaries'); };
  map.searchAddress = () => { throw new Error('Coordinate search made an address request'); };
  map.boundaries = [{ retained: true }];
  map.getBoundsPolygon('40.7128, -74.0060', null);
  assert.deepStrictEqual(calls, [['center', -74.006, 40.7128], ['zoom', 17]]);
  assert.strictEqual(map.boundaries[0].retained, true);
  calls.length = 0;
  map.getBoundsPolygon('91, 0', null);
  assert.deepStrictEqual(calls, []);
}
assert.strictEqual(warnings.length, 2);

// Azure navigation must remove only location markers from its shared drawing source.
const azureMap = Object.create(context.window.AzureMap.prototype);
const boundary = { getProperties: () => ({ type: 'boundary', isCircle: true }) };
const otherShape = { getProperties: () => ({}) };
const marker = { getProperties: () => ({ searchResult: true }) };
let shapes = [boundary, otherShape, marker];
azureMap.searchDataSource = {
  getShapes: () => shapes,
  remove: removed => { shapes = shapes.filter(shape => !removed.includes(shape)); },
  clear() { throw new Error('Navigation must not clear boundary drawings'); }
};
azureMap.clearSearchResultMarkers();
assert.deepStrictEqual(shapes, [boundary, otherShape]);
shapes.push(marker);
azureMap.setCenter = () => {};
azureMap.setZoom = () => {};
context.window.CoordinateSearch.handle('40.7128, -74.0060', azureMap);
assert.deepStrictEqual(shapes, [boundary, otherShape]);

// Shared-input keyboard coverage lives in test_location_search.js.
const googleMap = Object.create(context.window.GoogleMap.prototype);

// A Google fallback point without a Place must no longer throw.
context.googleMap = googleMap;
googleMap.resetBoundaries = () => {};
googleMap.boundaries = [];
googleMap.map = { getBounds: () => ({}), fitBounds() {} };
context.$ = { ajax(options) {
  assert.strictEqual(options.data.q, 'Example address');
  options.success([{ geojson: { type: 'Point' }, display_name: 'Example' }]);
} };
assert.doesNotThrow(() => googleMap.getBoundsPolygon('Example address', null));

console.log('Coordinate search regression checks PASSED');
