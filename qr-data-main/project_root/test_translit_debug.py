# -*- coding: utf-8 -*-
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.transliteration import transliterate_to_cyrillic, TRANSLITERATION_MARKER

# Тест с вопросом
text = "__cyr__Privet? hello"
parts = text.split('?', 1)
print(f"Исходный текст: '{text}'")
print(f"Часть 1: '{parts[0]}'")
print(f"Часть 2: '{parts[1]}'")

transliterated_part = transliterate_to_cyrillic(parts[0])
print(f"\nПосле транслитерации части 1: '{transliterated_part}'")
print(f"Результат: '{transliterated_part}? {parts[1]}'")

# Проверка looks_like_russian_transliteration
from app.core.transliteration import looks_like_russian_transliteration

test_texts = ["hello", "world", "Privet", "test"]
for t in test_texts:
    result = looks_like_russian_transliteration(t)
    print(f"\nlooks_like_russian_transliteration('{t}'): {result}")
