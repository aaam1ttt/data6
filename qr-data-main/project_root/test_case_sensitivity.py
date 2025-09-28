#!/usr/bin/env python3

"""Test script to verify case sensitivity issues with code types"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_by_type

def test_case_sensitivity():
    test_text = "Test123"
    test_cases = [
        "QR", "qr", "Qr", "qR",
        "DM", "dm", "Dm", "dM", 
        "AZTEC", "aztec", "Aztec",
        "CODE128", "code128", "Code128",
        "PDF417", "pdf417", "Pdf417"
    ]
    
    for code_type in test_cases:
        try:
            img = generate_by_type(code_type, test_text, size=300)
            print(f"OK {code_type}: Success")
        except ValueError as e:
            print(f"FAIL {code_type}: {e}")
        except Exception as e:
            print(f"ERROR {code_type}: {e}")

if __name__ == "__main__":
    test_case_sensitivity()