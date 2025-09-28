#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
sys.path.insert(0, os.path.abspath('.'))

def test_decoder():
    print("Testing decoder issues...")
    
    try:
        from app.core.codes import generate_by_type, decode_auto, save_image
        
        # Test with QR first (known working)
        qr_img = generate_by_type("qr", "TEST QR", 300)
        qr_results = decode_auto(qr_img)
        print(f"QR decode test: {len(qr_results) if qr_results else 0} results")
        
        if qr_results:
            print(f"QR result: {qr_results[0]}")
        
        # Test Code128 generation and check what happens
        c128_img = generate_by_type("code128", "TEST123", 300)
        print(f"Code128 generated: {c128_img.size}")
        
        # Save to file for manual inspection
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            save_image(c128_img, f.name)
            print(f"Code128 saved to: {f.name}")
        
        # Try to decode
        c128_results = decode_auto(c128_img)
        print(f"Code128 decode results: {c128_results}")
        
        # Check what pyzbar can see
        try:
            from pyzbar import pyzbar
            pyzbar_results = pyzbar.decode(c128_img)
            print(f"Direct pyzbar results: {pyzbar_results}")
            for obj in pyzbar_results:
                print(f"  Type: {obj.type}, Data: {obj.data}")
        except Exception as e:
            print(f"Pyzbar direct test failed: {e}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_decoder()