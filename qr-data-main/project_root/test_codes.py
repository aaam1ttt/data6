#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.codes import generate_by_type

def test_code_generation():
    print("Testing code generation...")
    
    types_to_test = ['QR', 'DM', 'C128', 'PDF417', 'AZTEC']
    
    for code_type in types_to_test:
        try:
            print(f'Testing {code_type}...')
            img = generate_by_type(code_type, 'test')
            print(f'{code_type} OK: {img.size}')
        except Exception as e:
            print(f'{code_type} Error: {e}')
            return False
    
    return True

if __name__ == "__main__":
    success = test_code_generation()
    sys.exit(0 if success else 1)