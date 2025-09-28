#!/usr/bin/env python3
"""
Simple QR code quality test without problematic decode tests.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_qr, save_image

def test_basic_generation():
    """Test basic QR generation with quality improvements"""
    print("Testing QR code generation quality...")
    
    test_cases = [
        ("Test123", 300, "H"),
        ("https://example.com", 600, "H"),  
        ("Simple text", 900, "H"),
        ("Longer text for capacity test", 600, "Q")
    ]
    
    for i, (text, size, ecc) in enumerate(test_cases):
        try:
            print(f"Test {i+1}: {text[:30]} -> {size}px, ECC:{ecc}")
            qr_img = generate_qr(text, size=size, preferred_ecc=ecc)
            

            if qr_img.size == (size, size):
                print(f"  [OK] Dimensions: {qr_img.size}")
            else:
                print(f"  [ERROR] Expected {size}x{size}, got {qr_img.size}")
                

            print(f"  [INFO] Mode: {qr_img.mode}, Format: {qr_img.format}")
            
        except Exception as e:
            print(f"  [ERROR] Generation failed: {e}")

if __name__ == "__main__":
    test_basic_generation()
    print("Basic generation test completed.")