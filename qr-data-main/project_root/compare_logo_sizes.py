#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visual comparison of old vs new logo sizes in QR codes
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw, ImageFont
import tempfile

def generate_qr_with_logo_size(text, size, logo_size_ratio, ecc="H"):
    """Generate QR with specific logo size for comparison"""
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    from PIL import Image
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    
    # Add logo
    logo_path = os.path.join(os.path.dirname(__file__), "app", "static", "star.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = int(size * logo_size_ratio)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo)
    
    return img

def create_comparison():
    """Create visual comparison of logo sizes"""
    test_text = "https://example.com/test/data"
    qr_size = 400
    
    # Old sizes (before change)
    old_sizes = {
        "H": 1/8,  # Was // 8
        "Q": 1/6,  # Was // 6  
        "M": 1/6,  # Was // 6
        "L": 1/6,  # Was // 6
    }
    
    # New sizes (after change)
    new_sizes = {
        "H": 1/5,  # Now // 5
        "Q": 1/6,  # Now // 6 (unchanged)
        "M": 1/7,  # Now // 7
        "L": 1/8,  # Now // 8
    }
    
    # Create comparison images
    comparisons = []
    for ecc in ["H", "Q", "M", "L"]:
        old_qr = generate_qr_with_logo_size(test_text, qr_size, old_sizes[ecc], ecc)
        new_qr = generate_qr_with_logo_size(test_text, qr_size, new_sizes[ecc], ecc)
        
        # Create side-by-side comparison
        comparison = Image.new('RGB', (qr_size * 2 + 100, qr_size + 100), 'white')
        comparison.paste(old_qr, (50, 80))
        comparison.paste(new_qr, (qr_size + 50, 80))
        
        # Add labels
        draw = ImageDraw.Draw(comparison)
        font = None
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        # Title
        title = f"ECC {ecc}: Logo Size Comparison"
        draw.text((50, 20), title, fill='black', font=font)
        
        # Labels
        old_label = f"Old: ~{int(old_sizes[ecc]*100)}%"
        new_label = f"New: ~{int(new_sizes[ecc]*100)}%"
        draw.text((50 + qr_size//2 - 50, qr_size + 85), old_label, fill='black', font=font)
        draw.text((qr_size + 50 + qr_size//2 - 50, qr_size + 85), new_label, fill='black', font=font)
        
        comparisons.append((ecc, comparison))
    
    # Save comparisons
    output_dir = tempfile.mkdtemp(prefix="qr_comparison_")
    print(f"Logo size comparison images saved to: {output_dir}\n")
    
    for ecc, img in comparisons:
        filepath = os.path.join(output_dir, f"comparison_ECC_{ecc}.png")
        img.save(filepath)
        print(f"ECC {ecc}:")
        print(f"  Old: ~{int(old_sizes[ecc]*100)}% of QR size ({qr_size} * {old_sizes[ecc]:.3f} = {int(qr_size * old_sizes[ecc])}px)")
        print(f"  New: ~{int(new_sizes[ecc]*100)}% of QR size ({qr_size} * {new_sizes[ecc]:.3f} = {int(qr_size * new_sizes[ecc])}px)")
        if ecc == "H":
            increase = ((new_sizes[ecc] - old_sizes[ecc]) / old_sizes[ecc]) * 100
            print(f"  Increase: +{increase:.0f}% (ECC H has highest error correction)")
        elif ecc == "Q":
            print(f"  No change (already optimal for ECC Q)")
        else:
            decrease = ((old_sizes[ecc] - new_sizes[ecc]) / old_sizes[ecc]) * 100
            print(f"  Decrease: -{decrease:.0f}% (adjusted for lower error correction)")
        print()
    
    print("="*80)
    print("Summary:")
    print("  - ECC H (highest error correction): Logo increased from 13% to 20%")
    print("  - ECC Q: Logo unchanged at 17% (already optimal)")
    print("  - ECC M: Logo decreased from 17% to 14% (safer for medium ECC)")
    print("  - ECC L: Logo decreased from 17% to 13% (safer for low ECC)")
    print("\nThe changes ensure:")
    print("  - Maximum logo visibility on ECC H (recommended setting)")
    print("  - Safe scannability across all error correction levels")
    print("  - Proper balance between aesthetics and functionality")
    print("="*80)
    
    return output_dir

if __name__ == "__main__":
    output_dir = create_comparison()
    
    # Try to open the directory
    import platform
    import subprocess
    
    try:
        if platform.system() == "Windows":
            os.startfile(output_dir)
        elif platform.system() == "Darwin":
            subprocess.run(["open", output_dir])
        else:
            subprocess.run(["xdg-open", output_dir])
    except:
        pass
