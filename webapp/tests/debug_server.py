#!/usr/bin/env python3
"""
Simplified TowerScout server starter for debugging
"""

import sys
import os

# Add the current directory to sys.path to import towerscout modules
sys.path.insert(0, '.')

def start_server():
    print("🚀 Starting TowerScout server...")
    
    # Import required modules
    from flask import Flask
    from waitress import serve
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv('.env')
    
    # Check critical environment variables
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    secret_key = os.getenv('FLASK_SECRET_KEY')
    
    print(f"✅ Azure Maps Key: {'Configured' if azure_key else 'Missing'}")
    print(f"✅ Flask Secret Key: {'Configured' if secret_key else 'Missing'}")
    
    if not secret_key:
        print("❌ FLASK_SECRET_KEY is required but missing!")
        return
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key
    
    @app.route('/')
    def home():
        return f'''
        <html>
        <head><title>TowerScout Test</title></head>
        <body>
            <h1>TowerScout Server Test</h1>
            <p>Azure Maps Key: {'Configured' if azure_key else 'Missing'}</p>
            <p>Server Time: {os.popen('date /t').read().strip()}</p>
        </body>
        </html>
        '''
    
    @app.route('/getproviders')
    def get_providers():
        providers = []
        if azure_key:
            providers.append({'id': 'azure', 'name': 'Azure Maps'})
        return {'providers': providers}
    
    print("📡 Starting Waitress server on http://localhost:5000...")
    print("   Press Ctrl+C to stop")
    
    try:
        serve(app, host='localhost', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server()