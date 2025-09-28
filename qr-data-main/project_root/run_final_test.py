#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.codes import generate_by_type, decode_auto

# Test all barcode types
test_cases = [
    ("code128", "CODE128TEST"),
    ("pdf417", "PDF417TEST"),  
    ("aztec", "AZTECTEST")
]

print("Testing fixed barcodes...")

for code_type, text in test_cases:
    try:
        img = generate_by_type(code_type, text, 350)
        results = decode_auto(img)
        
        if results and results[0].get('text') == text:
            status = "WORKING"
        else:
            status = "NOT_SCANNING"
            
        print(f"{code_type}: {status}")
        
    except Exception as e:
        print(f"{code_type}: ERROR - {e}")

print("Test complete.")