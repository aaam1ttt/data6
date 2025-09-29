#!/usr/bin/env python3
"""
Test Aztec code generation through web interface
"""

import sys
import os
sys.path.append('.')

from app import create_app
import tempfile
from werkzeug.test import Client
from werkzeug.serving import WSGIRequestHandler

def test_web_aztec():
    """Test Aztec generation through web interface"""
    print("Testing web interface Aztec generation...")
    
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test AZTEC code generation
        response = client.post('/forms/api_generate', json={
            'text': 'AZTEC TEST',
            'code_type': 'AZTEC',
            'size': '300',
            'human_text': ''
        })
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: AZTEC code generation via web interface works!")
            
            # Save response data to check image
            with open('web_aztec_test.png', 'wb') as f:
                f.write(response.data)
            print("Saved generated image to web_aztec_test.png")
            
        else:
            print(f"ERROR: Web request failed with status {response.status_code}")
            print(f"Response data: {response.data.decode()}")

if __name__ == "__main__":
    test_web_aztec()