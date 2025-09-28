#!/usr/bin/env python3
"""
Final comprehensive test for scanning fixes
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.codes import generate_by_type, decode_auto, save_image

def test_all_fixed_barcodes():
    """Test all problematic barcode types with fixes"""
    
    print("🔧 Testing Fixed Barcode Generation and Scanning")
    print("=" * 60)
    
    # Test cases for problematic codes
    test_cases = [
        {
            "type": "code128", 
            "text": "TESTCODE128", 
            "label": "Code 128",
            "expected_issues": "Scanning problems"
        },
        {
            "type": "pdf417", 
            "text": "PDF417-TEST-DATA-123", 
            "label": "PDF417",
            "expected_issues": "Generation/scanning errors"
        },
        {
            "type": "aztec", 
            "text": "AZTEC-CODE-TEST", 
            "label": "Aztec Code",
            "expected_issues": "Custom implementation issues"
        }
    ]
    
    results = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for test_case in test_cases:
            code_type = test_case["type"]
            test_text = test_case["text"]
            label = test_case["label"]
            
            print(f"\n🧪 Testing {label} ({code_type}):")
            print("-" * 40)
            
            generation_success = False
            scanning_success = False
            error_msg = None
            
            try:
                # Test generation
                print("  🔨 Generating barcode...")
                img = generate_by_type(code_type, test_text, size=500)  # Larger size for better scanning
                generation_success = True
                print(f"    ✅ Generated successfully: {img.size}")
                
                # Save for inspection
                temp_file = os.path.join(temp_dir, f"{code_type}_fixed.png")
                save_image(img, temp_file)
                print(f"    💾 Saved: {temp_file}")
                
                # Test scanning
                print("  🔍 Testing scanning...")
                decoded_results = decode_auto(img)
                
                if decoded_results and len(decoded_results) > 0:
                    decoded_text = decoded_results[0].get('text', '').strip()
                    detected_type = decoded_results[0].get('type', 'UNKNOWN')
                    
                    if decoded_text == test_text.strip():
                        scanning_success = True
                        print(f"    ✅ Scanned successfully!")
                        print(f"    📋 Detected type: {detected_type}")
                        print(f"    📄 Text matches: '{decoded_text}'")
                    else:
                        print(f"    ❌ Text mismatch!")
                        print(f"       Expected: '{test_text}'")
                        print(f"       Got: '{decoded_text}'")
                        print(f"       Type: {detected_type}")
                else:
                    print(f"    ❌ No data decoded from barcode")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"    ❌ Error: {error_msg}")
                import traceback
                print(f"    🔍 Details: {traceback.format_exc()}")
            
            # Record results
            results[code_type] = {
                'generation': generation_success,
                'scanning': scanning_success,
                'error': error_msg,
                'expected_issues': test_case['expected_issues']
            }
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS:")
    print("=" * 60)
    
    total_tests = len(test_cases)
    working_generation = sum(1 for r in results.values() if r['generation'])
    working_scanning = sum(1 for r in results.values() if r['scanning'])
    
    for code_type, result in results.items():
        status_gen = "✅" if result['generation'] else "❌"
        status_scan = "✅" if result['scanning'] else "❌"
        
        print(f"{code_type.upper():10} | Gen: {status_gen} | Scan: {status_scan}")
        if result['error']:
            print(f"            └─ Error: {result['error']}")
        print(f"            └─ Previous issue: {result['expected_issues']}")
    
    print(f"\nGeneration success: {working_generation}/{total_tests}")
    print(f"Scanning success: {working_scanning}/{total_tests}")
    
    if working_generation == total_tests and working_scanning == total_tests:
        print("\n🎉 ALL ISSUES FIXED! All barcodes now work properly!")
        return True
    else:
        print(f"\n⚠️  Still have issues:")
        if working_generation < total_tests:
            print(f"   - {total_tests - working_generation} generation failures")
        if working_scanning < total_tests:
            print(f"   - {total_tests - working_scanning} scanning failures")
        return False

if __name__ == "__main__":
    success = test_all_fixed_barcodes()
    sys.exit(0 if success else 1)