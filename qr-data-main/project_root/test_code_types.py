#!/usr/bin/env python3

"""Test script to verify code types work in generate_by_type function"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_by_type

def test_code_types():
    test_text = "Test123"
    code_types_to_test = ['QR', 'DM', 'AZTEC', 'CODE128', 'PDF417']
    
    for code_type in code_types_to_test:
        try:
            img = generate_by_type(code_type, test_text, size=300)
            print(f"OK {code_type}: Success")
        except ValueError as e:
            print(f"FAIL {code_type}: {e}")
        except Exception as e:
            print(f"ERROR {code_type}: Other error: {e}")

if __name__ == "__main__":
    test_code_types()