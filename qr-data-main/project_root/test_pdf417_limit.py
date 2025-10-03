#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to determine the maximum character limit for PDF417 encoding
"""

import pdf417gen

def test_pdf417_max_length():
    """Test different text lengths to find the actual PDF417 limit"""
    
    test_lengths = [100, 500, 1000, 1500, 1800, 2000, 2500, 2710, 2750]
    
    print("Testing PDF417 encoding limits...")
    print("-" * 50)
    
    max_working = 0
    
    for length in test_lengths:
        text = "A" * length
        try:
            codes = pdf417gen.encode(
                text,
                columns=15,  # Maximum columns
                security_level=1  # Minimum security
            )
            print(f"[OK] {length} символов: успешно")
            max_working = length
        except Exception as e:
            print(f"[FAIL] {length} символов: ошибка - {type(e).__name__}: {e}")
    
    print("-" * 50)
    print(f"Максимальная рабочая длина: {max_working} символов")
    
    # Test around the boundary to find exact limit
    if max_working > 0 and max_working < 3000:
        print("\nТочная проверка границы...")
        for length in range(max_working + 1, min(max_working + 100, 3000)):
            text = "A" * length
            try:
                codes = pdf417gen.encode(text, columns=15, security_level=1)
                max_working = length
            except:
                print(f"Точный лимит найден: {max_working} символов")
                break
    
    return max_working

if __name__ == "__main__":
    max_chars = test_pdf417_max_length()
    print(f"\n==> Рекомендуемый лимит для PDF417: {max_chars} символов")
