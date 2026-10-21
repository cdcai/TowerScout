#!/usr/bin/env python3
"""
Simple Azure Maps test server
"""
import os
from flask import Flask, render_template_string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'test-key')

# Minimal template for testing Azure Maps
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Azure Maps Test</title>
    <link rel="stylesheet" href="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.css" />
    <link rel="stylesheet" href="https://atlas.microsoft.com/sdk/javascript/drawing/1.0/atlas-drawing.min.css" />
    <script src="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.js" onload="console.log('Azure Maps main SDK loaded')"></script>
    <script src="https://atlas.microsoft.com/sdk/javascript/drawing/1.0/atlas-drawing.min.js" onload="console.log('Azure Maps drawing SDK loaded')"></script>
    <style>
        #azureMap { width: 800px; height: 600px; border: 1px solid #ccc; }
        body { font-family: Arial; margin: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Azure Maps Integration Test</h1>
    <p>Azure API Key: {{ 'Configured' if azure_map_key else 'Missing' }}</p>
    
    <div id="status" class="status">Initializing Azure Maps...</div>
    <div id="azureMap"></div>
    
    <script>
        let aak = "{{ azure_map_key }}";
        
        function checkAzureMapsLoaded() {
            return typeof atlas !== 'undefined' && typeof atlas.Map !== 'undefined';
        }
        
        function initAzureMap() {
            const status = document.getElementById('status');
            
            if (!checkAzureMapsLoaded()) {
                status.className = 'status error';
                status.textContent = 'Azure Maps SDK not loaded';
                return;
            }
            
            if (!aak) {
                status.className = 'status error';
                status.textContent = 'Azure Maps API key missing';
                return;
            }
            
            try {
                # Set authentication BEFORE creating map
                atlas.setAuthenticationOptions({
                    authType: 'subscriptionKey',
                    subscriptionKey: aak
                });
                
                console.log('Authentication configured with key:', aak ? aak.substring(0, 8) + '...' : 'missing');
                
                // Create map with minimal configuration to avoid service-specific errors
                const map = new atlas.Map('azureMap', {
                    center: [-74.006, 40.7128],
                    zoom: 10,
                    style: 'road', // Use 'road' instead of 'satellite' to avoid traffic dependencies
                    authOptions: {
                        authType: 'subscriptionKey',
                        subscriptionKey: aak
                    },
                    // Disable traffic layer to avoid 401 errors
                    traffic: false
                });
                
                map.events.add('ready', function() {
                    status.className = 'status success';
                    status.textContent = 'Azure Maps initialized successfully!';
                    
                    console.log('Azure Maps ready event fired successfully');
                    
                    // Test changing to satellite style after successful initialization
                    setTimeout(function() {
                        try {
                            map.setStyle({ style: 'satellite' });
                            console.log('Satellite style applied successfully');
                        } catch (e) {
                            console.warn('Could not apply satellite style:', e.message);
                        }
                    }, 2000);
                    
                    // Test drawing tools only if they're available
                    if (typeof atlas.drawing !== 'undefined') {
                        try {
                            const drawingManager = new atlas.drawing.DrawingManager(map);
                            console.log('Drawing tools initialized successfully');
                        } catch (e) {
                            console.warn('Drawing tools initialization failed:', e.message);
                        }
                    } else {
                        console.log('Drawing SDK not loaded, skipping drawing tools test');
                    }
                });
                
                map.events.add('error', function(e) {
                    status.className = 'status error';
                    const errorMsg = e.error ? e.error.message : 'Unknown error';
                    status.textContent = 'Azure Maps error: ' + errorMsg;
                    
                    console.error('Azure Maps error details:', {
                        error: e.error,
                        message: errorMsg,
                        timestamp: new Date().toISOString()
                    });
                    
                    // Try to provide helpful error messages
                    if (errorMsg.includes('401') || errorMsg.includes('Unauthorized')) {
                        console.error('Authentication Error: Check your Azure Maps subscription key');
                        console.error('Key being used:', aak ? aak.substring(0, 8) + '...' : 'missing');
                    } else if (errorMsg.includes('403') || errorMsg.includes('Forbidden')) {
                        console.error('Permission Error: Your subscription may not have access to this service');
                    } else if (errorMsg.includes('429') || errorMsg.includes('rate')) {
                        console.error('Rate Limit Error: Too many requests to Azure Maps API');
                    }
                });
                
            } catch (error) {
                status.className = 'status error';
                status.textContent = 'Initialization failed: ' + error.message;
            }
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                initAzureMap();
            }, 1000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, 
        azure_map_key=os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', ''))

if __name__ == '__main__':
    print("Starting Azure Maps test server...")
    print(f"Azure API Key: {'Configured' if os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY') else 'Missing'}")
    app.run(debug=True, host='0.0.0.0', port=5002)