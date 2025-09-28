#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick validation of barcode fixes
"""

def validate_fixes():
    print("Validating barcode fixes...")
    
    try:
        # Check imports
        from app.core.codes import generate_by_type, decode_auto
        print("Import successful")
        
        # Test problematic codes
        test_cases = ["code128", "pdf417", "aztec"]
        
        for code_type in test_cases:
            try:
                # Generate
                img = generate_by_type(code_type, f"TEST-{code_type.upper()}", 300)
                print(f"[OK] {code_type}: Generation OK - {img.size}")
                
                # Basic decode test
                try:
                    results = decode_auto(img)
                    if results:
                        print(f"[OK] {code_type}: Decode OK - {len(results)} results")
                    else:
                        print(f"[WARN] {code_type}: Decode returned empty")
                except Exception as e:
                    print(f"[WARN] {code_type}: Decode error - {e}")
                    
            except Exception as e:
                print(f"[ERROR] {code_type}: Failed - {e}")
        
        print("\nBasic validation complete")
        return True
        
    except Exception as e:
        print(f"Validation failed: {e}")
        return False

if __name__ == "__main__":
    validate_fixes()