#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

try:
    from app.core.codes import generate_code128, generate_pdf417
    c128 = generate_code128('TEST123', 400, 'TEST123')
    pdf417 = generate_pdf417('TEST456', 400, 'TEST456')
    print(f"SUCCESS: Code128={c128.size}, PDF417={pdf417.size}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)