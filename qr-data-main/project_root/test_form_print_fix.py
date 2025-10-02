#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test that print button works in all form templates
"""

import os
import re

def test_print_button_in_forms():
    """Check that all form templates include print size controls correctly"""
    
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    
    # List of all form templates to check
    form_templates = [
        'form_torg12.html',
        'form_message.html', 
        'form_exploitation.html',
        'form_transport.html',
        'form_custom.html',
        'form_env.html'
    ]
    
    all_pass = True
    
    for template_name in form_templates:
        try:
            template_path = os.path.join(template_dir, template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n[CHECKING] {template_name}")
            
            # Check 1: Template includes _print_size_controls.html
            if "{% include '_print_size_controls.html' %}" in content:
                print(f"  [OK] Includes _print_size_controls.html")
            else:
                print(f"  [FAIL] Missing include for _print_size_controls.html")
                all_pass = False
                continue
            
            # Check 2: Template calls initPrintSizeControls
            if 'initPrintSizeControls' in content:
                print(f"  [OK] Calls initPrintSizeControls")
            else:
                print(f"  [FAIL] Missing call to initPrintSizeControls")
                all_pass = False
                continue
            
            # Check 3: Template passes correct parameters
            if re.search(r'initPrintSizeControls\([^)]*code_type[^)]*size[^)]*encoded[^)]*\)', content):
                print(f"  [OK] Passes correct parameters (code_type, size, encoded)")
            else:
                print(f"  [FAIL] Missing or incorrect parameters")
                all_pass = False
                continue
                
            print(f"  [PASS] {template_name} is correctly configured")
            
        except Exception as e:
            print(f"  [ERROR] Failed to check {template_name}: {e}")
            all_pass = False
    
    print("\n" + "="*60)
    if all_pass:
        print("[SUCCESS] All form templates have print button correctly configured")
    else:
        print("[FAILURE] Some form templates have issues")
    print("="*60)
    
    return all_pass

if __name__ == '__main__':
    success = test_print_button_in_forms()
    exit(0 if success else 1)
