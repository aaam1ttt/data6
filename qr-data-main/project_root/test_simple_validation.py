#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

try:
    from app.core.codes import generate_code128, generate_pdf417, decode_auto, generate_qr
    from PIL import Image
    
    c128 = generate_code128('TEST123', 400, 'TEST123')
    pdf417 = generate_pdf417('TEST456', 400, 'TEST456')
    
    # Test decode function
    empty_img = Image.new('RGB', (100, 100), 'white')
    result = decode_auto(empty_img)
    
    # Test QR decode
    qr_img = generate_qr('test123', 300)
    qr_result = decode_auto(qr_img)
    
    print(f"SUCCESS: Code128={c128.size}, PDF417={pdf417.size}, Decode result type: {type(result)}")
    print(f"Decode empty result: {result}")
    print(f"QR decode result: {qr_result}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)