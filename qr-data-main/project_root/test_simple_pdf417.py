#!/usr/bin/env python3

import sys
import os
import tempfile
sys.path.insert(0, os.path.abspath('.'))

def test_simple_pdf417():
    print("Testing simple PDF417...")
    
    try:
        import pdf417gen
        from pyzbar import pyzbar
        from PIL import Image
        
        # Create very simple PDF417
        text = "123"
        codes = pdf417gen.encode(text, columns=2, security_level=0)
        img = pdf417gen.render_image(codes, scale=10, ratio=3)
        
        print(f"Simple PDF417 size: {img.size}")
        
        # Save it
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            print(f"Saved: {f.name}")
        
        # Try to decode
        results = pyzbar.decode(img)
        print(f"Decode results: {len(results)}")
        
        for result in results:
            print(f"  Type: {result.type}")
            print(f"  Data: {result.data}")
            
        # Try different scales
        for scale in [5, 8, 12, 15]:
            test_img = pdf417gen.render_image(codes, scale=scale, ratio=3)
            test_results = pyzbar.decode(test_img)
            print(f"Scale {scale}: {len(test_results)} results")
            
            if test_results:
                print(f"  SUCCESS at scale {scale}")
                break
                
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_pdf417()