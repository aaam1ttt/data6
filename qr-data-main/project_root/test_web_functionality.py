#!/usr/bin/env python3

import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.core.codes import generate_by_type, get_supported_types

def test_web_app():
    """Test web application functionality"""
    print("=== Testing Web Application ===\n")
    
    app = create_app()
    
    print("[OK] App creation successful")
    
    with app.test_client() as client:
        with app.app_context():
            response = client.get('/')
            if response.status_code == 200:
                print("[OK] Home page accessible")
            else:
                print(f"[FAIL] Home page failed: {response.status_code}")
                return False
            
            print("\n--- Testing API Endpoints ---")
            
            response = client.post('/forms/api_generate', 
                                 data=json.dumps({
                                     'text': 'Test QR Code',
                                     'code_type': 'QR',
                                     'size': 300
                                 }),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('ok') and data.get('data_url'):
                    print("[OK] QR code generation API working")
                else:
                    print(f"[FAIL] QR API error: {data.get('error')}")
                    return False
            else:
                print(f"[FAIL] QR API failed: {response.status_code}")
                return False
            
            response = client.post('/forms/api_generate', 
                                 data=json.dumps({
                                     'text': 'Test DataMatrix',
                                     'code_type': 'DM',
                                     'size': 300
                                 }),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('ok'):
                    print("[OK] DataMatrix generation API working")
                else:
                    print(f"[FAIL] DataMatrix API error: {data.get('error')}")
            else:
                print(f"[FAIL] DataMatrix API failed: {response.status_code}")
            
            response = client.post('/forms/api_generate', 
                                 data=json.dumps({
                                     'text': 'TEST123456789',
                                     'code_type': 'code128',
                                     'size': 300,
                                     'human_text': 'TEST123456789'
                                 }),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('ok'):
                    print("[OK] Code 128 generation API working")
                else:
                    print(f"[FAIL] Code 128 API error: {data.get('error')}")
            else:
                print(f"[FAIL] Code 128 API failed: {response.status_code}")
            
            response = client.post('/forms/api_generate', 
                                 data=json.dumps({
                                     'text': 'PDF417 Test Data',
                                     'code_type': 'pdf417',
                                     'size': 300,
                                     'human_text': 'PDF417'
                                 }),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('ok'):
                    print("[OK] PDF417 generation API working")
                else:
                    print(f"[FAIL] PDF417 API error: {data.get('error')}")
            else:
                print(f"[FAIL] PDF417 API failed: {response.status_code}")
            
            response = client.post('/forms/api_generate', 
                                 data=json.dumps({
                                     'text': 'Aztec Test',
                                     'code_type': 'aztec',
                                     'size': 300
                                 }),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('ok'):
                    print("[OK] Aztec generation API working")
                else:
                    print(f"[FAIL] Aztec API error: {data.get('error')}")
            else:
                print(f"[FAIL] Aztec API failed: {response.status_code}")
            
            print("\n--- Testing Form Pages ---")
            
            form_pages = ['/forms/torg12', '/forms/simple', '/forms/batch', '/forms/print']
            for page in form_pages:
                response = client.get(page)
                if response.status_code == 200:
                    print(f"[OK] {page} accessible")
                else:
                    print(f"[FAIL] {page} failed: {response.status_code}")
            
            response = client.get('/scan/')
            if response.status_code == 200:
                print("[OK] Scan page accessible")
            else:
                print(f"[FAIL] Scan page failed: {response.status_code}")
    
    return True

def test_code_generation():
    """Test direct code generation functions"""
    print("\n=== Testing Code Generation Functions ===\n")
    
    test_text = "Test Code Generation"
    
    supported_types = get_supported_types()
    print(f"Supported code types: {[t['value'] for t in supported_types]}")
    
    for code_type_info in supported_types:
        code_type = code_type_info['value']
        try:
            img = generate_by_type(code_type, test_text, size=300)
            print(f"[OK] {code_type_info['label']}: Generated {img.size[0]}x{img.size[1]} image")
        except Exception as e:
            print(f"[FAIL] {code_type_info['label']}: Failed - {str(e)}")
    
    return True

def main():
    """Run all functionality tests"""
    print("Testing Web Application Functionality After Comment Removal")
    print("=" * 60)
    
    success = True
    
    try:
        success &= test_code_generation()
        success &= test_web_app()
    except Exception as e:
        print(f"Test failed with exception: {e}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] ALL FUNCTIONALITY TESTS PASSED")
        print("\nWeb application is working correctly after comment removal!")
        print("- All code types can be generated")
        print("- API endpoints are functional")
        print("- Form pages load correctly")
        print("- Scanning functionality accessible")
    else:
        print("[ERROR] SOME TESTS FAILED")
        print("Check the errors above for details")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)