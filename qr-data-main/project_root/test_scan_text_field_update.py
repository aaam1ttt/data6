"""
Test to verify scan text field properly updates with each new scan
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.core.codes import generate_qr
import qrcode


def test_scan_consecutive_codes():
    """Test scanning different QR codes consecutively"""
    print("\n=== Testing Consecutive Scan Updates ===\n")
    
    app = create_app()
    
    # Generate test QR codes with different content
    test_data = [
        ("https://example.com/first", "First QR Code"),
        ("https://example.com/second", "Second QR Code"),
        ("https://example.com/third", "Third QR Code"),
        ("https://example.com/first", "Repeat First QR Code"),
    ]
    
    test_dir = tempfile.mkdtemp(prefix="scan_update_test_")
    print(f"Test images saved to: {test_dir}\n")
    
    with app.test_client() as client:
        for data, description in test_data:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save test image
            filename = f"test_{data.split('/')[-1]}.png"
            filepath = os.path.join(test_dir, filename)
            img.save(filepath)
            
            # Scan via API
            with open(filepath, 'rb') as f:
                response = client.post('/scan/api', 
                                     data={'image': (f, filename)},
                                     content_type='multipart/form-data')
            
            # Verify response
            assert response.status_code == 200, f"Failed: {description} - Status {response.status_code}"
            result = response.get_json()
            assert result['ok'] == True, f"Failed: {description} - Not OK"
            assert result['text'] == data, f"Failed: {description} - Expected '{data}', got '{result['text']}'"
            
            print(f"✓ {description}: '{result['text']}'")
    
    print(f"\nAll scan update tests PASSED!")
    print(f"Test images: {test_dir}")
    return True


if __name__ == "__main__":
    try:
        success = test_scan_consecutive_codes()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
