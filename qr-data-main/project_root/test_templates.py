#!/usr/bin/env python3
"""
Test template structure for size selection functionality
"""
import sys
import os
import re
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

def test_size_preset_js_syntax():
    """Test that _size_preset_js.html has valid JavaScript structure"""
    print("Testing _size_preset_js.html syntax...")
    
    with open('app/templates/_size_preset_js.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for GOST_PRESETS object structure
    assert 'const GOST_PRESETS={' in content, "Should have GOST_PRESETS object"
    
    # Check for all code types
    assert 'QR:[' in content, "Should have QR presets"
    assert 'DM:[' in content, "Should have DM presets"
    assert 'C128:[' in content, "Should have C128 presets"
    assert 'PDF417:[' in content, "Should have PDF417 presets"
    assert 'AZTEC:[' in content, "Should have AZTEC presets"
    
    # Count brackets - they should be balanced
    open_curly = content.count('{')
    close_curly = content.count('}')
    open_square = content.count('[')
    close_square = content.count(']')
    
    assert open_curly == close_curly, f"Unbalanced curly brackets: {open_curly} open, {close_curly} close"
    assert open_square == close_square, f"Unbalanced square brackets: {open_square} open, {close_square} close"
    
    # Check that there are no double closing brackets
    assert ']\n    ]' not in content, "Should not have double closing square brackets"
    # Check proper object closing
    assert ']' in content and '};' in content, "Should properly close GOST_PRESETS object"
    
    print("  [OK] JavaScript syntax is correct")
    return True

def test_form_templates_have_size_elements():
    """Test that all form templates have size selection elements"""
    print("\nTesting form templates for size selection elements...")
    
    templates = [
        ('app/templates/form_torg12.html', 't_type', 't_size'),
        ('app/templates/form_message.html', 'm_type', 'm_size'),
        ('app/templates/form_transport.html', 'code_type', 'size'),
        ('app/templates/form_exploitation.html', 'code_type', 'size'),
        ('app/templates/form_custom.html', 'code_type', 'size'),
    ]
    
    for template_path, type_id, size_id in templates:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for type select element
        assert f'id="{type_id}"' in content, f"{template_path} should have type select with id={type_id}"
        
        # Check for size select element
        assert f'id="{size_id}"' in content, f"{template_path} should have size select with id={size_id}"
        
        print(f"  [OK] {template_path} has required size elements")
    
    return True

def test_create_live_template():
    """Test form_create_live.html for size selection"""
    print("\nTesting form_create_live.html...")
    
    with open('app/templates/form_create_live.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for code type and size preset selects
    assert 'id="codeType"' in content, "Should have codeType select"
    assert 'id="sizePreset"' in content, "Should have sizePreset select"
    
    # Check for PRESETS object
    assert 'const PRESETS' in content or 'PRESETS=' in content, "Should have PRESETS object"
    
    print("  [OK] form_create_live.html has required elements")
    return True

def test_api_receives_size():
    """Test that API endpoints properly receive size parameter"""
    print("\nTesting API endpoints for size parameter handling...")
    
    app = create_app()
    with app.test_client() as client:
        # Test with QR code
        response = client.post('/forms/api_generate',
                              json={"text": "Test", "code_type": "QR", "size": 236},
                              headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200, "API should accept size parameter"
        json_data = response.get_json()
        assert json_data.get('ok') == True, "API should succeed with size parameter"
        
        print("  [OK] API endpoint properly handles size parameter")
    
    return True

def test_gost_code_storage():
    """Test that GOST code is stored in hidden input"""
    print("\nTesting GOST code storage...")
    
    with open('app/templates/form_torg12.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for hidden GOST code input
    assert 'name="gost_code"' in content, "Should have hidden gost_code input"
    assert 'id="gost_code"' in content, "Should have gost_code id"
    
    print("  [OK] GOST code storage implemented correctly")
    return True

def main():
    print("=" * 60)
    print("Template Size Selection Test Suite")
    print("=" * 60)
    
    try:
        test_size_preset_js_syntax()
        test_form_templates_have_size_elements()
        test_create_live_template()
        test_api_receives_size()
        test_gost_code_storage()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All template tests PASSED!")
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
