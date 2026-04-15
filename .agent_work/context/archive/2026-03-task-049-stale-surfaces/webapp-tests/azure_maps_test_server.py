#!/usr/bin/env python3
"""
Simple Azure Maps test server
"""

from flask import Flask, render_template_string
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

app = Flask(__name__)

# Simple HTML template with Azure Maps
AZURE_MAPS_TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Azure Maps Test</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.js"></script>
    <link href="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.css" rel="stylesheet" />
    <script src="https://atlas.microsoft.com/sdk/javascript/drawing/1.0/atlas-drawing.min.js"></script>
    <link href="https://atlas.microsoft.com/sdk/javascript/drawing/1.0/atlas-drawing.min.css" rel="stylesheet" />
    <style>
        #mapContainer {
            width: 100vw;
            height: 100vh;
        }
        #status {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div id="status">
        <h3>Azure Maps Test</h3>
        <div id="statusText">Initializing...</div>
        <div id="keyInfo">API Key: {{ 'Configured' if azure_key else 'Missing' }}</div>
    </div>
    <div id="mapContainer"></div>

    <script>
        var map;
        var drawingManager;
        
        function updateStatus(message) {
            document.getElementById('statusText').innerHTML = message;
        }
        
        function initializeMap() {
            updateStatus('Loading Azure Maps SDK...');
            
            try {
                // Initialize the map
                map = new atlas.Map('mapContainer', {
                    center: [-122.335167, 47.608013], // Seattle
                    zoom: 10,
                    language: 'en-US',
                    authOptions: {
                        authType: 'subscriptionKey',
                        subscriptionKey: '{{ azure_key }}'
                    }
                });
                
                map.events.add('ready', function() {
                    updateStatus('✅ Map loaded successfully!');
                    
                    // Initialize drawing tools
                    drawingManager = new atlas.drawing.DrawingManager(map, {
                        toolbar: new atlas.control.DrawingToolbar({
                            buttons: ['draw-polygon', 'edit-geometry', 'delete-geometry'],
                            position: 'top-right'
                        })
                    });
                    
                    map.controls.add(drawingManager.getControls(), 'top-right');
                    
                    // Add drawing event listeners
                    map.events.add('drawingcomplete', drawingManager, function(shape) {
                        updateStatus('✅ Polygon drawn! Coordinates: ' + JSON.stringify(shape.getCoordinates()[0][0]));
                    });
                    
                    updateStatus('✅ Azure Maps with drawing tools ready!');
                });
                
                map.events.add('error', function(error) {
                    updateStatus('❌ Map error: ' + error.message);
                });
                
            } catch (error) {
                updateStatus('❌ Error: ' + error.message);
            }
        }
        
        // Wait for page to load
        window.onload = function() {
            if (typeof atlas === 'undefined') {
                updateStatus('❌ Azure Maps SDK failed to load');
            } else {
                initializeMap();
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
    return render_template_string(AZURE_MAPS_TEST_HTML, azure_key=azure_key)

@app.route('/health')
def health():
    return {
        'status': 'ok',
        'azure_maps_key_configured': bool(os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')),
        'key_length': len(os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', ''))
    }

if __name__ == '__main__':
    print("🚀 Starting Azure Maps Test Server...")
    print(f"Azure Maps Key: {'Configured' if os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY') else 'Missing'}")
    print("📍 Open: http://localhost:5000")
    print("🏥 Health: http://localhost:5000/health")
    app.run(debug=True, host='localhost', port=5000)