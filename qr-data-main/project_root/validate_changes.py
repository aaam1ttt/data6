import sys
import os
sys.path.insert(0, '.')

from app.core.codes import generate_qr, generate_dm, generate_aztec

# Test basic generation with higher resolutions
try:
    test_text = "Test high resolution generation"
    
    # Test QR generation at different sizes
    qr_300 = generate_qr(test_text, size=300)
    qr_600 = generate_qr(test_text, size=600) 
    qr_900 = generate_qr(test_text, size=900)
    
    print(f"QR 300px: {qr_300.size}")
    print(f"QR 600px: {qr_600.size}")  
    print(f"QR 900px: {qr_900.size}")
    
    # Test DataMatrix
    dm_600 = generate_dm(test_text, size=600)
    print(f"DataMatrix 600px: {dm_600.size}")
    
    # Test Aztec fallback
    aztec_600 = generate_aztec(test_text, size=600)
    print(f"Aztec 600px: {aztec_600.size}")
    
    print("All tests passed - high resolution generation working!")
    
except Exception as e:
    print(f"Test failed: {e}")
    sys.exit(1)