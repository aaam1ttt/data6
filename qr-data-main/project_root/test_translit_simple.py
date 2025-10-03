# -*- coding: utf-8 -*-
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.transliteration import prepare_text_for_barcode, transliterate_to_cyrillic

print("=== Тест транслитерации ===\n")

# Тест 1: Простой текст
text1 = "Привет мир"
print(f"1. Оригинал: '{text1}'")
encoded1 = prepare_text_for_barcode(text1)
print(f"   Закодирован: '{encoded1}'")
decoded1 = transliterate_to_cyrillic(encoded1)
print(f"   Декодирован: '{decoded1}'")
print(f"   Совпадает: {decoded1 == text1}\n")

# Тест 2: С буквой ы
text2 = "Тестовый текст"
print(f"2. Оригинал: '{text2}'")
encoded2 = prepare_text_for_barcode(text2)
print(f"   Закодирован: '{encoded2}'")
decoded2 = transliterate_to_cyrillic(encoded2)
print(f"   Декодирован: '{decoded2}'")
print(f"   Совпадает: {decoded2 == text2}\n")

# Тест 3: С вопросом
text3 = "Привет? hello"
print(f"3. Оригинал: '{text3}'")
encoded3 = prepare_text_for_barcode(text3)
print(f"   Закодирован: '{encoded3}'")
decoded3 = transliterate_to_cyrillic(encoded3)
print(f"   Декодирован: '{decoded3}'")
print(f"   Совпадает: {decoded3 == text3}\n")
