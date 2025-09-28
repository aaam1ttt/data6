#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

try:
    from app import create_app
    app = create_app()
    print('Build successful')
    
    # Test the scan API functionality
    from app.core.codes import generate_qr, decode_auto
    from PIL import Image
    
    # Create a test QR code
    qr_img = generate_qr('test123', 300)
    result = decode_auto(qr_img)
    
    print(f'QR Test: Generated {qr_img.size}, Decoded: {result}')
    
    if result and len(result) > 0:
        print(f'First result: text="{result[0]["text"]}", type="{result[0]["type"]}"')
        
except Exception as e:
    print(f"BUILD ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)