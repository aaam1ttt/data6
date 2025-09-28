#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_decode_fix():
    print("Testing barcode decode fixes...")
    
    try:
        from app.core.codes import generate_by_type, decode_auto
        
        # Test each problematic type
        test_cases = [
            ("code128", "TESTCODE128"),
            ("pdf417", "PDF417TESTDATA"),  
            ("aztec", "AZTECTEST")
        ]
        
        for code_type, text in test_cases:
            print(f"\nTesting {code_type}:")
            
            # Generate barcode
            img = generate_by_type(code_type, text, 400)  # Larger size
            print(f"  Generated: {img.size}")
            
            # Try to decode
            results = decode_auto(img)
            print(f"  Decode results: {results}")
            
            if results:
                decoded_text = results[0].get('text', '')
                detected_type = results[0].get('type', 'UNKNOWN')
                print(f"  SUCCESS: '{decoded_text}' ({detected_type})")
                
                if decoded_text == text:
                    print(f"  TEXT MATCH: Perfect!")
                else:
                    print(f"  TEXT MISMATCH: Expected '{text}'")
            else:
                print(f"  FAILED: No decode results")
                
                # Try direct pyzbar test
                try:
                    from pyzbar import pyzbar
                    direct_results = pyzbar.decode(img)
                    print(f"  Direct pyzbar: {len(direct_results)} results")
                    for obj in direct_results:
                        print(f"    {obj.type}: {obj.data}")
                except Exception as e:
                    print(f"  Direct pyzbar error: {e}")
        
        print("\nDecode test complete.")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_decode_fix()