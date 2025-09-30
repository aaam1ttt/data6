#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test UI changes for QR code preview window resizing
"""

import sys
import os
import re

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

def test_scan_html_changes():
    """Test that scan.html has correct preview window sizes"""
    try:
        with open('app/templates/scan.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that preview image has reduced size (210px instead of 420px)
        if 'max-height:210px' in content and 'min-height:210px' in content:
            print("✓ scan.html: Preview window size reduced by half (210px)")
        else:
            print("✗ scan.html: Preview window size not properly reduced")
            return False
        
        # Check that dynamic resize function exists
        if 'function dynamicResize(img)' in content:
            print("✓ scan.html: Dynamic resize function exists")
        else:
            print("✗ scan.html: Dynamic resize function not found")
            return False
        
        # Check that dynamic resize is called
        if 'dynamicResize(previewImg)' in content:
            print("✓ scan.html: Dynamic resize function is called")
        else:
            print("✗ scan.html: Dynamic resize function not called")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing scan.html: {e}")
        return False

def test_form_create_live_changes():
    """Test that form_create_live.html has correct preview window sizes"""
    try:
        with open('app/templates/form_create_live.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that preview image has reduced size (210px instead of 420px)
        if 'max-height:210px' in content and 'min-height:210px' in content:
            print("✓ form_create_live.html: Preview window size reduced by half (210px)")
        else:
            print("✗ form_create_live.html: Preview window size not properly reduced")
            return False
        
        # Check that dynamic resize function exists
        if 'function dynamicResize(img)' in content:
            print("✓ form_create_live.html: Dynamic resize function exists")
        else:
            print("✗ form_create_live.html: Dynamic resize function not found")
            return False
        
        # Check that dynamic resize is called in renderPreview
        if 'dynamicResize(previewImg)' in content:
            print("✓ form_create_live.html: Dynamic resize function is called")
        else:
            print("✗ form_create_live.html: Dynamic resize function not called")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing form_create_live.html: {e}")
        return False

def test_create_html_changes():
    """Test that create.html has correct preview window sizes"""
    try:
        with open('app/templates/create.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that dynamic resize function exists
        if 'function dynamicResize(img)' in content:
            print("✓ create.html: Dynamic resize function exists")
        else:
            print("✗ create.html: Dynamic resize function not found")
            return False
        
        # Check that dynamic resize is called
        if 'dynamicResize(previewImg)' in content:
            print("✓ create.html: Dynamic resize function is called")
        else:
            print("✗ create.html: Dynamic resize function not called")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing create.html: {e}")
        return False

def test_base_css_changes():
    """Test that base.html has correct CSS for preview"""
    try:
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that preview CSS has reduced size
        if 'max-height:210px' in content and 'min-height:210px' in content:
            print("✓ base.html: Preview CSS updated with reduced size (210px)")
        else:
            print("✗ base.html: Preview CSS not properly updated")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing base.html: {e}")
        return False

def main():
    """Run all UI tests"""
    print("Testing UI changes for QR code preview window resizing\n")
    print("=" * 60)
    
    results = []
    
    print("\n1. Testing scan.html changes:")
    print("-" * 60)
    results.append(test_scan_html_changes())
    
    print("\n2. Testing form_create_live.html changes:")
    print("-" * 60)
    results.append(test_form_create_live_changes())
    
    print("\n3. Testing create.html changes:")
    print("-" * 60)
    results.append(test_create_html_changes())
    
    print("\n4. Testing base.html CSS changes:")
    print("-" * 60)
    results.append(test_base_css_changes())
    
    print("\n" + "=" * 60)
    if all(results):
        print("\n✓ ALL TESTS PASSED")
        print("\nSummary:")
        print("- Preview window size reduced by half (420px → 210px)")
        print("- Dynamic resizing implemented for larger QR codes (>600px)")
        print("- Changes applied to scan upload view, code creation view, and base CSS")
        return True
    else:
        print("\n✗ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
