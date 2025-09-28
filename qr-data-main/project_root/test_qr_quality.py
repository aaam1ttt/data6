#!/usr/bin/env python3
"""
Test script to verify QR code quality improvements.
Tests generation with different parameters and attempts to decode generated codes.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_qr, generate_dm, generate_aztec, decode_auto, save_image
from PIL import Image
import tempfile
import json

def test_qr_quality():
    """Test QR code generation with various quality settings"""
    
    test_data = [
        "Simple test text",
        "https://example.com/test?param=value&other=123",
        "Тестовый текст на русском языке с кириллицей",
        "Complex JSON data: " + json.dumps({"name": "Test User", "id": 12345, "roles": ["admin", "user"], "active": True}),
        "Very long text " * 50  # Long text to test capacity
    ]
    
    sizes = [300, 600, 900]  # Test different output sizes
    error_levels = ["H", "Q", "M", "L"]
    
    print("Testing QR code quality improvements...")
    print("=" * 50)
    
    total_tests = 0
    successful_tests = 0
    
    for i, text in enumerate(test_data):
        print(f"\nTest {i+1}: Text length {len(text)} chars")
        print(f"Text preview: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        for size in sizes:
            for ecc in error_levels:
                total_tests += 1
                try:
                    # Generate QR code
                    qr_img = generate_qr(text, size=size, preferred_ecc=ecc)
                    
                    # Verify dimensions
                    if qr_img.size != (size, size):
                        print(f"  [ERROR] Size mismatch for {size}px/{ecc}: got {qr_img.size}")
                        continue
                    
                    # Test decoding
                    decoded = decode_auto(qr_img)
                    if decoded and len(decoded) > 0:
                        decoded_text = decoded[0].get('text', '')
                        if decoded_text.strip() == text.strip():
                            print(f"  [OK] {size}px/{ecc}: Generated and decoded successfully")
                            successful_tests += 1
                        else:
                            print(f"  [ERROR] {size}px/{ecc}: Decode mismatch")
                            print(f"     Expected: {text[:30]}...")
                            print(f"     Got: {decoded_text[:30]}...")
                    else:
                        print(f"  [ERROR] {size}px/{ecc}: Could not decode generated QR")
                        
                except Exception as e:
                    if "Слишком длинный текст" in str(e):
                        print(f"  [WARN] {size}px/{ecc}: Text too long for this ECC level")
                    else:
                        print(f"  [ERROR] {size}px/{ecc}: Error - {e}")
    
    # Test other code types
    print(f"\nTesting other barcode types...")
    test_text = "Test123"
    
    try:
        dm_img = generate_dm(test_text, 600)
        decoded_dm = decode_auto(dm_img)
        if decoded_dm:
            print("  [OK] DataMatrix: Generated and decoded successfully")
            successful_tests += 1
        else:
            print("  [ERROR] DataMatrix: Could not decode")
        total_tests += 1
    except Exception as e:
        print(f"  [ERROR] DataMatrix: Error - {e}")
        total_tests += 1
    
    try:
        aztec_img = generate_aztec(test_text, 600)
        decoded_aztec = decode_auto(aztec_img)
        if decoded_aztec:
            print("  [OK] Aztec (QR fallback): Generated and decoded successfully")
            successful_tests += 1
        else:
            print("  [ERROR] Aztec (QR fallback): Could not decode")
        total_tests += 1
    except Exception as e:
        print(f"  [ERROR] Aztec: Error - {e}")
        total_tests += 1
    
    print(f"\nTest Results:")
    print(f"=" * 50)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

def test_visual_quality():
    """Generate sample images for visual quality inspection"""
    print(f"\nGenerating sample images for visual inspection...")
    
    sample_text = "https://example.com/test-qr-quality-check"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test different sizes and quality settings
        test_configs = [
            (300, "H", "300px_high_quality"),
            (600, "H", "600px_high_quality"), 
            (900, "H", "900px_high_quality"),
            (300, "M", "300px_medium_quality"),
            (600, "M", "600px_medium_quality"),
        ]
        
        for size, ecc, filename in test_configs:
            try:
                img = generate_qr(sample_text, size=size, preferred_ecc=ecc)
                file_path = os.path.join(temp_dir, f"{filename}.png")
                save_image(img, file_path)
                
                # Verify file was created and get size
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  [OK] {filename}: {size}x{size}px, {file_size} bytes, ECC:{ecc}")
                else:
                    print(f"  [ERROR] {filename}: File not created")
                    
            except Exception as e:
                print(f"  [ERROR] {filename}: Error - {e}")
        
        print(f"\nSample images generated in: {temp_dir}")
        print("(Note: Temporary directory will be cleaned up automatically)")

if __name__ == "__main__":
    print("QR Code Quality Test")
    print("=" * 50)
    
    success = test_qr_quality()
    test_visual_quality()
    
    if success:
        print(f"\n[SUCCESS] All quality tests passed!")
        sys.exit(0)
    else:
        print(f"\n[FAILED] Some tests failed. Check the output above for details.")
        sys.exit(1)