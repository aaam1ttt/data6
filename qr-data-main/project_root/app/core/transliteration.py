# -*- coding: utf-8 -*-
"""
Модуль транслитерации кириллицы в латиницу и обратно
"""

import re
from typing import Optional

# Таблица транслитерации кириллица -> латиница
CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}

# Обратная таблица латиница -> кириллица
LATIN_TO_CYRILLIC = {
    'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 'e': 'е', 'yo': 'ё',
    'zh': 'ж', 'z': 'з', 'i': 'и', 'y': 'й', 'k': 'к', 'l': 'л', 'm': 'м',
    'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
    'f': 'ф', 'kh': 'х', 'ts': 'ц', 'ch': 'ч', 'sh': 'ш', 'shch': 'щ',
    'yu': 'ю', 'ya': 'я',
    
    'A': 'А', 'B': 'Б', 'V': 'В', 'G': 'Г', 'D': 'Д', 'E': 'Е', 'Yo': 'Ё',
    'Zh': 'Ж', 'Z': 'З', 'I': 'И', 'Y': 'Й', 'K': 'К', 'L': 'Л', 'M': 'М',
    'N': 'Н', 'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
    'F': 'Ф', 'Kh': 'Х', 'Ts': 'Ц', 'Ch': 'Ч', 'Sh': 'Ш', 'Shch': 'Щ',
    'Yu': 'Ю', 'Ya': 'Я'
}

# Маркер для обозначения транслитерированного текста
TRANSLITERATION_MARKER = "__cyr__"

def contains_cyrillic(text: str) -> bool:
    """Проверяет, содержит ли текст кириллические символы"""
    return bool(re.search(r'[а-яё]', text, re.IGNORECASE))

def transliterate_to_latin(text: str) -> str:
    """Транслитерирует кириллический текст в латиницу"""
    if not contains_cyrillic(text):
        return text
    
    result = ""
    i = 0
    while i < len(text):
        char = text[i]
        
        # Проверяем четырехсимвольные комбинации (shch)
        if i < len(text) - 3:
            four_char = char + text[i + 1] + text[i + 2] + text[i + 3]
            if four_char.lower() in CYRILLIC_TO_LATIN:
                result += CYRILLIC_TO_LATIN[four_char]
                i += 4
                continue
        
        # Проверяем трехсимвольные комбинации
        if i < len(text) - 2:
            three_char = char + text[i + 1] + text[i + 2]
            if three_char.lower() in CYRILLIC_TO_LATIN:
                result += CYRILLIC_TO_LATIN[three_char]
                i += 3
                continue
        
        # Проверяем двухсимвольные комбинации
        if i < len(text) - 1:
            two_char = char + text[i + 1]
            if two_char.lower() in CYRILLIC_TO_LATIN:
                result += CYRILLIC_TO_LATIN[two_char]
                i += 2
                continue
        
        # Одиночный символ
        if char in CYRILLIC_TO_LATIN:
            result += CYRILLIC_TO_LATIN[char]
        else:
            result += char
        i += 1
    
    return result

def transliterate_to_cyrillic(text: str) -> str:
    """Транслитерирует латинский текст в кириллицу"""
    if not text:
        return text
    
    # Сначала проверяем маркер
    if text.startswith(TRANSLITERATION_MARKER):
        text = text[len(TRANSLITERATION_MARKER):]
        is_marked = True
    else:
        is_marked = False
    
    # Если текст не помечен как транслитерация, проверяем, похож ли он на русский
    if not is_marked and not looks_like_russian_transliteration(text):
        return text
    
    result = ""
    i = 0
    while i < len(text):
        # Проверяем четырехсимвольные комбинации
        if i < len(text) - 3:
            four_char = text[i:i+4].lower()
            if four_char in LATIN_TO_CYRILLIC:
                result += LATIN_TO_CYRILLIC[four_char]
                i += 4
                continue
        
        # Проверяем трехсимвольные комбинации
        if i < len(text) - 2:
            three_char = text[i:i+3].lower()
            if three_char in LATIN_TO_CYRILLIC:
                result += LATIN_TO_CYRILLIC[three_char]
                i += 3
                continue
        
        # Проверяем двухсимвольные комбинации
        if i < len(text) - 1:
            two_char = text[i:i+2].lower()
            if two_char in LATIN_TO_CYRILLIC:
                result += LATIN_TO_CYRILLIC[two_char]
                i += 2
                continue
        
        # Одиночный символ
        char = text[i]
        if char.lower() in LATIN_TO_CYRILLIC:
            result += LATIN_TO_CYRILLIC[char]
        else:
            result += char
        i += 1
    
    return result

def looks_like_russian_transliteration(text: str) -> bool:
    """Проверяет, похож ли текст на транслитерацию русского языка"""
    if not text:
        return False
    
    # Убираем знаки препинания и цифры для анализа
    clean_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    words = clean_text.split()
    
    if not words:
        return False
    
    # Проверяем характерные русские звуки в транслитерации
    russian_patterns = [
        r'shch', r'zh', r'kh', r'ts', r'ch', r'sh', r'yu', r'ya', r'yo'
    ]
    
    # Проверяем окончания слов, характерные для русского
    russian_endings = [
        r'ov$', r'ev$', r'in$', r'yn$', r'aya$', r'aya$', r'oye$', r'iy$', r'aya$'
    ]
    
    pattern_score = 0
    ending_score = 0
    
    for word in words:
        # Проверяем паттерны
        for pattern in russian_patterns:
            if re.search(pattern, word):
                pattern_score += 1
        
        # Проверяем окончания
        for ending in russian_endings:
            if re.search(ending, word):
                ending_score += 1
    
    # Если есть характерные русские паттерны или окончания, считаем транслитерацией
    return pattern_score > 0 or ending_score > len(words) * 0.3

def prepare_text_for_barcode(text: str, add_marker: bool = True) -> str:
    """Подготавливает текст для кодирования в штрих-код"""
    if contains_cyrillic(text):
        transliterated = transliterate_to_latin(text)
        if add_marker:
            return TRANSLITERATION_MARKER + transliterated
        return transliterated
    return text

def process_scanned_text(text: str) -> str:
    """Обрабатывает отсканированный текст, возвращая кириллицу если нужно"""
    return transliterate_to_cyrillic(text)
