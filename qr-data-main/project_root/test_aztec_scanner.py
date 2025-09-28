#!/usr/bin/env python3

"""Test script to verify Aztec codes can be scanned properly"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_aztec, decode_auto
import tempfile

def test_aztec_scanning():
    """Test if generated Aztec codes can be decoded"""
    
    test_texts = [
        "TEST123",
        "Hello World",
        "1234567890",
        "AZTEC_CODE_TEST"
    ]
    
    print("Testing Aztec code scanning...")
    
    for text in test_texts:
        print(f"\nTesting: '{text}'")
        
        try:
            # Generate Aztec code
            img = generate_aztec(text, 400)  # Use larger size for better scanning
            print(f"  Generated: {img.size}")
            
            # Try to decode it
            decoded_results = decode_auto(img)
            
            if decoded_results:
                print(f"  Decoded: {decoded_results}")
                if text in decoded_results:
                    print("  [SUCCESS] SCAN SUCCESS: Original text found")
                else:
                    print("  [PARTIAL] SCAN PARTIAL: Text decoded but doesn't match exactly")
            else:
                print("  [FAILED] SCAN FAILED: No text decoded")
                # Save for manual inspection
                with tempfile.NamedTemporaryFile(suffix=f'_aztec_{text[:8]}.png', delete=False) as tmp:
                    img.save(tmp.name)
                    print(f"  Saved for inspection: {tmp.name}")
                    
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\nAztec scanning test completed")

if __name__ == "__main__":
    test_aztec_scanning()