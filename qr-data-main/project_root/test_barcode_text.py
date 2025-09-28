#!/usr/bin/env python3
"""
Test script to verify increased font size for Code 128 and PDF417 barcode text labels
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_code128, generate_pdf417
from PIL import Image

def test_barcode_text():
    """Test Code 128 and PDF417 with human text to verify font size increase"""
    print("Testing barcode text font size improvements...")
    

    try:
        print("\n1. Testing Code 128 with human text...")
        code128_img = generate_code128("TEST123", size=400, human_text="TEST123")
        print(f"   Code 128 generated: {code128_img.size}")
        

        code128_img.save("test_code128_with_text.png")
        print("   Saved as: test_code128_with_text.png")
        
    except Exception as e:
        print(f"   [ERROR] Code 128 generation failed: {e}")
    

    try:
        print("\n2. Testing PDF417 with human text...")
        pdf417_img = generate_pdf417("TEST123", size=400, human_text="TEST123")
        print(f"   PDF417 generated: {pdf417_img.size}")
        

        pdf417_img.save("test_pdf417_with_text.png")
        print("   Saved as: test_pdf417_with_text.png")
        
    except Exception as e:
        print(f"   [ERROR] PDF417 generation failed: {e}")
    
    print("\nFont size test completed. Check generated images to verify text size increase.")

if __name__ == "__main__":
    test_barcode_text()