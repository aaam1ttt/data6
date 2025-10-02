#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test syntax for _print_size_controls.html
"""

def test_template_syntax():
    """Check that _print_size_controls.html loads without errors"""
    from jinja2 import Environment, FileSystemLoader
    import os
    
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    try:
        template = env.get_template('_print_size_controls.html')
        print("[OK] Template _print_size_controls.html is syntactically correct")
        
        # Check that template can be rendered
        result = template.render()
        print("[OK] Template renders successfully")
        
        # Check for key elements
        assert 'printBtn' in result, "Button printBtn is missing"
        assert 'printDropdown' in result, "Dropdown printDropdown is missing"
        assert 'printSizeSelect' in result, "Select printSizeSelect is missing"
        assert 'initPrintSizeControls' in result, "Function initPrintSizeControls is missing"
        assert 'GOST_PRESETS' in result, "Constant GOST_PRESETS is missing"
        print("[OK] All key elements are present")
        
        # Check JavaScript structure
        assert result.count('GOST_PRESETS = {') == 1, "Invalid GOST_PRESETS structure"
        assert 'QR:' in result and 'DM:' in result and 'C128:' in result, "Code types are missing"
        print("[OK] JavaScript structure is correct")
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_template_syntax()
    exit(0 if success else 1)
