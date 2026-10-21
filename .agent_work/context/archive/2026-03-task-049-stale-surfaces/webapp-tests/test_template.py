#!/usr/bin/env python3
"""
Test Flask app to verify Azure Maps template changes
"""
import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'test-key-for-development')

@app.route('/')
def index():
    # Mock the template context with the same variables used in the real app
    context = {
        'google_map_key': os.getenv('GOOGLE_API_KEY', ''),
        'azure_map_key': os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', ''),
        'dev': True
    }
    
    return render_template('towerscout.html', **context)

if __name__ == '__main__':
    print("Starting test Flask app to verify Azure Maps template...")
    print(f"Azure Maps Key: {'Configured' if os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY') else 'Missing'}")
    print(f"Google Maps Key: {'Configured' if os.getenv('GOOGLE_API_KEY') else 'Missing'}")
    
    app.run(debug=True, host='0.0.0.0', port=5001)