#!/usr/bin/env python3
"""
Test script to verify font scaling with larger barcode sizes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_code128, generate_pdf417

def test_large_barcodes():
    """Test larger barcodes to verify proportional font scaling"""
    print("Testing larger barcode sizes for font scaling...")
    
    # Test different sizes
    sizes_to_test = [300, 450, 600]
    
    for size in sizes_to_test:
        print(f"\n--- Testing size {size}px ---")
        
        # Code 128
        try:
            test_text = f"SIZE{size}TEST"
            c128 = generate_code128(test_text, size=size, human_text=test_text)
            filename = f"test_code128_{size}px.png"
            c128.save(filename)
            print(f"Code128 {size}px: {c128.size} -> {filename}")
        except Exception as e:
            print(f"Code128 {size}px failed: {e}")
        
        # PDF417
        try:
            test_text = f"PDF{size}DATA"
            p417 = generate_pdf417(test_text, size=size, human_text=test_text)
            filename = f"test_pdf417_{size}px.png"
            p417.save(filename)
            print(f"PDF417 {size}px: {p417.size} -> {filename}")
        except Exception as e:
            print(f"PDF417 {size}px failed: {e}")
    
    print("\nLarge barcode font scaling test completed.")

if __name__ == "__main__":
    test_large_barcodes()