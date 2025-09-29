#!/usr/bin/env python3
"""
Visual test for Aztec code generation
"""

import sys
import os
sys.path.append('.')

from app.core.codes import generate_aztec, decode_auto
from PIL import Image

def test_aztec_visual():
    """Test Aztec code visual appearance and decoding"""
    print("Testing Aztec code visual appearance...")
    
    test_text = "AZTEC"
    
    # Generate Aztec code
    aztec_img = generate_aztec(test_text, 575)  # Same size as in the provided image
    aztec_img.save("test_aztec_575x575.png")
    
    print(f"Generated Aztec code: {aztec_img.size}")
    print(f"Mode: {aztec_img.mode}")
    
    # Test decoding
    try:
        decoded = decode_auto(aztec_img)
        print(f"Decoded results: {decoded}")
        
        if decoded and any(result.get('type') == 'AZTEC' for result in decoded):
            print("SUCCESS: Successfully generated and decoded Aztec code!")
        else:
            print("WARNING: Generated Aztec code but decoding failed or wrong type")
            
    except Exception as e:
        print(f"Decoding error: {e}")
    
    # Generate smaller version for comparison
    aztec_small = generate_aztec(test_text, 300)
    aztec_small.save("test_aztec_300x300.png")
    
    print("Visual test complete! Check generated PNG files.")

if __name__ == "__main__":
    test_aztec_visual()