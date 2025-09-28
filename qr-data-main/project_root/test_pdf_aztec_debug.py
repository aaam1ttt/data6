#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
sys.path.insert(0, os.path.abspath('.'))

def debug_pdf_aztec():
    print("Debug PDF417 and Aztec generation...")
    
    try:
        from app.core.codes import generate_pdf417, generate_aztec
        import pdf417gen
        
        # Test raw PDF417
        print("\n=== PDF417 Debug ===")
        test_text = "SIMPLE123"
        
        # Direct PDF417gen test
        codes = pdf417gen.encode(test_text, columns=3, security_level=1)
        raw_img = pdf417gen.render_image(codes, scale=8, ratio=3)
        print(f"Raw PDF417gen: {raw_img.size}")
        
        # Save for inspection
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            raw_img.save(f.name)
            print(f"Raw PDF417 saved: {f.name}")
        
        # Our implementation
        our_img = generate_pdf417(test_text, 300)
        print(f"Our PDF417: {our_img.size}")
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            our_img.save(f.name)
            print(f"Our PDF417 saved: {f.name}")
        
        # Test decode on raw
        from app.core.codes import decode_auto
        raw_decode = decode_auto(raw_img)
        our_decode = decode_auto(our_img)
        print(f"Raw decode: {raw_decode}")
        print(f"Our decode: {our_decode}")
        
        # === Aztec Debug ===
        print("\n=== Aztec Debug ===")
        
        # Try treepoem if available
        try:
            import treepoem
            aztec_img = treepoem.generate_barcode('azteccode', test_text)
            print(f"Treepoem Aztec: {aztec_img.size}")
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                aztec_img.save(f.name)
                print(f"Treepoem Aztec saved: {f.name}")
            
            aztec_decode = decode_auto(aztec_img)
            print(f"Treepoem decode: {aztec_decode}")
            
        except ImportError:
            print("Treepoem not available")
        except Exception as e:
            print(f"Treepoem error: {e}")
        
        # Our implementation
        our_aztec = generate_aztec(test_text, 300)
        print(f"Our Aztec: {our_aztec.size}")
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            our_aztec.save(f.name)
            print(f"Our Aztec saved: {f.name}")
            
        our_aztec_decode = decode_auto(our_aztec)
        print(f"Our Aztec decode: {our_aztec_decode}")
        
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_aztec()