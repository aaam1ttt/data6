#!/usr/bin/env python3
"""Quick implementation check without running the server"""

import os
import sys

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_file_contains(filepath, search_strings, description):
    if not os.path.exists(filepath):
        print(f"❌ {description}: File not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for search_str, label in search_strings:
        if search_str in content:
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label} NOT FOUND")
            all_found = False
    
    return all_found

def main():
    print("=" * 70)
    print("Excel Save Dialog Implementation Check")
    print("=" * 70 + "\n")
    
    base_dir = os.path.dirname(__file__)
    
    # Check backend file
    scan_py = os.path.join(base_dir, 'app', 'routes', 'scan.py')
    print("1. Backend Route File (scan.py)")
    if check_file_exists(scan_py, "Backend file"):
        backend_checks = [
            ('def export_excel():', 'export_excel function exists'),
            ('jsonify', 'Uses jsonify for errors'),
            ('send_file(bio', 'Returns file with send_file'),
            ('as_attachment=True', 'File marked as attachment'),
            ('download_name=filename', 'Filename specified'),
        ]
        check_file_contains(scan_py, backend_checks, "Backend implementation")
    print()
    
    # Check frontend file
    scan_html = os.path.join(base_dir, 'app', 'templates', 'scan.html')
    print("2. Frontend Template (scan.html)")
    if check_file_exists(scan_html, "Frontend file"):
        frontend_checks = [
            ('Сохранить в Excel', 'Button label updated'),
            ('openExcelBtn', 'Button element exists'),
            ('currentExcelData', 'Excel data storage'),
            ('window.showSaveFilePicker', 'File System Access API'),
            ('getDefaultFilename', 'Default filename function'),
            ('fallbackDownload', 'Fallback for older browsers'),
            ("'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'", 'Excel MIME type'),
            ("types:[{", 'File type filter'),
            ('Файл успешно сохранен', 'Success message'),
            ('Ошибка при сохранении файла', 'Error message'),
        ]
        check_file_contains(scan_html, frontend_checks, "Frontend implementation")
    print()
    
    # Check documentation
    print("3. Documentation")
    doc_files = [
        (os.path.join(base_dir, 'EXCEL_SAVE_DIALOG.md'), 'Implementation documentation'),
        (os.path.join(base_dir, 'MANUAL_TEST_GUIDE.md'), 'Manual testing guide'),
    ]
    
    for filepath, description in doc_files:
        check_file_exists(filepath, description)
    print()
    
    # Check syntax
    print("4. Python Syntax Check")
    try:
        import py_compile
        py_compile.compile(scan_py, doraise=True)
        print("  ✅ scan.py: Valid Python syntax")
    except Exception as e:
        print(f"  ❌ scan.py: Syntax error - {e}")
    print()
    
    # Summary
    print("=" * 70)
    print("Implementation Check Complete")
    print("=" * 70)
    print("\nTo test the implementation:")
    print("1. Run: python run.py")
    print("2. Open: http://127.0.0.1:5000/scan")
    print("3. Scan a QR code with table data")
    print("4. Click 'Сохранить в Excel' button")
    print("5. Verify save dialog appears")
    print("\nFor detailed testing steps, see MANUAL_TEST_GUIDE.md")
    print("=" * 70)

if __name__ == "__main__":
    main()
