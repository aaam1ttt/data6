#!/usr/bin/env python3

import subprocess
import sys
import os

def run_test(test_file):
    """Run a test file and return result"""
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=os.getcwd())
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Run all tests"""
    print("Running comprehensive tests after comment removal...")
    print("=" * 60)
    
    tests = [
        ("Build Test", "test_build.py"),
        ("Web Functionality", "test_web_functionality.py"),
        ("Simple QR", "simple_qr_test.py"),
        ("Barcode Text", "test_barcode_text.py"),
        ("High Resolution", "test_high_res.py")
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_file in tests:
        print(f"\n--- Running {test_name} ({test_file}) ---")
        success, stdout, stderr = run_test(test_file)
        
        if success:
            print(f"[PASS] {test_name}: PASSED")
            passed += 1
        else:
            print(f"[FAIL] {test_name}: FAILED")
            if stdout:
                print("STDOUT:")
                print(stdout[:1000])
            if stderr:
                print("STDERR:")
                print(stderr[:1000])
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED - Comment removal was successful!")
        return True
    else:
        print("[ERROR] Some tests failed - Check output above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)