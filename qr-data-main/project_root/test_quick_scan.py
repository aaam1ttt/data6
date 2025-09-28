#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_quick():
    try:
        from app.core.codes import generate_code128, generate_pdf417, generate_aztec
        
        # Test Code 128
        try:
            img = generate_code128("TEST123", 300)
            print(f"Code128: OK - {img.size}")
        except Exception as e:
            print(f"Code128: FAIL - {e}")
        
        # Test PDF417
        try:
            img = generate_pdf417("TEST123", 300)
            print(f"PDF417: OK - {img.size}")
        except Exception as e:
            print(f"PDF417: FAIL - {e}")
        
        # Test Aztec
        try:
            img = generate_aztec("TEST123", 300)
            print(f"Aztec: OK - {img.size}")
        except Exception as e:
            print(f"Aztec: FAIL - {e}")
            
    except ImportError as e:
        print(f"Import failed: {e}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    test_quick()