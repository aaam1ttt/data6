#!/usr/bin/env python3
"""Test full GOST system integration with web interface"""

import sys
import os
import tempfile
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.core.codes import generate_by_type
from app.core.gost_dimensions import get_gost_dimensions

def test_web_integration():
    """Test GOST integration with web interface"""
    print("=== Testing GOST Web Integration ===\n")
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Test API endpoint with GOST code
            response = client.post('/forms/api_generate', 
                                 data=json.dumps({
                                     'text': 'Test GOST QR',
                                     'code_type': 'QR',
                                     'size': 236,
                                     'gost_code': 'QR-S2'
                                 }),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                if data.get('ok'):
                    print("OK API endpoint accepts GOST parameters")
                    # Check if data URL is valid base64 PNG
                    if data.get('data_url', '').startswith('data:image/png;base64,'):
                        print("OK Generated valid PNG data URL")
                    else:
                        print("FAIL Invalid PNG data URL format")
                        return False
                else:
                    print(f"FAIL API returned error: {data.get('error')}")
                    return False
            else:
                print(f"FAIL API request failed with status {response.status_code}")
                return False
            
            # Test TORG-12 form rendering
            response = client.get('/forms/torg12')
            if response.status_code == 200:
                html = response.data.decode('utf-8')
                if 'GOST_PRESETS' in html:
                    print("OK TORG-12 form contains GOST presets")
                else:
                    print("FAIL TORG-12 form missing GOST presets")
                    return False
                    
                if 'QR-S2' in html:
                    print("OK GOST size codes present in template")
                else:
                    print("FAIL GOST size codes missing from template")
                    return False
            else:
                print("FAIL Failed to load TORG-12 form")
                return False
    
    return True

def test_size_accuracy():
    """Test that GOST sizes produce accurate dimensions"""
    print("\n=== Testing Size Accuracy ===\n")
    
    test_text = "ТЕСТ РАЗМЕРОВ ПО ГОСТ"
    
    # Test QR codes
    qr_dims = get_gost_dimensions("QR")
    for dim in qr_dims:
        try:
            img = generate_by_type("QR", test_text, gost_code=dim.code)
            expected_size = dim.pixels_300dpi
            actual_size = img.size[0]  # QR codes are square
            
            if actual_size == expected_size:
                print(f"OK {dim.code}: {actual_size}px (expected {expected_size}px)")
            else:
                print(f"FAIL {dim.code}: {actual_size}px (expected {expected_size}px) - MISMATCH")
                return False
                
        except Exception as e:
            print(f"FAIL {dim.code}: Failed to generate - {e}")
            return False
    
    # Test DataMatrix codes
    dm_dims = get_gost_dimensions("DM")[:2]  # Test first 2 to save time
    for dim in dm_dims:
        try:
            img = generate_by_type("DM", test_text, gost_code=dim.code)
            expected_size = dim.pixels_300dpi
            actual_size = img.size[0]  # DataMatrix codes are square
            
            if actual_size == expected_size:
                print(f"OK {dim.code}: {actual_size}px (expected {expected_size}px)")
            else:
                print(f"FAIL {dim.code}: {actual_size}px (expected {expected_size}px) - MISMATCH")
                return False
                
        except Exception as e:
            print(f"FAIL {dim.code}: Failed to generate - {e}")
            return False
                return False
                
        except Exception as e:
            print(f"FAIL {dim.code}: Failed to generate - {e}")
            return False
    
    return True

def test_print_layout_calculations():
    """Test A4 layout calculations"""
    print("\n=== Testing Print Layout Calculations ===\n")
    
    from app.core.gost_dimensions import get_a4_layout_info
    
    # Test QR-S2 (TORG-12 standard)
    qr_s2 = get_gost_dimensions("QR")[1]  # S2
    layout = get_a4_layout_info(qr_s2)
    
    print(f"QR-S2 (20x20mm) on A4:")
    print(f"  Layout: {layout['horizontal_count']}x{layout['vertical_count']}")
    print(f"  Total codes: {layout['total_per_page']}")
    print(f"  Page efficiency: {layout['usage_efficiency']}%")
    
    # Verify calculations
    expected_h = int((210 - 10) / (20 + 2))  # A4 width minus margins, divided by code + spacing
    expected_v = int((297 - 10) / (20 + 2))  # A4 height minus margins
    
    if layout['horizontal_count'] == expected_h and layout['vertical_count'] == expected_v:
        print("OK Layout calculations correct")
    else:
        print(f"FAIL Layout calculations incorrect: expected {expected_h}x{expected_v}")
        return False
    
    return True

def main():
    """Run all GOST system tests"""
    print("Testing GOST standardized barcode dimensions system")
    print("=" * 60)
    
    success = True
    
    # Test basic functionality
    try:
        success &= test_size_accuracy()
        success &= test_print_layout_calculations()
        success &= test_web_integration()
    except Exception as e:
        print(f"Test failed with exception: {e}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("OK ALL GOST SYSTEM TESTS PASSED")
        print("\nGOST standardized dimensions are working correctly!")
        print("- Accurate size calculations")
        print("- Proper web interface integration")  
        print("- Correct print layout calculations")
        print("- Compatible with existing TORG-12 forms")
    else:
        print("FAIL SOME TESTS FAILED")
        print("Check the errors above for details")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)