#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест транслитерации кириллицы при сканировании кодов
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.codes import generate_by_type, decode_auto
from app.core.transliteration import (
    transliterate_to_latin, 
    transliterate_to_cyrillic,
    TRANSLITERATION_MARKER,
    looks_like_russian_transliteration
)
from PIL import Image
import io

def test_transliteration_functions():
    """Тест основных функций транслитерации"""
    print("\n=== Тест функций транслитерации ===")
    
    # Тест базовой транслитерации
    cyrillic_text = "Привет мир"
    latin_text = transliterate_to_latin(cyrillic_text)
    print(f"Кириллица: {cyrillic_text}")
    print(f"→ Латиница: {latin_text}")
    
    # Тест обратной транслитерации с маркером
    marked_text = TRANSLITERATION_MARKER + latin_text
    reversed_text = transliterate_to_cyrillic(marked_text)
    print(f"С маркером: {marked_text}")
    print(f"→ Обратно: {reversed_text}")
    assert reversed_text.lower() == cyrillic_text.lower(), f"Неверная обратная транслитерация: {reversed_text}"
    
    # Тест определения русской транслитерации
    print(f"\nОпределение транслитерации:")
    print(f"'{latin_text}' похож на русский? {looks_like_russian_transliteration(latin_text)}")
    print(f"'Hello world' похож на русский? {looks_like_russian_transliteration('Hello world')}")
    print(f"'Ivanov' похож на русский? {looks_like_russian_transliteration('Ivanov')}")
    
    print("✓ Функции транслитерации работают корректно")

def test_code_type(code_type: str, test_text: str):
    """Тест генерации и сканирования для конкретного типа кода"""
    print(f"\n--- Тест {code_type} ---")
    print(f"Исходный текст: {test_text}")
    
    try:
        # Генерация кода
        img, metadata = generate_by_type(code_type, test_text, size=300)
        print(f"✓ Код сгенерирован (транслитерация: {metadata.get('transliterated', False)})")
        
        # Сканирование кода
        results = decode_auto(img)
        
        if not results:
            print(f"✗ Не удалось отсканировать {code_type}")
            return False
        
        scanned_text = results[0]['text']
        print(f"Отсканированный текст: {scanned_text}")
        
        # Проверка соответствия
        if scanned_text.lower() == test_text.lower():
            print(f"✓ {code_type}: Текст совпадает идеально")
            return True
        else:
            print(f"✗ {code_type}: Текст не совпадает!")
            print(f"  Ожидалось: {test_text}")
            print(f"  Получено: {scanned_text}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка при тестировании {code_type}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_code_types():
    """Тест всех типов кодов с кириллическим текстом"""
    print("\n=== Тест сканирования кириллицы для всех типов кодов ===")
    
    test_texts = [
        "Привет мир",
        "Тест 123",
        "Иванов Иван",
        "Товар: Хлеб белый",
    ]
    
    code_types = [
        "QR",
        "DataMatrix",
        "Code128",
        "PDF417",
        "Aztec"
    ]
    
    results = {}
    
    for code_type in code_types:
        results[code_type] = []
        for text in test_texts:
            success = test_code_type(code_type, text)
            results[code_type].append(success)
    
    # Итоги
    print("\n=== ИТОГИ ===")
    for code_type, test_results in results.items():
        success_count = sum(test_results)
        total_count = len(test_results)
        status = "✓" if success_count == total_count else "✗"
        print(f"{status} {code_type}: {success_count}/{total_count} тестов пройдено")
    
    return results

def test_form_data():
    """Тест с данными форм"""
    print("\n=== Тест данных форм ===")
    
    # ТОРГ-12
    from app.core.forms_parser import torg12_make_string, torg12_parse_string
    
    torg12_data = {
        "ORG": "ООО Рога и Копыта",
        "PROD": "Хлеб белый",
        "QTY": "10"
    }
    
    print("\nФорма ТОРГ-12:")
    print(f"Исходные данные: {torg12_data}")
    
    encoded = torg12_make_string(torg12_data)
    print(f"Закодировано: {encoded}")
    
    # Тест QR
    img_qr, _ = generate_by_type("QR", encoded, size=300)
    results_qr = decode_auto(img_qr)
    if results_qr:
        decoded_text = results_qr[0]['text']
        print(f"QR - отсканировано: {decoded_text}")
        parsed = torg12_parse_string(decoded_text)
        print(f"QR - распарсено: {parsed}")
        if parsed.get('ORG') == torg12_data['ORG']:
            print("✓ ТОРГ-12 через QR: Кириллица сохранилась")
        else:
            print(f"✗ ТОРГ-12 через QR: Кириллица потеряна! Ожидалось '{torg12_data['ORG']}', получено '{parsed.get('ORG')}'")
    
    # Тест Aztec
    img_aztec, metadata = generate_by_type("Aztec", encoded, size=300)
    print(f"Aztec - транслитерация применена: {metadata.get('transliterated', False)}")
    results_aztec = decode_auto(img_aztec)
    if results_aztec:
        decoded_text = results_aztec[0]['text']
        print(f"Aztec - отсканировано: {decoded_text}")
        parsed = torg12_parse_string(decoded_text)
        print(f"Aztec - распарсено: {parsed}")
        if parsed.get('ORG') == torg12_data['ORG']:
            print("✓ ТОРГ-12 через Aztec: Кириллица восстановлена")
        else:
            print(f"✗ ТОРГ-12 через Aztec: Кириллица не восстановлена! Ожидалось '{torg12_data['ORG']}', получено '{parsed.get('ORG')}'")

def test_mixed_content():
    """Тест с смешанным содержимым (кириллица + латиница + цифры)"""
    print("\n=== Тест смешанного содержимого ===")
    
    test_cases = [
        "ABC-123-Москва",
        "Товар: Product-001",
        "Email: test@example.com, Имя: Иван",
    ]
    
    for test_text in test_cases:
        print(f"\nИсходный текст: {test_text}")
        
        # QR код
        img, _ = generate_by_type("QR", test_text, size=300)
        results = decode_auto(img)
        if results:
            scanned = results[0]['text']
            match = scanned == test_text
            status = "✓" if match else "✗"
            print(f"{status} QR: {scanned}")
        
        # Aztec код
        img, metadata = generate_by_type("Aztec", test_text, size=300)
        results = decode_auto(img)
        if results:
            scanned = results[0]['text']
            match = scanned.lower() == test_text.lower()
            status = "✓" if match else "✗"
            print(f"{status} Aztec: {scanned}")

def test_latin_preservation():
    """Тест что латинский текст остается без изменений"""
    print("\n=== Тест сохранения латинского текста ===")
    
    latin_texts = [
        "Hello World",
        "Test123",
        "user@example.com",
    ]
    
    for text in latin_texts:
        print(f"\nИсходный текст: {text}")
        
        for code_type in ["QR", "Aztec", "DataMatrix"]:
            img, metadata = generate_by_type(code_type, text, size=300)
            results = decode_auto(img)
            
            if results:
                scanned = results[0]['text']
                match = scanned == text
                status = "✓" if match else "✗"
                print(f"{status} {code_type}: {scanned} (транслит: {metadata.get('transliterated', False)})")
                
                if not match:
                    print(f"  ОШИБКА: Латинский текст изменился!")

if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ТРАНСЛИТЕРАЦИИ КИРИЛЛИЦЫ ПРИ СКАНИРОВАНИИ")
    print("=" * 60)
    
    try:
        # Тест 1: Базовые функции
        test_transliteration_functions()
        
        # Тест 2: Все типы кодов
        test_all_code_types()
        
        # Тест 3: Данные форм
        test_form_data()
        
        # Тест 4: Смешанное содержимое
        test_mixed_content()
        
        # Тест 5: Сохранение латиницы
        test_latin_preservation()
        
        print("\n" + "=" * 60)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n!!! КРИТИЧЕСКАЯ ОШИБКА !!!")
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
