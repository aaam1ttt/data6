#!/usr/bin/env python3
"""
Test build and imports
"""

import sys
import os
sys.path.append('.')

def test_build():
    """Test build and core imports"""
    try:
        from app import create_app
        app = create_app()
        print("SUCCESS: App creation successful")
        
        from app.core.codes import generate_aztec, generate_by_type
        print("SUCCESS: Aztec code imports successful")
        
        # Test Aztec generation
        aztec_img = generate_aztec("TEST", 300)
        print(f"SUCCESS: Aztec generation works - {aztec_img.size}")
        
        # Test via generate_by_type
        aztec_img2 = generate_by_type("AZTEC", "TEST", 300)
        print(f"SUCCESS: generate_by_type works for AZTEC - {aztec_img2.size}")
        
        print("\nBuild test PASSED!")
        return True
        
    except Exception as e:
        print(f"ERROR: Build test failed: {e}")
        return False

if __name__ == "__main__":
    test_build()