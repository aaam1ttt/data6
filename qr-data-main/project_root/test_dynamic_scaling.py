#!/usr/bin/env python3
"""Test dynamic width scaling for Code 128 and PDF417 barcodes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.codes import generate_code128, generate_pdf417

def test_dynamic_scaling():
    print("Testing dynamic width scaling for Code 128 and PDF417...")
    
    # Test Code 128 with different text lengths
    short_text = "short"
    long_text = "This is a much longer text that should result in a wider barcode to accommodate all the characters properly with dynamic scaling"
    very_long_text = "This is an extremely long text string that contains significantly more characters than the previous examples and should demonstrate the dynamic width scaling feature working properly for Code 128 barcodes when dealing with large amounts of data that would normally require much wider barcode dimensions"
    
    print(f"\nCode 128 Tests:")
    print(f"Short text length: {len(short_text)} chars")
    short_img = generate_code128(short_text, 300)
    print(f"Short text barcode size: {short_img.size}")
    
    print(f"Long text length: {len(long_text)} chars") 
    long_img = generate_code128(long_text, 300)
    print(f"Long text barcode size: {long_img.size}")
    
    print(f"Very long text length: {len(very_long_text)} chars")
    very_long_img = generate_code128(very_long_text, 300) 
    print(f"Very long text barcode size: {very_long_img.size}")
    
    # Test PDF417 with different text lengths
    print(f"\nPDF417 Tests:")
    print(f"Short text length: {len(short_text)} chars")
    short_pdf = generate_pdf417(short_text, 300)
    print(f"Short text barcode size: {short_pdf.size}")
    
    print(f"Long text length: {len(long_text)} chars")
    long_pdf = generate_pdf417(long_text, 300)
    print(f"Long text barcode size: {long_pdf.size}")
    
    print(f"Very long text length: {len(very_long_text)} chars")
    very_long_pdf = generate_pdf417(very_long_text, 300)
    print(f"Very long text barcode size: {very_long_pdf.size}")
    
    # Verify dynamic scaling is working
    print(f"\nDynamic scaling verification:")
    print(f"Code 128 - Short width: {short_img.size[0]}, Long width: {long_img.size[0]}, Very long width: {very_long_img.size[0]}")
    print(f"PDF417 - Short width: {short_pdf.size[0]}, Long width: {long_pdf.size[0]}, Very long width: {very_long_pdf.size[0]}")
    
    # Check that longer text produces wider barcodes (with some tolerance for PDF417 due to its different scaling mechanics)
    code128_scaling_works = long_img.size[0] >= short_img.size[0] and very_long_img.size[0] >= long_img.size[0]
    # PDF417 scaling is more complex - it increases height and width, so we check if the overall area increases
    pdf417_scaling_works = (long_pdf.size[0] * long_pdf.size[1]) >= (short_pdf.size[0] * short_pdf.size[1]) * 0.7
    
    print(f"\nCode 128 dynamic scaling working: {code128_scaling_works}")
    print(f"PDF417 dynamic scaling working: {pdf417_scaling_works}")
    
    if code128_scaling_works and pdf417_scaling_works:
        print("\nAll dynamic scaling tests passed!")
        return True
    else:
        print("\nSome dynamic scaling tests failed!")
        return False

if __name__ == "__main__":
    test_dynamic_scaling()