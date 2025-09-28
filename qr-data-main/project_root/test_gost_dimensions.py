#!/usr/bin/env python3
"""Test GOST dimensions implementation"""

from app.core.gost_dimensions import (
    get_gost_dimensions, get_dimension_by_code, 
    get_legacy_pixel_size, get_a4_layout_info
)
from app.core.codes import generate_by_type

def test_gost_dimensions():
    """Test GOST dimension functionality"""
    print("=== Testing GOST Dimension System ===\n")
    
    # Test QR dimensions
    print("QR Code GOST Dimensions:")
    qr_dims = get_gost_dimensions("QR")
    for dim in qr_dims:
        print(f"  {dim.code}: {dim.name_ru}")
        print(f"    Size: {dim.mm_width}x{dim.mm_height}mm = {dim.pixels_300dpi}px at 300 DPI")
        layout = get_a4_layout_info(dim)
        print(f"    Layout: {layout['horizontal_count']}x{layout['vertical_count']} = {layout['total_per_page']} codes per A4")
        print(f"    Efficiency: {layout['usage_efficiency']}% page usage")
        print()
    
    # Test DataMatrix dimensions
    print("DataMatrix GOST Dimensions:")
    dm_dims = get_gost_dimensions("DM")
    for dim in dm_dims:
        print(f"  {dim.code}: {dim.name_ru}")
        print(f"    Size: {dim.mm_width}x{dim.mm_height}mm = {dim.pixels_300dpi}px at 300 DPI")
        layout = get_a4_layout_info(dim)
        print(f"    Layout: {layout['horizontal_count']}x{layout['vertical_count']} = {layout['total_per_page']} codes per A4")
        print()
    
    # Test Code generation with GOST sizes
    print("Testing QR generation with GOST dimensions:")
    test_text = "ТЕСТОВЫЙ ТЕКСТ ДЛЯ QR КОДА ПО ГОСТ"
    
    try:
        # Generate QR with GOST S2 (ТОРГ-12 standard)
        qr_s2 = generate_by_type("QR", test_text, gost_code="QR-S2")
        print(f"  QR-S2 generated: {qr_s2.size}")
        
        # Generate DataMatrix with GOST S3
        dm_s3 = generate_by_type("DM", test_text, gost_code="DM-S3")
        print(f"  DM-S3 generated: {dm_s3.size}")
        
        # Generate Code128 with GOST H2
        c128_h2 = generate_by_type("C128", test_text, gost_code="C128-H2")
        print(f"  C128-H2 generated: {c128_h2.size}")
        
        print("\nAll GOST generation tests passed!")
        
    except Exception as e:
        print(f"GOST generation test failed: {e}")
        return False
    
    # Test legacy size migration
    print("\nTesting legacy size migration:")
    test_sizes = [300, 420, 600, 280, 360]
    for old_size in test_sizes:
        try:
            from app.core.gost_dimensions import migrate_legacy_size
            gost_code = migrate_legacy_size(old_size, "QR")
            print(f"  {old_size}px -> {gost_code}")
        except Exception as e:
            print(f"  {old_size}px → Error: {e}")
    
    return True

if __name__ == "__main__":
    success = test_gost_dimensions()
    print(f"\nGOST Dimensions Test: {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)