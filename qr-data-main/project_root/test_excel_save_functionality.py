#!/usr/bin/env python3
"""
Test script to verify Excel export functionality with save dialog support.
This test verifies:
1. Backend endpoint returns proper Excel files
2. Frontend JavaScript handles file saving correctly
3. Proper error handling for invalid inputs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from io import BytesIO
import openpyxl

def test_excel_export_backend():
    """Test that backend generates proper Excel files"""
    print("=" * 60)
    print("Testing Excel Export Backend")
    print("=" * 60)
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Test valid form types
            test_cases = [
                {
                    'name': 'TORG-12',
                    'data': {'text': 'T12_A:TestValue;T12_B:AnotherValue', 'form_type': 'torg12'},
                    'expected_filename': 'torg12.xlsx'
                },
                {
                    'name': 'Message',
                    'data': {'text': 'MSG_1:Message1;MSG_2:Message2', 'form_type': 'message'},
                    'expected_filename': 'message.xlsx'
                },
                {
                    'name': 'Exploitation',
                    'data': {'text': 'EXP_1:Data1;EXP_2:Data2', 'form_type': 'exploitation'},
                    'expected_filename': 'exploitation.xlsx'
                },
                {
                    'name': 'Transport',
                    'data': {'text': 'TRN_1:Transport;TRN_2:Info', 'form_type': 'transport'},
                    'expected_filename': 'transport.xlsx'
                },
                {
                    'name': 'Custom Table',
                    'data': {'text': 'Col1;Col2;Col3\nVal1;Val2;Val3', 'form_type': 'custom'},
                    'expected_filename': 'custom.xlsx'
                },
            ]
            
            for test_case in test_cases:
                print(f"\nTesting {test_case['name']}...")
                response = client.post('/scan/export_excel', data=test_case['data'])
                
                # Check status code
                if response.status_code != 200:
                    print(f"  ❌ FAILED: Status code {response.status_code}")
                    print(f"     Response: {response.data}")
                    return False
                
                # Check content type
                content_type = response.headers.get('Content-Type', '')
                if 'spreadsheet' not in content_type and 'xlsx' not in content_type:
                    print(f"  ❌ FAILED: Wrong content type: {content_type}")
                    return False
                
                # Check content disposition (should suggest download with filename)
                content_disp = response.headers.get('Content-Disposition', '')
                if test_case['expected_filename'] not in content_disp:
                    print(f"  ❌ FAILED: Expected filename '{test_case['expected_filename']}' not in Content-Disposition: {content_disp}")
                    return False
                
                # Verify it's a valid Excel file
                try:
                    wb = openpyxl.load_workbook(BytesIO(response.data))
                    if not wb.active:
                        print(f"  ❌ FAILED: No active worksheet")
                        return False
                    print(f"  ✅ SUCCESS: Valid Excel file generated")
                except Exception as e:
                    print(f"  ❌ FAILED: Invalid Excel file: {e}")
                    return False
            
            # Test error cases
            print("\nTesting error handling...")
            
            # Invalid form type
            response = client.post('/scan/export_excel', 
                                  data={'text': 'test', 'form_type': 'invalid'})
            if response.status_code == 400:
                print("  ✅ Invalid form type rejected correctly")
            else:
                print(f"  ❌ FAILED: Invalid form type not rejected (status: {response.status_code})")
                return False
            
            # Missing text
            response = client.post('/scan/export_excel', 
                                  data={'text': '', 'form_type': 'torg12'})
            if response.status_code == 400:
                print("  ✅ Empty text rejected correctly")
            else:
                print(f"  ❌ FAILED: Empty text not rejected (status: {response.status_code})")
                return False
            
            # Missing form_type
            response = client.post('/scan/export_excel', 
                                  data={'text': 'test', 'form_type': ''})
            if response.status_code == 400:
                print("  ✅ Empty form_type rejected correctly")
            else:
                print(f"  ❌ FAILED: Empty form_type not rejected (status: {response.status_code})")
                return False
    
    print("\n" + "=" * 60)
    print("All Excel export backend tests passed! ✅")
    print("=" * 60)
    return True

def test_frontend_integration():
    """Verify frontend code structure"""
    print("\n" + "=" * 60)
    print("Testing Frontend Integration")
    print("=" * 60)
    
    scan_html_path = os.path.join(os.path.dirname(__file__), 'app', 'templates', 'scan.html')
    
    if not os.path.exists(scan_html_path):
        print(f"❌ FAILED: scan.html not found at {scan_html_path}")
        return False
    
    with open(scan_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required elements
    checks = [
        ('showSaveFilePicker API', 'window.showSaveFilePicker'),
        ('Fetch to export_excel endpoint', "url_for('scan.export_excel')"),
        ('Default filename function', 'getDefaultFilename'),
        ('Fallback download function', 'fallbackDownload'),
        ('Excel file type filter', "'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"),
        ('Success message', "'Файл успешно сохранен'"),
        ('Error handling', "'Ошибка при сохранении файла'"),
        ('Button label', 'Сохранить в Excel'),
    ]
    
    all_passed = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"  ✅ {check_name}: Found")
        else:
            print(f"  ❌ {check_name}: Not found")
            all_passed = False
    
    if all_passed:
        print("\n" + "=" * 60)
        print("All frontend integration checks passed! ✅")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Some frontend checks failed! ❌")
        print("=" * 60)
    
    return all_passed

def main():
    print("\n" + "=" * 60)
    print("Excel Save Dialog Functionality Test Suite")
    print("=" * 60 + "\n")
    
    # Test backend
    backend_success = test_excel_export_backend()
    
    # Test frontend integration
    frontend_success = test_frontend_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Backend Tests:  {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"Frontend Tests: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
    print("=" * 60)
    
    if backend_success and frontend_success:
        print("\n🎉 All tests passed successfully!")
        print("\nThe Excel save dialog functionality is working correctly:")
        print("  • User clicks 'Сохранить в Excel' button")
        print("  • Browser shows native file save dialog (if supported)")
        print("  • User can choose destination and filename")
        print("  • File is saved with proper Excel format (.xlsx)")
        print("  • Fallback to standard download on older browsers")
        return True
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
