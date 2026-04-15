#!/usr/bin/env python3
"""
Simplified Flask development server for testing Azure Maps integration
"""

import sys
import os

# Add the current directory to sys.path
sys.path.insert(0, '.')

def start_flask_dev_server():
    print("🚀 Starting Flask development server...")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv('.env')
    
    # Check Azure Maps configuration
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    secret_key = os.getenv('FLASK_SECRET_KEY')
    
    print(f"✅ Azure Maps Key: {azure_key[:10]}...{azure_key[-6:] if azure_key else 'Missing'}")
    print(f"✅ Flask Secret Key: {'Configured' if secret_key else 'Missing'}")
    
    # Create Flask app
    from flask import Flask, jsonify
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key or 'dev-secret-key'
    app.config['DEBUG'] = True
    
    @app.route('/')
    def home():
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>TowerScout - Azure Maps Test</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>🗼 TowerScout - Azure Maps Integration Test</h1>
            <div style="background: #f0f8ff; padding: 20px; border-radius: 8px;">
                <h2>Configuration Status</h2>
                <p><strong>Azure Maps Key:</strong> {'✅ Configured (' + str(len(azure_key)) + ' chars)' if azure_key else '❌ Missing'}</p>
                <p><strong>Flask Secret:</strong> {'✅ Configured' if secret_key else '❌ Missing'}</p>
                <p><strong>Server:</strong> ✅ Running (Flask Dev Server)</p>
            </div>
            <div style="margin-top: 20px;">
                <h2>Test Endpoints</h2>
                <ul>
                    <li><a href="/getproviders">📡 Get Providers</a></li>
                    <li><a href="/azure-test">🗺️  Azure Maps Test</a></li>
                </ul>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/getproviders')
    def get_providers():
        providers = []
        if azure_key:
            providers.append({'id': 'azure', 'name': 'Azure Maps'})
        return jsonify(providers)
    
    @app.route('/azure-test')
    def azure_test():
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Azure Maps Test</title>
            <script src="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.js"></script>
            <link href="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3.0/atlas.min.css" rel="stylesheet" />
        </head>
        <body>
            <div id="myMap" style="width: 100%; height: 400px;"></div>
            <div id="status" style="margin-top: 10px; padding: 10px; background: #f0f0f0;">
                <strong>Status:</strong> <span id="statusText">Initializing...</span>
            </div>
            <script>
                let statusElement = document.getElementById('statusText');
                
                function updateStatus(message) {{
                    statusElement.textContent = message;
                    console.log('Status:', message);
                }}
                
                try {{
                    updateStatus('Creating Azure Maps instance...');
                    let map = new atlas.Map('myMap', {{
                        center: [-122.335167, 47.608013],
                        zoom: 10,
                        authOptions: {{
                            authType: 'subscriptionKey',
                            subscriptionKey: '{azure_key}'
                        }}
                    }});
                    
                    map.events.add('ready', function() {{
                        updateStatus('✅ Azure Maps loaded successfully!');
                    }});
                    
                    map.events.add('error', function(e) {{
                        updateStatus('❌ Error: ' + (e.error ? e.error.message : 'Unknown error'));
                    }});
                }} catch (error) {{
                    updateStatus('❌ JavaScript Error: ' + error.message);
                }}
            </script>
        </body>
        </html>
        '''
    
    print("📡 Starting Flask server on http://localhost:5001...")
    print("   Open your browser to test Azure Maps integration")
    print("   Press Ctrl+C to stop")
    
    try:
        app.run(host='localhost', port=5001, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")

if __name__ == "__main__":
    start_flask_dev_server()