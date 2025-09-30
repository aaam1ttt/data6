#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

def test_excel_export():
    print("Testing Excel export endpoint...")
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            test_cases = [
                {'text': 'T12_A:Test;T12_B:Value', 'form_type': 'torg12'},
                {'text': 'MSG_1:Message;MSG_2:Data', 'form_type': 'message'},
                {'text': 'EXP_1:Data1;EXP_2:Data2', 'form_type': 'exploitation'},
                {'text': 'TRN_1:Transport;TRN_2:Info', 'form_type': 'transport'},
                {'text': 'Row1,Col1,Col2\nRow2,Val1,Val2', 'form_type': 'custom'},
            ]
            
            for test_case in test_cases:
                response = client.post('/scan/export_excel', 
                                     data=test_case)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type')
                    if 'spreadsheet' in content_type or 'xlsx' in content_type:
                        print(f"Excel export for {test_case['form_type']}: OK")
                    else:
                        print(f"Excel export for {test_case['form_type']}: Wrong content type: {content_type}")
                        return False
                else:
                    print(f"Excel export for {test_case['form_type']}: Failed with status {response.status_code}")
                    return False
            
            # Test invalid form type
            response = client.post('/scan/export_excel', 
                                  data={'text': 'test', 'form_type': 'invalid'})
            if response.status_code == 400:
                print("Invalid form type handled correctly: OK")
            else:
                print(f"Invalid form type not handled: {response.status_code}")
                return False
    
    print("\nAll Excel export tests passed!")
    return True

if __name__ == "__main__":
    success = test_excel_export()
    sys.exit(0 if success else 1)
