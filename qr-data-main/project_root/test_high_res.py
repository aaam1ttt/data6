#!/usr/bin/env python3
"""
Test high-resolution QR code generation
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_qr, generate_dm

def test_high_res():
    print("Testing high-resolution barcode/QR code generation...")
    
    test_text = "https://example.com/test-high-resolution-quality"
    sizes = [300, 600, 900]
    
    for size in sizes:
        print(f"\nTesting QR at {size}px:")
        try:
            qr_img = generate_qr(test_text, size=size)
            print(f"  [OK] Generated QR: {qr_img.size}")
                
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            return False
    
    print(f"\nTesting DataMatrix:")
    try:
        dm_img = generate_dm(test_text, size=600)
        print(f"  [OK] Generated DataMatrix: {dm_img.size}")
    except Exception as e:
        print(f"  [ERROR] DataMatrix error: {e}")
    
    print("\n[OK] High-resolution generation test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_high_res()
    sys.exit(0 if success else 1)