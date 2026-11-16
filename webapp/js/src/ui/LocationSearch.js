// One persistent location input, with provider-specific suggestions and navigation.
(function () {
  'use strict';

  class LocationSearchController {
    constructor(input) {
      this.input = input;
      this.epoch = 0;
      this.timer = null;
      this.abort = null;
      this.token = null;
      this.tokenCreated = 0;
      this.items = [];
      this.active = -1;
      this.menuSnapshot = null;
      const host = document.createElement('div');
      host.className = 'location-search';
      input.replaceWith(host);
      host.appendChild(input);
      this.panel = document.createElement('div');
      this.panel.className = 'location-search-panel';
      this.panel.hidden = true;
      this.list = document.createElement('div');
      this.list.id = 'location-suggestions';
      this.list.setAttribute('role', 'listbox');
      this.attribution = document.createElement('div');
      this.attribution.className = 'location-search-attribution';
      this.attribution.setAttribute('translate', 'no');
      this.panel.appendChild(this.list);
      this.panel.appendChild(this.attribution);
      this.status = document.createElement('div');
      this.status.className = 'location-search-status';
      this.status.id = 'location-search-status';
      this.status.setAttribute('role', 'status');
      host.appendChild(this.panel);
      host.appendChild(this.status);
      input.placeholder = 'Address, ZIP, or latitude, longitude';
      input.setAttribute('aria-label', 'Search location');
      input.setAttribute('role', 'combobox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-controls', this.list.id);
      input.setAttribute('aria-describedby', this.status.id);
      input.setAttribute('aria-expanded', 'false');
      input.setAttribute('autocomplete', 'off');
      input.addEventListener('input', event => {
        this.invalidate(false);
        this.status.textContent = '';
        if (!event.isComposing) this.schedule();
      });
      input.addEventListener('compositionstart', () => this.invalidate());
      input.addEventListener('compositionend', () => this.schedule());
      input.addEventListener('keydown', event => this.keydown(event));
      input.addEventListener('blur', () => {
        this.invalidate();
        this.status.textContent = '';
      });
    }

    snapshot() {
      return {
        epoch: this.epoch, query: this.input.value.trim(),
        provider: window.providerManager.getCurrentProvider(),
        map: window.providerManager.getMap()
      };
    }

    current(snapshot) {
      const ui = document.querySelector('input[name="uis"]:checked');
      return snapshot.epoch === this.epoch && snapshot.query === this.input.value.trim()
        && snapshot.provider === window.providerManager.getCurrentProvider()
        && snapshot.map === window.providerManager.getMap()
        && !window.providerManager.isSwitching()
        && (!ui || ui.value === snapshot.provider);
    }

    isZip(query) {
      return /^\d{5}$/.test(query) || /^"\d{5}"$/.test(query) || /^zipcode\s/i.test(query);
    }

    special(query) {
      return this.isZip(query) || window.CoordinateSearch.parse(query) !== null;
    }

    close() {
      this.items = [];
      this.active = -1;
      this.menuSnapshot = null;
      this.list.replaceChildren();
      this.panel.hidden = true;
      this.input.setAttribute('aria-expanded', 'false');
      this.input.removeAttribute('aria-activedescendant');
    }

    invalidate(resetToken = true) {
      ++this.epoch;
      clearTimeout(this.timer);
      this.timer = null;
      this.abort?.abort();
      this.abort = null;
      this.close();
      this.status.textContent = '';
      if (resetToken) this.token = null;
    }

    schedule() {
      const query = this.input.value.trim();
      if (query.length < 3 || this.special(query)) {
        this.token = null;
        return;
      }
      this.timer = setTimeout(() => { void this.suggest(); }, 300);
    }

    async bounded(request) {
      let timer;
      try {
        return await Promise.race([
          request,
          new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('search timeout')), 8000); })
        ]);
      } finally {
        clearTimeout(timer);
      }
    }

    async azure(query, map) {
      const [lon, lat] = map.getCenter();
      this.abort = new AbortController();
      const params = new URLSearchParams({ query, limit: '5', countrySet: 'US', lat, lon });
      const response = await window.TowerScoutConfigApi.fetchJson(`/api/maps/azure/suggest?${params}`, {
        signal: this.abort.signal, timeoutMs: 8000
      });
      return (response.results || []).filter(result => result.position).map(result => ({
        label: result.address?.freeformAddress || query, result
      }));
    }

    async suggest() {
      const snapshot = this.snapshot();
      if (!this.current(snapshot) || !snapshot.map || snapshot.query.length < 3 || this.special(snapshot.query)) return;
      this.status.textContent = 'Searching…';
      try {
        let items;
        if (snapshot.provider === 'google') {
          const places = google.maps.places;
          if (!this.token || Date.now() - this.tokenCreated > 180000) {
            this.token = new places.AutocompleteSessionToken();
            this.tokenCreated = Date.now();
          }
          const response = await this.bounded(places.AutocompleteSuggestion.fetchAutocompleteSuggestions({
            input: snapshot.query, sessionToken: this.token,
            locationBias: snapshot.map.map.getBounds()
          }));
          items = response.suggestions.filter(item => item.placePrediction).map(item => ({
            label: item.placePrediction.text.toString(), prediction: item.placePrediction
          }));
        } else if (snapshot.provider === 'azure') {
          items = await this.azure(snapshot.query, snapshot.map);
        } else return;
        if (!this.current(snapshot)) return;
        this.show(items.slice(0, 5), snapshot);
      } catch (_) {
        if (this.current(snapshot)) {
          this.close();
          this.status.textContent = 'Suggestions unavailable. Press Enter to search.';
        }
      }
    }

    show(items, snapshot) {
      this.close();
      this.items = items;
      this.menuSnapshot = snapshot;
      this.status.textContent = items.length ? `${items.length} suggestions. Use arrow keys to choose.` : 'No suggestions. Press Enter to search.';
      items.forEach((item, index) => {
        const option = document.createElement('div');
        option.id = `location-option-${this.epoch}-${index}`;
        option.setAttribute('role', 'option');
        option.setAttribute('aria-selected', 'false');
        option.textContent = item.label;
        // Keep focus on the combobox so blur does not discard the clicked result.
        option.addEventListener('mousedown', event => event.preventDefault());
        option.addEventListener('click', () => { void this.choose(index); });
        this.list.appendChild(option);
      });
      this.attribution.textContent = snapshot.provider === 'google' ? 'Google Maps' : 'Azure Maps';
      this.panel.hidden = items.length === 0;
      this.input.setAttribute('aria-expanded', String(items.length > 0));
    }

    keydown(event) {
      if (event.isComposing) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        this.invalidate();
      } else if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && this.items.length) {
        event.preventDefault();
        this.active = (this.active + (event.key === 'ArrowDown' ? 1 : (this.active < 0 ? 0 : -1)) + this.items.length) % this.items.length;
        Array.from(this.list.children).forEach((node, index) => node.setAttribute('aria-selected', String(index === this.active)));
        const option = this.list.children[this.active];
        this.input.setAttribute('aria-activedescendant', option.id);
        option.scrollIntoView({ block: 'nearest' });
      } else if (event.key === 'Enter') {
        event.preventDefault();
        if (this.active >= 0) void this.choose(this.active);
        else void this.submit();
      }
    }

    async choose(index) {
      const item = this.items[index];
      const snapshot = this.menuSnapshot;
      if (!item || !snapshot || !this.current(snapshot)) return;
      this.invalidate();
      this.input.value = item.label;
      const selection = this.snapshot();
      this.status.textContent = 'Finding location…';
      try {
        if (selection.provider === 'google') {
          const place = item.prediction.toPlace();
          await this.bounded(place.fetchFields({ fields: ['location', 'viewport', 'displayName', 'formattedAddress'] }));
          if (!this.current(selection)) return;
          this.showGoogle(place, selection);
        } else {
          this.showAzure(item.result, selection);
        }
      } catch (_) {
        if (this.current(selection)) this.status.textContent = 'Location unavailable. Press Enter to search the address.';
      }
    }

    showGoogle(place, snapshot) {
      if (!this.current(snapshot) || !place.location) throw new Error('location unavailable');
      // Address results navigate only; boundaries are selected explicitly by the user.
      snapshot.map.map.setCenter(place.location);
      if (place.viewport) snapshot.map.map.fitBounds(place.viewport);
      else snapshot.map.setZoom(17);
      this.status.textContent = 'Location found.';
    }

    showAzure(result, snapshot) {
      if (!this.current(snapshot) || !result?.position) return;
      snapshot.map.setCenter([result.position.lon, result.position.lat]);
      snapshot.map.setZoom(17);
      snapshot.map.addSearchResultMarker(result);
      this.status.textContent = 'Location found.';
    }

    async submit() {
      this.invalidate();
      const snapshot = this.snapshot();
      if (!snapshot.query) return;
      if (!snapshot.map || !this.current(snapshot) || !window.providerManager.isFullyInitialized()) {
        this.status.textContent = 'Map is still loading. Try again in a moment.';
        return;
      }
      if (window.CoordinateSearch.handle(snapshot.query, snapshot.map)) return;
      if (this.isZip(snapshot.query)) {
        getZipcodePolygon(snapshot.query, () => this.current(snapshot));
        return;
      }
      this.status.textContent = 'Finding location…';
      try {
        if (snapshot.provider === 'google') {
          const response = await this.bounded(new google.maps.Geocoder().geocode({ address: snapshot.query }));
          if (!this.current(snapshot)) return;
          const place = response.results[0];
          if (!place) throw new Error('no results');
          this.showGoogle({
            location: place.geometry.location, viewport: place.geometry.viewport,
            formattedAddress: place.formatted_address
          }, snapshot);
        } else if (snapshot.provider === 'azure') {
          const results = await this.bounded(snapshot.map.searchAddress(snapshot.query));
          if (!this.current(snapshot)) return;
          if (!results.length) throw new Error('no results');
          this.showAzure(results[0], snapshot);
        }
      } catch (_) {
        if (this.current(snapshot)) this.status.textContent = 'Location not found or search unavailable. Check the address and try again.';
      }
    }
  }

  let controller;
  window.LocationSearchController = LocationSearchController;
  window.LocationSearch = {
    init() {
      const input = document.getElementById('search');
      if (input && !controller) controller = new LocationSearchController(input);
      if (input) input.style.display = '';
      const legacy = document.getElementById('google-autocomplete-container');
      if (legacy) legacy.style.display = 'none';
      return controller;
    },
    invalidate() { controller?.invalidate(); },
    submit() { this.init(); return controller?.submit(); }
  };
})();
