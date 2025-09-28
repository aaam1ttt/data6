#!/usr/bin/env python3

"""Test script to verify Aztec code quality and scannability"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_by_type, generate_aztec
from PIL import Image
import numpy as np

def test_aztec_quality():
    """Test various aspects of Aztec code quality"""
    
    test_cases = [
        ("Short", "ABC123"),
        ("Medium", "This is a medium length test string"),
        ("Long", "This is a much longer test string that should require a larger Aztec matrix to encode properly and test the scaling"),
        ("Unicode", "Тест русского текста 123"),
        ("Numbers", "1234567890" * 5),
    ]
    
    for name, text in test_cases:
        print(f"\nTesting {name}: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        try:
            # Test different sizes
            for size in [200, 300, 450]:
                img = generate_aztec(text, size)
                print(f"  Size {size}: Generated {img.size}")
                
                # Basic quality checks
                if img.mode != 'RGB':
                    print(f"    WARNING: Image mode is {img.mode}, expected RGB")
                
                # Check if image has proper contrast
                img_array = np.array(img.convert('L'))
                unique_values = len(np.unique(img_array))
                if unique_values < 2:
                    print(f"    ERROR: Poor contrast, only {unique_values} unique values")
                else:
                    print(f"    OK: Good contrast with {unique_values} levels")
                
                # Check for proper quiet zone (border should be white)
                border_width = size // 20
                top_border = img_array[:border_width, :]
                if np.mean(top_border) < 200:  # Should be mostly white
                    print(f"    WARNING: Quiet zone may be insufficient")
                else:
                    print(f"    OK: Proper quiet zone detected")
            
            # Test generate_by_type integration
            img_by_type = generate_by_type("aztec", text, 300)
            print(f"  generate_by_type: {img_by_type.size}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nAztec quality test completed")

def test_aztec_pattern():
    """Test that Aztec codes have proper finder pattern"""
    print("\nTesting Aztec finder pattern...")
    
    img = generate_aztec("TEST", 300)
    img_array = np.array(img.convert('L'))
    
    center = img_array.shape[0] // 2
    
    # Check for bullseye pattern in center
    center_region = img_array[center-10:center+11, center-10:center+11]
    
    if center_region.size > 0:
        # Should have alternating black/white rings
        center_pixel = center_region[10, 10]  # Should be white (center)
        if center_pixel > 128:
            print("  OK: Center pixel is white")
        else:
            print("  WARNING: Center pixel should be white")
    
    print("  Finder pattern test completed")

if __name__ == "__main__":
    test_aztec_quality()
    test_aztec_pattern()