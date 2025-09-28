#!/usr/bin/env python3
"""
Test scanner compatibility with high-quality QR codes
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_qr, save_image, decode_auto

def test_scanner_compatibility():
    """Test QR codes with different quality settings for scanner compatibility"""
    
    print("Testing scanner compatibility with improved QR quality...")
    print("=" * 60)
    
    test_data = [
        "https://example.com/test",
        "Simple Test 123",
        "Contact: John Doe, Phone: +1-234-567-8900, Email: test@example.com"
    ]
    
    # Test different quality configurations
    quality_configs = [
        {"size": 300, "ecc": "H", "name": "Standard High Quality"},
        {"size": 600, "ecc": "H", "name": "High Resolution"},
        {"size": 900, "ecc": "H", "name": "Ultra High Resolution"},
        {"size": 600, "ecc": "Q", "name": "Medium ECC Large"},
        {"size": 300, "ecc": "M", "name": "Standard Medium ECC"}
    ]
    
    total_tests = 0
    successful_scans = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for data_idx, test_text in enumerate(test_data):
            print(f"\nTest data {data_idx + 1}: {test_text[:40]}...")
            
            for config in quality_configs:
                total_tests += 1
                try:
                    # Generate QR code
                    qr_img = generate_qr(
                        test_text, 
                        size=config["size"], 
                        preferred_ecc=config["ecc"]
                    )
                    
                    # Save to temp file
                    temp_file = os.path.join(temp_dir, f"qr_{data_idx}_{config['name'].replace(' ', '_')}.png")
                    save_image(qr_img, temp_file)
                    
                    # Test decoding (simulating scanner)
                    decoded_results = decode_auto(qr_img)
                    
                    if decoded_results and len(decoded_results) > 0:
                        decoded_text = decoded_results[0].get('text', '').strip()
                        
                        if decoded_text == test_text.strip():
                            print(f"  [PASS] {config['name']} ({config['size']}px, ECC:{config['ecc']})")
                            successful_scans += 1
                        else:
                            print(f"  [FAIL] {config['name']} - Text mismatch")
                            print(f"    Expected: {test_text[:30]}...")
                            print(f"    Got: {decoded_text[:30]}...")
                    else:
                        print(f"  [FAIL] {config['name']} - Could not decode")
                        
                    # File size info
                    if os.path.exists(temp_file):
                        file_size = os.path.getsize(temp_file)
                        print(f"    File: {file_size} bytes")
                    
                except Exception as e:
                    print(f"  [ERROR] {config['name']}: {e}")
        
        print(f"\nScanner Compatibility Results:")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Successful scans: {successful_scans}")
        print(f"Success rate: {(successful_scans/total_tests)*100:.1f}%")
        
        if successful_scans == total_tests:
            print("\n[SUCCESS] All QR codes are scanner-compatible!")
            return True
        else:
            print(f"\n[PARTIAL] {total_tests - successful_scans} codes had scanning issues")
            return False

if __name__ == "__main__":
    success = test_scanner_compatibility()
    sys.exit(0 if success else 1)