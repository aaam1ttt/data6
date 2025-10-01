#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Aztec API with transliteration notifications
"""

import sys
import json
from app import create_app

def test_api_with_cyrillic():
    """Test API generates warning for Cyrillic text"""
    app = create_app()
    
    with app.test_client() as client:
        # Test Cyrillic text
        response = client.post('/api_generate', 
            json={
                'text': 'Привет Мир',
                'code_type': 'aztec',
                'size': 300
            },
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        print("Testing API with Cyrillic text...")
        print(f"  Response status: {response.status_code}")
        print(f"  Success: {data.get('ok')}")
        print(f"  Has warning: {'warning' in data}")
        
        if 'warning' in data:
            print(f"  Warning message: {data['warning']}")
            print("[PASS] Cyrillic transliteration warning generated")
            return True
        else:
            print("[FAIL] No warning message for Cyrillic text")
            return False

def test_api_with_latin():
    """Test API does not generate warning for Latin text"""
    app = create_app()
    
    with app.test_client() as client:
        # Test Latin text
        response = client.post('/api_generate',
            json={
                'text': 'Hello World',
                'code_type': 'aztec',
                'size': 300
            },
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        print("\nTesting API with Latin text...")
        print(f"  Response status: {response.status_code}")
        print(f"  Success: {data.get('ok')}")
        print(f"  Has warning: {'warning' in data}")
        
        if 'warning' not in data:
            print("[PASS] No warning for Latin text")
            return True
        else:
            print(f"[FAIL] Unexpected warning: {data.get('warning')}")
            return False

def main():
    print("=" * 60)
    print("Testing Aztec API Transliteration Notifications")
    print("=" * 60)
    
    results = []
    results.append(test_api_with_cyrillic())
    results.append(test_api_with_latin())
    
    print("\n" + "=" * 60)
    if all(results):
        print("All API tests PASSED")
        return 0
    else:
        print("Some API tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
