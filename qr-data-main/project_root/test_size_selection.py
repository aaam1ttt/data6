#!/usr/bin/env python3
"""
Test size selection functionality across all code generation paths
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.core.codes import generate_qr, generate_dm, generate_code128, generate_pdf417, generate_aztec, generate_by_type
from PIL import Image

def test_size_parameter_qr():
    """Test QR code generation with different sizes"""
    print("Testing QR code size selection...")
    
    text = "Test QR Code"
    sizes = [177, 236, 295, 354]  # GOST standard sizes
    
    for size in sizes:
        img = generate_qr(text, size=size)
        assert isinstance(img, Image.Image), "Should return PIL Image"
        assert img.size[0] == size, f"QR code should be {size}x{size}, got {img.size[0]}x{img.size[1]}"
        assert img.size[1] == size, f"QR code should be {size}x{size}, got {img.size[0]}x{img.size[1]}"
        print(f"  [OK] QR code generated at size {size}x{size}")
    
    return True

def test_size_parameter_dm():
    """Test DataMatrix code generation with different sizes"""
    print("\nTesting DataMatrix size selection...")
    
    text = "Test DM"
    sizes = [94, 142, 189, 236]  # GOST standard sizes
    
    for size in sizes:
        img = generate_dm(text, size=size)
        assert isinstance(img, Image.Image), "Should return PIL Image"
        assert img.size[0] == size, f"DM code should be {size}x{size}, got {img.size[0]}x{img.size[1]}"
        assert img.size[1] == size, f"DM code should be {size}x{size}, got {img.size[0]}x{img.size[1]}"
        print(f"  [OK] DataMatrix generated at size {size}x{size}")
    
    return True

def test_size_parameter_code128():
    """Test Code128 barcode generation with different sizes"""
    print("\nTesting Code128 size selection...")
    
    text = "TEST123"
    sizes = [94, 142, 177, 236]  # GOST standard heights
    
    for size in sizes:
        img = generate_code128(text, size=size)
        assert isinstance(img, Image.Image), "Should return PIL Image"
        assert img.size[1] == size, f"Code128 height should be {size}, got {img.size[1]}"
        print(f"  [OK] Code128 generated with height {size}")
    
    return True

def test_size_parameter_pdf417():
    """Test PDF417 barcode generation with different sizes"""
    print("\nTesting PDF417 size selection...")
    
    text = "TEST PDF417"
    sizes = [118, 177, 236, 295]  # GOST standard heights
    
    for size in sizes:
        img = generate_pdf417(text, size=size)
        assert isinstance(img, Image.Image), "Should return PIL Image"
        assert img.size[1] == size, f"PDF417 height should be {size}, got {img.size[1]}"
        print(f"  [OK] PDF417 generated with height {size}")
    
    return True

def test_size_parameter_aztec():
    """Test Aztec code generation with different sizes"""
    print("\nTesting Aztec size selection...")
    
    text = "Test Aztec"
    sizes = [177, 236, 295, 354]  # GOST standard sizes
    
    for size in sizes:
        img = generate_aztec(text, size=size)
        assert isinstance(img, Image.Image), "Should return PIL Image"
        assert img.size[0] == size, f"Aztec should be {size}x{size}, got {img.size[0]}x{img.size[1]}"
        assert img.size[1] == size, f"Aztec should be {size}x{size}, got {img.size[0]}x{img.size[1]}"
        print(f"  [OK] Aztec generated at size {size}x{size}")
    
    return True

def test_generate_by_type():
    """Test generate_by_type wrapper function with sizes"""
    print("\nTesting generate_by_type with size parameters...")
    
    test_cases = [
        ("QR", "Test QR", 236),
        ("DM", "Test DM", 142),
        ("C128", "TEST123", 142),
        ("PDF417", "Test PDF", 177),
        ("AZTEC", "Test AZ", 236)
    ]
    
    for code_type, text, size in test_cases:
        img = generate_by_type(code_type, text, size=size)
        assert isinstance(img, Image.Image), f"Should return PIL Image for {code_type}"
        
        if code_type in ["QR", "DM", "AZTEC"]:
            assert img.size[0] == size, f"{code_type} should be {size}x{size}"
            assert img.size[1] == size, f"{code_type} should be {size}x{size}"
        else:  # Barcodes (C128, PDF417)
            assert img.size[1] == size, f"{code_type} height should be {size}"
        
        print(f"  [OK] {code_type} generated via generate_by_type")
    
    return True

def test_api_endpoints():
    """Test Flask API endpoints receive and use size parameter"""
    print("\nTesting API endpoints with size parameters...")
    
    app = create_app()
    with app.test_client() as client:
        # Test api_generate endpoint
        test_cases = [
            {"text": "Test QR", "code_type": "QR", "size": 236},
            {"text": "Test DM", "code_type": "DM", "size": 142},
            {"text": "TEST123", "code_type": "C128", "size": 142},
            {"text": "Test PDF", "code_type": "PDF417", "size": 177},
            {"text": "Test AZ", "code_type": "AZTEC", "size": 236}
        ]
        
        for data in test_cases:
            response = client.post('/forms/api_generate', 
                                  json=data,
                                  headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200, f"API should return 200 for {data['code_type']}"
            json_data = response.get_json()
            assert json_data.get('ok') == True, f"API should succeed for {data['code_type']}"
            assert 'data_url' in json_data, f"API should return data_url for {data['code_type']}"
            print(f"  [OK] API endpoint works with size {data['size']} for {data['code_type']}")
    
    return True

def test_gost_code_parameter():
    """Test GOST code parameter for standard sizes"""
    print("\nTesting GOST code parameter...")
    
    test_cases = [
        ("QR", "Test", "QR-S2", 236),
        ("DM", "Test", "DM-S2", 142),
        ("C128", "TEST", "C128-H2", 142),
        ("PDF417", "Test", "PDF417-S2", 177),
        ("AZTEC", "Test", "AZ-S2", 236)
    ]
    
    for code_type, text, gost_code, expected_size in test_cases:
        img = generate_by_type(code_type, text, size=expected_size, gost_code=gost_code)
        assert isinstance(img, Image.Image), f"Should generate image for {code_type} with GOST {gost_code}"
        print(f"  [OK] {code_type} generated with GOST code {gost_code}")
    
    return True

def main():
    print("=" * 60)
    print("Size Selection Functionality Test Suite")
    print("=" * 60)
    
    try:
        # Test individual generation functions
        test_size_parameter_qr()
        test_size_parameter_dm()
        test_size_parameter_code128()
        test_size_parameter_pdf417()
        test_size_parameter_aztec()
        
        # Test wrapper function
        test_generate_by_type()
        
        # Test API endpoints
        test_api_endpoints()
        
        # Test GOST code parameter
        test_gost_code_parameter()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All size selection tests PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
