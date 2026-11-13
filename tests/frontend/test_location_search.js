const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

class Element {
  constructor(tag = 'div') {
    this.tagName = tag;
    this.children = [];
    this.attributes = {};
    this.listeners = {};
    this.style = {};
    this.value = '';
    this.textContent = '';
  }
  appendChild(node) { this.children.push(node); node.parentElement = this; }
  replaceWith(node) {
    const parent = this.parentElement;
    parent.children[parent.children.indexOf(this)] = node;
    node.parentElement = parent;
  }
  replaceChildren() { this.children = []; }
  setAttribute(key, value) { this.attributes[key] = value; }
  removeAttribute(key) { delete this.attributes[key]; }
  addEventListener(type, callback) { (this.listeners[type] ||= []).push(callback); }
  scrollIntoView() {}
  fire(type, extra = {}) {
    const event = { preventDefault() {}, ...extra };
    (this.listeners[type] || []).forEach(callback => callback(event));
  }
}

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const flush = () => new Promise(resolve => setImmediate(resolve));
function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}

async function main() {
  const input = new Element('input');
  new Element().appendChild(input);
  const calls = [];
  let provider = 'google';
  let switching = false;
  let predictions = async () => ({ suggestions: [] });
  let details = async () => {};
  let azureResponse = async () => ({ results: [] });
  let tokenCount = 0;
  const makeMap = name => ({
    map: { getBounds: () => ({}), setCenter: value => calls.push([name, 'center', value]) },
    getCenter: () => [-74, 40],
    setCenter: value => calls.push([name, 'center', [...value]]),
    setZoom: zoom => calls.push([name, 'zoom', zoom]),
    getBoundsPolygon(query, place, current) { if (current()) calls.push([name, 'place', query]); },
    resetBoundaries: () => calls.push([name, 'reset']),
    addSearchResultMarker: () => calls.push([name, 'marker']),
    searchAddress: async () => [{ position: { lon: -77, lat: 38 }, address: {} }]
  });
  const maps = { google: makeMap('google'), azure: makeMap('azure') };
  const window = {
    TowerScoutLogger: { debug() {} },
    providerManager: {
      getCurrentProvider: () => provider, getMap: () => maps[provider],
      isSwitching: () => switching, isFullyInitialized: () => true
    },
    TowerScoutConfigApi: { fetchJson: (...args) => azureResponse(...args) }
  };
  const context = vm.createContext({
    window, document: {
      createElement: tag => new Element(tag),
      getElementById: id => id === 'search' ? input : null,
      querySelector: () => ({ value: provider })
    },
    google: { maps: {
      places: {
        AutocompleteSessionToken: class { constructor() { tokenCount++; } },
        AutocompleteSuggestion: { fetchAutocompleteSuggestions: (...args) => predictions(...args) }
      },
      Geocoder: class {
        async geocode() { return { results: [{ geometry: { location: {}, viewport: {} }, formatted_address: 'Address' }] }; }
      }
    } },
    TowerScoutErrorHandler: { showUserNotification: () => calls.push(['warning']) },
    getZipcodePolygon: (query, current) => { if (current()) calls.push(['zip', query]); },
    setTimeout, clearTimeout, AbortController, URLSearchParams, console
  });
  for (const file of ['utils/coordinates.js', 'ui/LocationSearch.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../../webapp/js/src', file), 'utf8'), context);
  }
  const search = window.LocationSearch.init();
  assert.strictEqual(window.LocationSearch.init(), search, 'Initialization must be idempotent');
  assert.strictEqual(search.input, input);
  assert.strictEqual(input.listeners.keydown.length, 1, 'Only one keyboard handler');

  let requested = [];
  const prediction = label => ({ placePrediction: {
    text: { toString: () => label },
    toPlace: () => ({ location: {}, viewport: {}, formattedAddress: label, fetchFields: () => details() })
  } });
  predictions = async request => { requested.push(request); return { suggestions: [prediction('<img onerror=bad>')] }; };
  input.value = 'Example'; input.fire('input');
  input.value = 'Example address'; input.fire('input');
  assert.strictEqual(requested.length, 0, 'Requests must be debounced');
  await delay(340);
  assert.strictEqual(requested.length, 1);
  assert.strictEqual(requested[0].input, 'Example address');
  assert.strictEqual(search.list.children[0].textContent, '<img onerror=bad>', 'Provider text stays text');
  assert.strictEqual(search.attribution.textContent, 'Google Maps');
  assert.strictEqual(input.attributes['aria-expanded'], 'true');
  input.fire('keydown', { key: 'ArrowDown' });
  assert.strictEqual(search.list.children[0].attributes['aria-selected'], 'true');
  input.fire('keydown', { key: 'Enter' });
  await flush();
  assert.ok(calls.some(call => call[1] === 'place'), 'Selection must resolve and navigate');
  assert.strictEqual(input.value, '<img onerror=bad>');
  assert.strictEqual(search.token, null, 'A selection ends the Google session');

  for (const query of ['40.7128, -74.0060', '10001', 'zipcode 10001', 'ab']) {
    input.value = query; input.fire('input');
    assert.strictEqual(search.timer, null, 'Coordinates, ZIPs, and short text do not request suggestions');
  }
  input.value = '40.7128, -74.0060';
  input.fire('keydown', { key: 'Enter' });
  assert.ok(calls.some(call => call[1] === 'center' && JSON.stringify(call[2]) === '[-74.006,40.7128]'));
  input.value = '91,0'; await search.submit();
  assert.ok(calls.some(call => call[0] === 'warning'));
  input.value = '10001'; await search.submit();
  assert.ok(calls.some(call => call[0] === 'zip'));

  // An older result must not replace suggestions for newer text, even on the same provider.
  input.value = 'Old query';
  const old = deferred(); predictions = () => old.promise;
  const pending = search.suggest();
  search.invalidate(false); input.value = 'New query';
  predictions = async () => ({ suggestions: [prediction('New result')] });
  await search.suggest();
  old.resolve({ suggestions: [prediction('Old result')] }); await pending;
  assert.strictEqual(search.items[0].label, 'New result');
  assert.strictEqual(tokenCount, 2, 'Typing within a session reuses its token');

  // Details resolving after typing again must not move the map.
  const detail = deferred(); details = () => detail.promise;
  const before = calls.length;
  const choosing = search.choose(0);
  search.invalidate(); input.value = 'Different query';
  detail.resolve(); await choosing;
  assert.strictEqual(calls.length, before);

  // A switch away and back also invalidates in-flight predictions.
  const switched = deferred(); predictions = () => switched.promise;
  const switchingRequest = search.suggest();
  search.invalidate(); provider = 'azure';
  search.invalidate(); provider = 'google';
  switched.resolve({ suggestions: [prediction('Stale Google result')] }); await switchingRequest;
  assert.strictEqual(search.items.length, 0);

  provider = 'azure';
  azureResponse = async (url, options) => {
    assert.ok(url.startsWith('/api/maps/azure/suggest?'));
    assert.ok(options.signal);
    return { results: [{ address: { freeformAddress: 'Azure address' }, position: { lon: -77, lat: 38 } }] };
  };
  await search.suggest();
  assert.strictEqual(search.attribution.textContent, 'Azure Maps');
  await search.choose(0);
  assert.ok(calls.some(call => call[0] === 'azure' && call[1] === 'marker'));
  assert.strictEqual(window.LocationSearch.init().input, input, 'Switching must keep the same input');

  azureResponse = async () => { throw new Error('provider unavailable'); };
  await search.suggest();
  assert.ok(search.status.textContent.includes('Press Enter'));
  await search.submit();
  assert.strictEqual(search.status.textContent, 'Location found.', 'Enter works when autocomplete fails');

  await search.suggest();
  input.fire('keydown', { key: 'Escape' });
  assert.strictEqual(search.items.length, 0);
  assert.strictEqual(input.attributes['aria-expanded'], 'false');
  switching = true;
  await search.submit();
  assert.ok(search.status.textContent.includes('loading'));
  search.invalidate();
  console.log('Shared location search regression checks PASSED');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
