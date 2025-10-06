#!/usr/bin/env python3
"""
Test template for scan preview fix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

def test_scan_template():
    """Test that scan.html has proper preview handling"""
    print("Testing scan.html preview logic...")
    
    with open('app/templates/scan.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for saveScanState with parameter
    assert 'saveScanState(includePreview' in content, "Should have saveScanState with includePreview parameter"
    
    # Check for user check in openFormBtn click handler
    assert 'const isLoggedIn' in content, "Should check if user is logged in"
    assert 'saveScanState(isLoggedIn)' in content, "Should call saveScanState with isLoggedIn flag"
    
    print("  [OK] scan.html has proper preview handling")
    return True

def test_app_builds():
    """Test that app still builds successfully"""
    print("\nTesting app build...")
    
    app = create_app()
    assert app is not None, "App should build successfully"
    
    print("  [OK] App builds successfully")
    return True

def main():
    print("=" * 60)
    print("Scan Preview Fix Test Suite")
    print("=" * 60)
    
    try:
        test_scan_template()
        test_app_builds()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
