# Intelligent Russian-to-Latin Transliteration for Aztec Codes

## Overview

This implementation adds intelligent transliteration that automatically converts Cyrillic (Russian) text to Latin characters when generating Aztec codes, ensuring compatibility with the aztec-code-generator library which only supports Latin-1 encoding.

## Features

### 1. **Selective Activation**
- Transliteration only activates for Aztec codes, not other barcode types
- Only applies when input contains Cyrillic characters (Unicode U+0400-U+04FF)
- Latin-1 compatible text passes through unchanged

### 2. **Cyrillic Detection**
```python
def contains_cyrillic(text: str) -> bool:
    """Проверяет, содержит ли текст кириллические символы (Unicode U+0400-U+04FF)"""
    return bool(re.search(r'[\u0400-\u04FF]', text))
```

Detects Cyrillic characters using the full Unicode Cyrillic block range (U+0400 to U+04FF), covering:
- Russian alphabet
- Ukrainian characters
- Belarusian characters
- Other Cyrillic scripts

### 3. **Standard Romanization Rules**

The transliteration follows standard Russian romanization:

| Cyrillic | Latin | Example |
|----------|-------|---------|
| а, А | a, A | Алекс → Aleks |
| б, Б | b, B | Борис → Boris |
| в, В | v, V | Владимир → Vladimir |
| г, Г | g, G | Григорий → Grigoriy |
| д, Д | d, D | Дмитрий → Dmitriy |
| е, Е | e, E | Елена → Elena |
| ё, Ё | yo, Yo | Ёлка → Yolka |
| ж, Ж | zh, Zh | Жанна → Zhanna |
| з, З | z, Z | Зоя → Zoya |
| и, И | i, I | Иван → Ivan |
| й, Й | y, Y | Николай → Nikolay |
| к, К | k, K | Константин → Konstantin |
| л, Л | l, L | Людмила → Lyudmila |
| м, М | m, M | Москва → Moskva |
| н, Н | n, N | Наталья → Natalya |
| о, О | o, O | Ольга → Olga |
| п, П | p, P | Павел → Pavel |
| р, Р | r, R | Роман → Roman |
| с, С | s, S | Светлана → Svetlana |
| т, Т | t, T | Татьяна → Tatyana |
| у, У | u, U | Ульяна → Ulyana |
| ф, Ф | f, F | Фёдор → Fyodor |
| х, Х | kh, Kh | Хабаровск → Khabarovsk |
| ц, Ц | ts, Ts | Царь → Tsar |
| ч, Ч | ch, Ch | Чехов → Chekhov |
| ш, Ш | sh, Sh | Шура → Shura |
| щ, Щ | shch, Shch | Щукин → Shchukin |
| ъ, Ъ | (omit) | Объект → Obekt |
| ы, Ы | y, Y | Крым → Krym |
| ь, Ь | (omit) | Тень → Ten |
| э, Э | e, E | Эмма → Emma |
| ю, Ю | yu, Yu | Юрий → Yuriy |
| я, Я | ya, Ya | Яна → Yana |

### 4. **User Notifications**

When transliteration occurs, users are notified through:

#### API Response (JSON)
```json
{
  "ok": true,
  "data_url": "data:image/png;base64,...",
  "warning": "Кириллический текст был автоматически транслитерирован в латиницу для совместимости с Aztec-кодом"
}
```

#### Frontend Display
The warning is automatically displayed in the UI alert area when using the live code generation interface.

#### Form Submissions
Flash messages are shown after form submission:
```
"Кириллический текст был автоматически транслитерирован в латиницу для совместимости с Aztec-кодом"
```

## Implementation Details

### Core Functions

**`transliterate_for_aztec(text: str) -> tuple[str, bool]`**
```python
def transliterate_for_aztec(text: str) -> tuple[str, bool]:
    """
    Интеллектуальная транслитерация для Aztec-кодов.
    Применяет транслитерацию только если текст содержит кириллицу.
    
    Returns:
        tuple: (обработанный текст, был ли применён транслит)
    """
    if contains_cyrillic(text):
        transliterated = transliterate_to_latin(text)
        return transliterated, True
    return text, False
```

**`is_latin1_compatible(text: str) -> bool`**
```python
def is_latin1_compatible(text: str) -> bool:
    """Проверяет, совместим ли текст с кодировкой Latin-1 (ISO-8859-1)"""
    try:
        text.encode('latin-1')
        return True
    except UnicodeEncodeError:
        return False
```

### Modified Functions

**`generate_aztec()`** - Returns tuple with transliteration flag
```python
def generate_aztec(text: str, size: int = 300, gost_code: str = None) -> tuple[Image.Image, bool]:
    """
    Generate Aztec barcode with proper implementation.
    
    Returns:
        tuple: (изображение, была ли применена транслитерация)
    """
    # Detect and transliterate if needed
    transliterated = False
    if not is_latin1_compatible(text):
        text, transliterated = transliterate_for_aztec(text)
    
    # Generate code...
    return img, transliterated
```

**`generate_by_type()`** - Returns metadata with transliteration info
```python
def generate_by_type(code_type: str, text: str, ...) -> tuple[Image.Image, dict]:
    """
    Returns:
        tuple: (изображение, метаданные с информацией о транслитерации)
    """
    metadata = {"transliterated": False, "code_type": code_type}
    
    if code_type_lower == "aztec":
        img, was_transliterated = generate_aztec(text, size, gost_code)
        metadata["transliterated"] = was_transliterated
        return img, metadata
    
    # Other code types...
```

## Testing

Run the test suite:
```bash
python test_aztec_transliteration.py
```

Tests cover:
1. Cyrillic character detection (U+0400-U+04FF)
2. Latin-1 compatibility checking
3. Intelligent transliteration activation
4. Standard romanization rules
5. Aztec code generation with metadata

## Usage Examples

### Latin Text (No Transliteration)
```python
# Input: "Hello World"
img, metadata = generate_by_type("aztec", "Hello World", size=300)
# metadata["transliterated"] == False
```

### Cyrillic Text (Transliterated)
```python
# Input: "Привет Мир"
img, metadata = generate_by_type("aztec", "Привет Мир", size=300)
# metadata["transliterated"] == True
# Actual encoded text: "Privet Mir"
```

### Mixed Text (Transliterated)
```python
# Input: "Test Тест"
img, metadata = generate_by_type("aztec", "Test Тест", size=300)
# metadata["transliterated"] == True
# Actual encoded text: "Test Test"
```

## Benefits

1. **Seamless User Experience**: Users can input Cyrillic text naturally without worrying about encoding
2. **Compatibility**: Ensures Aztec codes work with the aztec-code-generator library
3. **Transparency**: Users are informed when transliteration occurs
4. **Efficiency**: Only activates when needed, preserving Latin text unchanged
5. **Standards Compliance**: Uses standard Russian romanization rules for readability

## Files Modified

- `app/core/transliteration.py` - Added detection and transliteration functions
- `app/core/codes.py` - Modified `generate_aztec()` and `generate_by_type()`
- `app/routes/forms.py` - Added notification handling in all endpoints
- `app/templates/form_create_live.html` - Added warning display in frontend
- `test_aztec_transliteration.py` - Comprehensive test suite

## Future Enhancements

Potential improvements:
1. Support for other Cyrillic-based languages (Ukrainian, Belarusian, etc.)
2. Configurable romanization schemes (ISO 9, BGN/PCGN, etc.)
3. Reverse transliteration for scanned codes
4. User preference for transliteration rules
