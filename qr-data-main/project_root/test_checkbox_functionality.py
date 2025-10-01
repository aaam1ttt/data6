#!/usr/bin/env python3
"""
Test checkbox functionality for lock editing feature
"""
import sys
import os
import re
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

def test_form_create_live_checkbox():
    """Test that form_create_live.html has the correct checkbox"""
    print("Testing form_create_live.html checkbox...")
    
    with open('app/templates/form_create_live.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for lockEdit checkbox
    assert 'id="lockEdit"' in content, "Should have lockEdit checkbox"
    assert 'type="checkbox"' in content, "Should be a checkbox element"
    assert 'Заблокировать редактирование' in content, "Should have correct label text"
    
    # Check that old allowEdit is removed
    assert 'id="allowEdit"' not in content, "Should not have old allowEdit checkbox"
    assert 'Разрешить редактирование' not in content, "Should not have old label text"
    
    # Check for red accent color
    assert 'accent-color:#ef4444' in content or 'accent-color: #ef4444' in content, "Should have red accent color"
    
    # Check JavaScript uses lockEdit
    assert 'lockEdit.addEventListener' in content, "JavaScript should use lockEdit"
    assert 'lockEdit.checked' in content, "JavaScript should check lockEdit.checked"
    
    # Make sure allowEdit is not referenced
    assert 'allowEdit.addEventListener' not in content, "JavaScript should not use allowEdit"
    
    print("  [OK] form_create_live.html checkbox is correct")
    return True

def test_form_torg12_checkbox():
    """Test that form_torg12.html has the correct checkbox"""
    print("\nTesting form_torg12.html checkbox...")
    
    with open('app/templates/form_torg12.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for lockEdit checkbox
    assert 'id="lockEdit"' in content, "Should have lockEdit checkbox"
    assert 'type="checkbox"' in content, "Should be a checkbox element"
    assert 'Заблокировать редактирование' in content, "Should have correct label text"
    
    # Check that old readonlyToggle is removed
    assert 'id="readonlyToggle"' not in content, "Should not have old readonlyToggle checkbox"
    
    # Check for red accent color
    assert 'accent-color:#ef4444' in content or 'accent-color: #ef4444' in content, "Should have red accent color"
    
    # Check JavaScript uses lockEdit
    assert 'lockEdit.addEventListener' in content, "JavaScript should use lockEdit"
    assert 'lockEdit.checked' in content or 'isLocked' in content, "JavaScript should check lockEdit state"
    
    # Make sure readonlyToggle is not referenced
    assert 'readonlyToggle.addEventListener' not in content, "JavaScript should not use readonlyToggle"
    
    print("  [OK] form_torg12.html checkbox is correct")
    return True

def test_checkbox_logic():
    """Test that checkbox logic is inverted correctly"""
    print("\nTesting checkbox logic...")
    
    with open('app/templates/form_create_live.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that logic is inverted (locked = checked)
    # When checked (locked), contentEditable should be "false"
    assert 'lockEdit.checked ? "false" : "true"' in content, "Should use inverted logic for contentEditable"
    
    # Check that applyBtn is hidden when locked
    assert 'lockEdit.checked ? \'none\' : \'inline-block\'' in content, "Should hide applyBtn when locked"
    
    print("  [OK] Checkbox logic is correct")
    return True

def test_base_template_css():
    """Test that base.html CSS is updated"""
    print("\nTesting base.html CSS...")
    
    with open('app/templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that editToggleLabel CSS exists and is simplified
    assert '#editToggleLabel {' in content, "Should have editToggleLabel CSS"
    
    # Old complex toggle button CSS should not have display:none for checkbox
    assert not re.search(r'#editToggleLabel input\[type="checkbox"\]\s*\{[^}]*display:\s*none', content), \
        "Should not hide checkbox with display:none"
    
    print("  [OK] base.html CSS is updated")
    return True

def main():
    print("=" * 60)
    print("Checkbox Functionality Test Suite")
    print("=" * 60)
    
    try:
        test_form_create_live_checkbox()
        test_form_torg12_checkbox()
        test_checkbox_logic()
        test_base_template_css()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All checkbox tests PASSED!")
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
