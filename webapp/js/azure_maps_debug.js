// Simplified Azure Maps Debug Class
// This replaces the complex AzureMap class temporarily for debugging

class AzureMapDebug {
    constructor() {
        console.log('🔧 [AZURE DEBUG] Constructor called');

        // Simple properties
        this.boundaries = [];
        this.newShapes = [];
        this.subscriptionKey = null;
        this.map = null;
        this.isInitialized = false;
        this.debugStep = 1;

        // Start initialization immediately and track it
        console.log('🔧 [AZURE DEBUG] Starting initialization...');
        this.initializeDebugVersion();
    }

    debugLog(message, data = null) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`🗺️ [AZURE DEBUG ${this.debugStep}] [${timestamp}] ${message}`, data || '');
    }

    debugError(message, error = null) {
        const timestamp = new Date().toLocaleTimeString();
        console.error(`❌ [AZURE DEBUG ${this.debugStep}] [${timestamp}] ${message}`, error || '');
    }

    async initializeDebugVersion() {
        try {
            this.debugStep = 1;
            this.debugLog("Step 1: Checking Azure Maps SDK availability");

            // Check SDK
            if (typeof atlas === 'undefined') {
                throw new Error('Azure Maps SDK not loaded - atlas is undefined');
            }
            if (typeof atlas.Map === 'undefined') {
                throw new Error('Azure Maps Map class not available');
            }
            this.debugLog("✅ Azure Maps SDK check passed");

            this.debugStep = 2;
            this.debugLog("Step 2: Fetching subscription key from backend");

            // Fetch API key
            const response = await fetch('/getazurekey');
            this.debugLog(`API response status: ${response.status}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.debugLog("API response data:", data);

            if (!data.subscriptionKey) {
                throw new Error('No subscription key in API response');
            }

            this.subscriptionKey = data.subscriptionKey;
            this.debugLog(`✅ Subscription key received (${this.subscriptionKey.length} chars)`);

            this.debugStep = 3;
            this.debugLog("Step 3: Creating Azure Maps instance");

            // Create map with minimal config
            const mapConfig = {
                center: [-74.00820558171071, 40.71083794970947], // NYC in [lng,lat]
                zoom: 15,
                style: 'satellite',
                authOptions: {
                    authType: 'subscriptionKey',
                    subscriptionKey: this.subscriptionKey
                },
                // Disable non-essential features
                traffic: false,
                showBuildingModels: false,
                showPointsOfInterest: false
            };

            this.debugLog("Creating map with config:", mapConfig);

            this.map = new atlas.Map('azureMap', mapConfig);
            this.debugLog("✅ Map object created, setting up events");

            // Setup events
            this.map.events.add('ready', () => {
                this.debugLog("🎉 MAP READY EVENT - Azure Maps fully loaded!");
                this.isInitialized = true;

                // Log map state
                this.debugLog(`Map center: ${JSON.stringify(this.map.getCamera().center)}`);
                this.debugLog(`Map zoom: ${this.map.getCamera().zoom}`);

                // Make azureMap div visible
                const azureMapDiv = document.getElementById('azureMap');
                if (azureMapDiv) {
                    azureMapDiv.style.display = 'block';
                    this.debugLog("✅ Azure Maps div set to display:block");
                } else {
                    this.debugError("❌ Could not find azureMap div element");
                }
            });

            this.map.events.add('error', (error) => {
                this.debugError("MAP ERROR EVENT", error);
            });

            this.map.events.add('styledata', () => {
                this.debugLog("✅ Map style data loaded");
            });

            this.debugLog("✅ Event listeners attached, waiting for ready event...");

        } catch (error) {
            this.debugStep = 99;
            this.debugError("❌ Initialization failed", error);
            throw error;
        }
    }

    // Minimal required methods to prevent errors
    getBounds() {
        if (!this.map || !this.isInitialized) {
            this.debugError("getBounds() called before map is ready");
            return [0, 0, 0, 0];
        }

        const bounds = this.map.getCamera().bounds;
        this.debugLog("getBounds() called", bounds);
        return [bounds[1], bounds[0], bounds[3], bounds[2]]; // Convert to expected format
    }

    setCenter(center) {
        if (!this.map || !this.isInitialized) {
            this.debugError("setCenter() called before map is ready");
            return;
        }

        this.debugLog("setCenter() called", center);
        this.map.setCamera({ center: center });
    }

    // Other required methods (minimal implementation)
    makeMapRect() { this.debugLog("makeMapRect() called"); }
    clearAll() { this.debugLog("clearAll() called"); }
    addShapes() { this.debugLog("addShapes() called"); }
    clearShapes() { this.debugLog("clearShapes() called"); }
}

// Replace the original AzureMap class temporarily
console.log('🔧 [AZURE DEBUG] Replacing AzureMap with debug version');
window.AzureMap = AzureMapDebug;