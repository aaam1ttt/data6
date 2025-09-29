#!/usr/bin/env python3
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

def test_api_endpoint():
    print("Testing API endpoint...")
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            test_cases = [
                {'text': 'Test QR', 'code_type': 'QR', 'size': 300},
                {'text': 'Test DM', 'code_type': 'DM', 'size': 300},
                {'text': 'TEST123', 'code_type': 'C128', 'size': 300, 'human_text': 'TEST123'},
                {'text': 'PDF417 Test', 'code_type': 'PDF417', 'size': 300, 'human_text': 'PDF417'},
                {'text': 'Aztec Test', 'code_type': 'AZTEC', 'size': 300},
            ]
            
            for test_case in test_cases:
                response = client.post('/forms/api_generate', 
                                     data=json.dumps(test_case),
                                     content_type='application/json')
                
                if response.status_code == 200:
                    data = json.loads(response.data)
                    if data.get('ok') and data.get('data_url'):
                        print(f"{test_case['code_type']} API: OK")
                    else:
                        print(f"{test_case['code_type']} API Error: {data.get('error')}")
                        return False
                else:
                    print(f"{test_case['code_type']} API Failed: {response.status_code}")
                    return False
    
    return True

if __name__ == "__main__":
    success = test_api_endpoint()
    sys.exit(0 if success else 1)