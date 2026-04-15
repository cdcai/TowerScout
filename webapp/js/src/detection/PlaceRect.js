// STAGE 4: PlaceRect - Base class for Detection and Tile
// Rectangles on the map (results, tiles, bounding boxes)
(function () {
    'use strict';

    class PlaceRect {

        constructor(x1, y1, x2, y2, color, fillColor, opacity, classname, listener, renderOnMap = true) {

            this.x1 = x1;
            this.y1 = y1;
            this.x2 = x2;
            this.y2 = y2;
            this.color = color;
            this.fillColor = fillColor;
            this.opacity = opacity;
            this.classname = classname;
            this.address = "<unknown address>";
            this.map = currentMap
            this.renderOnMap = renderOnMap !== false;
            this.mapRect = this.renderOnMap ? this.map.makeMapRect(this, listener) : null;
            // FIX NEW-ISSUE-003: Don't call update() here - let Detection call it after setting 'inside' property
            // this.update();  // Removed to prevent showing markers before boundary filtering
            this.listener = listener;
        }

        centerInMap() {
            // this.map.setCenter([(this.x1 + this.x2) / 2, (this.y1 + this.y2) / 2]);
            // currentMap.setZoom(19);
            const targetMap = currentMap || this.map || googleMap;
            if (targetMap && typeof targetMap.setCenter === 'function') {
                targetMap.setCenter([(this.x1 + this.x2) / 2, (this.y1 + this.y2) / 2]);
                if (typeof targetMap.setZoom === 'function') {
                    targetMap.setZoom(19);
                }
            }
        }

        getCenter() {
            return [(this.x1 + this.x2) / 2, (this.y1 + this.y2) / 2];
        }

        getCenterUrl() {
            let c = this.getCenter();
            return c[1] + "," + c[0];
        }

        augment(addr) {
            this.addrSpan.innerText = addr;
            this.address = addr;
            //window.TowerScoutLogger.debug("tower " + i + ": " + addr)
        }

        highlight(color) {
            if (!this.mapRect) {
                return;
            }
            currentMap.colorMapRect(this, color);
            setTimeout(() => {
                currentMap.colorMapRect(this, this.color);
            }, 5000);
        }

        update(newMap) {
            if (typeof newMap !== 'undefined') {
                if (this.mapRect) {
                    this.map.updateMapRect(this, false);
                }
                this.map = newMap;
                this.mapRect = this.renderOnMap ? newMap.makeMapRect(this, this.listener) : null;
            }
            // FIX NEW-ISSUE-003: Don't automatically show markers - let Detection.update() control visibility
            // this.map.updateMapRect(this, true);  // Removed - Detection subclass handles visibility logic
        }
    }

    // Expose PlaceRect to global scope for Detection and Tile classes
    window.PlaceRect = PlaceRect;

    window.TowerScoutLogger.debug('✅ PlaceRect base class loaded');
})();
