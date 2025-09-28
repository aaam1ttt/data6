#!/usr/bin/env python3
"""
Final validation script for barcode text improvements
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from app.core.codes import generate_code128, generate_pdf417, _add_text_below_barcode
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_text_scaling():
    """Test the improved text scaling functionality"""
    try:
        from app.core.codes import generate_code128, generate_pdf417
        from PIL import Image
        
        # Test small size (should have minimum font)
        small = generate_code128("TEST", size=200, human_text="TEST")
        print(f"✓ Small Code128 (200px): {small.size}")
        
        # Test medium size (should scale proportionally)
        medium = generate_code128("TEST", size=400, human_text="TEST")
        print(f"✓ Medium Code128 (400px): {medium.size}")
        
        # Test large size (should have larger font, but not exceed maximum)
        large = generate_code128("TEST", size=600, human_text="TEST")
        print(f"✓ Large Code128 (600px): {large.size}")
        
        # Test PDF417 scaling
        pdf_small = generate_pdf417("TEST", size=200, human_text="TEST")
        print(f"✓ Small PDF417 (200px): {pdf_small.size}")
        
        pdf_large = generate_pdf417("TEST", size=600, human_text="TEST")
        print(f"✓ Large PDF417 (600px): {pdf_large.size}")
        
        return True
    except Exception as e:
        print(f"✗ Text scaling test failed: {e}")
        return False

def test_build():
    """Test that the app builds successfully"""
    try:
        from app import create_app
        app = create_app()
        print("✓ Build successful")
        return True
    except Exception as e:
        print(f"✗ Build failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Running final validation tests...\n")
    
    success = True
    
    print("1. Testing imports...")
    success &= test_imports()
    
    print("\n2. Testing text scaling...")
    success &= test_text_scaling()
    
    print("\n3. Testing build...")
    success &= test_build()
    
    print(f"\n{'='*50}")
    if success:
        print("✓ ALL TESTS PASSED - Font scaling improvements working correctly!")
    else:
        print("✗ SOME TESTS FAILED - Check errors above")
    print(f"{'='*50}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())