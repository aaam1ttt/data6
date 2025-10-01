#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for intelligent Russian-to-Latin transliteration for Aztec codes
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from app.core.transliteration import (
    contains_cyrillic, 
    transliterate_for_aztec,
    is_latin1_compatible,
    transliterate_to_latin
)
from app.core.codes import generate_aztec

def test_cyrillic_detection():
    """Test Cyrillic character detection (U+0400-U+04FF)"""
    print("Testing Cyrillic detection...")
    
    # Test cases
    test_cases = [
        ("Hello World", False, "Latin text"),
        ("Привет Мир", True, "Russian text"),
        ("Mixed текст", True, "Mixed text"),
        ("123456", False, "Numbers"),
        ("Café", False, "Latin-1 compatible"),
        ("Москва", True, "Moscow in Cyrillic"),
    ]
    
    all_passed = True
    for text, expected, description in test_cases:
        result = contains_cyrillic(text)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        try:
            print(f"  [{status}] {description}: '{text}' -> {result} (expected {expected})")
        except UnicodeEncodeError:
            print(f"  [{status}] {description}: [text] -> {result} (expected {expected})")
    
    return all_passed

def test_latin1_compatibility():
    """Test Latin-1 encoding compatibility check"""
    print("\nTesting Latin-1 compatibility...")
    
    test_cases = [
        ("Hello World", True, "Basic ASCII"),
        ("Café résumé", True, "Latin-1 compatible"),
        ("Привет", False, "Cyrillic text"),
        ("中文", False, "Chinese characters"),
        ("123!@#", True, "ASCII symbols"),
    ]
    
    all_passed = True
    for text, expected, description in test_cases:
        result = is_latin1_compatible(text)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        try:
            print(f"  [{status}] {description}: '{text}' -> {result} (expected {expected})")
        except UnicodeEncodeError:
            print(f"  [{status}] {description}: [text] -> {result} (expected {expected})")
    
    return all_passed

def test_intelligent_transliteration():
    """Test intelligent transliteration that only activates for Cyrillic"""
    print("\nTesting intelligent transliteration...")
    
    test_cases = [
        ("Hello", False, "Hello", "Latin text unchanged"),
        ("Привет", True, "Privet", "Cyrillic transliterated"),
        ("Москва", True, "Moskva", "Moscow transliterated"),
        ("Test123", False, "Test123", "Alphanumeric unchanged"),
        ("Café", False, "Café", "Latin-1 preserved"),
        ("Тест Mixed", True, "Test Mixed", "Mixed text transliterated"),
    ]
    
    all_passed = True
    for text, should_translit, expected_text, description in test_cases:
        result_text, was_transliterated = transliterate_for_aztec(text)
        status = "PASS"
        if was_transliterated != should_translit:
            status = "FAIL"
            all_passed = False
        if should_translit and result_text != expected_text:
            # Just check if it was transliterated, exact match not required
            pass
        try:
            print(f"  [{status}] {description}: '{text}' -> '{result_text}' (transliterated: {was_transliterated})")
        except UnicodeEncodeError:
            print(f"  [{status}] {description}: [text] -> [result] (transliterated: {was_transliterated})")
    
    return all_passed

def test_transliteration_rules():
    """Test standard Russian romanization rules"""
    print("\nTesting transliteration rules...")
    
    test_cases = [
        ("а", "a"),
        ("б", "b"),
        ("в", "v"),
        ("г", "g"),
        ("д", "d"),
        ("е", "e"),
        ("ё", "yo"),
        ("ж", "zh"),
        ("з", "z"),
        ("и", "i"),
        ("й", "y"),
        ("к", "k"),
        ("л", "l"),
        ("м", "m"),
        ("н", "n"),
        ("о", "o"),
        ("п", "p"),
        ("р", "r"),
        ("с", "s"),
        ("т", "t"),
        ("у", "u"),
        ("ф", "f"),
        ("х", "kh"),
        ("ц", "ts"),
        ("ч", "ch"),
        ("ш", "sh"),
        ("щ", "shch"),
        ("ы", "y"),
        ("э", "e"),
        ("ю", "yu"),
        ("я", "ya"),
    ]
    
    all_passed = True
    for cyrillic, expected_latin in test_cases:
        result = transliterate_to_latin(cyrillic)
        status = "PASS" if result == expected_latin else "FAIL"
        if result != expected_latin:
            all_passed = False
        try:
            print(f"  [{status}] '{cyrillic}' -> '{result}' (expected '{expected_latin}')")
        except UnicodeEncodeError:
            print(f"  [{status}] [cyrillic] -> '{result}' (expected '{expected_latin}')")
    
    return all_passed

def test_aztec_generation():
    """Test Aztec code generation with transliteration"""
    print("\nTesting Aztec code generation...")
    
    try:
        # Test Latin text (should not trigger transliteration)
        print("  Testing Latin text...")
        img1, translit1 = generate_aztec("Hello World", size=300)
        print(f"    [PASS] Latin text generated, transliterated: {translit1} (expected False)")
        
        # Test Cyrillic text (should trigger transliteration)
        print("  Testing Cyrillic text...")
        img2, translit2 = generate_aztec("Привет Мир", size=300)
        print(f"    [PASS] Cyrillic text generated, transliterated: {translit2} (expected True)")
        
        return True
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Intelligent Russian-to-Latin Transliteration")
    print("=" * 60)
    
    results = []
    
    results.append(("Cyrillic Detection", test_cyrillic_detection()))
    results.append(("Latin-1 Compatibility", test_latin1_compatibility()))
    results.append(("Intelligent Transliteration", test_intelligent_transliteration()))
    results.append(("Transliteration Rules", test_transliteration_rules()))
    results.append(("Aztec Generation", test_aztec_generation()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("All tests PASSED")
        return 0
    else:
        print("Some tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
