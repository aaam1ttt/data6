# -*- coding: utf-8 -*-
"""
Тест полной работы кириллицы во всех формах и типах кодов
"""

import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.codes import generate_by_type, decode_auto
from app.core.forms_parser import torg12_make_string, torg12_parse_string
from PIL import Image

def test_cyrillic_in_all_code_types():
    """Тест кириллицы во всех типах кодов"""
    print("\n=== Тест кириллицы во всех типах кодов ===\n")
    
    test_texts = [
        "Привет мир",
        "Тестовый текст на русском",
        "Москва 2024",
    ]
    
    code_types = ["QR", "DataMatrix", "Aztec", "Code128", "PDF417"]
    
    for text in test_texts:
        print(f"\nТестируем текст: '{text}'")
        print("-" * 60)
        
        for code_type in code_types:
            try:
                img, metadata = generate_by_type(code_type, text, size=300)
                results = decode_auto(img)
                
                if results:
                    decoded_text = results[0]['text']
                    if decoded_text == text:
                        print(f"  {code_type:12} - ✓ OK ('{decoded_text}')")
                    else:
                        print(f"  {code_type:12} - ✗ FAIL")
                        print(f"    Ожидалось: '{text}'")
                        print(f"    Получено:  '{decoded_text}'")
                else:
                    print(f"  {code_type:12} - ✗ FAIL (не отсканирован)")
            except Exception as e:
                print(f"  {code_type:12} - ✗ ERROR: {e}")

def test_question_mark_separator():
    """Тест разделителя знака вопроса"""
    print("\n=== Тест разделителя '?' ===\n")
    
    test_cases = [
        "Привет как дела? dxxxfghs hello",
        "Москва? London Paris",
        "Тест? test123",
    ]
    
    code_types = ["QR", "DataMatrix", "Aztec"]
    
    for text in test_cases:
        print(f"\nТестируем текст: '{text}'")
        print("-" * 60)
        
        # Ожидаемый результат: текст до ? транслитерируется обратно, после ? остаётся как есть
        if '?' in text:
            parts = text.split('?', 1)
            expected = parts[0] + '?' + parts[1]
        else:
            expected = text
        
        for code_type in code_types:
            try:
                img, metadata = generate_by_type(code_type, text, size=300)
                results = decode_auto(img)
                
                if results:
                    decoded_text = results[0]['text']
                    
                    # Проверяем что часть после ? не изменилась
                    if '?' in decoded_text:
                        after_question = decoded_text.split('?', 1)[1]
                        expected_after = text.split('?', 1)[1]
                        
                        if after_question == expected_after:
                            print(f"  {code_type:12} - ✓ OK")
                            print(f"    До ?:     транслитерировано")
                            print(f"    После ?:  '{after_question}' (не изменено)")
                        else:
                            print(f"  {code_type:12} - ✗ FAIL")
                            print(f"    После ? ожидалось: '{expected_after}'")
                            print(f"    После ? получено:  '{after_question}'")
                    else:
                        print(f"  {code_type:12} - ✗ FAIL (знак ? потерян)")
                else:
                    print(f"  {code_type:12} - ✗ FAIL (не отсканирован)")
            except Exception as e:
                print(f"  {code_type:12} - ✗ ERROR: {e}")

def test_form_torg12_cyrillic():
    """Тест формы ТОРГ-12 с кириллицей"""
    print("\n=== Тест формы ТОРГ-12 с кириллицей ===\n")
    
    torg12_data = {
        '1': 'ООО "Рога и Копыта"',
        '2': '1234567890',
        '3': 'Москва',
        '12': 'Иванов И.И.',
    }
    
    code_types = ["QR", "DataMatrix", "Aztec"]
    
    encoded = torg12_make_string(torg12_data)
    print(f"Исходные данные: {torg12_data}")
    print(f"Закодировано: {encoded}\n")
    
    for code_type in code_types:
        try:
            img, metadata = generate_by_type(code_type, encoded, size=300)
            results = decode_auto(img)
            
            if results:
                decoded_text = results[0]['text']
                parsed = torg12_parse_string(decoded_text)
                
                # Проверяем восстановление данных
                success = True
                for key, value in torg12_data.items():
                    if parsed.get(key) != value:
                        success = False
                        print(f"  {code_type:12} - ✗ FAIL")
                        print(f"    Поле {key}: ожидалось '{value}', получено '{parsed.get(key)}'")
                        break
                
                if success:
                    print(f"  {code_type:12} - ✓ OK (все поля восстановлены)")
            else:
                print(f"  {code_type:12} - ✗ FAIL (не отсканирован)")
        except Exception as e:
            print(f"  {code_type:12} - ✗ ERROR: {e}")

if __name__ == "__main__":
    test_cyrillic_in_all_code_types()
    test_question_mark_separator()
    test_form_torg12_cyrillic()
    print("\n" + "=" * 60)
    print("Тестирование завершено")
