"""
Test that print controls are properly initialized in all form templates
"""

import os
import re

def test_print_controls_in_forms():
    """Test that all form templates include print size controls and initialize them"""
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    
    form_templates = [
        'form_torg12.html',
        'form_message.html',
        'form_exploitation.html',
        'form_transport.html',
        'form_custom.html',
        'form_env.html'
    ]
    
    print("=" * 60)
    print("Form Print Controls Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    for template in form_templates:
        template_path = os.path.join(template_dir, template)
        
        if not os.path.exists(template_path):
            print(f"  [SKIP] {template} not found")
            continue
            
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for print controls include
        has_include = "{% include '_print_size_controls.html' %}" in content
        
        # Check for initialization (could be with window. prefix or without)
        has_init = "initPrintSizeControls" in content or "window.initPrintSizeControls" in content
        
        # Check if both are present in result section
        result_section_match = re.search(r'{% if result_image %}.*?{% endif %}', content, re.DOTALL)
        
        if not result_section_match:
            print(f"  [FAIL] {template} - No result_image section found")
            all_passed = False
            continue
            
        result_section = result_section_match.group(0)
        
        has_include_in_result = "{% include '_print_size_controls.html' %}" in result_section
        has_init_in_result = "initPrintSizeControls" in result_section
        
        if has_include_in_result and has_init_in_result:
            print(f"  [OK] {template} - Print controls properly configured")
        else:
            print(f"  [FAIL] {template} - Missing:")
            if not has_include_in_result:
                print(f"       - Print controls include")
            if not has_init_in_result:
                print(f"       - initPrintSizeControls call")
            all_passed = False
    
    print()
    
    # Also verify _print_size_controls.html exists and has the right structure
    print("Checking _print_size_controls.html...")
    controls_path = os.path.join(template_dir, '_print_size_controls.html')
    if os.path.exists(controls_path):
        with open(controls_path, 'r', encoding='utf-8') as f:
            controls_content = f.read()
        
        required_elements = [
            'printBtn',
            'printDropdown',
            'printSizeSelect',
            'printExecuteBtn',
            'multiSameBtn',
            'queueAddBtn',
            'queuePrintBtn',
            'viewQueueBtn',
            'queueClearBtn',
            'initPrintSizeControls'
        ]
        
        missing = []
        for elem in required_elements:
            if elem not in controls_content:
                missing.append(elem)
        
        if not missing:
            print(f"  [OK] _print_size_controls.html has all required elements")
        else:
            print(f"  [FAIL] _print_size_controls.html missing: {', '.join(missing)}")
            all_passed = False
    else:
        print(f"  [FAIL] _print_size_controls.html not found")
        all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("[SUCCESS] All forms have print controls properly configured")
    else:
        print("[FAILURE] Some forms are missing print controls")
    
    return all_passed

if __name__ == '__main__':
    success = test_print_controls_in_forms()
    exit(0 if success else 1)
