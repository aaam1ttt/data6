#!/usr/bin/env python3
"""
Test script for Aztec code generation fix
"""

import sys
import os
sys.path.append('.')

from app.core.codes import generate_aztec, generate_by_type
from PIL import Image

def test_aztec_generation():
    """Test Aztec code generation"""
    print("Testing Aztec code generation...")
    
    test_cases = [
        "Hello World",
        "Test123",
        "12345",
        "AZTEC TEST CODE",
        "https://example.com"
    ]
    
    for i, text in enumerate(test_cases):
        print(f"Testing case {i+1}: '{text}'")
        
        try:
            # Test direct aztec generation
            aztec_img = generate_aztec(text, 300)
            aztec_img.save(f"test_aztec_direct_{i+1}.png")
            print(f"  Direct generation: SUCCESS - {aztec_img.size}")
            
            # Test via generate_by_type
            aztec_img2 = generate_by_type("AZTEC", text, 300)
            aztec_img2.save(f"test_aztec_by_type_{i+1}.png")
            print(f"  By type generation: SUCCESS - {aztec_img2.size}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\nAztec generation test complete!")

if __name__ == "__main__":
    test_aztec_generation()