#!/usr/bin/env python3
"""
Comprehensive scanner test for all barcode types
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_by_type, decode_auto, save_image

def test_all_barcode_types():
    """Test generation and scanning of all supported barcode types"""
    
    print("Testing all barcode types generation and scanning...")
    print("=" * 70)
    
    # Test data for different code types
    test_cases = [
        {"type": "qr", "text": "https://example.com/qr-test", "label": "QR Code"},
        {"type": "dm", "text": "DM12345678", "label": "DataMatrix"},
        {"type": "code128", "text": "CODE128TEST", "label": "Code 128"},
        {"type": "pdf417", "text": "PDF417-DATA-TEST", "label": "PDF417"},
        {"type": "aztec", "text": "AZTEC-TEST-123", "label": "Aztec"},
    ]
    
    total_tests = 0
    successful_generations = 0
    successful_scans = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for test_case in test_cases:
            code_type = test_case["type"]
            test_text = test_case["text"]
            label = test_case["label"]
            
            total_tests += 1
            
            print(f"\n{label} ({code_type}):")
            print("-" * 40)
            
            try:
                # Try generation
                img = generate_by_type(code_type, test_text, size=400)
                print(f"  ✓ Generation: SUCCESS ({img.size})")
                successful_generations += 1
                
                # Save for debugging
                temp_file = os.path.join(temp_dir, f"{code_type}_test.png")
                save_image(img, temp_file)
                print(f"  ✓ Saved to: {temp_file}")
                
                # Try scanning
                decoded_results = decode_auto(img)
                
                if decoded_results and len(decoded_results) > 0:
                    decoded_text = decoded_results[0].get('text', '').strip()
                    detected_type = decoded_results[0].get('type', 'UNKNOWN')
                    
                    if decoded_text == test_text.strip():
                        print(f"  ✓ Scanning: SUCCESS")
                        print(f"    Detected type: {detected_type}")
                        print(f"    Text matches: {decoded_text}")
                        successful_scans += 1
                    else:
                        print(f"  ✗ Scanning: TEXT MISMATCH")
                        print(f"    Expected: {test_text}")
                        print(f"    Got: {decoded_text}")
                        print(f"    Detected type: {detected_type}")
                else:
                    print(f"  ✗ Scanning: FAILED - No data decoded")
                    print(f"    Decoder results: {decoded_results}")
                    
            except Exception as e:
                print(f"  ✗ Generation: FAILED - {str(e)}")
                print(f"    Error type: {type(e).__name__}")
                import traceback
                print(f"    Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST RESULTS:")
    print("=" * 70)
    print(f"Total tests: {total_tests}")
    print(f"Successful generations: {successful_generations}/{total_tests}")
    print(f"Successful scans: {successful_scans}/{total_tests}")
    print(f"Generation rate: {(successful_generations/total_tests)*100:.1f}%")
    print(f"Scanning rate: {(successful_scans/total_tests)*100:.1f}%")
    
    if successful_generations == total_tests and successful_scans == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  ISSUES FOUND:")
        if successful_generations < total_tests:
            print(f"   - {total_tests - successful_generations} generation failures")
        if successful_scans < total_tests:
            print(f"   - {total_tests - successful_scans} scanning failures")
        return False

if __name__ == "__main__":
    success = test_all_barcode_types()
    sys.exit(0 if success else 1)