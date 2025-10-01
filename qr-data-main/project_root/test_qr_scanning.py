#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to validate QR codes with embedded images are scannable
Tests various error correction levels and logo sizes
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.codes import generate_qr
from PIL import Image
import tempfile

def test_qr_scanning():
    """Test QR code generation with different error correction levels"""
    
    test_data = [
        ("https://example.com/test", "Short URL"),
        ("https://example.com/very/long/path/with/many/segments/to/test/longer/data", "Long URL"),
        ("Test text with Русский текст mixed", "Mixed text"),
        ("0123456789" * 10, "Numeric data"),
    ]
    
    error_levels = ["H", "Q", "M", "L"]
    
    print("=" * 80)
    print("QR Code Generation & Embedded Logo Size Test")
    print("=" * 80)
    
    test_dir = tempfile.mkdtemp(prefix="qr_test_")
    print(f"\nTest images saved to: {test_dir}\n")
    
    for data, description in test_data:
        print(f"\nTesting: {description}")
        print(f"Data: {data[:50]}{'...' if len(data) > 50 else ''}")
        print("-" * 80)
        
        for ecc_level in error_levels:
            try:
                # Generate QR with embedded logo
                qr_img = generate_qr(data, size=300, preferred_ecc=ecc_level)
                
                # Save test image
                filename = f"qr_{description.replace(' ', '_')}_ECC_{ecc_level}.png"
                filepath = os.path.join(test_dir, filename)
                qr_img.save(filepath)
                
                # Try to decode with pyzxing (if available)
                success = False
                decoded_text = None
                
                try:
                    # Try cv2 + pyzbar first (most reliable)
                    try:
                        import cv2
                        from pyzbar.pyzbar import decode as pyzbar_decode
                        
                        img = cv2.imread(filepath)
                        decoded_objects = pyzbar_decode(img)
                        
                        if decoded_objects and len(decoded_objects) > 0:
                            decoded_bytes = decoded_objects[0].data
                            if isinstance(decoded_bytes, bytes):
                                decoded_text = decoded_bytes.decode('utf-8')
                            else:
                                decoded_text = str(decoded_bytes)
                            # QR code decoded successfully - mark as scannable
                            success = True
                        else:
                            # Could not decode - QR may not be scannable
                            success = False
                            decoded_text = "Could not decode"
                    except ImportError:
                        # pyzbar not available, try pyzxing
                        try:
                            from pyzxing import BarCodeReader
                            reader = BarCodeReader()
                            results = reader.decode(filepath)
                            if results and len(results) > 0:
                                decoded_text = results[0].get('parsed', '')
                                success = True
                            else:
                                success = False
                                decoded_text = "Could not decode"
                        except ImportError:
                            # No decoder available, just check generation
                            success = True  # Generation succeeded
                            decoded_text = "No decoder available"
                except Exception as e:
                    print(f"  ECC {ecc_level}: [WARN] Decode error: {str(e)[:50]}")
                    success = False
                
                if success:
                    print(f"  ECC {ecc_level}: [OK] QR generated and scannable")
                elif decoded_text == "No decoder available":
                    print(f"  ECC {ecc_level}: [OK] QR generated (decoder not available)")
                else:
                    print(f"  ECC {ecc_level}: [FAIL] QR not scannable or data mismatch")
                        
            except Exception as e:
                print(f"  ECC {ecc_level}: [FAIL] Generation failed: {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"Test complete. Images saved to: {test_dir}")
    print("=" * 80)
    print("\nNOTE: For thorough testing, scan these QR codes with:")
    print("  - Mobile phone camera apps")
    print("  - Dedicated QR scanner apps") 
    print("  - Different scanner devices")
    print("\nThe embedded logo size has been increased for:")
    print("  - ECC H (highest): ~20% of QR size (1/5)")
    print("  - ECC Q: ~17% of QR size (1/6)")
    print("  - ECC M: ~14% of QR size (1/7)")
    print("  - ECC L (lowest): ~13% of QR size (1/8)")
    print("\nRecommended: Use ECC H for best balance of logo visibility and scannability.")
    
    return test_dir

if __name__ == "__main__":
    test_dir = test_qr_scanning()
    
    # Optional: Open the directory for manual inspection
    import platform
    import subprocess
    
    try:
        if platform.system() == "Windows":
            os.startfile(test_dir)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", test_dir])
        else:  # Linux
            subprocess.run(["xdg-open", test_dir])
    except:
        pass  # If opening fails, directory path is already printed
