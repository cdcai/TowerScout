// TowerScout - AzureMap Module
// Azure Maps provider implementation
// TASK-038 Stage 3: Extracted from monolithic towerscout.js

(function () {
  'use strict';

  class AzureMap extends TSMap {
    constructor() {
      super();
      // Check if Azure Maps SDK is available
      if (typeof atlas === 'undefined') {
        throw new Error('Azure Maps SDK not loaded. Please ensure the Azure Maps scripts are loaded before initializing the map.');
      }

      if (typeof atlas.Map === 'undefined') {
        throw new Error('Azure Maps Map class not available. Please check Azure Maps SDK loading.');
      }

      console.log('Azure Maps SDK loaded, initializing with subscription key authentication...');

      this.boundaries = [];
      this.newShapes = [];
      this.drawingManager = null;
      this.drawingContext = null; // Track drawing context: 'search' or 'manual'
      this.drawingNotificationId = null; // Track persistent notification
      this.searchDataSource = null;
      this.subscriptionKey = null;
      this.map = null; // Will be initialized after getting API key
      this.mapEventListeners = []; // Track map-specific event listeners for cleanup

      // TASK-041 Phase 2 Step 2.1: Track created shapes for explicit cleanup
      this.activeShapes = {
        circles: [],      // Circle boundaries created via circle tool
        polygons: [],     // Polygon boundaries drawn by user
        markers: []       // Future: detection result markers
      };

      this.initializationPromise = this.initializeWithSubscriptionKey();
    }

    async initializeWithSubscriptionKey() {
      try {
        // Fetch Azure Maps subscription key from backend
        console.log('🔑 Fetching Azure Maps subscription key...');
        const response = await fetch('/getazurekey');

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (!data.subscriptionKey) {
          throw new Error('Azure Maps subscription key not available: ' + (data.message || 'Unknown error'));
        }

        this.subscriptionKey = data.subscriptionKey;
        console.log('✅ Azure Maps subscription key loaded, initializing map...');

        // Validate subscription key format
        if (this.subscriptionKey.length < 20 || !this.subscriptionKey.match(/^[A-Za-z0-9\-_]+$/)) {
          console.warn('⚠️ Subscription key format may be invalid:', this.subscriptionKey.substring(0, 8) + '...');
        }

        // Now initialize Azure Maps with proper authentication and error recovery
        this.map = new atlas.Map('azureMap', {
          center: [nyc[0], nyc[1]], // Azure Maps uses [longitude, latitude] order
          zoom: 14,
          maxZoom: 21,
          // Use satellite style for cooling tower detection with fallback
          style: 'satellite',
          authOptions: {
            authType: 'subscriptionKey',
            subscriptionKey: this.subscriptionKey
          },
          // Enable features needed for satellite imagery
          traffic: false,                // Keep traffic disabled for performance
          showBuildingModels: false,     // Disable 3D buildings for performance
          showPointsOfInterest: false,   // Keep POI disabled for cleaner view
          showRoadLabels: false,         // Disable road labels over satellite imagery
          enableAccessibility: false     // Simplify for performance
        });

        // Force resize after map loads to ensure proper container sizing
        this.map.events.addOnce('ready', () => {
          console.log('✅ Azure Maps ready, forcing resize...');

          // Basic container sizing
          const container = document.getElementById('azureMap');
          if (container) {
            container.style.width = '100%';
            container.style.height = '100%';
            container.style.position = 'relative';
          }

          this.map.resize();
          console.log('✅ Azure Maps container resized');

          // Validate style loaded correctly
          this.validateStyleLoading();
        });

        // Add style error recovery
        this.map.events.add('styleimagemissing', (e) => {
          console.warn('⚠️ Azure Maps style image missing:', e);
        });

        console.log('✅ Azure Maps instance created with subscription key authentication');
        return this.setupMapEvents();
      } catch (error) {
        console.error('❌ Azure Maps initialization failed:', error);
        console.error('Azure provider available:', !!aak); // aak is boolean flag

        // Enhanced error reporting
        if (error.message && error.message.includes('401')) {
          console.error('🔑 Authentication Error: Subscription key may be invalid or expired');
        } else if (error.message && error.message.includes('fetch')) {
          console.error('🌐 Network Error: Unable to fetch subscription key from backend');
        }

        throw new Error('Failed to create Azure Maps instance: ' + error.message);
      }
    }

    validateStyleLoading() {
      try {
        // Check if satellite style loaded correctly
        const currentStyle = this.map.getStyle();
        console.log('🗺️ Azure Maps current style:', currentStyle ? currentStyle.name || 'unknown' : 'none');

        if (!currentStyle || currentStyle.name !== 'satellite') {
          console.warn('⚠️ Satellite style may not have loaded correctly, attempting fallback...');

          // Try to switch back to satellite style
          setTimeout(() => {
            try {
              this.map.setStyle('satellite');
              console.log('🔄 Attempted to reload satellite style');
              // TASK-041 Phase 1: Mark style loaded after successful reload
              providerManager.markInitialized('azure', 'styleLoaded');
            } catch (styleError) {
              console.error('❌ Failed to reload satellite style:', styleError);
              console.log('📍 Using default style as fallback');
              // Mark as loaded anyway to not block other operations
              providerManager.markInitialized('azure', 'styleLoaded');
            }
          }, 1000);
        } else {
          console.log('✅ Satellite style loaded successfully');
          // TASK-041 Phase 1: Mark style loaded
          providerManager.markInitialized('azure', 'styleLoaded');
        }
      } catch (validationError) {
        console.warn('⚠️ Style validation error (non-critical):', validationError);
        // Mark as loaded anyway to not block other operations
        providerManager.markInitialized('azure', 'styleLoaded');
      }
    }

    setupMapEvents() {
      // Add error event handling
      this.map.events.add('error', (e) => {
        // Improved error logging to show actual error details
        let errorMsg = 'Unknown error';
        if (e && e.error) {
          if (typeof e.error === 'string') {
            errorMsg = e.error;
          } else if (e.error.message) {
            errorMsg = e.error.message;
          } else {
            try {
              errorMsg = JSON.stringify(e.error, null, 2);
            } catch (jsonError) {
              errorMsg = e.error.toString();
            }
          }
        } else if (e && e.message) {
          errorMsg = e.message;
        }

        console.error('Azure Maps error:', errorMsg);
        console.error('Full error object:', e);

        // Provide helpful error messages for common issues
        if (errorMsg.includes('401') || errorMsg.includes('Unauthorized')) {
          console.error('Authentication Error: Invalid or missing Azure Maps subscription key');
          console.error('Azure provider available:', !!aak); // aak is boolean flag
        } else if (errorMsg.includes('403') || errorMsg.includes('Forbidden')) {
          console.error('Permission Error: Subscription key may not have access to requested service');
        } else if (errorMsg.includes('traffic') || errorMsg.includes('tileset')) {
          console.warn('Service Access Error: Trying fallback configuration...');
          // Could implement fallback logic here
        }
      });

      // Wait for Azure Maps to be ready before initializing drawing tools
      this.map.events.add('ready', () => {
        console.log('Azure Maps ready event fired');

        // Azure Maps already initialized with satellite style
        console.log('Azure Maps initialized with satellite style for optimal detection performance');

        this.initializeDrawingTools();
        this.initializeSearchBox();
        this.initializeAzureSearch();
      });

      // Add view change event for Azure-specific functionality
      this.map.events.add('moveend', () => {
        // Azure Maps doesn't need to bias Google's search box
        // Azure Maps uses native search that auto-biases to current viewport
        console.log('Azure Maps view changed - native search automatically biased');
      });

      return this.map;
    }

    initializeDrawingTools(retryCount = 0) {
      // Check if drawing SDK is available
      if (typeof atlas.drawing === 'undefined') {
        if (retryCount >= CONFIG.DRAWING_TOOLS_MAX_RETRIES) {
          console.error('❌ Azure Maps Drawing SDK failed to load after maximum retries');
          return;
        }
        console.warn(`Azure Maps Drawing SDK not loaded yet, retrying in ${CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS}ms... (attempt ${retryCount + 1}/${CONFIG.DRAWING_TOOLS_MAX_RETRIES})`);
        timerManager.setTimeout(() => this.initializeDrawingTools(retryCount + 1), CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS);
        return;
      }

      if (typeof atlas.drawing.DrawingManager === 'undefined' || typeof atlas.control.DrawingToolbar === 'undefined') {
        if (retryCount >= CONFIG.DRAWING_TOOLS_MAX_RETRIES) {
          console.error('❌ Azure Maps DrawingManager or DrawingToolbar failed to load after maximum retries');
          return;
        }
        console.warn(`Azure Maps DrawingManager or DrawingToolbar not available, retrying in ${CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS}ms... (attempt ${retryCount + 1}/${CONFIG.DRAWING_TOOLS_MAX_RETRIES})`);
        timerManager.setTimeout(() => this.initializeDrawingTools(retryCount + 1), CONFIG.DRAWING_TOOLS_RETRY_DELAY_MS);
        return;
      }

      console.log('Initializing Azure Maps drawing tools...');

      // Create drawing manager with polygon, rectangle, and edit tools
      // TASK-041 Phase 1: Added edit controls for better polygon completion UX
      // TASK-033 Phase 2: Added purple styling for manual tower polygons
      this.drawingManager = new atlas.drawing.DrawingManager(this.map, {
        toolbar: new atlas.control.DrawingToolbar({
          position: 'top-right',
          style: 'light',
          buttons: ['draw-polygon', 'draw-rectangle', 'edit-geometry'],
          numColumns: 3
        }),
        // Configure purple styling for manual tower polygons (distinct from green search boundaries)
        fillColor: '#800080',
        strokeColor: '#800080',
        fillOpacity: 0.1,
        strokeWidth: 2
      });

      // Track drawing context for notification management
      this.drawingContext = null; // 'search' or 'manual'
      this.drawingNotificationId = null;

      // Listen for drawing mode changes to show instructions when user clicks drawing tools
      this.map.events.add('drawingmodechanged', this.drawingManager, (mode) => {
        console.log('🎨 Azure Maps drawing mode changed:', mode);

        if (mode === 'draw-polygon' || mode === 'draw-rectangle') {
          // User clicked drawing tool - show persistent instructions
          console.log('📝 Drawing started, showing persistent instructions...');

          // Determine context: search boundary (no detections yet) or manual tower (after detection)
          const hasDetections = window.providerManager && window.providerManager.getDetectionsLength() > 0;
          this.drawingContext = hasDetections ? 'manual' : 'search';
          console.log('📍 Drawing context:', this.drawingContext, '(detections:', hasDetections ? 'YES' : 'NO', ')');

          // Show persistent notification with provider-specific instructions
          const message = this.drawingContext === 'search'
            ? 'Draw your search area. Double-click to complete the polygon.'
            : 'Draw around the tower. Double-click to complete the polygon.';

          this.drawingNotificationId = TowerScoutErrorHandler.showUserNotification(
            message,
            'info',
            0 // Persistent until drawing completes (0 = no timeout)
          );
        } else if (mode === 'idle' || mode === 'edit-geometry') {
          // Drawing ended or switched to edit mode - clear persistent notification
          if (this.drawingNotificationId) {
            TowerScoutErrorHandler.dismissNotification(this.drawingNotificationId);
            this.drawingNotificationId = null;
          }
        }
      });

      // Listen for drawing completion events
      this.map.events.add('drawingcomplete', this.drawingManager, (drawingCompleteEvent) => {
        console.log('🎨 Azure Maps drawingcomplete event fired');
        let shape = drawingCompleteEvent;

        // Dismiss persistent drawing instruction notification
        if (this.drawingNotificationId) {
          TowerScoutErrorHandler.dismissNotification(this.drawingNotificationId);
          this.drawingNotificationId = null;
        }

        // TASK-033: Azure Maps passes the shape directly, not as drawingCompleteEvent.data
        // The shape is an atlas.Shape object which doesn't have getType() function
        if (!shape) {
          console.warn('⚠️ No shape data from drawing event, ignoring');
          return;
        }

        this.newShapes.push(shape);
        console.log('✅ New Azure Maps shape captured');
        console.log('  - Total shapes in newShapes array:', this.newShapes.length);

        // Context-aware completion notification
        const message = this.drawingContext === 'search'
          ? 'Polygon complete! Click "Custom Shape" again to use as search area, or "Estimate Tiles" to proceed.'
          : 'Polygon complete! Click "Save Towers" button below to add it to the detection list.';

        TowerScoutErrorHandler.showUserNotification(
          message,
          'success',
          6000
        );

        // Reset context
        this.drawingContext = null;
      });

      // TASK-041 Phase 1: Mark drawing manager ready
      providerManager.markInitialized('azure', 'drawingManagerReady');
      console.log('✅ Azure Maps drawing tools initialized');
    }

    initializeSearchBox() {
      // TASK-039: Ensure standard search input is visible for Azure Maps
      const searchInput = document.getElementById('search');
      if (searchInput) {
        searchInput.style.display = 'inline';
        console.log('✅ Standard search input shown for Azure Maps');
      }

      // Create data source for search results
      this.searchDataSource = new atlas.source.DataSource();
      this.map.sources.add(this.searchDataSource);

      // Create data source for detection rectangles
      this.detectionDataSource = new atlas.source.DataSource();
      this.map.sources.add(this.detectionDataSource);

      // TASK-041 Phase 1: Mark data source ready
      providerManager.markInitialized('azure', 'dataSourceReady');
      console.log('✅ Azure Maps data sources initialized');

      // Add layer for search result markers (only for point features, not boundaries)
      this.map.layers.add(new atlas.layer.BubbleLayer(this.searchDataSource, null, {
        strokeColor: 'blue',
        strokeWidth: 2,
        fillColor: 'transparent',
        filter: ['==', ['geometry-type'], 'Point']
      }));

      // Add polygon layer for boundary visualization (transparent fill for clean map view)
      this.map.layers.add(new atlas.layer.PolygonLayer(this.searchDataSource, null, {
        fillColor: 'transparent',
        fillOpacity: 0,
        filter: ['==', ['get', 'type'], 'boundary']
      }));

      // Add line layer for boundary outlines (blue to match Google Maps styling)
      this.map.layers.add(new atlas.layer.LineLayer(this.searchDataSource, null, {
        strokeColor: 'blue',
        strokeWidth: 2,
        filter: ['==', ['get', 'type'], 'boundary']
      }));

      // Add polygon layer for detection rectangles with dynamic styling
      this.detectionPolygonLayer = new atlas.layer.PolygonLayer(this.detectionDataSource, null, {
        fillColor: [
          'case',
          ['has', 'fillColor'], ['get', 'fillColor'],
          'rgba(255, 0, 0, 0.2)' // default
        ],
        fillOpacity: [
          'case',
          ['has', 'opacity'], ['get', 'opacity'],
          0.2 // default
        ]
      });
      this.map.layers.add(this.detectionPolygonLayer);

      // Add line layer for detection rectangle outlines with dynamic styling
      this.detectionLineLayer = new atlas.layer.LineLayer(this.detectionDataSource, null, {
        strokeColor: [
          'case',
          ['has', 'strokeColor'], ['get', 'strokeColor'],
          'rgba(255, 0, 0, 1.0)' // default
        ],
        strokeWidth: 1
      });
      this.map.layers.add(this.detectionLineLayer);

      // FIX NEW-ISSUE-004: Add click event handler for detection shapes
      // Azure Maps filters out functions from shape properties, so we look up Detection by ID
      this.map.events.add('click', this.detectionPolygonLayer, (e) => {
        if (e.shapes && e.shapes.length > 0) {
          const shape = e.shapes[0];

          // Handle both Shape objects (with .getProperties()) and Feature objects (with .properties)
          const props = (typeof shape.getProperties === 'function')
            ? shape.getProperties()
            : shape.properties;

          if (props && props.detectionId !== undefined) {
            // Look up Detection object by ID from global array
            const detection = providerManager.getDetectionsArrayDirect()[props.detectionId];
            if (detection) {
              console.log(`🖱️ Azure Maps detection ${props.detectionId} clicked - triggering highlight`);
              detection.highlight(true, true);  // Call Detection.highlight() directly
            } else {
              console.warn(`⚠️ Clicked detection ${props.detectionId} but Detection object not found`);
            }
          } else {
            console.warn('⚠️ Click detected but shape has no detectionId:', props);
          }
        }
      });

      console.log('✅ Azure Maps: Detection DataSource and layers initialized');

      // Initialize Azure-native search for this provider
      this.initializeAzureSearch();
    }

    initializeAzureSearch() {
      // Prevent duplicate initialization
      if (this.searchInitialized) {
        console.log('⚠️ Azure search already initialized, skipping...');
        return;
      }

      console.log('Initializing Azure-native search system');
      this.searchInitialized = true;

      // Store reference to search input for Azure-specific handling
      this.searchInput = document.getElementById("search");

      // Use already-loaded subscription key from initialization
      if (this.subscriptionKey) {
        console.log('Using pre-loaded Azure Maps subscription key for search');

        // Initialize Azure Maps search with proper authentication
        if (typeof atlas.service !== 'undefined' && typeof atlas.service.SearchURL !== 'undefined') {
          this.searchURL = new atlas.service.SearchURL(atlas.service.MapsURL.newPipeline(
            new atlas.service.SubscriptionKeyCredential(this.subscriptionKey)
          ));
          console.log('Azure Maps Search service initialized with authentication');
        }
      } else {
        console.warn('Azure Maps subscription key not available for search initialization');
      }

      // Disable Google Places autocomplete when Azure is active
      this.disableGooglePlacesWhenActive();
    }

    updateMapAuthentication() {
      // Update map authentication from anonymous to subscription key
      if (this.map && this.subscriptionKey) {
        console.log('Updating Azure Maps authentication to use subscription key');

        // Set authentication for the map instance
        this.map.setAuthenticationOptions({
          authType: 'subscriptionKey',
          subscriptionKey: this.subscriptionKey
        });
      }
    }

    disableGooglePlacesWhenActive() {
      // Critical fix: Disable Google Places SearchBox when Azure is active
      const searchInput = document.getElementById('search');

      // Remove Google Places classes and listeners when Azure is selected
      if (currentProvider === 'azure') {
        console.log('🔧 Completely disabling Google Places for Azure Maps');

        // Remove Google Places autocomplete classes
        searchInput.classList.remove('pac-target-input');

        // Remove Google Places autocomplete attribute
        searchInput.removeAttribute('autocomplete');
        searchInput.setAttribute('autocomplete', 'off');

        // Hide Google Places autocomplete dropdown
        const pacContainer = document.querySelector('.pac-container');
        if (pacContainer) {
          pacContainer.style.display = 'none';
          pacContainer.style.visibility = 'hidden';
        }

        // Clear any existing Google Places listeners
        const newInput = searchInput.cloneNode(true);
        searchInput.parentNode.replaceChild(newInput, searchInput);

        // CRITICAL: Update global input reference to new element
        input = document.getElementById('search');

        // Re-add the Azure Maps event listener to the new input
        eventManager.addEventListener(input, 'keypress', function (e) {
          if (e.key === 'Enter') {
            handleGlobalSearch();
          }
        });

        // Set Azure Maps placeholder
        input.setAttribute('placeholder', 'Search with Azure Maps...');

        console.log('✅ Google Places completely disabled, Azure Maps search active');
      }
    }

    addSearchResultMarker(result) {
      // Add a marker for search results with proper Azure coordinates
      const lng = result.position.lon;
      const lat = result.position.lat;

      // Clear previous search markers
      this.searchDataSource.clear();

      // Create marker using Azure Maps Point with [lng, lat] format
      const searchMarker = new atlas.data.Feature(
        new atlas.data.Point([lng, lat]),
        {
          title: result.address.freeformAddress || 'Search Result',
          description: `${result.address.municipality || ''} ${result.address.countrySubdivision || ''}`.trim(),
          searchResult: true,
          confidence: result.score || 1.0
        }
      );

      this.searchDataSource.add(searchMarker);

      // Log search result details instead of showing popup
      const address = result.address || {};
      console.log('🎯 Search Result Details:', {
        location: address.freeformAddress || 'Search Result',
        municipality: address.municipality || '',
        region: address.countrySubdivision || '',
        confidence: Math.round((result.score || 0) * 100) + '%',
        coordinates: [lng, lat]
      });

      console.log(`Added Azure Maps search marker at [${lng}, ${lat}]`);
      return searchMarker;
    }

    getBounds() {
      // Force map to update camera state before retrieving bounds
      this.map.resize();
      let bounds = this.map.getCamera().bounds;
      return [
        bounds[0], // west
        bounds[3], // north  
        bounds[2], // east
        bounds[1]  // south
      ];
    }

    getCenter() {
      // Get current map center from Azure Maps camera
      const camera = this.map.getCamera();
      const center = camera.center;

      // Ensure we have valid coordinates
      if (!center || !Array.isArray(center) || center.length < 2) {
        console.warn('⚠️ Invalid camera center, using default');
        return [0, 0];
      }

      const result = [center[0], center[1]]; // [lng, lat]
      console.log('🎯 Azure Maps getCenter() - camera center:', center, '→ result:', result);
      return result;
    }

    fitBounds(b) {
      // Convert bounds to Azure Maps format [west, south, east, north]
      this.map.setCamera({
        bounds: [b[0], b[3], b[2], b[1]],
        padding: 50
      });
    }

    setCenter(c) {
      this.map.setCamera({
        center: [c[0], c[1]] // Azure Maps uses [lng, lat]
      });
    }

    getZoom() {
      return this.map.getCamera().zoom;
    }

    setZoom(z) {
      this.map.setCamera({
        zoom: z
      });
    }

    fitCenter() {
      this.fitBounds(this.getBounds());
    }

    async search(place) {
      console.log('Azure Maps search for:', place);

      if (!this.searchURL) {
        console.error('Azure Maps Search service not initialized');
        return;
      }

      try {
        console.log('Performing Azure Maps search...');
        const results = await this.searchURL.searchAddressReverse(
          atlas.service.Aborter.none,
          [0, 0], // This will be replaced with proper query
          {
            query: place,
            limit: 1,
            language: 'en-US'
          }
        );

        if (results && results.results && results.results.length > 0) {
          const result = results.results[0];
          console.log('Azure Maps search result:', result);

          // Add search marker and center map
          this.addSearchResultMarker(result);

          // Center and zoom map to result
          const position = [result.position.lon, result.position.lat];
          this.map.setCamera({
            center: position,
            zoom: 18,
            duration: 1000
          });

          return result;
        } else {
          console.warn('No Azure Maps search results found for:', place);
        }
      } catch (error) {
        console.error('Azure Maps search error:', error);
        throw error;
      }
    }

    biasSearchBox() {
      // Azure Maps does not need to bias Google's SearchBox
      // Azure Maps uses native search that is automatically biased to current viewport
      console.log('Azure Maps search bias not needed - using native Azure search');

      // Optional: Could add Azure-specific search viewport biasing here if needed
      // For now, Azure Maps native search provides proper geographic relevance
    }

    makeMapRect(o, listener) {
      // Create a rectangle overlay for detection results
      // CRITICAL: Azure Maps Polygon expects [longitude, latitude] order
      // TowerScout uses x=longitude, y=latitude, so [o.x1, o.y1] is correct
      let rectangle = new atlas.data.Polygon([[
        [o.x1, o.y1], // top-left: [lng, lat]
        [o.x1, o.y2], // bottom-left: [lng, lat]
        [o.x2, o.y2], // bottom-right: [lng, lat]
        [o.x2, o.y1], // top-right: [lng, lat]
        [o.x1, o.y1]  // close polygon
      ]]);

      // Handle detection ID - may be undefined if called before ID assignment
      const detectionId = (o.id !== undefined) ? o.id : 'pending';

      // FIX NEW-ISSUE-003: Use separate opacity properties for fill and stroke
      let feature = new atlas.data.Feature(rectangle, {
        type: 'detection',
        confidence: o.confidence || 0,
        strokeColor: o.color || '#FF0000',
        fillColor: o.fillColor || '#FF0000',
        fillOpacity: o.opacity || 0.5,
        strokeOpacity: 1.0,
        detectionId: detectionId
      });

      // Store reference for later updates
      o.azureFeature = feature;

      // Skip rendering for tiles - they're data objects only, not visual elements
      const isTile = o.classname === 'tile';

      // FIX NEW-ISSUE-004: Don't add shapes here - let updateMapRect() be the single source of truth
      // This prevents Feature/Shape type mismatches and ensures click listeners work correctly
      if (!isTile) {
        // Calculate box dimensions for debugging coordinate precision
        const widthDeg = Math.abs(o.x2 - o.x1);
        const heightDeg = Math.abs(o.y1 - o.y2);
        const widthMeters = widthDeg * 111320 * Math.cos(o.y1 * Math.PI / 180); // approximate meters
        const heightMeters = heightDeg * 110540; // approximate meters

        console.log(`\ud83c\udfed makeMapRect: Created Feature ${detectionId} (listener stored: ${typeof o.clickListener}, NOT added to data source)`);
        console.log(`  Coordinates: [${o.x1.toFixed(6)}, ${o.y1.toFixed(6)}] to [${o.x2.toFixed(6)}, ${o.y2.toFixed(6)}]`);
        console.log(`  Box size: ${widthMeters.toFixed(1)}m x ${heightMeters.toFixed(1)}m`);

        // Warn if detection is suspiciously small (< 10m)
        if (widthMeters < 10 || heightMeters < 10) {
          console.warn(`⚠️ Detection ${detectionId} is very small (${widthMeters.toFixed(1)}m x ${heightMeters.toFixed(1)}m) - possible coordinate transformation issue`);
        }
      } else if (isTile) {
        console.log(`Tile ${detectionId} created for metadata (not rendered on map)`);
      }

      // Handle click listener if provided
      if (listener) {
        // Store listener on the detection object for access in updateMapRect()
        o.clickListener = listener;
      }

      return feature;
    }

    updateMapRect(o, onoff) {
      // Show or hide detection rectangle using style-based visibility (opacity)
      // FIX NEW-ISSUE-003: Use opacity instead of add/remove to prevent duplicate shapes

      if (!this.detectionDataSource) {
        console.warn(`⚠️ Azure Maps data source not initialized`);
        return;
      }

      // Skip tiles - they're metadata only, not visual elements
      const isTile = o.classname === 'tile';
      if (isTile) {
        return;
      }

      // Handle detection ID - may be undefined if called before ID assignment
      const detectionId = (o.id !== undefined) ? o.id : 'pending';

      // Find existing shape by detection ID (shapes are atlas.Shape instances, not features)
      const shapes = this.detectionDataSource.getShapes();
      const existingShapes = shapes ? shapes.filter(s => {
        const props = s.getProperties();
        return props && props.detectionId === detectionId;
      }) : [];

      if (existingShapes.length > 0) {
        // REUSE EXISTING SHAPE - just change opacity and border visibility
        const shape = existingShapes[0];

        if (onoff === false || !onoff) {
          // HIDE: Set opacity to 0 and make border transparent
          console.log(`🔴 Hiding detection ${detectionId} (opacity=0, transparent border)`);
          shape.setProperties({
            detectionId: detectionId,  // MUST preserve ID
            fillOpacity: 0.0,
            strokeColor: 'transparent',
            strokeWidth: 0
          });
        } else {
          // SHOW: Restore opacity and colors
          console.log(`🟢 Showing detection ${detectionId} (opacity=0.5, visible border)`);
          shape.setProperties({
            detectionId: detectionId,  // MUST preserve ID
            fillColor: o.fillColor,
            strokeColor: o.color,
            fillOpacity: 0.5,
            strokeWidth: 2
          });
        }
        return; // IMPORTANT: Exit early, don't create new shape
      }

      // Create NEW shape ONLY if it doesn't exist AND should be visible
      if (onoff) {
        // Create polygon geometry
        const polygon = new atlas.data.Polygon([[
          [o.x1, o.y1], // top-left: [lng, lat]
          [o.x1, o.y2], // bottom-left: [lng, lat]
          [o.x2, o.y2], // bottom-right: [lng, lat]
          [o.x2, o.y1], // top-right: [lng, lat]
          [o.x1, o.y1]  // close polygon
        ]]);

        // Create shape with detectionId property (click handler will look up Detection by ID)
        const shape = new atlas.Shape(polygon, null, {
          detectionId: detectionId,
          fillColor: o.fillColor,
          strokeColor: o.color,
          fillOpacity: 0.5,
          strokeWidth: 2
        });

        // Add to data source
        this.detectionDataSource.add(shape);

        // Store reference for future updates
        o.azureShape = shape;
      }
    }

    colorMapRect(o, color) {
      // Update rectangle color for highlighting
      // FIX NEW-ISSUE-005: Use setProperties() to properly update shape colors without mixing
      if (!this.detectionDataSource) {
        console.warn(`⚠️ Azure Maps data source not initialized`);
        return;
      }

      // Handle detection ID
      const detectionId = (o.id !== undefined) ? o.id : 'pending';

      // Find the shape in the data source by detectionId
      const shapes = this.detectionDataSource.getShapes();
      const existingShapes = shapes ? shapes.filter(s => {
        const props = (typeof s.getProperties === 'function')
          ? s.getProperties()
          : s.properties;
        return props && props.detectionId === detectionId;
      }) : [];

      if (existingShapes.length === 0) {
        console.warn(`⚠️ Cannot color detection ${detectionId} - shape not found in data source`);
        return;
      }

      if (existingShapes.length > 1) {
        console.warn(`⚠️ Found ${existingShapes.length} shapes with detectionId ${detectionId} - using first one`);
      }

      const shape = existingShapes[0];

      // Determine if detection is selected (green) or unselected (red)
      const isSelected = (color === 'green' ||
        color === '#00FF00' ||
        color.toLowerCase().includes('0, 255, 0') ||
        color.toLowerCase().includes('0,255,0'));

      // FIX NEW-ISSUE-005: CRITICAL - Always preserve detectionId when calling setProperties()
      // Azure Maps setProperties() REPLACES all properties, doesn't merge
      // If we don't include detectionId, it gets cleared and future lookups fail

      // Update shape properties directly for immediate visual update
      if (isSelected) {
        // Selected: Pure green with higher opacity
        shape.setProperties({
          detectionId: detectionId,  // MUST preserve ID
          fillColor: 'rgba(0, 255, 0, 0.3)',
          strokeColor: 'green',
          fillOpacity: 0.3,
          strokeWidth: 2
        });
        console.log(`✅ Highlighted detection ${detectionId} with green (opacity: 0.3)`);
      } else {
        // Unselected: Red with standard opacity
        shape.setProperties({
          detectionId: detectionId,  // MUST preserve ID
          fillColor: 'rgba(255, 0, 0, 0.15)',
          strokeColor: o.color || '#FF0000',
          fillOpacity: 0.15,
          strokeWidth: 1
        });
        console.log(`🔴 Reset detection ${detectionId} to red (opacity: 0.15)`);
      }
    }

    resetBoundaries() {
      console.log('🧹 Azure Maps: Resetting boundaries...');

      // Use clear-and-rebuild pattern (proven reliable in Step 2.2)
      if (this.searchDataSource) {
        try {
          // Get all shapes from searchDataSource
          const allShapes = this.searchDataSource.getShapes();

          // Filter to keep only non-boundary shapes (like markers)
          const nonBoundaryShapes = allShapes.filter(feature => {
            const props = feature.getProperties();  // Use getProperties() method
            return !(props && props.type === 'boundary');
          });

          const boundaryCount = allShapes.length - nonBoundaryShapes.length;
          console.log(`✅ Removing ${boundaryCount} boundary shapes`);

          // Clear all shapes and re-add non-boundary shapes
          this.searchDataSource.clear();
          if (nonBoundaryShapes.length > 0) {
            this.searchDataSource.add(nonBoundaryShapes);
          }

        } catch (e) {
          console.warn('⚠️ Boundary removal failed, clearing all:', e.message);
          this.searchDataSource.clear();
        }
      }

      // Clear drawing manager's data source (polygons being drawn)
      if (this.drawingManager && this.drawingManager.getSource()) {
        this.drawingManager.getSource().clear();
      }

      // Clear activeShapes tracking
      this.activeShapes.circles = [];
      this.activeShapes.polygons = [];

      // Clear boundary tracking and release references
      if (this.boundaries && this.boundaries.length > 0) {
        const boundaryCount = this.boundaries.length;
        this.boundaries.forEach(b => {
          if (b) {
            b.azureObject = null; // Release reference to enable garbage collection
          }
        });
        console.log(`✅ Cleared ${boundaryCount} boundary references`);
      }
      this.boundaries = [];
      console.log('✅ Azure Maps boundaries reset complete');
    }

    clearCircles() {
      console.log(`🔄 Clearing ${this.activeShapes.circles.length} circle(s) from Azure Maps...`);

      if (this.activeShapes.circles.length === 0) {
        console.log('✅ No circles to clear');
        return;
      }

      // Step 1: Remove circle features from searchDataSource
      if (this.searchDataSource) {
        try {
          // Get all shapes from data source
          const allShapes = this.searchDataSource.getShapes();
          console.log(`  - searchDataSource BEFORE cleanup: ${allShapes.length} total shapes`);

          // Filter to separate circles from other shapes using PROPERTIES (not object references)
          // Object reference matching with .includes() doesn't work reliably with Azure Maps
          const circleShapes = [];
          const nonCircleShapes = [];

          allShapes.forEach(shape => {
            const props = shape.getProperties();
            // Check if this is a circle by looking at properties
            if (props && props.type === 'boundary' && props.isCircle === true) {
              circleShapes.push(shape);
            } else {
              nonCircleShapes.push(shape);
            }
          });

          console.log(`  - Circle shapes found: ${circleShapes.length}`);
          console.log(`  - Non-circle shapes to preserve: ${nonCircleShapes.length}`);

          // Clear entire data source
          this.searchDataSource.clear();
          console.log('  - Cleared all shapes from searchDataSource');

          // Re-add only non-circle shapes
          if (nonCircleShapes.length > 0) {
            this.searchDataSource.add(nonCircleShapes);
            console.log(`  - Re-added ${nonCircleShapes.length} non-circle shape(s)`);
          }

          // Verify final state
          const afterShapes = this.searchDataSource.getShapes();
          console.log(`  - searchDataSource AFTER cleanup: ${afterShapes.length} total shapes`);
          console.log('  - ✅ Circle removal complete');

        } catch (e) {
          console.warn('  - Failed to clear circles:', e.message);
          console.error('  - Error details:', e);
        }
      }

      // Step 2: Also clear from drawing manager's data source (Azure Maps keeps separate sources)
      if (this.drawingManager) {
        try {
          const drawingSource = this.drawingManager.getSource();
          console.log('  - Drawing manager source exists:', !!drawingSource);

          if (drawingSource) {
            // Get all shapes from drawing source and remove circles
            const allShapes = drawingSource.getShapes();
            console.log(`  - Total shapes in drawing source: ${allShapes.length}`);

            const circleShapes = allShapes.filter(shape => {
              const props = shape.getProperties();
              console.log('  - Shape properties:', props);
              return props && props.type === 'boundary' && props.isCircle;
            });

            console.log(`  - Circle shapes found in drawing source: ${circleShapes.length}`);

            if (circleShapes.length > 0) {
              drawingSource.remove(circleShapes);
              console.log(`  - Removed ${circleShapes.length} circle(s) from drawing manager source`);
            } else {
              // If no circles found by properties, try removing ALL shapes and re-add non-circles
              console.log('  - No circles found with properties, trying comprehensive clear...');
              const nonCircleBoundaries = this.boundaries.filter(b => !b.isCircle);

              // Clear everything from drawing source
              drawingSource.clear();
              console.log('  - Cleared all shapes from drawing manager source');

              // Re-add non-circle boundaries if any
              if (nonCircleBoundaries.length > 0) {
                console.log(`  - Re-adding ${nonCircleBoundaries.length} non-circle boundaries`);
              }
            }
          }
        } catch (e) {
          console.warn('  - Failed to clear circles from drawing manager:', e.message);
          console.error('  - Full error:', e);
        }
      }

      // Step 3: Filter circles from boundaries array
      const beforeCount = this.boundaries.length;
      this.boundaries = this.boundaries.filter(b => !b.isCircle);
      const removedCount = beforeCount - this.boundaries.length;
      console.log(`  - Removed ${removedCount} circle boundary reference(s)`);

      // Step 4: Clear tracking array
      const clearedCount = this.activeShapes.circles.length;
      this.activeShapes.circles = [];

      console.log(`✅ Cleared ${clearedCount} circle(s)`);
    }

    addBoundary(b) {
      // Safety check: Ensure searchDataSource is initialized
      if (!this.searchDataSource) {
        console.warn('⚠️ Azure Maps searchDataSource not initialized yet, initializing now');
        // Initialize if not ready (fallback)
        this.searchDataSource = new atlas.source.DataSource();
        this.map.sources.add(this.searchDataSource);

        // Add all the necessary layers since initializeSearchBox wasn't called
        console.log('Adding missing layers for boundary display');

        // Add layer for search result markers (only for point features, not boundaries)
        this.map.layers.add(new atlas.layer.BubbleLayer(this.searchDataSource, null, {
          strokeColor: 'blue',
          strokeWidth: 2,
          fillColor: 'transparent',
          filter: ['==', ['geometry-type'], 'Point']
        }));

        // Add polygon layer for boundary visualization (transparent fill for clean map view)
        this.map.layers.add(new atlas.layer.PolygonLayer(this.searchDataSource, null, {
          fillColor: 'transparent',
          fillOpacity: 0,
          filter: ['==', ['get', 'type'], 'boundary']
        }));

        // Add line layer for boundary outlines (blue to match Google Maps styling)
        this.map.layers.add(new atlas.layer.LineLayer(this.searchDataSource, null, {
          strokeColor: 'blue',
          strokeWidth: 2,
          filter: ['==', ['get', 'type'], 'boundary']
        }));
      }

      // Add boundary polygon to the map
      let coordinates;

      if (b.type === 'simple') {
        // Rectangle boundary: [x1, y1, x2, y2]
        coordinates = [[[b.x1, b.y1], [b.x1, b.y2], [b.x2, b.y2], [b.x2, b.y1], [b.x1, b.y1]]];
      } else {
        // Polygon boundary: array of [lng, lat] pairs
        coordinates = [b.points.concat([b.points[0]])]; // Close the polygon
      }

      let polygon = new atlas.data.Polygon(coordinates);
      let feature = new atlas.data.Feature(polygon, {
        type: 'boundary',
        isCircle: b.isCircle || false  // TASK-041: Mark circles for property-based filtering
      });

      b.azureObject = feature;
      this.searchDataSource.add(feature);
      this.boundaries.push(b);

      // TASK-041 Phase 2 Step 2.2: Track circle boundaries for cleanup
      if (b.isCircle) {
        this.activeShapes.circles.push(feature);
        console.log('  - Tracked circle in activeShapes (total:', this.activeShapes.circles.length + ')');
      }
    }

    hasNonCircleBoundaries() {
      return this.boundaries.some(boundary => !boundary.isCircle);
    }

    showBoundaries() {
      // Fit map to show all boundaries
      if (this.boundaries.length > 0) {
        let allCoordinates = [];
        for (let b of this.boundaries) {
          if (b.azureObject && b.azureObject.geometry) {
            let coords = b.azureObject.geometry.coordinates[0];
            allCoordinates = allCoordinates.concat(coords);
          }
        }

        if (allCoordinates.length > 0) {
          let bounds = atlas.data.BoundingBox.fromData(allCoordinates);
          this.map.setCamera({
            bounds: bounds,
            padding: 100
          });
        }
      }
    }

    retrieveDrawnBoundaries() {
      console.log('🔍 Retrieving drawn boundaries from Azure Maps...');
      console.log('  - newShapes array length:', this.newShapes.length);
      console.log('  - drawingManager exists:', !!this.drawingManager);

      let polys = [];

      // TASK-041 Debug: Check if drawing manager has shapes we didn't capture
      if (this.drawingManager) {
        const source = this.drawingManager.getSource();
        const allShapes = source.getShapes();
        console.log('  - Drawing manager source shapes:', allShapes.length);

        // If we have shapes in drawing manager but not in newShapes, use those
        if (allShapes.length > 0 && this.newShapes.length === 0) {
          console.log('  ⚠️ Found shapes in drawing manager that were not captured in event');
          this.newShapes = allShapes;
        }
      }

      for (let shape of this.newShapes) {
        console.log('  - Processing shape:', shape.getType());
        let geometry = shape.toJson().geometry;

        if (geometry.type === 'Polygon') {
          let coordinates = geometry.coordinates[0];
          let poly = [];
          for (let coord of coordinates) {
            poly.push([coord[0], coord[1]]); // [lng, lat]
          }
          console.log('  ✅ Created PolygonBoundary with', poly.length, 'points');
          polys.push(new PolygonBoundary(poly));
        } else if (geometry.type === 'Rectangle') {
          // Handle rectangle if Azure Maps provides this type
          let coords = geometry.coordinates[0];
          let minLng = Math.min(...coords.map(c => c[0]));
          let maxLng = Math.max(...coords.map(c => c[0]));
          let minLat = Math.min(...coords.map(c => c[1]));
          let maxLat = Math.max(...coords.map(c => c[1]));
          console.log('  ✅ Created SimpleBoundary (rectangle)');
          polys.push(new SimpleBoundary([minLng, maxLat, maxLng, minLat]));
        }
      }

      console.log('📊 Total boundaries retrieved:', polys.length);
      this.clearShapes();
      return polys;
    }

    hasShapes() {
      return this.newShapes.length !== 0;
    }

    addShapes() {
      console.log('🏗️ Azure Maps addShapes() called');
      console.log(`  - newShapes array length: ${this.newShapes.length}`);

      // TASK-033: Validation - Check if shapes exist
      if (this.newShapes.length === 0) {
        console.warn('⚠️ No shapes to add (newShapes array empty)');
        TowerScoutErrorHandler.showUserNotification(
          'Draw a polygon first. Click "Add Towers" to enable drawing, then click "Save Towers" to add detections.',
          'warning',
          4000
        );
        return;
      }

      // TASK-033: Validation - Check if model has been run (Tile_tiles populated)
      if (typeof Tile_tiles === 'undefined' || !Tile_tiles || Object.keys(Tile_tiles).length === 0) {
        console.error('❌ Cannot add manual towers: Model has not been run yet');
        TowerScoutErrorHandler.showUserNotification(
          'Please run a detection search first before adding manual towers',
          'error',
          4000
        );
        return;
      }

      // Process drawn shapes and add as detections
      let bounds;
      let addedCount = 0;

      for (let shape of this.newShapes) {
        let geometry = shape.toJson().geometry;

        // Calculate bounds for the shape
        let coordinates = geometry.coordinates[0];
        let lngs = coordinates.map(c => c[0]);
        let lats = coordinates.map(c => c[1]);

        let x1 = Math.min(...lngs);
        let x2 = Math.max(...lngs);
        let y1 = Math.max(...lats);
        let y2 = Math.min(...lats);

        // TASK-033 Phase 2: Create only ONE detection per drawn polygon (use center tile)
        // This prevents multiple detections when polygon spans tile boundaries
        let centerX = (x1 + x2) / 2;
        let centerY = (y1 + y2) / 2;
        let tileIds = Tile.getTileIds(centerX, centerY, centerX, centerY);

        if (tileIds.length > 0) {
          let tileArrayIndex = tileIds[0];
          let tile = providerManager.getTilesArrayDirect()[tileArrayIndex];
          // TASK-033 Phase 3: Use tile.id (not array index) for export matching
          let tileId = tile.id;

          // Clamp bounds to tile boundaries
          x1 = Math.max(x1, tile.x1);
          x1 = Math.min(x1, tile.x2);
          x2 = Math.max(x2, tile.x1);
          x2 = Math.min(x2, tile.x2);
          y1 = Math.max(y1, tile.y2);
          y1 = Math.min(y1, tile.y1);
          y2 = Math.max(y2, tile.y2);
          y2 = Math.min(y2, tile.y1);

          let det = new Detection(x1, y1, x2, y2,
            'added', 1.0, tileId, -1, true, true); // id_in_tile parameter

          // TASK-033: Geocode manual tower location to get address
          this.geocodeDetection(det);

          det.update();
          addedCount++;
        }
      }

      // TASK-033: Cleanup and user feedback
      this.newShapes = [];

      // Turn off drawing mode
      if (this.drawingManager) {
        this.drawingManager.setOptions({ mode: 'idle' });
      }

      Detection.generateList();
      adjustConfidence();

      // TASK-033 Phase 4: Lock provider switching after manual towers added
      if (typeof lockProviderSwitching === 'function') {
        lockProviderSwitching();
      }

      // TASK-033: User feedback
      console.log(`✅ Successfully added ${addedCount} manual tower(s)`);
      TowerScoutErrorHandler.showUserNotification(
        `Successfully added ${addedCount} manual tower(s)`,
        'success',
        3000
      );
    }

    // TASK-033: Geocode detection coordinates to get building address
    async geocodeDetection(detection) {
      try {
        const center = detection.getCenter();
        const lat = center[1];
        const lng = center[0];

        console.log(`🌍 Geocoding manual tower at ${lat}, ${lng}...`);

        const response = await fetch('/api/geocode/reverse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            lat: lat,
            lng: lng,
            provider: 'auto'
          })
        });

        if (!response.ok) {
          throw new Error(`Geocoding failed: ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.address) {
          detection.address = data.address;
          detection.addressConfidence = data.confidence;
          detection.addressProvider = data.provider;
          console.log(`✅ Geocoded address: ${data.address}`);
        } else {
          // Fallback to coordinates
          detection.address = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
          detection.addressConfidence = 0.0;
          detection.addressProvider = 'fallback';
          console.warn(`⚠️ Geocoding failed, using coordinates`);
        }

        // TASK-033: Update detection list to show the new address
        Detection.generateList();

      } catch (error) {
        console.error('❌ Geocoding error:', error);
        // Fallback to coordinates
        const center = detection.getCenter();
        detection.address = `${center[1].toFixed(6)}, ${center[0].toFixed(6)}`;
        detection.addressConfidence = 0.0;
        detection.addressProvider = 'error';

        // Update list even with fallback address
        Detection.generateList();
      }
    }

    clearShapes() {
      // Remove unsaved drawn polygons only
      // Note: To delete saved manual towers, uncheck them in the detection list
      // Clear all drawn shapes from newShapes array
      for (let shape of this.newShapes) {
        this.drawingManager.getSource().remove(shape);
      }
      this.newShapes = [];

      // TASK-033 Phase 2: Also clear all shapes from drawing manager layer
      // (Important: After "Save Towers", shapes are no longer in newShapes but remain in drawing layer)
      if (this.drawingManager) {
        const drawingSource = this.drawingManager.getSource();
        if (drawingSource) {
          const allDrawnShapes = drawingSource.getShapes();
          if (allDrawnShapes && allDrawnShapes.length > 0) {
            console.log(`🧹 Clearing ${allDrawnShapes.length} shapes from Azure drawing manager layer`);
            drawingSource.clear();
          }
        }
        // Turn off drawing mode
        this.drawingManager.setOptions({ mode: 'idle' });
      }
    }

    clearAll() {
      this.clearShapes();

      // TASK-033 Phase 2: Properly remove manual towers from map before removing from array
      // First hide all manual tower rectangles (conf=1.0) and remove from data source
      if (this.detectionDataSource) {
        const shapes = this.detectionDataSource.getShapes();
        const manualShapes = shapes.filter(s => {
          const props = s.getProperties();
          if (!props || props.detectionId === undefined) return false;
          const det = providerManager.getDetectionsArrayDirect()[props.detectionId];
          return det && det.conf === 1.0;
        });

        if (manualShapes.length > 0) {
          console.log(`🗑️ Removing ${manualShapes.length} manual tower shapes from Azure Maps`);
          this.detectionDataSource.remove(manualShapes);
        }
      }

      // Then remove manual detections from array
      let dets = [];
      for (let det of providerManager.getDetections()) {
        if (det.conf !== 1.0) {
          det.id = dets.length;
          dets.push(det);
        }
      }
      providerManager.setDetections(dets);
      // FIX NEW-ISSUE-003: generateList() now calls adjustConfidence() to filter outside detections
      Detection.generateList();

      // TASK-033 Phase 4: Unlock provider switching after clearing all manual towers
      if (typeof unlockProviderSwitching === 'function') {
        unlockProviderSwitching();
      }
    }

    getBoundsPolygon(query, place) {
      // Azure Maps native search integration - NO Google dependency
      this.resetBoundaries();

      console.log("Azure Maps native search for: " + query);

      // Use Azure Maps Search API directly with proper coordinate handling
      this.searchAddress(query).then(searchResults => {
        if (searchResults && searchResults.length > 0) {
          const result = searchResults[0]; // Use the first/best result

          // CRITICAL: Use native Azure Maps coordinates [lng, lat] directly
          const lng = result.position.lon;
          const lat = result.position.lat;

          console.log(`Azure Maps result: ${result.address.freeformAddress} at [${lng}, ${lat}]`);

          // Set map view to the search result using correct Azure coordinates
          console.log('🎯 Centering Azure Maps on search result:', [lng, lat]);
          console.log('🗺️ Map instance available:', !!this.map);

          // Use correct Azure Maps API methods
          if (this.map) {
            // Azure Maps proper centering method
            this.map.setCamera({
              center: [lng, lat],
              zoom: 17,
              type: 'fly',
              duration: 1500
            });

            console.log('🎯 Azure Maps setCamera called with fly animation');
          } else {
            console.error('❌ Azure Maps instance not available for centering');
          }

          // Clear any existing search markers and add new result marker
          const searchMarker = this.addSearchResultMarker(result);

          // USER JOURNEY FIX: Do NOT auto-create boundary on search
          // User should manually define search area using Circle or Polygon tools
          // This matches Google Maps behavior (center only, no auto-boundary)
          console.log('✅ Azure Maps search complete - map centered, no auto-boundary');
          console.log('💡 User can now define search area using Circle or Polygon tools');

          // Final verification of map center using proper Azure Maps methods
          setTimeout(() => {
            if (this.map) {
              try {
                const camera = this.map.getCamera();
                console.log('🔍 Final map state - Center:', camera.center, 'Zoom:', camera.zoom);
                console.log('🎯 Expected center:', [lng, lat]);

                // Verify the centering worked
                const actualCenter = camera.center;
                const expectedLng = lng;
                const expectedLat = lat;

                if (actualCenter && Math.abs(actualCenter[0] - expectedLng) < 0.01 && Math.abs(actualCenter[1] - expectedLat) < 0.01) {
                  console.log('✅ Map successfully centered on search result!');
                } else {
                  console.log('⚠️ Map centering may not have worked as expected');
                }
              } catch (error) {
                console.error('❌ Error checking map state:', error);
              }
            }
          }, 2000);

          // Note: Google Maps synchronization disabled when Azure is primary provider
          console.log('✅ Azure Maps search completed successfully');
        } else {
          console.warn("Azure Maps search returned no results for: " + query);
          // Show user-friendly message instead of silent fallback
          console.log('🔍 No results found for:', query);
          // Could add a non-intrusive notification here instead of alert
        }
      }).catch(error => {
        console.error("🐛 Azure Maps search error:", error.message || error);
        // Log error instead of showing alert popup
        console.warn('⚠️ Search request failed - this may be a temporary network issue');
      });
    }

    async searchAddress(query) {
      // Azure Maps Search API integration with enhanced error handling
      try {
        console.log('🔍 Azure Maps search request:', query);

        // Clean and prepare query for Azure Maps Search
        const cleanQuery = query.trim();

        // Use server-side proxy for Azure Maps search to protect API keys
        const url = `/api/maps/azure/search?query=${encodeURIComponent(cleanQuery)}&limit=5&countrySet=US`;

        const response = await fetch(url);

        console.log('🌐 Azure search proxy response status:', response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ Azure search proxy error:', response.status, errorText);

          if (response.status === 401) {
            throw new Error('Azure Maps authentication failed: Invalid subscription key');
          } else if (response.status === 403) {
            throw new Error('Azure Maps access denied: Subscription key lacks search permissions');
          } else if (response.status === 429) {
            throw new Error('Azure Maps rate limit exceeded');
          } else {
            throw new Error(`Azure Maps search failed: ${response.status} - ${errorText}`);
          }
        }

        const data = await response.json();
        console.log('✅ Azure Maps search results:', data.results ? data.results.length : 0, 'results found');

        if (data.results && data.results.length > 0) {
          console.log('📍 First result:', data.results[0].address?.freeformAddress || 'No address');
        }

        return data.results || [];
      } catch (error) {
        console.error('❌ Azure Maps search API error:', error.message || error);
        throw new Error(`Azure Maps search failed: ${error.message || error}`);
      }
    }

    // Memory Management: Cleanup Methods

    cleanupDrawingManager() {
      if (this.drawingManager) {
        console.log('🧹 Cleaning up Azure DrawingManager...');

        // Remove event listeners
        if (this.map && this.map.events) {
          this.map.events.remove('drawingcomplete', this.drawingManager);
        }

        // Clear drawn shapes
        try {
          const source = this.drawingManager.getSource();
          if (source) {
            source.clear();
          }
        } catch (e) {
          console.warn('⚠️ Error clearing drawing source:', e.message);
        }

        // Dispose drawing manager if method exists
        if (typeof this.drawingManager.dispose === 'function') {
          try {
            this.drawingManager.dispose();
          } catch (e) {
            console.warn('⚠️ Error disposing drawing manager:', e.message);
          }
        }

        this.drawingManager = null;
        console.log('✅ Azure DrawingManager cleaned up');
      }
    }

    cleanupMapListeners() {
      if (this.map && this.map.events && this.mapEventListeners.length > 0) {
        console.log(`🧹 Cleaning up ${this.mapEventListeners.length} Azure map listeners...`);

        for (const listener of this.mapEventListeners) {
          try {
            this.map.events.remove(listener.eventType, listener.handler);
          } catch (e) {
            console.warn(`⚠️ Error removing listener ${listener.eventType}:`, e.message);
          }
        }

        this.mapEventListeners = [];
        console.log('✅ Azure map listeners cleaned up');
      }
    }

    cleanupSearch() {
      console.log('🧹 Cleaning up Azure search infrastructure...');

      // Remove search result markers and boundaries
      if (this.searchDataSource) {
        try {
          this.searchDataSource.clear();

          // Remove layers that reference this data source
          if (this.map && this.map.layers) {
            const layers = this.map.layers.getLayers();
            if (layers && Array.isArray(layers)) {
              layers.forEach(layer => {
                try {
                  if (layer && typeof layer.getSource === 'function') {
                    const layerSource = layer.getSource();
                    if (layerSource === this.searchDataSource) {
                      this.map.layers.remove(layer);
                    }
                  }
                } catch (e) {
                  console.warn('⚠️ Error removing layer:', e.message);
                }
              });
            }
          }

          // Remove data source
          if (this.map && this.map.sources) {
            try {
              this.map.sources.remove(this.searchDataSource);
            } catch (e) {
              console.warn('⚠️ Error removing search data source:', e.message);
            }
          }

          this.searchDataSource = null;
        } catch (e) {
          console.warn('⚠️ Error during search cleanup:', e.message);
        }
      }

      // Clear SearchURL and reset initialization flag
      this.searchURL = null;
      this.searchInitialized = false;

      console.log('✅ Azure search infrastructure cleaned up');
    }

    cleanup() {
      console.log('🧹 Starting Azure Maps cleanup...');

      try {
        // 1. Cleanup drawing manager
        this.cleanupDrawingManager();

        // 2. Cleanup map event listeners
        this.cleanupMapListeners();

        // 3. Cleanup search infrastructure
        this.cleanupSearch();

        // 4. Reset boundaries
        this.resetBoundaries();

        // 5. Clear drawn shapes
        if (this.newShapes && this.newShapes.length > 0) {
          this.clearShapes();
        }

        console.log('✅ Azure Maps cleanup complete');
      } catch (error) {
        console.error('❌ Error during Azure Maps cleanup:', error);
        // Don't throw - allow cleanup to complete partially
      }
    }

    getBoundariesStr() {
      let result = [];
      for (let b of this.boundaries) {
        result.push(b.toString());
      }
      return "[" + result.join(",") + "]";
    }
  }

  // Export to window for global access (IIFE pattern)
  window.AzureMap = AzureMap;

  console.log('✅ AzureMap module loaded');
})();
