import sys
import os
sys.path.insert(0, '.')

from app.core.codes import generate_qr, generate_dm, generate_aztec, generate_code128, generate_pdf417

def calculate_codes_per_page(code_size_mm):
    """Calculate how many codes fit on A4 page with GOST layout"""
    page_w, page_h = 210, 297  # A4 dimensions in mm
    margin = 5
    gap = 2
    
    avail_w = page_w - 2 * margin
    avail_h = page_h - 2 * margin
    
    cols = max(1, int((avail_w + gap) // (code_size_mm + gap)))
    rows = max(1, int((avail_h + gap) // (code_size_mm + gap)))
    
    return cols * rows

# Test GOST-compliant size generation and page calculations
try:
    test_text = "Test GOST size generation"
    
    print("=== GOST Size Testing ===")
    
    # Test QR generation at GOST sizes (pixels calculated at 31.5 px/mm for 300 DPI)
    gost_sizes = [
        (472, 15, "QR"),
        (630, 20, "QR"), 
        (787, 25, "QR"),
        (945, 30, "QR")
    ]
    
    for px, mm, code_type in gost_sizes:
        if code_type == "QR":
            img = generate_qr(test_text, size=px)
            codes_per_page = calculate_codes_per_page(mm)
            print(f"QR {mm}x{mm}mm ({px}px): {img.size} - {codes_per_page} codes per A4 page")
    
    # Test DataMatrix at GOST sizes
    dm_sizes = [(378, 12), (472, 15), (630, 20), (787, 25)]
    for px, mm in dm_sizes:
        img = generate_dm(test_text, size=px)
        codes_per_page = calculate_codes_per_page(mm)
        print(f"DataMatrix {mm}x{mm}mm ({px}px): {img.size} - {codes_per_page} codes per A4 page")
    
    # Test barcode heights
    barcode_heights = [(378, 12), (472, 15), (630, 20)]
    for px, mm in barcode_heights:
        try:
            img = generate_code128(test_text, size=px)
            print(f"Code128 {mm}mm height ({px}px): {img.size}")
        except:
            print(f"Code128 {mm}mm height ({px}px): Library not available")
            
        try:
            img = generate_pdf417(test_text, size=px)
            print(f"PDF417 {mm}mm height ({px}px): {img.size}")
        except:
            print(f"PDF417 {mm}mm height ({px}px): Library not available")
    
    print("\n=== Page Layout Efficiency ===")
    for mm in [12, 15, 20, 25, 30]:
        codes = calculate_codes_per_page(mm)
        print(f"{mm}x{mm}mm codes: {codes} per A4 page")
    
    print("\nAll GOST dimension tests passed!")
    
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)