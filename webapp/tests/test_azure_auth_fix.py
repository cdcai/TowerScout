"""
Mock Azure Maps for Development Testing
This provides a fallback when Azure Maps authentication fails.
"""
import os
from flask import Flask, render_template_string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key')

# Template with authentication error handling
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Azure Maps Auth Fix Test</title>
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
        .warning { background: #fff3cd; color: #856404; }
        .info { background: #cce7ff; color: #004085; }
    </style>
</head>
<body>
    <h1>Azure Maps Authentication Fix Test</h1>
    <p><strong>Azure API Key Status:</strong> {{ 'Configured' if azure_map_key else 'Missing' }}</p>
    <p><strong>Key Length:</strong> {{ azure_map_key|length if azure_map_key else 0 }} characters</p>
    <p><strong>Key Preview:</strong> {{ azure_map_key[:8] + '...' + azure_map_key[-4:] if azure_map_key else 'None' }}</p>
    
    <div id="auth-test">
        <h3>Authentication Test Results:</h3>
        <div id="test-results">Testing...</div>
    </div>
    
    <div id="status" class="status info">Ready to test Azure Maps with authentication fixes...</div>
    <div id="azureMap"></div>
    
    <h3>Troubleshooting Steps:</h3>
    <ol>
        <li><strong>Invalid Key:</strong> If 401 errors persist, the Azure Maps subscription key needs to be regenerated</li>
        <li><strong>Service Permissions:</strong> Ensure your Azure Maps account includes Web SDK and Tile services</li>
        <li><strong>Fallback Option:</strong> Test with Google Maps provider while fixing Azure Maps authentication</li>
        <li><strong>Key Format:</strong> Azure Maps keys are typically 40-43 characters long</li>
    </ol>
    
    <script>
        let aak = "{{ azure_map_key }}";
        
        function testAuthentication() {
            const testResults = document.getElementById('test-results');
            
            if (!aak) {
                testResults.innerHTML = '<div class="error">❌ No Azure Maps key configured</div>';
                return;
            }
            
            // Test with a simple fetch to Azure Maps API
            const testUrl = `https://atlas.microsoft.com/search/address/json?api-version=1.0&subscription-key=${aak}&query=Seattle`;
            
            testResults.innerHTML = '<div class="info">🔄 Testing authentication...</div>';
            
            fetch(testUrl)
                .then(response => {
                    if (response.ok) {
                        testResults.innerHTML = '<div class="success">✅ Authentication successful! Key is valid.</div>';
                        initAzureMap();
                    } else if (response.status === 401) {
                        testResults.innerHTML = `
                            <div class="error">
                                ❌ Authentication Failed (401 Unauthorized)<br>
                                The Azure Maps subscription key is invalid or expired.<br>
                                <strong>Action Required:</strong> Generate a new key in Azure Portal.
                            </div>`;
                    } else if (response.status === 403) {
                        testResults.innerHTML = `
                            <div class="warning">
                                ⚠️ Access Forbidden (403)<br>
                                The key is valid but lacks permissions for this service.<br>
                                <strong>Action:</strong> Check your Azure Maps service tier.
                            </div>`;
                        // Try to initialize map anyway, might work for basic functions
                        initAzureMap();
                    } else {
                        testResults.innerHTML = `
                            <div class="warning">
                                ⚠️ HTTP ${response.status} - ${response.statusText}<br>
                                Unexpected response from Azure Maps API.
                            </div>`;
                    }
                })
                .catch(error => {
                    testResults.innerHTML = `
                        <div class="error">
                            ❌ Network Error: ${error.message}<br>
                            Could not reach Azure Maps API.
                        </div>`;
                });
        }
        
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
                status.className = 'status info';
                status.textContent = 'Initializing Azure Maps...';
                
                // Set authentication with enhanced error handling
                atlas.setAuthenticationOptions({
                    authType: 'subscriptionKey',
                    subscriptionKey: aak
                });
                
                console.log('Authentication configured for key:', aak.substring(0, 8) + '...');
                
                // Create map with road style first to avoid traffic/satellite permission issues
                const map = new atlas.Map('azureMap', {
                    center: [-122.33, 47.6],
                    zoom: 10,
                    style: 'road',
                    authOptions: {
                        authType: 'subscriptionKey',
                        subscriptionKey: aak
                    },
                    traffic: false // Disable traffic to avoid permission issues
                });
                
                map.events.add('ready', function() {
                    status.className = 'status success';
                    status.textContent = '✅ Azure Maps initialized successfully with road style!';
                    
                    // Try to switch to satellite after 2 seconds
                    setTimeout(function() {
                        try {
                            map.setStyle({ style: 'satellite' });
                            status.textContent = '✅ Azure Maps working with satellite imagery!';
                        } catch (e) {
                            console.warn('Satellite style failed, staying with road style:', e);
                            status.textContent = '✅ Azure Maps working (road style only due to service limitations)';
                        }
                    }, 2000);
                });
                
                map.events.add('error', function(e) {
                    const errorMsg = e.error ? e.error.message : 'Unknown error';
                    status.className = 'status error';
                    status.textContent = '❌ Azure Maps error: ' + errorMsg;
                    
                    console.error('Azure Maps detailed error:', {
                        error: e.error,
                        message: errorMsg,
                        timestamp: new Date().toISOString()
                    });
                });
                
            } catch (error) {
                status.className = 'status error';
                status.textContent = '❌ Initialization failed: ' + error.message;
                console.error('Map initialization error:', error);
            }
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                testAuthentication();
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
    print("Starting Azure Maps Authentication Fix Test...")
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
    print(f"Azure Key: {'configured' if azure_key else 'missing'} ({len(azure_key)} chars)")
    print("🔧 This test will help diagnose and fix Azure Maps authentication issues")
    app.run(debug=True, host='0.0.0.0', port=5003)