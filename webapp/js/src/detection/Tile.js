// TowerScout - Tile Module
// Tile grid system and coordinate mapping
// TASK-038 Stage 4: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  class Tile extends PlaceRect {
    static resetAll() {
      for (let tile of providerManager.getTiles()) {
        currentMap.updateMapRect(tile, false);
      }
      providerManager.clearTiles(); // Phase 2: Use state manager for clearing
    }

    constructor(x1, y1, x2, y2, metadata, url, id) {
      super(x1, y1, x2, y2, "#0000FF", "#0000FF", 0.0, "tile")
      this.metadata = metadata; // for map metadata
      this.url = url
      this.id = (id !== undefined) ? id : providerManager.getTilesLength();  // Phase 2: Use state manager for length

      providerManager.addTile(this); // Phase 2: Use state manager for adding
    }

    // find the ids for all tiles that the center of this box belongs to
    static getTileIds(x1, y1, x2, y2) {
      let result = [];
      const tiles = providerManager.getTilesArrayDirect();
      for (let i = 0; i < tiles.length; i++) {
        let t = tiles[i]
        // compute center
        let cx = (x1 + x2) / 2;
        let cy = (y1 + y2) / 2;

        // check if center in tile
        if (cx >= t.x1 && cx <= t.x2 && cy <= t.y1 && cy >= t.y2) {
          result.push(i);
        }
      }
      return result;
    }

    // tile navigation for review pane
    static number() {
      let index = document.getElementById("tile").value;
      if (index === "") {
        index = "0";
      } else {
        index = Number(index) % providerManager.getTilesLength();
      }
      document.getElementById("tile").value = String(index);
      providerManager.getTilesArrayDirect()[index].centerInMap();
    }

    static prev() {
      let index = document.getElementById("tile").value;
      if (index === "") {
        index = "0";
      } else {
        const len = providerManager.getTilesLength();
        index = (((Number(index) - 1) % len) + len) % len; // don't ask
      }
      document.getElementById("tile").value = String(index);
      providerManager.getTilesArrayDirect()[index].centerInMap();
    }

    static next() {
      let index = document.getElementById("tile").value;
      if (index === "") {
        index = "0";
      } else {
        index = (Number(index) + 1) % providerManager.getTilesLength();
      }
      document.getElementById("tile").value = String(index);
      providerManager.getTilesArrayDirect()[index].centerInMap();
    }
  }

  // Expose to window for inline HTML handlers
  window.Tile = Tile;

  console.log('✅ Tile module loaded');

})();
