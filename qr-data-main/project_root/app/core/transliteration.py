# -*- coding: utf-8 -*-
"""
Модуль транслитерации кириллицы в латиницу и обратно
"""

import re
from typing import Optional

# Таблица транслитерации кириллица -> латиница
CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'yy', 'ь': '', 'э': 'eh', 'ю': 'yu', 'я': 'ya',
    
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'J', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'YY', 'Ь': '', 'Э': 'Eh', 'Ю': 'Yu', 'Я': 'Ya'
}

# Обратная таблица латиница -> кириллица
LATIN_TO_CYRILLIC = {
    'shch': 'щ', 'Shch': 'Щ', 'SHCH': 'Щ',
    'zh': 'ж', 'Zh': 'Ж', 'ZH': 'Ж',
    'kh': 'х', 'Kh': 'Х', 'KH': 'Х',
    'ts': 'ц', 'Ts': 'Ц', 'TS': 'Ц',
    'ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч',
    'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш',
    'yo': 'ё', 'Yo': 'Ё', 'YO': 'Ё',
    'yu': 'ю', 'Yu': 'Ю', 'YU': 'Ю',
    'ya': 'я', 'Ya': 'Я', 'YA': 'Я',
    'yy': 'ы', 'Yy': 'Ы', 'YY': 'Ы',
    'eh': 'э', 'Eh': 'Э', 'EH': 'Э',
    'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 'e': 'е',
    'z': 'з', 'i': 'и', 'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м',
    'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
    'f': 'ф',
    'A': 'А', 'B': 'Б', 'V': 'В', 'G': 'Г', 'D': 'Д', 'E': 'Е',
    'Z': 'З', 'I': 'И', 'J': 'Й', 'K': 'К', 'L': 'Л', 'M': 'М',
    'N': 'Н', 'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
    'F': 'Ф'
}

# Маркер для обозначения транслитерированного текста
TRANSLITERATION_MARKER = "__cyr__"

def contains_cyrillic(text: str) -> bool:
    """Проверяет, содержит ли текст кириллические символы (Unicode U+0400-U+04FF)"""
    return bool(re.search(r'[\u0400-\u04FF]', text))

def transliterate_to_latin(text: str) -> str:
    """Транслитерирует кириллический текст в латиницу"""
    if not contains_cyrillic(text):
        return text
    
    result = ""
    i = 0
    while i < len(text):
        char = text[i]
        
        # Однобуквенные символы
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
    
    # Проверяем наличие маркера транслитерации
    if text.startswith(TRANSLITERATION_MARKER):
        text = text[len(TRANSLITERATION_MARKER):]
        is_marked = True
    else:
        is_marked = False
    
    # Если нет маркера и текст не похож на транслитерацию - возвращаем как есть
    if not is_marked and not looks_like_russian_transliteration(text):
        return text
    
    result = ""
    i = 0
    while i < len(text):
        # Проверяем четырёхбуквенные комбинации (shch)
        if i < len(text) - 3:
            four_char = text[i:i+4]
            if four_char in LATIN_TO_CYRILLIC:
                result += LATIN_TO_CYRILLIC[four_char]
                i += 4
                continue
        
        # Проверяем двухбуквенные комбинации
        if i < len(text) - 1:
            two_char = text[i:i+2]
            if two_char in LATIN_TO_CYRILLIC:
                result += LATIN_TO_CYRILLIC[two_char]
                i += 2
                continue
        
        # Однобуквенные символы
        char = text[i]
        if char in LATIN_TO_CYRILLIC:
            result += LATIN_TO_CYRILLIC[char]
        else:
            result += char
        i += 1
    
    return result

def looks_like_russian_transliteration(text: str) -> bool:
    """Проверяет, похож ли текст на транслитерацию русского языка"""
    if not text:
        return False
    
    # Удаляем знаки препинания и спецсимволы
    clean_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    words = clean_text.split()
    
    if not words:
        return False
    
    # Паттерны характерные для русской транслитерации
    russian_patterns = [
        r'shch', r'zh', r'kh', r'ts', r'ch', r'sh', r'yu', r'ya', r'yo', r'yy', r'eh', r'j'
    ]
    
    # Окончания характерные для русских слов
    russian_endings = [
        r'ov$', r'ev$', r'in$', r'yn$', r'aya$', r'oye$', r'iy$', r'yy$', r'yyj$'
    ]
    
    # Общие русские слова в транслитерации
    common_russian_words = [
        'privet', 'moskva', 'test', 'tekst', 'mir', 'den', 'gorod', 'dom', 'vodka'
    ]
    
    pattern_score = 0
    ending_score = 0
    word_score = 0
    
    for word in words:
        # Проверяем характерные паттерны
        for pattern in russian_patterns:
            if re.search(pattern, word):
                pattern_score += 1
        
        # Проверяем окончания
        for ending in russian_endings:
            if re.search(ending, word):
                ending_score += 1
        
        # Проверяем общие слова
        if word in common_russian_words:
            word_score += 1
    
    # Считаем что текст похож на русский если есть характерные паттерны, окончания или известные слова
    return pattern_score > 0 or ending_score > len(words) * 0.3 or word_score > 0

def prepare_text_for_barcode(text: str, add_marker: bool = True) -> str:
    """
    Подготавливает текст для кодирования в штрих-код.
    Текст после знака вопроса (?) не транслитерируется.
    """
    if '?' in text:
        parts = text.split('?', 1)
        if contains_cyrillic(parts[0]):
            transliterated = transliterate_to_latin(parts[0])
            if add_marker:
                result = TRANSLITERATION_MARKER + transliterated + '?' + parts[1]
            else:
                result = transliterated + '?' + parts[1]
            return result
        return text
    
    if contains_cyrillic(text):
        transliterated = transliterate_to_latin(text)
        if add_marker:
            return TRANSLITERATION_MARKER + transliterated
        return transliterated
    return text

def process_scanned_text(text: str) -> str:
    """
    Обрабатывает отсканированный текст, возвращая кириллицу если нужно.
    Текст после знака вопроса (?) не транслитерируется.
    """
    if not text:
        return text
    
    if '?' in text:
        parts = text.split('?', 1)
        transliterated_part = transliterate_to_cyrillic(parts[0])
        # Часть после ? оставляем как есть (не транслитерируем)
        return transliterated_part + '?' + parts[1]
    
    return transliterate_to_cyrillic(text)

def is_latin1_compatible(text: str) -> bool:
    """Проверяет, совместим ли текст с кодировкой Latin-1 (ISO-8859-1)"""
    try:
        text.encode('latin-1')
        return True
    except UnicodeEncodeError:
        return False

def transliterate_for_aztec(text: str) -> tuple[str, bool]:
    """
    Интеллектуальная транслитерация для Aztec-кодов.
    Применяет транслитерацию только если текст содержит кириллицу.
    Текст после знака вопроса (?) не транслитерируется.
    
    Returns:
        tuple: (обработанный текст, был ли применён транслит)
    """
    if '?' in text:
        parts = text.split('?', 1)
        if contains_cyrillic(parts[0]):
            transliterated = transliterate_to_latin(parts[0])
            return transliterated + '?' + parts[1], True
        return text, False
    
    if contains_cyrillic(text):
        transliterated = transliterate_to_latin(text)
        return transliterated, True
    return text, False
