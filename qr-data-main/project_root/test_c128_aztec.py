#!/usr/bin/env python3

"""Test script to verify C128 and AZTEC code types work"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_by_type

def test_c128_aztec():
    test_text = "Test123"
    code_types_to_test = ['C128', 'AZTEC']
    
    for code_type in code_types_to_test:
        try:
            img = generate_by_type(code_type, test_text, size=300)
            print(f"OK {code_type}: Success - {img.size}")
        except ValueError as e:
            print(f"FAIL {code_type}: {e}")
        except Exception as e:
            print(f"ERROR {code_type}: Other error: {e}")
    
    # Test case sensitivity
    for code_type in ['c128', 'aztec']:
        try:
            img = generate_by_type(code_type, test_text, size=300)
            print(f"OK {code_type} (lowercase): Success - {img.size}")
        except Exception as e:
            print(f"ERROR {code_type} (lowercase): {e}")

if __name__ == "__main__":
    test_c128_aztec()